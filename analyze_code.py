#!/usr/bin/env python3
"""
CLI interface for the Code Analysis Engine
"""

import argparse
import json
import sys
from pathlib import Path
from code_analyzer import CodeAnalysisEngine

def print_analysis_summary(result):
    """Print a formatted summary of analysis results"""
    
    if "error" in result:
        print(f"❌ Error: {result['error']}")
        return
    
    print(f"\n📁 File: {result['file_path']}")
    print(f"🔤 Language: {result['language'].upper()}")
    
    static = result['static_analysis']
    print(f"📊 Issues Found: {static['issues_found']}")
    
    if static['severity_breakdown']:
        print("📈 Severity Breakdown:")
        for severity, count in static['severity_breakdown'].items():
            if count > 0:
                print(f"   {severity.upper()}: {count}")
    
    # LLM Analysis
    llm = result.get('llm_analysis', {})
    if llm and "error" not in llm:
        print(f"\n🤖 AI Analysis:")
        print(f"   Quality Score: {llm.get('quality_score', 'N/A')}/10")
        
        priority_issues = llm.get('priority_issues', [])
        if priority_issues:
            print(f"\n🚨 Top Priority Issues:")
            for i, issue in enumerate(priority_issues[:3], 1):
                print(f"   {i}. {issue}")
        
        recommendations = llm.get('recommendations', [])
        if recommendations:
            print(f"\n💡 Key Recommendations:")
            for i, rec in enumerate(recommendations[:2], 1):
                print(f"   {i}. {rec}")
        
        security = llm.get('security_concerns', [])
        if security:
            print(f"\n🔒 Security Concerns:")
            for concern in security[:2]:
                print(f"   • {concern}")

def main():
    parser = argparse.ArgumentParser(description="Analyze code with static analysis + LLM feedback")
    parser.add_argument("path", help="File or directory to analyze")
    parser.add_argument("--output", "-o", help="Output file for detailed results (JSON)")
    parser.add_argument("--summary-only", "-s", action="store_true", help="Show summary only")
    
    args = parser.parse_args()
    
    if not Path(args.path).exists():
        print(f"❌ Path not found: {args.path}")
        sys.exit(1)
    
    print("🔍 Code Analysis Engine")
    print("=" * 40)
    
    engine = CodeAnalysisEngine()
    
    try:
        if Path(args.path).is_file():
            # Analyze single file
            result = engine.analyze_file(args.path)
            results = [result]
        else:
            # Analyze directory
            print(f"📂 Analyzing directory: {args.path}")
            results = engine.analyze_directory(args.path)
        
        # Print summaries
        for result in results:
            print_analysis_summary(result)
            print("-" * 40)
        
        # Save detailed results if requested
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(results, f, indent=2)
            print(f"\n📄 Detailed results saved to: {args.output}")
        
        # Summary statistics
        total_files = len(results)
        total_issues = sum(r.get('static_analysis', {}).get('issues_found', 0) for r in results)
        
        print(f"\n📈 Summary:")
        print(f"   Files analyzed: {total_files}")
        print(f"   Total issues: {total_issues}")
        
        if total_files > 0:
            avg_issues = total_issues / total_files
            print(f"   Average issues per file: {avg_issues:.1f}")
    
    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
