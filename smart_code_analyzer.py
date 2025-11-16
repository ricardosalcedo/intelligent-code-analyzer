#!/usr/bin/env python3
"""
Smart Code Analyzer with LLM Feedback Loop

A robust system that analyzes code, provides intelligent feedback,
and tracks improvement over iterations.
"""

import json
import os
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional
import boto3

class SmartCodeAnalyzer:
    """Main analyzer with integrated feedback loop"""
    
    def __init__(self):
        self.bedrock = boto3.client('bedrock-runtime', region_name='us-west-2')
        self.model_id = "anthropic.claude-3-sonnet-20240229-v1:0"
        self.analysis_history = []
    
    def detect_language(self, file_path: str) -> Optional[str]:
        """Detect programming language"""
        ext_map = {
            '.py': 'python', '.js': 'javascript', '.ts': 'typescript',
            '.java': 'java', '.go': 'go', '.rs': 'rust', '.cpp': 'cpp',
            '.c': 'c', '.rb': 'ruby', '.php': 'php'
        }
        return ext_map.get(Path(file_path).suffix.lower())
    
    def run_static_analysis(self, file_path: str, language: str) -> Dict[str, Any]:
        """Run basic static analysis based on language"""
        
        results = {'tools_used': [], 'issues': []}
        
        if language == 'python':
            # Try flake8
            try:
                result = subprocess.run(
                    ['flake8', '--format=json', file_path],
                    capture_output=True, text=True, timeout=10
                )
                if result.returncode == 0 and result.stdout:
                    try:
                        flake8_issues = json.loads(result.stdout)
                        results['tools_used'].append('flake8')
                        results['issues'].extend(flake8_issues)
                    except json.JSONDecodeError:
                        pass
            except:
                pass
            
            # Basic Python syntax check
            try:
                with open(file_path, 'r') as f:
                    code = f.read()
                compile(code, file_path, 'exec')
                results['syntax_valid'] = True
            except SyntaxError as e:
                results['syntax_valid'] = False
                results['syntax_error'] = str(e)
        
        return results
    
    def analyze_with_llm(self, code_content: str, language: str, static_results: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze code with LLM"""
        
        prompt = f"""Analyze this {language} code for quality, security, and best practices:

```{language}
{code_content}
```

Static Analysis Results: {json.dumps(static_results, indent=2)}

Provide analysis in this JSON format:
{{
    "quality_score": <1-10>,
    "issues": [
        {{"type": "security|performance|style|bug", "severity": "high|medium|low", "description": "...", "line": <number>}}
    ],
    "recommendations": ["specific actionable advice"],
    "code_improvements": [
        {{"issue": "description", "fix": "specific code fix or pattern"}}
    ],
    "overall_assessment": "brief summary"
}}"""
        
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
            response_text = result['content'][0]['text']
            
            # Extract JSON from response
            try:
                start = response_text.find('{')
                end = response_text.rfind('}') + 1
                if start >= 0 and end > start:
                    json_str = response_text[start:end]
                    return json.loads(json_str)
            except:
                pass
            
            # Fallback parsing
            return {
                "quality_score": 5,
                "issues": [],
                "recommendations": ["Review the code manually"],
                "code_improvements": [],
                "overall_assessment": response_text[:200] + "...",
                "raw_response": response_text
            }
            
        except Exception as e:
            return {"error": f"LLM analysis failed: {e}"}
    
    def analyze_file(self, file_path: str) -> Dict[str, Any]:
        """Complete analysis of a single file"""
        
        # Basic validation
        if not os.path.exists(file_path):
            return {"error": f"File not found: {file_path}"}
        
        language = self.detect_language(file_path)
        if not language:
            return {"error": f"Unsupported file type: {file_path}"}
        
        # Read code
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                code_content = f.read()
        except Exception as e:
            return {"error": f"Could not read file: {e}"}
        
        # Run static analysis
        static_results = self.run_static_analysis(file_path, language)
        
        # Run LLM analysis
        llm_results = self.analyze_with_llm(code_content, language, static_results)
        
        # Compile results
        analysis = {
            "file_path": file_path,
            "language": language,
            "lines_of_code": len(code_content.split('\n')),
            "static_analysis": static_results,
            "llm_analysis": llm_results,
            "timestamp": "2024-11-16T11:04:00Z"
        }
        
        # Track in history
        self.analysis_history.append(analysis)
        
        return analysis
    
    def iterative_improvement(self, file_path: str, iterations: int = 2) -> Dict[str, Any]:
        """Run iterative analysis with improvement suggestions"""
        
        results = {
            "file_path": file_path,
            "iterations": [],
            "progress_summary": {}
        }
        
        current_file = file_path
        
        for i in range(iterations):
            print(f"\n🔄 Iteration {i + 1}/{iterations}")
            
            # Analyze current version
            analysis = self.analyze_file(current_file)
            
            if "error" in analysis:
                print(f"❌ Error in iteration {i + 1}: {analysis['error']}")
                break
            
            # Extract key metrics
            llm = analysis.get('llm_analysis', {})
            quality_score = llm.get('quality_score', 0)
            issues_count = len(llm.get('issues', []))
            
            print(f"   Quality Score: {quality_score}/10")
            print(f"   Issues Found: {issues_count}")
            
            iteration_data = {
                "iteration": i + 1,
                "analysis": analysis,
                "quality_score": quality_score,
                "issues_count": issues_count
            }
            
            results["iterations"].append(iteration_data)
            
            # Generate improved code for next iteration (if not last)
            if i < iterations - 1:
                improved_code = self.generate_improved_code(analysis)
                if improved_code:
                    # Create temporary file for next iteration
                    temp_file = f"temp_improved_{i + 1}.py"
                    with open(temp_file, 'w') as f:
                        f.write(improved_code)
                    current_file = temp_file
        
        # Calculate progress
        if len(results["iterations"]) >= 2:
            first = results["iterations"][0]
            last = results["iterations"][-1]
            
            results["progress_summary"] = {
                "initial_quality": first["quality_score"],
                "final_quality": last["quality_score"],
                "quality_improvement": last["quality_score"] - first["quality_score"],
                "initial_issues": first["issues_count"],
                "final_issues": last["issues_count"],
                "issues_resolved": first["issues_count"] - last["issues_count"]
            }
        
        # Clean up temp files
        for i in range(1, iterations):
            temp_file = f"temp_improved_{i}.py"
            if os.path.exists(temp_file):
                os.remove(temp_file)
        
        return results
    
    def generate_improved_code(self, analysis: Dict[str, Any]) -> Optional[str]:
        """Generate improved version of code based on analysis"""
        
        llm_analysis = analysis.get('llm_analysis', {})
        improvements = llm_analysis.get('code_improvements', [])
        
        if not improvements:
            return None
        
        # Read original code
        try:
            with open(analysis['file_path'], 'r') as f:
                original_code = f.read()
        except:
            return None
        
        # Apply simple text replacements (basic implementation)
        improved_code = original_code
        
        # This is a simplified approach - in practice, you'd use AST manipulation
        common_fixes = {
            'eval(': 'ast.literal_eval(',  # Security fix
            'open(': 'with open(',  # Resource management
            '== None': 'is None',  # Style fix
            '!= None': 'is not None',  # Style fix
        }
        
        for old, new in common_fixes.items():
            if old in improved_code:
                improved_code = improved_code.replace(old, new)
        
        return improved_code if improved_code != original_code else None
    
    def generate_report(self, results: Dict[str, Any]) -> str:
        """Generate comprehensive analysis report"""
        
        report = f"""# Code Analysis Report

## File: {results['file_path']}

## Summary
"""
        
        progress = results.get('progress_summary', {})
        if progress:
            report += f"""
- **Quality Improvement**: {progress.get('quality_improvement', 0):+.1f} points
- **Issues Resolved**: {progress.get('issues_resolved', 0)}
- **Final Quality Score**: {progress.get('final_quality', 'N/A')}/10
"""
        
        report += "\n## Iteration Details\n"
        
        for iteration in results.get('iterations', []):
            num = iteration['iteration']
            analysis = iteration['analysis']
            llm = analysis.get('llm_analysis', {})
            
            report += f"\n### Iteration {num}\n"
            report += f"- **Quality Score**: {iteration['quality_score']}/10\n"
            report += f"- **Issues Found**: {iteration['issues_count']}\n"
            
            if llm.get('overall_assessment'):
                report += f"- **Assessment**: {llm['overall_assessment']}\n"
            
            recommendations = llm.get('recommendations', [])
            if recommendations:
                report += "\n**Key Recommendations**:\n"
                for i, rec in enumerate(recommendations[:3], 1):
                    report += f"{i}. {rec}\n"
        
        return report

def demo_smart_analyzer():
    """Demo the smart code analyzer"""
    
    # Create sample code with various issues
    sample_code = '''
import os
import sys

def calculate_average(numbers):
    # Potential division by zero
    return sum(numbers) / len(numbers)

def read_file(filename):
    # File not properly closed
    file = open(filename, 'r')
    content = file.read()
    return content

def process_user_input():
    # Security vulnerability
    user_code = input("Enter Python code: ")
    result = eval(user_code)
    return result

def check_value(value):
    # Style issue
    if value == None:
        return False
    return True

class Calculator:
    def __init__(self):
        self.history = []
    
    def divide(self, a, b):
        # No zero check
        result = a / b
        self.history.append(result)
        return result

# Global variable (not ideal)
GLOBAL_CONFIG = {}

def main():
    calc = Calculator()
    numbers = [1, 2, 3, 4, 5]
    
    avg = calculate_average(numbers)
    print(f"Average: {avg}")
    
    # This will cause an error
    result = calc.divide(10, 0)

if __name__ == "__main__":
    main()
'''
    
    sample_file = "demo_code.py"
    with open(sample_file, 'w') as f:
        f.write(sample_code)
    
    print("🧠 Smart Code Analyzer with LLM Feedback")
    print("=" * 50)
    
    try:
        analyzer = SmartCodeAnalyzer()
        
        # Run iterative analysis
        results = analyzer.iterative_improvement(sample_file, iterations=2)
        
        # Generate report
        report = analyzer.generate_report(results)
        
        # Save results
        with open("smart_analysis_report.md", 'w') as f:
            f.write(report)
        
        with open("smart_analysis_results.json", 'w') as f:
            json.dump(results, f, indent=2)
        
        # Print summary
        print(f"\n📊 Analysis Complete!")
        progress = results.get('progress_summary', {})
        if progress:
            print(f"   Quality improvement: {progress.get('quality_improvement', 0):+.1f} points")
            print(f"   Issues resolved: {progress.get('issues_resolved', 0)}")
            print(f"   Final quality: {progress.get('final_quality', 'N/A')}/10")
        
        print(f"\n📄 Files generated:")
        print(f"   - Report: smart_analysis_report.md")
        print(f"   - Results: smart_analysis_results.json")
        
    finally:
        # Clean up
        if os.path.exists(sample_file):
            os.remove(sample_file)
    
    print("\n✅ Smart analysis complete!")

if __name__ == "__main__":
    demo_smart_analyzer()
