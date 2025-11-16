#!/usr/bin/env python3
"""
Intelligent Code Analyzer with LLM Feedback

Runs static analysis tools based on programming language,
then uses LLM to analyze results and provide actionable feedback.
"""

import os
import json
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import boto3

@dataclass
class AnalysisResult:
    """Results from static analysis tools"""
    language: str
    file_path: str
    tool_results: Dict[str, Any]
    issues_found: int
    severity_breakdown: Dict[str, int]

class StaticAnalyzer:
    """Handles static analysis for different programming languages"""
    
    def __init__(self):
        self.analyzers = {
            'python': self._analyze_python,
            'javascript': self._analyze_javascript,
            'typescript': self._analyze_typescript,
            'java': self._analyze_java,
            'go': self._analyze_go,
            'rust': self._analyze_rust
        }
    
    def detect_language(self, file_path: str) -> Optional[str]:
        """Detect programming language from file extension"""
        ext_map = {
            '.py': 'python',
            '.js': 'javascript', 
            '.ts': 'typescript',
            '.java': 'java',
            '.go': 'go',
            '.rs': 'rust'
        }
        return ext_map.get(Path(file_path).suffix.lower())
    
    def analyze_file(self, file_path: str) -> AnalysisResult:
        """Run static analysis on a file"""
        language = self.detect_language(file_path)
        if not language:
            raise ValueError(f"Unsupported file type: {file_path}")
        
        analyzer = self.analyzers[language]
        tool_results = analyzer(file_path)
        
        # Count issues and severity
        issues_found = 0
        severity_breakdown = {'error': 0, 'warning': 0, 'info': 0}
        
        for tool, results in tool_results.items():
            if isinstance(results, list):
                issues_found += len(results)
                for issue in results:
                    severity = issue.get('severity', 'info').lower()
                    if severity in severity_breakdown:
                        severity_breakdown[severity] += 1
        
        return AnalysisResult(
            language=language,
            file_path=file_path,
            tool_results=tool_results,
            issues_found=issues_found,
            severity_breakdown=severity_breakdown
        )
    
    def _run_command(self, cmd: List[str], cwd: str = None) -> Dict[str, Any]:
        """Run command and return parsed results"""
        try:
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                cwd=cwd,
                timeout=30
            )
            return {
                'success': result.returncode == 0,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'returncode': result.returncode
            }
        except subprocess.TimeoutExpired:
            return {'success': False, 'error': 'Command timeout'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _analyze_python(self, file_path: str) -> Dict[str, Any]:
        """Analyze Python code"""
        results = {}
        
        # Flake8 - Style and error checking
        flake8_result = self._run_command(['flake8', '--format=json', file_path])
        if flake8_result['success']:
            try:
                results['flake8'] = json.loads(flake8_result['stdout']) if flake8_result['stdout'] else []
            except json.JSONDecodeError:
                results['flake8'] = self._parse_flake8_output(flake8_result['stdout'])
        
        # Pylint - Comprehensive analysis
        pylint_result = self._run_command(['pylint', '--output-format=json', file_path])
        if pylint_result['success']:
            try:
                results['pylint'] = json.loads(pylint_result['stdout'])
            except json.JSONDecodeError:
                results['pylint'] = []
        
        # Bandit - Security analysis
        bandit_result = self._run_command(['bandit', '-f', 'json', file_path])
        if bandit_result['success']:
            try:
                bandit_data = json.loads(bandit_result['stdout'])
                results['bandit'] = bandit_data.get('results', [])
            except json.JSONDecodeError:
                results['bandit'] = []
        
        return results
    
    def _analyze_javascript(self, file_path: str) -> Dict[str, Any]:
        """Analyze JavaScript code"""
        results = {}
        
        # ESLint
        eslint_result = self._run_command(['eslint', '--format=json', file_path])
        if eslint_result['success']:
            try:
                results['eslint'] = json.loads(eslint_result['stdout'])
            except json.JSONDecodeError:
                results['eslint'] = []
        
        return results
    
    def _analyze_typescript(self, file_path: str) -> Dict[str, Any]:
        """Analyze TypeScript code"""
        results = {}
        
        # TSLint/ESLint for TypeScript
        tslint_result = self._run_command(['tslint', '--format', 'json', file_path])
        if tslint_result['success']:
            try:
                results['tslint'] = json.loads(tslint_result['stdout'])
            except json.JSONDecodeError:
                results['tslint'] = []
        
        return results
    
    def _analyze_java(self, file_path: str) -> Dict[str, Any]:
        """Analyze Java code"""
        results = {}
        
        # SpotBugs (if available)
        # PMD (if available)
        # For now, basic compilation check
        javac_result = self._run_command(['javac', '-Xlint:all', file_path])
        results['javac'] = {
            'success': javac_result['success'],
            'warnings': javac_result['stderr'].split('\n') if javac_result['stderr'] else []
        }
        
        return results
    
    def _analyze_go(self, file_path: str) -> Dict[str, Any]:
        """Analyze Go code"""
        results = {}
        
        # go vet
        vet_result = self._run_command(['go', 'vet', file_path])
        results['go_vet'] = {
            'success': vet_result['success'],
            'issues': vet_result['stderr'].split('\n') if vet_result['stderr'] else []
        }
        
        # golint (if available)
        lint_result = self._run_command(['golint', file_path])
        if lint_result['success']:
            results['golint'] = lint_result['stdout'].split('\n') if lint_result['stdout'] else []
        
        return results
    
    def _analyze_rust(self, file_path: str) -> Dict[str, Any]:
        """Analyze Rust code"""
        results = {}
        
        # clippy
        clippy_result = self._run_command(['cargo', 'clippy', '--', '--allow', 'warnings'])
        results['clippy'] = {
            'success': clippy_result['success'],
            'output': clippy_result['stdout']
        }
        
        return results
    
    def _parse_flake8_output(self, output: str) -> List[Dict[str, Any]]:
        """Parse flake8 text output into structured format"""
        issues = []
        for line in output.strip().split('\n'):
            if ':' in line:
                parts = line.split(':', 3)
                if len(parts) >= 4:
                    issues.append({
                        'line': int(parts[1]) if parts[1].isdigit() else 0,
                        'column': int(parts[2]) if parts[2].isdigit() else 0,
                        'code': parts[3].strip().split()[0],
                        'message': parts[3].strip(),
                        'severity': 'warning'
                    })
        return issues

class LLMAnalyzer:
    """Uses LLM to analyze static analysis results and provide feedback"""
    
    def __init__(self, model_id: str = "anthropic.claude-3-sonnet-20240229-v1:0"):
        self.bedrock = boto3.client('bedrock-runtime', region_name='us-west-2')
        self.model_id = model_id
    
    def analyze_results(self, analysis_result: AnalysisResult, code_content: str) -> Dict[str, Any]:
        """Analyze static analysis results with LLM"""
        
        prompt = self._build_analysis_prompt(analysis_result, code_content)
        
        try:
            response = self.bedrock.invoke_model(
                modelId=self.model_id,
                body=json.dumps({
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": 2000,
                    "messages": [{"role": "user", "content": prompt}]
                })
            )
            
            result = json.loads(response['body'].read())
            return self._parse_llm_response(result['content'][0]['text'])
            
        except Exception as e:
            return {"error": f"LLM analysis failed: {e}"}
    
    def _build_analysis_prompt(self, analysis_result: AnalysisResult, code_content: str) -> str:
        """Build prompt for LLM analysis"""
        
        prompt = f"""Analyze the following {analysis_result.language} code and its static analysis results.

CODE:
```{analysis_result.language}
{code_content}
```

STATIC ANALYSIS RESULTS:
{json.dumps(analysis_result.tool_results, indent=2)}

SUMMARY:
- Issues found: {analysis_result.issues_found}
- Severity breakdown: {analysis_result.severity_breakdown}

Please provide:
1. **Priority Issues**: Top 3 most critical issues to fix
2. **Code Quality Assessment**: Overall code quality score (1-10) with reasoning
3. **Specific Recommendations**: Actionable fixes for each major issue
4. **Best Practices**: Suggestions for improving code quality
5. **Security Concerns**: Any security-related issues found

Format your response as JSON with these keys: priority_issues, quality_score, quality_reasoning, recommendations, best_practices, security_concerns."""
        
        return prompt
    
    def _parse_llm_response(self, response_text: str) -> Dict[str, Any]:
        """Parse LLM response into structured format"""
        try:
            # Try to extract JSON from response
            start = response_text.find('{')
            end = response_text.rfind('}') + 1
            if start >= 0 and end > start:
                json_str = response_text[start:end]
                return json.loads(json_str)
        except:
            pass
        
        # Fallback to text parsing
        return {
            "priority_issues": ["Parse error - see raw response"],
            "quality_score": 5,
            "quality_reasoning": "Could not parse LLM response",
            "recommendations": [response_text[:500] + "..."],
            "best_practices": [],
            "security_concerns": [],
            "raw_response": response_text
        }

class CodeAnalysisEngine:
    """Main engine that orchestrates analysis and feedback"""
    
    def __init__(self):
        self.static_analyzer = StaticAnalyzer()
        self.llm_analyzer = LLMAnalyzer()
    
    def analyze_file(self, file_path: str) -> Dict[str, Any]:
        """Complete analysis of a code file"""
        
        # Read file content
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                code_content = f.read()
        except Exception as e:
            return {"error": f"Could not read file: {e}"}
        
        # Run static analysis
        try:
            static_results = self.static_analyzer.analyze_file(file_path)
        except Exception as e:
            return {"error": f"Static analysis failed: {e}"}
        
        # Run LLM analysis
        llm_results = self.llm_analyzer.analyze_results(static_results, code_content)
        
        return {
            "file_path": file_path,
            "language": static_results.language,
            "static_analysis": {
                "issues_found": static_results.issues_found,
                "severity_breakdown": static_results.severity_breakdown,
                "tool_results": static_results.tool_results
            },
            "llm_analysis": llm_results,
            "timestamp": "2024-11-16T11:04:00Z"
        }
    
    def analyze_directory(self, directory_path: str) -> List[Dict[str, Any]]:
        """Analyze all supported files in a directory"""
        results = []
        
        for file_path in Path(directory_path).rglob("*"):
            if file_path.is_file() and self.static_analyzer.detect_language(str(file_path)):
                try:
                    result = self.analyze_file(str(file_path))
                    results.append(result)
                except Exception as e:
                    results.append({
                        "file_path": str(file_path),
                        "error": str(e)
                    })
        
        return results

def main():
    """Demo the code analysis system"""
    
    # Create sample Python file for testing
    sample_code = '''
import os
import sys

def calculate_average(numbers):
    total = 0
    for num in numbers:
        total += num
    return total / len(numbers)  # Potential division by zero

def process_file(filename):
    file = open(filename, 'r')  # File not closed
    data = file.read()
    return data

class MyClass:
    def __init__(self):
        self.value = 0
    
    def unused_method(self):  # Unused method
        pass

if __name__ == "__main__":
    numbers = [1, 2, 3, 4, 5]
    avg = calculate_average(numbers)
    print("Average:", avg)
    
    # Security issue - eval
    user_input = input("Enter expression: ")
    result = eval(user_input)
    print("Result:", result)
'''
    
    # Write sample file
    sample_file = "sample_code.py"
    with open(sample_file, 'w') as f:
        f.write(sample_code)
    
    print("🔍 Code Analysis Engine Demo")
    print("=" * 50)
    
    # Initialize analyzer
    engine = CodeAnalysisEngine()
    
    # Analyze the sample file
    print(f"Analyzing: {sample_file}")
    result = engine.analyze_file(sample_file)
    
    # Display results
    if "error" in result:
        print(f"❌ Error: {result['error']}")
        return
    
    print(f"\n📊 Analysis Results for {result['language'].upper()} code:")
    print(f"Issues found: {result['static_analysis']['issues_found']}")
    print(f"Severity breakdown: {result['static_analysis']['severity_breakdown']}")
    
    # Show LLM analysis
    llm_analysis = result['llm_analysis']
    if "error" not in llm_analysis:
        print(f"\n🤖 LLM Analysis:")
        print(f"Quality Score: {llm_analysis.get('quality_score', 'N/A')}/10")
        print(f"Reasoning: {llm_analysis.get('quality_reasoning', 'N/A')}")
        
        print(f"\n🚨 Priority Issues:")
        for i, issue in enumerate(llm_analysis.get('priority_issues', [])[:3], 1):
            print(f"  {i}. {issue}")
        
        print(f"\n💡 Recommendations:")
        for i, rec in enumerate(llm_analysis.get('recommendations', [])[:3], 1):
            print(f"  {i}. {rec}")
    
    # Save detailed results
    output_file = "analysis_results.json"
    with open(output_file, 'w') as f:
        json.dump(result, f, indent=2)
    
    print(f"\n📄 Detailed results saved to: {output_file}")
    
    # Clean up
    os.remove(sample_file)
    
    print("\n✅ Analysis complete!")

if __name__ == "__main__":
    main()
