from enum import Enum


class SectionType(Enum):
    RequestHeaders = "req-hdr"
    ResponseHeaders = "res-hdr"
    RequestBody = "req-body"
    ResponseBody = "res-body"
    OptionsBody = "opt-body"
    NullBody = "null-body"

    def is_body(self) -> bool:
        return self in {
            SectionType.RequestBody,
            SectionType.ResponseBody,
            SectionType.OptionsBody,
            SectionType.NullBody,
        }
