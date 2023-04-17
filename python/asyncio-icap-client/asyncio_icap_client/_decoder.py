import itertools
from enum import Enum, auto
from typing import Dict, List, Optional, Tuple, TypeVar, Union

from ._constants import ICAP_VERSION, NEWLINE
from ._sections import SectionType
from .errors import (
    EmptyEncapsulatedHeaderError,
    EncapsulatedBodyMissingError,
    EncapsulatedHeaderMissingError,
    InvalidChunkSizeError,
    InvalidChunkTerminatorError,
    InvalidEncapsulatedEntityOffsetError,
    InvalidEncapsulatedEntityTypeError,
    InvalidEncapsulatedHeaderError,
    InvalidHeaderError,
    InvalidProtocolError,
    InvalidStatusCodeError,
    InvalidStatusLineError,
)
from .response import ICAPResponse


class Incomplete:
    pass


INCOMPLETE = Incomplete()

T = TypeVar("T")
IncompleteOr = Union[Incomplete, T]


class ICAPDecoderState(Enum):
    DECODING_STATUS_LINE = auto()
    DECODING_HEADERS = auto()
    DECODING_SECTIONS = auto()


class ICAPResponseDecoder:
    _state: ICAPDecoderState
    _status: Optional[int]
    _reason: Optional[str]
    _headers: Dict[str, str]
    _sections: List[Tuple[SectionType, Optional[int]]]
    _chunked_body: bytearray
    _encapsulated_request_headers: Optional[bytes]
    _encapsulated_response_headers: Optional[bytes]
    _encapsulated_request_body: Optional[bytes]
    _encapsulated_response_body: Optional[bytes]
    _options_body: Optional[bytes]

    def __init__(self) -> None:
        self._buffer = bytearray()
        self._reset_state()

    def feed(self, data: bytes) -> None:
        self._buffer.extend(data)

    def decode_response(self) -> IncompleteOr[ICAPResponse]:
        if self._state is ICAPDecoderState.DECODING_STATUS_LINE:
            if isinstance(self._decode_status_line(), Incomplete):
                return INCOMPLETE
            self._state = ICAPDecoderState.DECODING_HEADERS
        if self._state is ICAPDecoderState.DECODING_HEADERS:
            if isinstance(self._decode_headers(), Incomplete):
                return INCOMPLETE
            self._state = ICAPDecoderState.DECODING_SECTIONS
        if self._state is ICAPDecoderState.DECODING_SECTIONS:
            if isinstance(self._decode_sections(), Incomplete):
                return INCOMPLETE
        assert self._status is not None and self._reason is not None
        response = ICAPResponse(
            status=self._status,
            reason=self._reason,
            headers=self._headers,
            encapsulated_request_headers=self._encapsulated_request_headers,
            encapsulated_response_headers=self._encapsulated_response_headers,
            encapsulated_request_body=self._encapsulated_request_body,
            encapsulated_response_body=self._encapsulated_response_body,
            options_body=self._options_body,
        )
        self._reset_state()
        return response

    def _decode_status_line(self) -> IncompleteOr[None]:
        line = self._decode_line()
        if isinstance(line, Incomplete):
            return INCOMPLETE
        fields = line.split(b" ", 2)
        if len(fields) != 3:
            raise InvalidStatusLineError()
        version, status_bytes, reason_bytes = fields
        if version != ICAP_VERSION:
            raise InvalidProtocolError()
        try:
            status = int(status_bytes)
        except ValueError as err:
            raise InvalidStatusCodeError() from err
        reason = reason_bytes.decode("ascii")
        self._status = status
        self._reason = reason
        return None

    def _decode_line(self) -> IncompleteOr[bytes]:
        newline = self._buffer.find(NEWLINE)
        if newline == -1:
            return INCOMPLETE
        line = self._buffer[0:newline]
        del self._buffer[0 : newline + len(NEWLINE)]
        return line

    def _decode_headers(self) -> IncompleteOr[None]:
        while not self._buffer.startswith(NEWLINE):
            if isinstance(self._decode_header(), Incomplete):
                return INCOMPLETE
        assert not isinstance(self._decode_line(), Incomplete)
        self._decode_encapsulated()
        return None

    def _decode_header(self) -> IncompleteOr[None]:
        line = self._decode_line()
        if isinstance(line, Incomplete):
            return INCOMPLETE
        fields = line.split(b":", 1)
        if len(fields) != 2:
            raise InvalidHeaderError()
        header_name = fields[0].decode("ascii")
        header_value = fields[1].strip().decode("ascii")
        self._headers[header_name] = header_value
        return None

    def _decode_encapsulated(self) -> None:
        encapsulated = self._lookup_header("Encapsulated")
        if encapsulated is None:
            raise EncapsulatedHeaderMissingError()
        sections: List[Tuple[SectionType, int]] = []
        for field in encapsulated.split(","):
            field = field.lstrip()
            key_value = field.split("=", 1)
            if len(key_value) != 2:
                raise InvalidEncapsulatedHeaderError()
            key, value = key_value
            try:
                section = SectionType(key)
            except ValueError as err:
                raise InvalidEncapsulatedEntityTypeError() from err
            try:
                offset = int(value)
            except ValueError as err:
                raise InvalidEncapsulatedEntityOffsetError() from err
            sections.append((section, offset))
        if not sections:
            raise EmptyEncapsulatedHeaderError()
        if not sections[-1][0].is_body():
            raise EncapsulatedBodyMissingError()
        assert not self._sections
        for (section1, offset1), (_, offset2) in itertools.zip_longest(
            sections, itertools.islice(sections, 1, None), fillvalue=(None, None)
        ):
            assert section1 is not None
            if offset1 is not None and offset2 is not None:
                if offset1 >= offset2:
                    raise InvalidEncapsulatedEntityOffsetError()
            if offset2 is None:
                self._sections.append((section1, None))
            else:
                assert offset1 is not None
                self._sections.append((section1, offset2 - offset1))
        return None

    def _decode_sections(self) -> IncompleteOr[None]:
        while self._sections:
            section, size = self._sections[0]
            if section in {
                SectionType.RequestBody,
                SectionType.ResponseBody,
                SectionType.OptionsBody,
            }:
                assert size is None
                if isinstance(self._decode_chunked_body(), Incomplete):
                    return INCOMPLETE
                self._sections.pop(0)
            elif section in {
                SectionType.RequestHeaders,
                SectionType.ResponseHeaders,
            }:
                assert size is not None
                if len(self._buffer) < size:
                    return INCOMPLETE
                data = self._buffer[0:size]
                del self._buffer[0:size]
                if section is SectionType.RequestHeaders:
                    self._encapsulated_request_headers = bytes(data)
                elif section is SectionType.ResponseHeaders:
                    self._encapsulated_response_headers = bytes(data)
                else:
                    assert False
                self._sections.pop(0)
            elif section in {SectionType.NullBody}:
                self._sections.pop(0)
            else:
                assert False
        return None

    def _decode_chunked_body(self) -> IncompleteOr[None]:
        # TODO: Support chunk extensions and trailers
        assert len(self._sections) == 1
        while True:
            newline = self._buffer.find(NEWLINE)
            if newline == -1:
                return INCOMPLETE
            chunk_content_start = newline + len(NEWLINE)
            try:
                chunk_size = int(self._buffer[0:newline], 16)
            except ValueError as err:
                raise InvalidChunkSizeError() from err
            if chunk_size < 0:
                raise InvalidChunkSizeError()
            chunk_content_end = chunk_content_start + chunk_size
            bytes_required = chunk_content_end + len(NEWLINE)
            if len(self._buffer) < bytes_required:
                return INCOMPLETE
            if (
                self._buffer[chunk_content_end : chunk_content_end + len(NEWLINE)]
                != NEWLINE
            ):
                raise InvalidChunkTerminatorError()
            data = self._buffer[chunk_content_start:chunk_content_end]
            del self._buffer[0:bytes_required]
            if chunk_size == 0:  # This is the last chunk
                section, _ = self._sections[0]
                if section is SectionType.RequestBody:
                    self._encapsulated_request_body = bytes(self._chunked_body)
                elif section is SectionType.ResponseBody:
                    self._encapsulated_response_body = bytes(self._chunked_body)
                elif section is SectionType.OptionsBody:
                    self._options_body = bytes(self._chunked_body)
                else:
                    assert False
                return None
            else:
                self._chunked_body.extend(data)

    def _reset_state(self) -> None:
        self._state = ICAPDecoderState.DECODING_STATUS_LINE
        self._status = None
        self._reason = None
        self._headers = {}
        self._sections = []
        self._chunked_body = bytearray()
        self._encapsulated_request_headers = None
        self._encapsulated_response_headers = None
        self._encapsulated_request_body = None
        self._encapsulated_response_body = None
        self._options_body = None

    def _lookup_header(self, name: str) -> Optional[str]:
        for header_name, header_value in self._headers.items():
            if name.lower() == header_name.lower():
                return header_value
        return None
