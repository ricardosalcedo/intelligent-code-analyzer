#!/usr/bin/env python3
"""
Enhanced Code Analyzer with Feedback Loop

Provides iterative code improvement suggestions and tracks progress.
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Any
from code_analyzer import CodeAnalysisEngine, LLMAnalyzer
import boto3

class FeedbackLoop:
    """Manages iterative code improvement feedback"""
    
    def __init__(self):
        self.llm_analyzer = LLMAnalyzer()
        self.history = []
    
    def generate_improvement_suggestions(self, analysis_result: Dict[str, Any], code_content: str) -> Dict[str, Any]:
        """Generate specific code improvement suggestions"""
        
        prompt = f"""Based on this code analysis, provide specific code improvements:

CURRENT CODE:
```python
{code_content}
```

ANALYSIS RESULTS:
{json.dumps(analysis_result.get('llm_analysis', {}), indent=2)}

Please provide:
1. **Specific Code Fixes**: Exact code snippets to replace problematic sections
2. **Refactored Functions**: Complete rewritten versions of problematic functions
3. **Security Improvements**: Secure alternatives for any security issues
4. **Performance Optimizations**: More efficient implementations
5. **Best Practice Examples**: Code examples following best practices

Format as JSON with keys: code_fixes, refactored_functions, security_improvements, performance_optimizations, best_practice_examples"""
        
        try:
            response = self.llm_analyzer.bedrock.invoke_model(
                modelId=self.llm_analyzer.model_id,
                body=json.dumps({
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": 3000,
                    "messages": [{"role": "user", "content": prompt}]
                })
            )
            
            result = json.loads(response['body'].read())
            return self.llm_analyzer._parse_llm_response(result['content'][0]['text'])
            
        except Exception as e:
            return {"error": f"Improvement generation failed: {e}"}
    
    def apply_suggestions(self, original_code: str, suggestions: Dict[str, Any]) -> str:
        """Apply improvement suggestions to code (simulation)"""
        
        improved_code = original_code
        
        # This is a simplified example - in practice, you'd use AST manipulation
        # or more sophisticated code transformation tools
        
        fixes = suggestions.get('code_fixes', [])
        for fix in fixes:
            if isinstance(fix, dict) and 'original' in fix and 'improved' in fix:
                improved_code = improved_code.replace(fix['original'], fix['improved'])
        
        return improved_code
    
    def track_progress(self, iteration: int, analysis_result: Dict[str, Any]):
        """Track improvement progress across iterations"""
        
        self.history.append({
            'iteration': iteration,
            'issues_found': analysis_result.get('static_analysis', {}).get('issues_found', 0),
            'quality_score': analysis_result.get('llm_analysis', {}).get('quality_score', 0),
            'severity_breakdown': analysis_result.get('static_analysis', {}).get('severity_breakdown', {}),
            'timestamp': analysis_result.get('timestamp')
        })
    
    def get_progress_summary(self) -> Dict[str, Any]:
        """Get summary of improvement progress"""
        
        if len(self.history) < 2:
            return {"message": "Need at least 2 iterations to show progress"}
        
        first = self.history[0]
        latest = self.history[-1]
        
        return {
            'iterations': len(self.history),
            'initial_issues': first['issues_found'],
            'current_issues': latest['issues_found'],
            'issues_resolved': first['issues_found'] - latest['issues_found'],
            'initial_quality': first['quality_score'],
            'current_quality': latest['quality_score'],
            'quality_improvement': latest['quality_score'] - first['quality_score'],
            'progress_trend': [h['quality_score'] for h in self.history]
        }

class EnhancedCodeAnalyzer:
    """Enhanced analyzer with feedback loop capabilities"""
    
    def __init__(self):
        self.engine = CodeAnalysisEngine()
        self.feedback_loop = FeedbackLoop()
    
    def iterative_analysis(self, file_path: str, max_iterations: int = 3) -> Dict[str, Any]:
        """Run iterative analysis with improvement suggestions"""
        
        results = {
            'file_path': file_path,
            'iterations': [],
            'final_summary': {}
        }
        
        # Read original code
        with open(file_path, 'r', encoding='utf-8') as f:
            current_code = f.read()
        
        original_code = current_code
        
        for iteration in range(max_iterations):
            print(f"\n🔄 Iteration {iteration + 1}/{max_iterations}")
            
            # Create temporary file for current iteration
            temp_file = f"temp_iteration_{iteration}.py"
            with open(temp_file, 'w') as f:
                f.write(current_code)
            
            try:
                # Analyze current code
                analysis = self.engine.analyze_file(temp_file)
                
                # Track progress
                self.feedback_loop.track_progress(iteration + 1, analysis)
                
                # Generate improvement suggestions
                suggestions = self.feedback_loop.generate_improvement_suggestions(analysis, current_code)
                
                iteration_result = {
                    'iteration': iteration + 1,
                    'analysis': analysis,
                    'suggestions': suggestions,
                    'code_length': len(current_code),
                    'lines_of_code': len(current_code.split('\n'))
                }
                
                results['iterations'].append(iteration_result)
                
                # Apply suggestions for next iteration (if not last)
                if iteration < max_iterations - 1:
                    if 'error' not in suggestions:
                        current_code = self.feedback_loop.apply_suggestions(current_code, suggestions)
                    
                    print(f"   Issues found: {analysis.get('static_analysis', {}).get('issues_found', 0)}")
                    print(f"   Quality score: {analysis.get('llm_analysis', {}).get('quality_score', 'N/A')}/10")
                
            finally:
                # Clean up temp file
                if os.path.exists(temp_file):
                    os.remove(temp_file)
        
        # Generate final summary
        progress = self.feedback_loop.get_progress_summary()
        results['final_summary'] = progress
        
        return results
    
    def generate_improvement_report(self, results: Dict[str, Any]) -> str:
        """Generate a comprehensive improvement report"""
        
        report = f"""# Code Analysis & Improvement Report

