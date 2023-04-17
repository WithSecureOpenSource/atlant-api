class APIException(Exception):
    """API Error"""

    def __init__(self, message: str, long_description: str):
        super().__init__(message)
        self.long_description = long_description
