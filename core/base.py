"""Base classes for the code analyzer system"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import logging

@dataclass
class AnalysisResult:
    """Standard analysis result structure"""
    file_path: str
    language: str
    quality_score: int
    issues: List[Dict[str, Any]]
    recommendations: List[str]
    metadata: Dict[str, Any] = None

@dataclass
class FixResult:
    """Standard fix result structure"""
    fixes_applied: int
    fixed_content: str
    fixes: List[Dict[str, Any]]
    success: bool
    error: Optional[str] = None

@dataclass
class TestResult:
    """Standard test result structure"""
    passed: bool
    syntax_valid: bool
    import_test: bool
    static_analysis: Dict[str, Any]
    error: Optional[str] = None

class BaseAnalyzer(ABC):
    """Base class for all analyzers"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.logger = logging.getLogger(self.__class__.__name__)
    
    @abstractmethod
    def analyze(self, file_path: str) -> AnalysisResult:
        """Analyze a file and return results"""
        pass
    
    def validate_file(self, file_path: str) -> bool:
        """Validate file exists and is supported"""
        from pathlib import Path
        return Path(file_path).exists() and Path(file_path).suffix in ['.py', '.js', '.ts', '.java', '.go', '.rs']

class BaseAgent(ABC):
    """Base class for Strands agents"""
    
    def __init__(self, name: str, system_prompt: str, tools: List = None):
        self.name = name
        self.system_prompt = system_prompt
        self.tools = tools or []
        self.logger = logging.getLogger(f"Agent.{name}")
    
    @abstractmethod
    def process(self, prompt: str) -> str:
        """Process a prompt and return response"""
        pass
    
    def log_interaction(self, prompt: str, response: str):
        """Log agent interaction"""
        self.logger.info(f"Prompt: {prompt[:100]}... Response: {response[:100]}...")

class BaseTool(ABC):
    """Base class for tools"""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.logger = logging.getLogger(f"Tool.{name}")
    
    @abstractmethod
    def execute(self, *args, **kwargs) -> Any:
        """Execute the tool"""
        pass
    
    def validate_input(self, *args, **kwargs) -> bool:
        """Validate tool input"""
        return True
