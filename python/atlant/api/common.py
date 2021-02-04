class APIException(Exception):
    """API Error"""

    def __init__(self, message, long_description):
        super().__init__(message)
        self.long_description = long_description
