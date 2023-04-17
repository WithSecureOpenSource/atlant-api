import hashlib
import json
import logging
import threading
from concurrent import futures
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, Union, cast

import requests

from atlant.auth import Scope
from atlant.cli import config_file
from atlant.scan import ScanClient, ScanContentMetadata, ScanMetadata, ScanResponse


def install(parser: Any) -> None:
    parser = parser.add_parser(
        "scan-dir",
        description="Scan all the files in a directory.",
    )
    parser.add_argument(
        "-r",
        "--recursive",
        action="store_true",
        help="Recursively scan files from subdirectories.",
    )
    parser.add_argument("dir", type=Path, help="Directory to scan.")
    parser.set_defaults(action=command)


def list_files(dir: Path, recursive: bool) -> Iterable[Path]:
    return (path for path in dir.glob("**" if recursive else "*") if path.is_file())


@dataclass
class FileScanResult:
    path: Path
    hash: str
    result: ScanResponse


def scan_files(
    session: requests.Session,
    config: config_file.Config,
    files: Iterable[Path],
) -> Iterable[FileScanResult]:
    # Here we do scanning in two steps: first, we try to scan the file using the
    # hash of its content without actually sending the full file for scanning.
    # For some files, this is enough and Atlant can identify the file using its
    # hash alone. For files where the hash is not enough to conclusively
    # identify the file, the response from Atlant will have the 'need_content'
    # warning set. In this case we proceed to send the file for a full scan.

    thread_context = threading.local()

    @dataclass
    class HashScanResult:
        hash: str
        response: ScanResponse

    @dataclass
    class HashScanContext:
        path: Path

    @dataclass
    class ContentScanContext:
        path: Path
        hash: str

    def initialize_thread() -> None:
        logging.debug("Initializing scanner thread.")
        thread_context.client = ScanClient(
            session,
            config.scanning_url,
            config.get_authenticator(session, [Scope.SCAN]),
        )

    def scan_with_content_hash(path: Path) -> HashScanResult:
        logging.debug(f"Scanning {path} using a hash of its content.")
        hash = hashlib.sha1(path.read_bytes()).hexdigest()
        scan_metadata = ScanMetadata(content_meta=ScanContentMetadata(sha1=hash))
        response = thread_context.client.scan_until_completion(scan_metadata)
        return HashScanResult(hash, response)

    def scan_with_content(path: Path) -> ScanResponse:
        logging.debug(f"Scanning {path} using its content.")
        with path.open("rb") as handle:
            return cast(
                ScanResponse,
                thread_context.client.scan_until_completion(ScanMetadata(), handle),
            )

    with futures.ThreadPoolExecutor(
        thread_name_prefix="ScanThread",
        initializer=initialize_thread,
    ) as thread_pool:
        task_contexts: Dict[
            futures.Future[Any], Union[HashScanContext, ContentScanContext]
        ] = {
            thread_pool.submit(scan_with_content_hash, path): HashScanContext(path)
            for path in files
        }
        tasks = set(task_contexts)

        while tasks:
            finished_tasks, tasks = futures.wait(
                tasks,
                return_when=futures.FIRST_COMPLETED,
            )
            for finished in finished_tasks:
                context = task_contexts.pop(finished)
                if isinstance(context, HashScanContext):
                    hash_scan_result: HashScanResult = finished.result()
                    # If the need_content flag is set in the response it means
                    # the result from the hash based scan is not conclusive and
                    # the file should be submitted for a full scan.
                    if hash_scan_result.response.warnings.need_content:
                        logging.debug(f"Submitting {context.path} for a content scan.")
                        future = thread_pool.submit(scan_with_content, context.path)
                        task_contexts[future] = ContentScanContext(
                            path=context.path,
                            hash=hash_scan_result.hash,
                        )
                        tasks.add(future)
                    else:
                        yield FileScanResult(
                            path=context.path,
                            hash=hash_scan_result.hash,
                            result=hash_scan_result.response,
                        )
                elif isinstance(context, ContentScanContext):
                    content_scan_result: ScanResponse = finished.result()
                    yield FileScanResult(
                        path=context.path,
                        hash=context.hash,
                        result=content_scan_result,
                    )
                else:
                    assert False


def command(
    *,
    session: requests.Session,
    config: config_file.Config,
    recursive: bool,
    dir: Path,
) -> None:
    results = {
        str(result.path): {
            "sha1_hash": result.hash,
            "result": json.loads(result.result.json()),
        }
        for result in scan_files(session, config, list_files(dir, recursive))
    }
    print(json.dumps(results, indent=2))
