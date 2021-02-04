import concurrent.futures as futures
import csv
import hashlib
import json
import logging
import sys
import threading
import traceback
from argparse import ArgumentParser
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from atlant.api import APIException, AuthClient, ScanClient, ScanResult

CSV_HEADER = ("FILENAME", "SHA-1", "RESULT", "DETECTIONS")

thread_ctx = threading.local()


@dataclass
class Config:
    authorization_address: str
    scanner_address: str
    client_id: str
    client_secret: str
    security_cloud: bool
    allow_upstream_application_files: bool
    allow_upstream_data_files: bool

    @classmethod
    def load(cls, path):
        with open(path) as handle:
            conf = json.load(handle)
        return cls(
            conf["authorization_address"],
            conf["scanner_address"],
            conf["client_id"],
            conf["client_secret"],
            conf.get("security_cloud", False),
            conf.get("allow_upstream_application_files", True),
            conf.get("allow_upstream_data_files", False),
        )


def scan_thread_initializer(
    authorization_address,
    scanning_address,
    client_id,
    client_secret,
):
    logging.debug("Initializing scanner thread")
    authenticator = AuthClient(authorization_address, client_id, client_secret)
    thread_ctx.scanner = ScanClient(scanning_address, authenticator)


def scan_metadata(path):
    logging.info("Metadata query for %s", path)
    hash = hashlib.sha1(path.read_bytes()).hexdigest()
    resp = thread_ctx.scanner.scan_until_complete(
        metadata={"content_meta": {"sha1": hash}}
    )
    return hash, resp


def scan_content(path, config):
    logging.info("Scanning %s", path)
    if config.security_cloud:
        metadata = {
            "scan_settings": {
                "security_cloud": {
                    "allow_upstream_application_files": config.allow_upstream_application_files,
                    "allow_upstream_data_files": config.allow_upstream_data_files,
                }
            }
        }
    else:
        metadata = None
    return thread_ctx.scanner.scan_until_complete(path.read_bytes(), metadata)


def files(root):
    yield from (
        entry.resolve() for entry in Path(root).rglob("*") if entry.is_file()
    )


def scan_files(config, paths):
    scanner_pool = futures.ThreadPoolExecutor(
        max_workers=None,
        thread_name_prefix="scanner",
        initializer=scan_thread_initializer,
        initargs=(
            config.authorization_address,
            config.scanner_address,
            config.client_id,
            config.client_secret,
        ),
    )
    metadata_scans = {
        scanner_pool.submit(scan_metadata, path): path for path in paths
    }
    content_scans = {}
    # We start by doing a metadata-only query for each file. This might be
    # enough to detect some of the files as malicious. If a file is classified
    # as clean at this phase we submit it for a full scan since metadata-only
    # scans might not detect all threats.
    for future in futures.as_completed(metadata_scans):
        path = metadata_scans[future]
        try:
            hash, response = future.result()
            logging.info("Received metadata query results for %s: %s", path, response.result.name)
        except Exception as err:
            print(
                "Failed to scan {}: {}\n{}".format(
                    path, err, traceback.format_exc()
                ),
                file=sys.stderr,
            )
            continue
        if response.result == ScanResult.CLEAN:
            content_scans[scanner_pool.submit(scan_content, path, config)] = (
                path,
                hash,
            )
        else:
            yield path, hash, response
    for future in futures.as_completed(content_scans):
        path, hash = content_scans[future]
        try:
            response = future.result()
            logging.info("Received scan results for %s: %s", path, response.result.name)
        except Exception as err:
            print(
                "Failed to scan {}: {}\n{}".format(
                    path, err, traceback.format_exc()
                ),
                file=sys.stderr,
            )
            continue
        yield path, hash, response


def parse_args():
    parser = ArgumentParser(description="Scan directory for harmful files.")
    parser.add_argument("--verbose", help="Enable extra output.", action="store_true")
    parser.add_argument("config", help="Configuration file path.")
    parser.add_argument("dir", help="Directory to scan.")
    parser.add_argument("output", help="Output file path.")
    return parser.parse_args()


def main():
    args = parse_args()
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)-15s (%(threadName)-0s): %(message)s",
    )

    try:
        config = Config.load(args.config)
    except Exception as er:
        print("Failed to load configuration: {}".format(er))
        exit(1)

    with open(args.output, "w") as handle:
        writer = csv.writer(handle)
        writer.writerow(CSV_HEADER)
        for path, hash, response in scan_files(
            config,
            files(args.dir),
        ):
            detections = ";".join(
                "{}".format(detection.name)
                for detection in response.detections
            )
            writer.writerow([path, hash, response.result.name, detections])
