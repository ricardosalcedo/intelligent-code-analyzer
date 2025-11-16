"""Interfaces for dependency injection and loose coupling"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any
from .base import AnalysisResult, FixResult, TestResult

class ICodeAnalyzer(ABC):
    """Interface for code analyzers"""
    
    @abstractmethod
    def analyze_file(self, file_path: str) -> AnalysisResult:
        pass
    
    @abstractmethod
    def detect_language(self, file_path: str) -> str:
        pass

class IFixGenerator(ABC):
    """Interface for fix generators"""
    
    @abstractmethod
    def generate_fixes(self, analysis: AnalysisResult, code_content: str) -> FixResult:
        pass
    
    @abstractmethod
    def apply_fixes(self, file_path: str, fix_result: FixResult) -> str:
        pass

class ITestRunner(ABC):
    """Interface for test runners"""
    
    @abstractmethod
    def run_tests(self, file_path: str) -> TestResult:
        pass
    
    @abstractmethod
    def validate_syntax(self, file_path: str) -> bool:
        pass

class IPRManager(ABC):
    """Interface for PR management"""
    
    @abstractmethod
    def create_branch(self, branch_name: str) -> bool:
        pass
    
    @abstractmethod
    def create_pull_request(self, branch_name: str, title: str, description: str) -> str:
        pass
    
    @abstractmethod
    def commit_changes(self, files: List[str], message: str) -> bool:
        pass

class ILLMProvider(ABC):
    """Interface for LLM providers"""
    
    @abstractmethod
    def generate_response(self, prompt: str, max_tokens: int = 2000) -> str:
        pass
    
    @abstractmethod
    def parse_structured_response(self, response: str) -> Dict[str, Any]:
        pass
