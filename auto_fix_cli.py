#!/usr/bin/env python3
"""
Auto-Fix CLI - Automated code fixing with PR creation
"""

import argparse
import sys
from pathlib import Path
from auto_fix_pr import AutoFixWorkflow

def main():
    parser = argparse.ArgumentParser(
        description="Automatically fix code issues and create pull requests",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 auto_fix_cli.py myfile.py
  python3 auto_fix_cli.py src/main.py --dry-run
  python3 auto_fix_cli.py app.py --skip-pr
        """
    )
    
    parser.add_argument("file", help="Python file to analyze and fix")
    parser.add_argument("--dry-run", action="store_true", 
                       help="Analyze and generate fixes but don't apply them")
    parser.add_argument("--skip-pr", action="store_true",
                       help="Apply fixes but don't create pull request")
    parser.add_argument("--output", "-o", help="Save workflow results to JSON file")
    
    args = parser.parse_args()
    
    # Validate file
    if not Path(args.file).exists():
        print(f"❌ File not found: {args.file}")
        sys.exit(1)
    
    if not args.file.endswith('.py'):
        print(f"❌ Only Python files are currently supported")
        sys.exit(1)
    
    print("🤖 Automated Code Fix Workflow")
    print("=" * 40)
    
    try:
        workflow = AutoFixWorkflow()
        
        if args.dry_run:
            print("🔍 DRY RUN MODE - No changes will be made")
            # Just run analysis
            analysis = workflow.analyzer.analyze_file(args.file)
            
            if "error" in analysis:
                print(f"❌ Analysis failed: {analysis['error']}")
                sys.exit(1)
            
            llm_analysis = analysis.get('llm_analysis', {})
            issues = llm_analysis.get('issues', [])
            quality_score = llm_analysis.get('quality_score', 0)
            
            print(f"\n📊 Analysis Results:")
            print(f"   Quality Score: {quality_score}/10")
            print(f"   Issues Found: {len(issues)}")
            
            if issues:
                print(f"\n🚨 Issues that would be fixed:")
                for i, issue in enumerate(issues[:5], 1):
                    severity = issue.get('severity', 'unknown')
                    desc = issue.get('description', 'No description')
                    print(f"   {i}. [{severity.upper()}] {desc}")
            
            # Generate fixes preview
            fixes_data = workflow.fixer.generate_fixes(args.file, analysis)
            if "fixes" in fixes_data:
                fixes = fixes_data["fixes"]
                print(f"\n🛠️  Fixes that would be applied: {len(fixes)}")
                for i, fix in enumerate(fixes[:3], 1):
                    print(f"   {i}. {fix.get('issue_description', 'Code improvement')}")
        
        else:
            # Run full workflow
            results = workflow.run_auto_fix_workflow(args.file)
            
            # Print summary
            print(f"\n📊 Workflow Summary:")
            print(f"   File: {results['file_path']}")
            print(f"   Success: {'✅' if results['success'] else '❌'}")
            
            if results.get('pr_url'):
                print(f"   Pull Request: {results['pr_url']}")
            
            # Print step details
            print(f"\n📋 Steps:")
            for step in results['steps']:
                status = step['status']
                emoji = "✅" if status in ['completed', 'passed'] else "❌"
                step_name = step['step'].replace('_', ' ').title()
                print(f"   {emoji} {step_name}: {status}")
                
                # Show additional details
                if step['step'] == 'analysis' and 'issues_found' in step:
                    print(f"      Issues found: {step['issues_found']}")
                    print(f"      Quality score: {step['quality_score']}/10")
                elif step['step'] == 'fix_generation' and 'fixes_generated' in step:
                    print(f"      Fixes generated: {step['fixes_generated']}")
            
            # Save results if requested
            if args.output:
                import json
                with open(args.output, 'w') as f:
                    json.dump(results, f, indent=2)
                print(f"\n💾 Results saved to: {args.output}")
    
    except KeyboardInterrupt:
        print("\n⏹️  Workflow interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Workflow failed: {e}")
        sys.exit(1)
    
    print("\n✅ Auto-fix workflow complete!")

if __name__ == "__main__":
    main()
