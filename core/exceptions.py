"""Custom exceptions for the code analyzer system"""

class CodeAnalyzerError(Exception):
    """Base exception for code analyzer"""
    pass

class AnalysisError(CodeAnalyzerError):
    """Raised when code analysis fails"""
    pass

class FixGenerationError(CodeAnalyzerError):
    """Raised when fix generation fails"""
    pass

class TestFailureError(CodeAnalyzerError):
    """Raised when tests fail"""
    pass

class PRCreationError(CodeAnalyzerError):
    """Raised when PR creation fails"""
    pass

class ConfigurationError(CodeAnalyzerError):
    """Raised when configuration is invalid"""
    pass

class UnsupportedFileTypeError(CodeAnalyzerError):
    """Raised when file type is not supported"""
    pass
