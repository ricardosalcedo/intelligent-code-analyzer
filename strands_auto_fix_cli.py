#!/usr/bin/env python3
"""
Strands-Powered Auto-Fix CLI

Combines Strands Agents coordination with the existing auto-fix workflow.
"""

import argparse
import sys
import json
from pathlib import Path
from strands_code_analyzer import StrandsCodeAnalyzer
from auto_fix_pr import AutoFixWorkflow

class StrandsAutoFixCLI:
    """CLI that uses Strands agents for coordinated auto-fix workflow"""
    
    def __init__(self):
        self.strands_analyzer = StrandsCodeAnalyzer()
        self.auto_fix_workflow = AutoFixWorkflow()
    
    def run_strands_workflow(self, file_path: str, mode: str = "full") -> dict:
        """Run Strands-coordinated workflow"""
        
        print("🤖 Strands Agents Auto-Fix Workflow")
        print("=" * 50)
        
        if mode == "analysis_only":
            # Use Strands agents for analysis only
            return self.strands_analyzer.analyze_with_agents(file_path)
        
        elif mode == "coordinated":
            # Use Strands for coordination, existing system for execution
            print("🎯 Using Strands agents for workflow coordination...")
            
            # Step 1: Strands analysis
            strands_results = self.strands_analyzer.analyze_with_agents(file_path)
            
            # Step 2: If Strands analysis is successful, use existing auto-fix for PR creation
            if strands_results['final_results']['workflow_success']:
                print("\n🔄 Executing auto-fix workflow with real PR creation...")
                auto_fix_results = self.auto_fix_workflow.run_auto_fix_workflow(file_path)
                
                # Combine results
                combined_results = {
                    'strands_analysis': strands_results,
                    'auto_fix_execution': auto_fix_results,
                    'workflow_type': 'coordinated'
                }
                
                return combined_results
            
            return strands_results
        
        else:  # full mode
            # Use existing auto-fix workflow enhanced with Strands coordination
            return self.auto_fix_workflow.run_auto_fix_workflow(file_path)
    
    def print_results_summary(self, results: dict, mode: str):
        """Print formatted results summary"""
        
        print(f"\n📊 Results Summary ({mode} mode):")
        
        if mode == "analysis_only":
            final = results['final_results']
            print(f"   Quality Score: {final['analysis']['quality_score']}/10")
            print(f"   Issues Found: {final['analysis']['total_issues']}")
            print(f"   Fixes Available: {final['fixes']['fixes_applied']}")
            print(f"   Agent Interactions: {len(results['agent_interactions'])}")
        
        elif mode == "coordinated":
            if 'auto_fix_execution' in results:
                strands = results['strands_analysis']['final_results']
                auto_fix = results['auto_fix_execution']
                
                print(f"   Strands Analysis: ✅")
                print(f"   Quality Score: {strands['analysis']['quality_score']}/10")
                print(f"   Auto-Fix Success: {'✅' if auto_fix['success'] else '❌'}")
                
                if auto_fix.get('pr_url'):
                    print(f"   Real PR Created: {auto_fix['pr_url']}")
            else:
                final = results['final_results']
                print(f"   Strands Workflow: {'✅' if final['workflow_success'] else '❌'}")
        
        else:  # full mode
            print(f"   Success: {'✅' if results['success'] else '❌'}")
            if results.get('pr_url'):
                print(f"   PR Created: {results['pr_url']}")

def main():
    parser = argparse.ArgumentParser(
        description="Strands-powered automated code analysis and fixing",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Modes:
  analysis_only   - Use Strands agents for analysis and coordination only
  coordinated     - Strands analysis + real auto-fix execution  
  full           - Complete auto-fix workflow (default)

Examples:
  python3 strands_auto_fix_cli.py myfile.py --mode analysis_only
  python3 strands_auto_fix_cli.py myfile.py --mode coordinated
  python3 strands_auto_fix_cli.py myfile.py  # full mode (default)
        """
    )
    
    parser.add_argument("file", help="Python file to analyze and fix")
    parser.add_argument("--mode", choices=["analysis_only", "coordinated", "full"], 
                       default="full", help="Workflow mode")
    parser.add_argument("--output", "-o", help="Save results to JSON file")
    parser.add_argument("--summary", "-s", help="Save agent summary to markdown file")
    
    args = parser.parse_args()
    
    # Validate file
    if not Path(args.file).exists():
        print(f"❌ File not found: {args.file}")
        sys.exit(1)
    
    if not args.file.endswith('.py'):
        print(f"❌ Only Python files are currently supported")
        sys.exit(1)
    
    try:
        # Initialize CLI
        cli = StrandsAutoFixCLI()
        
        # Run workflow
        results = cli.run_strands_workflow(args.file, args.mode)
        
        # Print summary
        cli.print_results_summary(results, args.mode)
        
        # Save results if requested
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(results, f, indent=2)
            print(f"\n💾 Results saved to: {args.output}")
        
        # Save agent summary if requested and available
        if args.summary and 'strands_analysis' in results:
            summary = cli.strands_analyzer.get_agent_summary(results['strands_analysis'])
            with open(args.summary, 'w') as f:
                f.write(summary)
            print(f"📄 Agent summary saved to: {args.summary}")
        elif args.summary and 'agent_interactions' in results:
            summary = cli.strands_analyzer.get_agent_summary(results)
            with open(args.summary, 'w') as f:
                f.write(summary)
            print(f"📄 Agent summary saved to: {args.summary}")
    
    except KeyboardInterrupt:
        print("\n⏹️  Workflow interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Workflow failed: {e}")
        sys.exit(1)
    
    print("\n✅ Strands-powered workflow complete!")

if __name__ == "__main__":
    main()
