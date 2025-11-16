#!/usr/bin/env python3
"""
Code Review CLI - Intelligent Code Analysis Tool

Usage:
    python3 code_review_cli.py <file_or_directory> [options]
"""

import argparse
import json
import sys
from pathlib import Path
from smart_code_analyzer import SmartCodeAnalyzer

def print_analysis_summary(analysis):
    """Print formatted analysis summary"""
    
    if "error" in analysis:
        print(f"❌ {analysis['error']}")
        return
    
    print(f"\n📁 {analysis['file_path']}")
    print(f"🔤 Language: {analysis['language'].upper()}")
    print(f"📏 Lines of code: {analysis['lines_of_code']}")
    
    # Static analysis results
    static = analysis.get('static_analysis', {})
    if static.get('syntax_valid') is False:
        print(f"❌ Syntax Error: {static.get('syntax_error', 'Unknown')}")
    elif static.get('syntax_valid'):
        print(f"✅ Syntax: Valid")
    
    # LLM analysis results
    llm = analysis.get('llm_analysis', {})
    if llm and "error" not in llm:
        quality = llm.get('quality_score', 0)
        print(f"📊 Quality Score: {quality}/10")
        
        # Quality indicator
        if quality >= 8:
            print("🟢 Excellent code quality")
        elif quality >= 6:
            print("🟡 Good code quality with room for improvement")
        elif quality >= 4:
            print("🟠 Moderate code quality - needs attention")
        else:
            print("🔴 Poor code quality - significant issues")
        
        # Issues breakdown
        issues = llm.get('issues', [])
        if issues:
            severity_count = {'high': 0, 'medium': 0, 'low': 0}
            for issue in issues:
                severity = issue.get('severity', 'low')
                severity_count[severity] += 1
            
            print(f"\n🚨 Issues Found: {len(issues)}")
            for severity, count in severity_count.items():
                if count > 0:
                    emoji = {'high': '🔴', 'medium': '🟡', 'low': '🟢'}[severity]
                    print(f"   {emoji} {severity.upper()}: {count}")
        
        # Top recommendations
        recommendations = llm.get('recommendations', [])
        if recommendations:
            print(f"\n💡 Top Recommendations:")
            for i, rec in enumerate(recommendations[:3], 1):
                print(f"   {i}. {rec}")

def print_iterative_summary(results):
    """Print summary of iterative analysis"""
    
    print(f"\n🔄 Iterative Analysis Results")
    print(f"📁 File: {results['file_path']}")
    
    progress = results.get('progress_summary', {})
    if progress:
        initial_q = progress.get('initial_quality', 0)
        final_q = progress.get('final_quality', 0)
        improvement = progress.get('quality_improvement', 0)
        
        print(f"\n📈 Progress Summary:")
        print(f"   Initial Quality: {initial_q}/10")
        print(f"   Final Quality: {final_q}/10")
        print(f"   Improvement: {improvement:+.1f} points")
        
        issues_resolved = progress.get('issues_resolved', 0)
        if issues_resolved > 0:
            print(f"   Issues Resolved: {issues_resolved}")
        elif issues_resolved < 0:
            print(f"   New Issues Found: {abs(issues_resolved)}")
        else:
            print(f"   Issues Resolved: 0")
    
    # Show iteration details
    iterations = results.get('iterations', [])
    if len(iterations) > 1:
        print(f"\n📊 Quality Trend:")
        quality_scores = [iter_data['quality_score'] for iter_data in iterations]
        trend_line = " → ".join(f"{score}/10" for score in quality_scores)
        print(f"   {trend_line}")