## File: {results['file_path']}

## Executive Summary
"""
        
        summary = results.get('final_summary', {})
        if 'iterations' in summary:
            report += f"""
- **Iterations Completed**: {summary['iterations']}
- **Issues Resolved**: {summary.get('issues_resolved', 0)}
- **Quality Improvement**: {summary.get('quality_improvement', 0):.1f} points
- **Final Quality Score**: {summary.get('current_quality', 'N/A')}/10
"""
        
        report += "\n## Iteration Details\n"
        
        for iteration_data in results.get('iterations', []):
            iteration = iteration_data['iteration']
            analysis = iteration_data['analysis']
            
            report += f"\n### Iteration {iteration}\n"
            
            static = analysis.get('static_analysis', {})
            llm = analysis.get('llm_analysis', {})
            
            report += f"- **Issues Found**: {static.get('issues_found', 0)}\n"
            report += f"- **Quality Score**: {llm.get('quality_score', 'N/A')}/10\n"
            
            if llm.get('priority_issues'):
                report += f"\n**Priority Issues**:\n"
                for i, issue in enumerate(llm['priority_issues'][:3], 1):
                    report += f"{i}. {issue}\n"
            
            if llm.get('recommendations'):
                report += f"\n**Recommendations**:\n"
                for i, rec in enumerate(llm['recommendations'][:3], 1):
                    report += f"{i}. {rec}\n"
        
        report += "\n## Progress Visualization\n"
        if 'progress_trend' in summary:
            trend = summary['progress_trend']
            report += f"Quality Score Trend: {' → '.join(map(str, trend))}\n"
        
        return report

def demo_enhanced_analyzer():
    """Demo the enhanced analyzer with feedback loop"""
    
    # Create a more complex sample with multiple issues
    complex_sample = '''
import os
import sys
import pickle

def divide_numbers(a, b):
    return a / b  # No zero check

def read_config(filename):
    f = open(filename)  # Not closed
    data = f.read()
    return eval(data)  # Security issue

def process_data(items):
    result = []
    for i in range(len(items)):  # Non-pythonic
        if items[i] != None:  # Should use 'is not'
            result.append(items[i] * 2)
    return result

class DataProcessor:
    def __init__(self):
        self.data = []
    
    def load_pickle(self, filename):
        with open(filename, 'rb') as f:
            self.data = pickle.load(f)  # Security issue
    
    def calculate_stats(self):
        if len(self.data) == 0:
            return None
        total = sum(self.data)
        return total / len(self.data)

# Global variables (bad practice)
GLOBAL_DATA = []

def main():
    processor = DataProcessor()
    numbers = [1, 2, 3, 4, 5]
    
    # Multiple issues in one line
    result = divide_numbers(10, 0)  # Will crash
    
    processed = process_data(numbers)
    print(processed)

if __name__ == "__main__":
    main()
'''
    
    # Write sample file
    sample_file = "complex_sample.py"
    with open(sample_file, 'w') as f:
        f.write(complex_sample)
    
    print("🚀 Enhanced Code Analyzer with Feedback Loop")
    print("=" * 60)
    
    try:
        # Run iterative analysis
        analyzer = EnhancedCodeAnalyzer()
        results = analyzer.iterative_analysis(sample_file, max_iterations=3)
        
        # Generate and save report
        report = analyzer.generate_improvement_report(results)
        
        report_file = "improvement_report.md"
        with open(report_file, 'w') as f:
            f.write(report)
        
        # Save detailed results
        results_file = "detailed_results.json"
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        # Print summary
        print(f"\n📊 Final Results:")
        summary = results['final_summary']
        if 'iterations' in summary:
            print(f"   Iterations: {summary['iterations']}")
            print(f"   Issues resolved: {summary.get('issues_resolved', 0)}")
            print(f"   Quality improvement: +{summary.get('quality_improvement', 0):.1f} points")
            print(f"   Final quality: {summary.get('current_quality', 'N/A')}/10")
        
        print(f"\n📄 Reports generated:")
        print(f"   - Improvement report: {report_file}")
        print(f"   - Detailed results: {results_file}")
        
    finally:
        # Clean up
        if os.path.exists(sample_file):
            os.remove(sample_file)
    
    print("\n✅ Enhanced analysis complete!")

if __name__ == "__main__":
    demo_enhanced_analyzer()
