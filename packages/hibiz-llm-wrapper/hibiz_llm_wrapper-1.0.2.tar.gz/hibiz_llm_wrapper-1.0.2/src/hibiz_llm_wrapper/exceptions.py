class LLMWrapperError(Exception):
    """Base exception for LLM Wrapper"""
    pass

class DatabaseError(LLMWrapperError):
    """Database-related errors"""
    pass

class APIError(LLMWrapperError):
    """API-related errors"""
    pass

class TokenizationError(LLMWrapperError):
    """Tokenization-related errors"""
    pass