"""Unified analyzer combining static and LLM analysis"""

from typing import Dict, List, Any
from core.base import BaseAnalyzer, AnalysisResult
from core.interfaces import ICodeAnalyzer
from core.exceptions import AnalysisError
from .static_analyzer import StaticAnalyzer
from .llm_analyzer import LLMAnalyzer

class UnifiedAnalyzer(BaseAnalyzer, ICodeAnalyzer):
    """Combines static and LLM analysis for comprehensive results"""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.static_analyzer = StaticAnalyzer(config)
        self.llm_analyzer = LLMAnalyzer(config)
    
    def analyze_file(self, file_path: str) -> AnalysisResult:
        """Analyze file using both static and LLM analysis"""
        if not self.validate_file(file_path):
            raise AnalysisError(f"Invalid file: {file_path}")
        
        try:
            # Run static analysis
            static_result = self.static_analyzer.analyze_file(file_path)
            
            # Run LLM analysis
            llm_result = self.llm_analyzer.analyze_file(file_path)
            
            # Combine results
            return self._combine_results(static_result, llm_result)
            
        except Exception as e:
            raise AnalysisError(f"Unified analysis failed for {file_path}: {e}")
    
    def detect_language(self, file_path: str) -> str:
        """Detect programming language"""
        return self.static_analyzer.detect_language(file_path)
    
    def _combine_results(self, static_result: AnalysisResult, llm_result: AnalysisResult) -> AnalysisResult:
        """Combine static and LLM analysis results"""
        
        # Merge issues, removing duplicates
        combined_issues = static_result.issues.copy()
        
        for llm_issue in llm_result.issues:
            if not self._is_duplicate_issue(llm_issue, combined_issues):
                combined_issues.append(llm_issue)
        
        # Calculate combined quality score (weighted average)
        static_weight = 0.4
        llm_weight = 0.6
        combined_score = int(
            static_result.quality_score * static_weight + 
            llm_result.quality_score * llm_weight
        )
        
        # Merge recommendations
        combined_recommendations = list(set(
            static_result.recommendations + llm_result.recommendations
        ))
        
        # Combine metadata
        combined_metadata = {
            'analyzer': 'unified',
            'static_metadata': static_result.metadata,
            'llm_metadata': llm_result.metadata,
            'total_issues': len(combined_issues)
        }
        
        return AnalysisResult(
            file_path=static_result.file_path,
            language=static_result.language,
            quality_score=combined_score,
            issues=combined_issues,
            recommendations=combined_recommendations,
            metadata=combined_metadata
        )
    
    def _is_duplicate_issue(self, new_issue: Dict[str, Any], existing_issues: List[Dict[str, Any]]) -> bool:
        """Check if issue is duplicate"""
        for existing in existing_issues:
            if (existing.get('type') == new_issue.get('type') and
                existing.get('line') == new_issue.get('line') and
                existing.get('description', '').lower() in new_issue.get('description', '').lower()):
                return True
        return False
