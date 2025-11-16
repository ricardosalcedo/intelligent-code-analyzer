"""Static code analysis implementation"""

import json
from typing import Dict, List, Any
from core.base import BaseAnalyzer, AnalysisResult
from core.interfaces import ICodeAnalyzer
from core.utils import FileUtils, ProcessUtils
from core.exceptions import AnalysisError, UnsupportedFileTypeError

class StaticAnalyzer(BaseAnalyzer, ICodeAnalyzer):
    """Static analysis implementation"""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.timeout = self.config.get('static_analysis_timeout', 30)
    
    def analyze_file(self, file_path: str) -> AnalysisResult:
        """Analyze file using static analysis tools"""
        if not self.validate_file(file_path):
            raise UnsupportedFileTypeError(f"Unsupported file: {file_path}")
        
        language = self.detect_language(file_path)
        if not language:
            raise UnsupportedFileTypeError(f"Could not detect language for: {file_path}")
        
        try:
            issues = self._run_static_analysis(file_path, language)
            quality_score = self._calculate_quality_score(issues)
            
            return AnalysisResult(
                file_path=file_path,
                language=language,
                quality_score=quality_score,
                issues=issues,
                recommendations=self._generate_recommendations(issues),
                metadata={'analyzer': 'static', 'tools_used': self._get_tools_used(language)}
            )
            
        except Exception as e:
            raise AnalysisError(f"Static analysis failed for {file_path}: {e}")
    
    def detect_language(self, file_path: str) -> str:
        """Detect programming language"""
        return FileUtils.detect_language(file_path)
    
    def _run_static_analysis(self, file_path: str, language: str) -> List[Dict[str, Any]]:
        """Run language-specific static analysis"""
        if language == 'python':
            return self._analyze_python(file_path)
        elif language in ['javascript', 'typescript']:
            return self._analyze_javascript(file_path)
        else:
            return []
    
    def _analyze_python(self, file_path: str) -> List[Dict[str, Any]]:
        """Analyze Python code"""
        issues = []
        
        # Flake8 analysis
        flake8_result = ProcessUtils.run_command(['flake8', '--format=json', file_path], self.timeout)
        if flake8_result['success'] and flake8_result['stdout']:
            try:
                flake8_issues = json.loads(flake8_result['stdout'])
                issues.extend(self._normalize_flake8_issues(flake8_issues))
            except json.JSONDecodeError:
                pass
        
        # Syntax validation
        try:
            content = FileUtils.read_file(file_path)
            compile(content, file_path, 'exec')
        except SyntaxError as e:
            issues.append({
                'type': 'syntax',
                'severity': 'high',
                'description': f'Syntax error: {e.msg}',
                'line': e.lineno,
                'tool': 'python_compiler'
            })
        
        return issues
    
    def _analyze_javascript(self, file_path: str) -> List[Dict[str, Any]]:
        """Analyze JavaScript/TypeScript code"""
        issues = []
        
        # ESLint analysis
        eslint_result = ProcessUtils.run_command(['eslint', '--format=json', file_path], self.timeout)
        if eslint_result['success'] and eslint_result['stdout']:
            try:
                eslint_issues = json.loads(eslint_result['stdout'])
                issues.extend(self._normalize_eslint_issues(eslint_issues))
            except json.JSONDecodeError:
                pass
        
        return issues
    
    def _normalize_flake8_issues(self, flake8_issues: List[Dict]) -> List[Dict[str, Any]]:
        """Normalize flake8 issues to standard format"""
        normalized = []
        for issue in flake8_issues:
            normalized.append({
                'type': 'style' if issue.get('code', '').startswith('E') else 'warning',
                'severity': 'medium',
                'description': issue.get('text', ''),
                'line': issue.get('line_number', 0),
                'column': issue.get('column_number', 0),
                'tool': 'flake8',
                'code': issue.get('code', '')
            })
        return normalized
    
    def _normalize_eslint_issues(self, eslint_issues: List[Dict]) -> List[Dict[str, Any]]:
        """Normalize ESLint issues to standard format"""
        normalized = []
        for file_result in eslint_issues:
            for message in file_result.get('messages', []):
                severity_map = {1: 'low', 2: 'high'}
                normalized.append({
                    'type': 'style',
                    'severity': severity_map.get(message.get('severity', 1), 'medium'),
                    'description': message.get('message', ''),
                    'line': message.get('line', 0),
                    'column': message.get('column', 0),
                    'tool': 'eslint',
                    'rule': message.get('ruleId', '')
                })
        return normalized
    
    def _calculate_quality_score(self, issues: List[Dict[str, Any]]) -> int:
        """Calculate quality score based on issues"""
        if not issues:
            return 10
        
        penalty = 0
        for issue in issues:
            severity = issue.get('severity', 'low')
            if severity == 'high':
                penalty += 3
            elif severity == 'medium':
                penalty += 2
            else:
                penalty += 1
        
        return max(1, 10 - min(penalty, 9))
    
    def _generate_recommendations(self, issues: List[Dict[str, Any]]) -> List[str]:
        """Generate recommendations based on issues"""
        recommendations = []
        
        issue_types = set(issue.get('type', '') for issue in issues)
        
        if 'syntax' in issue_types:
            recommendations.append("Fix syntax errors before proceeding")
        if 'style' in issue_types:
            recommendations.append("Follow coding style guidelines")
        if 'security' in issue_types:
            recommendations.append("Address security vulnerabilities immediately")
        
        return recommendations
    
    def _get_tools_used(self, language: str) -> List[str]:
        """Get list of tools used for analysis"""
        tools_map = {
            'python': ['flake8', 'python_compiler'],
            'javascript': ['eslint'],
            'typescript': ['eslint']
        }
        return tools_map.get(language, [])
