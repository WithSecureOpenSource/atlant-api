class ICAPProtocolError(Exception):
    """ICAP protocol error"""


class InvalidStatusLineError(ICAPProtocolError):
    pass


class InvalidProtocolError(ICAPProtocolError):
    pass


class InvalidStatusCodeError(ICAPProtocolError):
    pass


class InvalidHeaderError(ICAPProtocolError):
    pass


class EncapsulatedHeaderMissingError(ICAPProtocolError):
    pass


class InvalidEncapsulatedHeaderError(ICAPProtocolError):
    pass


class InvalidEncapsulatedEntityTypeError(ICAPProtocolError):
    pass


class InvalidEncapsulatedEntityOffsetError(ICAPProtocolError):
    pass


class EmptyEncapsulatedHeaderError(ICAPProtocolError):
    pass


class EncapsulatedBodyMissingError(ICAPProtocolError):
    pass


class InvalidChunkSizeError(ICAPProtocolError):
    pass


class InvalidChunkTerminatorError(ICAPProtocolError):
    pass


class InvalidSectionsError(ICAPProtocolError):
    pass
