import email.utils
from dataclasses import dataclass
from typing import Dict, Final, FrozenSet, List, Optional, Set

from asyncio_icap_client import ICAPClient, ICAPResponse
from fastapi import FastAPI, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import AnyUrl, BaseModel, BaseSettings

ICAP_HEADERS: Final[Dict[str, str]] = {
    "Allow": "204",
}


class Settings(BaseSettings):
    icap_host: str
    icap_port: int = 1344
    cors_allowed_origins: List[str] = []


settings = Settings()

app = FastAPI()

if settings.cors_allowed_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_allowed_origins,
        allow_credentials=False,
        allow_methods=["POST"],
        allow_headers=["*"],
    )


class ScanError(Exception):
    """Scan Error"""


def _get_header_list(response: ICAPResponse, header: str) -> List[str]:
    value = response.headers.get(header)
    if value is None:
        return []
    return [field.strip() for field in value.split(",")]


@dataclass
class ScanResponse:
    verdict: str
    infection_name: Optional[str]
    warnings: Set[str]
    categories: Set[str]

    @classmethod
    def from_icap_response(cls, response: ICAPResponse) -> "ScanResponse":
        if response.status not in {200, 204}:
            raise ScanError("Unexpected scan response status.")
        verdict = response.headers.get("X-FSecure-Scan-Result")
        if verdict is None:
            raise ScanError("Verdict missing from scan response.")
        infection_name = response.headers.get("X-FSecure-Infection-Name")
        if infection_name is not None:
            infection_name = email.utils.unquote(infection_name)
        warnings = set(_get_header_list(response, "X-FSecure-Warnings"))
        categories = set(_get_header_list(response, "X-Attribute"))
        return cls(
            verdict=verdict,
            infection_name=infection_name,
            warnings=warnings,
            categories=categories,
        )


class AnalyzeFileResponse(BaseModel):
    verdict: str
    infection_name: Optional[str] = None


@app.post("/analysis/file/content/")
async def analyze_file_contents(file: UploadFile) -> AnalyzeFileResponse:
    async with ICAPClient(
        settings.icap_host,
        settings.icap_port,
        headers=ICAP_HEADERS,
    ) as connection:
        icap_response = await connection.respmod(
            "/respmod", encapsulated_response_body=file
        )
        response = ScanResponse.from_icap_response(icap_response)
        return AnalyzeFileResponse(
            verdict=response.verdict,
            infection_name=response.infection_name,
        )


SHA1_LENGTH: Final[int] = 40
SHA1_CHARACTERS: Final[FrozenSet[str]] = frozenset("0123456789abcdef")


def is_valid_sha1(value: str) -> bool:
    return len(value) == SHA1_LENGTH or all(c in SHA1_CHARACTERS for c in value.lower())


@app.post("/analysis/file/sha1/{sha1}")
async def analyze_file_sha1(sha1: str) -> AnalyzeFileResponse:
    async with ICAPClient(
        settings.icap_host,
        settings.icap_port,
        headers=ICAP_HEADERS,
    ) as connection:
        if not is_valid_sha1(sha1):
            raise HTTPException(422, detail="Invalid SHA1 hash.")
        icap_response = await connection.respmod(
            "/respmod", headers={"X-Meta-SHA1": sha1}
        )
        response = ScanResponse.from_icap_response(icap_response)
        if "need_content" in response.warnings:
            return AnalyzeFileResponse(verdict="content_required")
        return AnalyzeFileResponse(
            verdict=response.verdict,
            infection_name=response.infection_name,
        )


class AnalyzeUrlResponse(BaseModel):
    verdict: str
    categories: Set[str]


@app.post("/analysis/url/{url:path}")
async def analyze_url(url: AnyUrl) -> AnalyzeUrlResponse:
    async with ICAPClient(
        settings.icap_host,
        settings.icap_port,
        headers=ICAP_HEADERS,
    ) as connection:
        icap_response = await connection.reqmod("/reqmod", headers={"X-Meta-URI": url})
        response = ScanResponse.from_icap_response(icap_response)
        return AnalyzeUrlResponse(
            verdict=response.verdict,
            categories=response.categories,
        )