def main():
    parser = argparse.ArgumentParser(
        description="Intelligent Code Analysis with LLM Feedback",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 code_review_cli.py myfile.py
  python3 code_review_cli.py src/ --recursive
  python3 code_review_cli.py app.py --iterative --iterations 3
  python3 code_review_cli.py . --output results.json --report report.md
        """
    )
    
    parser.add_argument("path", help="File or directory to analyze")
    parser.add_argument("--recursive", "-r", action="store_true", 
                       help="Recursively analyze directory")
    parser.add_argument("--iterative", "-i", action="store_true",
                       help="Run iterative analysis with improvements")
    parser.add_argument("--iterations", type=int, default=2,
                       help="Number of iterations for iterative analysis")
    parser.add_argument("--output", "-o", help="Save detailed results to JSON file")
    parser.add_argument("--report", help="Generate markdown report")
    parser.add_argument("--summary-only", "-s", action="store_true",
                       help="Show summary only")
    
    args = parser.parse_args()
    
    # Validate path
    path = Path(args.path)
    if not path.exists():
        print(f"❌ Path not found: {args.path}")
        sys.exit(1)
    
    print("🧠 Intelligent Code Review Tool")
    print("=" * 40)
    
    analyzer = SmartCodeAnalyzer()
    
    try:
        if path.is_file():
            # Single file analysis
            if args.iterative:
                print(f"🔄 Running iterative analysis on {path}")
                results = analyzer.iterative_improvement(str(path), args.iterations)
                print_iterative_summary(results)
                
                if args.report:
                    report = analyzer.generate_report(results)
                    with open(args.report, 'w') as f:
                        f.write(report)
                    print(f"\n📄 Report saved to: {args.report}")
                
                if args.output:
                    with open(args.output, 'w') as f:
                        json.dump(results, f, indent=2)
                    print(f"💾 Results saved to: {args.output}")
            
            else:
                # Single analysis
                analysis = analyzer.analyze_file(str(path))
                print_analysis_summary(analysis)
                
                if args.output:
                    with open(args.output, 'w') as f:
                        json.dump(analysis, f, indent=2)
                    print(f"\n💾 Results saved to: {args.output}")
        
        else:
            # Directory analysis
            print(f"📂 Analyzing directory: {path}")
            
            supported_extensions = {'.py', '.js', '.ts', '.java', '.go', '.rs'}
            files_to_analyze = []
            
            if args.recursive:
                for ext in supported_extensions:
                    files_to_analyze.extend(path.rglob(f"*{ext}"))
            else:
                for ext in supported_extensions:
                    files_to_analyze.extend(path.glob(f"*{ext}"))
            
            if not files_to_analyze:
                print("❌ No supported code files found")
                sys.exit(1)
            
            print(f"📋 Found {len(files_to_analyze)} files to analyze")
            
            all_results = []
            total_quality = 0
            total_issues = 0
            
            for file_path in files_to_analyze:
                print(f"\n🔍 Analyzing: {file_path.name}")
                
                analysis = analyzer.analyze_file(str(file_path))
                all_results.append(analysis)
                
                if "error" not in analysis:
                    llm = analysis.get('llm_analysis', {})
                    quality = llm.get('quality_score', 0)
                    issues = len(llm.get('issues', []))
                    
                    total_quality += quality
                    total_issues += issues
                    
                    print(f"   Quality: {quality}/10, Issues: {issues}")
                else:
                    print(f"   ❌ {analysis['error']}")
            
            # Summary statistics
            valid_analyses = [r for r in all_results if "error" not in r]
            if valid_analyses:
                avg_quality = total_quality / len(valid_analyses)
                print(f"\n📊 Summary Statistics:")
                print(f"   Files analyzed: {len(valid_analyses)}")
                print(f"   Average quality: {avg_quality:.1f}/10")
                print(f"   Total issues: {total_issues}")
                print(f"   Average issues per file: {total_issues / len(valid_analyses):.1f}")
            
            if args.output:
                with open(args.output, 'w') as f:
                    json.dump(all_results, f, indent=2)
                print(f"\n💾 All results saved to: {args.output}")
    
    except KeyboardInterrupt:
        print("\n⏹️  Analysis interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        sys.exit(1)
    
    print("\n✅ Analysis complete!")

if __name__ == "__main__":
    main()
