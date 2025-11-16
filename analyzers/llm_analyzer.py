"""LLM-based code analysis implementation"""

from typing import Dict, List, Any
from core.base import BaseAnalyzer, AnalysisResult
from core.interfaces import ICodeAnalyzer, ILLMProvider
from core.utils import FileUtils, LLMUtils
from core.exceptions import AnalysisError

class LLMAnalyzer(BaseAnalyzer, ICodeAnalyzer, ILLMProvider):
    """LLM-based analysis implementation"""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.llm_utils = LLMUtils(
            region=self.config.get('aws_region', 'us-west-2'),
            model_id=self.config.get('model_id', 'anthropic.claude-3-sonnet-20240229-v1:0')
        )
        self.max_tokens = self.config.get('max_tokens', 2000)
    
    def analyze(self, file_path: str) -> AnalysisResult:
        """Analyze file using LLM (BaseAnalyzer method)"""
        return self.analyze_file(file_path)
    
    def analyze_file(self, file_path: str) -> AnalysisResult:
        """Analyze file using LLM"""
        if not self.validate_file(file_path):
            raise AnalysisError(f"Invalid file: {file_path}")
        
        language = self.detect_language(file_path)
        code_content = FileUtils.read_file(file_path)
        
        try:
            llm_response = self._analyze_with_llm(code_content, language)
            
            return AnalysisResult(
                file_path=file_path,
                language=language,
                quality_score=llm_response.get('quality_score', 5),
                issues=llm_response.get('issues', []),
                recommendations=llm_response.get('recommendations', []),
                metadata={'analyzer': 'llm', 'model': self.llm_utils.model_id}
            )
            
        except Exception as e:
            raise AnalysisError(f"LLM analysis failed for {file_path}: {e}")
    
    def detect_language(self, file_path: str) -> str:
        """Detect programming language"""
        return FileUtils.detect_language(file_path)
    
    def generate_response(self, prompt: str, max_tokens: int = None) -> str:
        """Generate LLM response"""
        return self.llm_utils.generate_response(prompt, max_tokens or self.max_tokens)
    
    def parse_structured_response(self, response: str) -> Dict[str, Any]:
        """Parse structured response from LLM"""
        return self.llm_utils.parse_json_response(response)
    
    def _analyze_with_llm(self, code_content: str, language: str) -> Dict[str, Any]:
        """Analyze code with LLM"""
        prompt = self._build_analysis_prompt(code_content, language)
        response = self.generate_response(prompt)
        
        try:
            return self.parse_structured_response(response)
        except ValueError:
            # Fallback parsing
            return self._fallback_parse(response)
    
    def _build_analysis_prompt(self, code_content: str, language: str) -> str:
        """Build analysis prompt for LLM"""
        return f"""Analyze this {language} code for quality, security, and best practices:

```{language}
{code_content}
```

Provide analysis in this JSON format:
{{
    "quality_score": <1-10>,
    "issues": [
        {{"type": "security|performance|style|bug", "severity": "high|medium|low", "description": "...", "line": <number>}}
    ],
    "recommendations": ["specific actionable advice"],
    "overall_assessment": "brief summary"
}}"""
    
    def _fallback_parse(self, response: str) -> Dict[str, Any]:
        """Fallback parsing when JSON extraction fails"""
        return {
            "quality_score": 5,
            "issues": [],
            "recommendations": ["Review the code manually"],
            "overall_assessment": response[:200] + "...",
            "raw_response": response
        }
