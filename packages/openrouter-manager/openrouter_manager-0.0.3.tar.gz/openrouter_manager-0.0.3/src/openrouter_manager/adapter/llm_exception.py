class LLMException(Exception):
    """Custom exception class for LLM errors."""

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message

    def __str__(self):
        return f"LLMException: {self.message}"
