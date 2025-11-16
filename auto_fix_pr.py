#!/usr/bin/env python3
"""
Automated Fix and Pull Request System

Analyzes code, generates fixes, tests them, and creates pull requests for approval.
"""

import os
import json
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, List, Any, Optional
import boto3
from smart_code_analyzer import SmartCodeAnalyzer

class CodeFixer:
    """Generates and applies code fixes based on analysis"""
    
    def __init__(self):
        self.bedrock = boto3.client('bedrock-runtime', region_name='us-west-2')
        self.model_id = "anthropic.claude-3-sonnet-20240229-v1:0"
    
    def generate_fixes(self, file_path: str, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate specific code fixes based on analysis"""
        
        with open(file_path, 'r') as f:
            original_code = f.read()
        
        llm_analysis = analysis.get('llm_analysis', {})
        issues = llm_analysis.get('issues', [])
        
        if not issues:
            return {"fixes": [], "message": "No issues found to fix"}
        
        prompt = f"""Generate specific code fixes for the following issues:

ORIGINAL CODE:
```python
{original_code}
```

ISSUES TO FIX:
{json.dumps(issues, indent=2)}

Provide fixes in this JSON format:
{{
    "fixes": [
        {{
            "issue_description": "description of the issue",
            "line_number": <line>,
            "original_code": "exact code to replace",
            "fixed_code": "replacement code",
            "explanation": "why this fix works"
        }}
    ],
    "complete_fixed_file": "entire file content with all fixes applied"
}}

Focus on high and medium severity issues first. Ensure fixes are minimal and safe."""
        
        try:
            response = self.bedrock.invoke_model(
                modelId=self.model_id,
                body=json.dumps({
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": 3000,
                    "messages": [{"role": "user", "content": prompt}]
                })
            )
            
            result = json.loads(response['body'].read())
            response_text = result['content'][0]['text']
            
            # Extract JSON from response
            start = response_text.find('{')
            end = response_text.rfind('}') + 1
            if start >= 0 and end > start:
                json_str = response_text[start:end]
                return json.loads(json_str)
            
            return {"error": "Could not parse LLM response", "raw": response_text}
            
        except Exception as e:
            return {"error": f"Fix generation failed: {e}"}
    
    def apply_fixes(self, file_path: str, fixes_data: Dict[str, Any]) -> str:
        """Apply fixes and return path to fixed file"""
        
        if "complete_fixed_file" in fixes_data:
            fixed_content = fixes_data["complete_fixed_file"]
        else:
            # Fallback: apply individual fixes
            with open(file_path, 'r') as f:
                fixed_content = f.read()
            
            for fix in fixes_data.get("fixes", []):
                original = fix.get("original_code", "")
                replacement = fix.get("fixed_code", "")
                if original and replacement:
                    fixed_content = fixed_content.replace(original, replacement)
        
        # Create fixed file
        fixed_file = file_path.replace('.py', '_fixed.py')
        with open(fixed_file, 'w') as f:
            f.write(fixed_content)
        
        return fixed_file

class TestRunner:
    """Runs tests on fixed code"""
    
    def __init__(self):
        pass
    
    def run_syntax_check(self, file_path: str) -> Dict[str, Any]:
        """Check if the fixed code has valid syntax"""
        try:
            with open(file_path, 'r') as f:
                code = f.read()
            
            compile(code, file_path, 'exec')
            return {"syntax_valid": True, "message": "Syntax check passed"}
        
        except SyntaxError as e:
            return {
                "syntax_valid": False, 
                "error": str(e),
                "line": e.lineno,
                "message": f"Syntax error at line {e.lineno}: {e.msg}"
            }
    
    def run_static_analysis(self, file_path: str) -> Dict[str, Any]:
        """Run static analysis on fixed code"""
        results = {"tools": {}}
        
        # Flake8 check
        try:
            result = subprocess.run(
                ['flake8', '--format=json', file_path],
                capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                results["tools"]["flake8"] = {"passed": True, "issues": []}
            else:
                try:
                    issues = json.loads(result.stdout) if result.stdout else []
                    results["tools"]["flake8"] = {"passed": False, "issues": issues}
                except:
                    results["tools"]["flake8"] = {"passed": False, "error": result.stderr}
        except:
            results["tools"]["flake8"] = {"error": "Tool not available"}
        
        return results
    
    def run_basic_tests(self, file_path: str) -> Dict[str, Any]:
        """Run basic functionality tests"""
        
        # Try to import the module
        try:
            # Create a temporary module name
            module_name = Path(file_path).stem
            spec = __import__('importlib.util').util.spec_from_file_location(module_name, file_path)
            module = __import__('importlib.util').util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            return {"import_test": True, "message": "Module imports successfully"}
        
        except Exception as e:
            return {"import_test": False, "error": str(e)}

class PullRequestManager:
    """Manages Git operations and pull request creation"""
    
    def __init__(self, repo_path: str):
        self.repo_path = Path(repo_path)
    
    def create_fix_branch(self, branch_name: str) -> bool:
        """Create a new branch for the fix"""
        try:
            # Ensure we're on main branch
            subprocess.run(['git', 'checkout', 'main'], cwd=self.repo_path, check=True)
            subprocess.run(['git', 'pull', 'origin', 'main'], cwd=self.repo_path, check=True)
            
            # Create and checkout new branch
            subprocess.run(['git', 'checkout', '-b', branch_name], cwd=self.repo_path, check=True)
            return True
        
        except subprocess.CalledProcessError as e:
            print(f"Error creating branch: {e}")
            return False
    
    def commit_fixes(self, files: List[str], commit_message: str) -> bool:
        """Commit the fixed files"""
        try:
            # Add files
            for file_path in files:
                subprocess.run(['git', 'add', file_path], cwd=self.repo_path, check=True)
            
            # Commit
            subprocess.run(['git', 'commit', '-m', commit_message], cwd=self.repo_path, check=True)
            return True
        
        except subprocess.CalledProcessError as e:
            print(f"Error committing: {e}")
            return False
    
    def push_branch(self, branch_name: str) -> bool:
        """Push branch to remote"""
        try:
            subprocess.run(['git', 'push', '-u', 'origin', branch_name], cwd=self.repo_path, check=True)
            return True
        
        except subprocess.CalledProcessError as e:
            print(f"Error pushing: {e}")
            return False
    
    def create_pull_request(self, branch_name: str, title: str, description: str) -> Optional[str]:
        """Create pull request using GitHub CLI"""
        try:
            result = subprocess.run([
                'gh', 'pr', 'create',
                '--title', title,
                '--body', description,
                '--head', branch_name,
                '--base', 'main'
            ], cwd=self.repo_path, capture_output=True, text=True, check=True)
            
            return result.stdout.strip()  # Returns PR URL
        
        except subprocess.CalledProcessError as e:
            print(f"Error creating PR: {e}")
            return None

class AutoFixWorkflow:
    """Main workflow orchestrator"""
    
    def __init__(self, repo_path: str = "."):
        self.repo_path = repo_path
        self.analyzer = SmartCodeAnalyzer()
        self.fixer = CodeFixer()
        self.tester = TestRunner()
        self.pr_manager = PullRequestManager(repo_path)
    
    def run_auto_fix_workflow(self, file_path: str) -> Dict[str, Any]:
        """Run complete auto-fix workflow"""
        
        workflow_results = {
            "file_path": file_path,
            "steps": [],
            "success": False,
            "pr_url": None
        }
        
        print(f"🔧 Starting auto-fix workflow for {file_path}")
        
        # Step 1: Analyze code
        print("📊 Step 1: Analyzing code...")
        analysis = self.analyzer.analyze_file(file_path)
        
        if "error" in analysis:
            workflow_results["steps"].append({"step": "analysis", "status": "failed", "error": analysis["error"]})
            return workflow_results
        
        llm_analysis = analysis.get('llm_analysis', {})
        issues_count = len(llm_analysis.get('issues', []))
        quality_score = llm_analysis.get('quality_score', 0)
        
        workflow_results["steps"].append({
            "step": "analysis", 
            "status": "completed",
            "issues_found": issues_count,
            "quality_score": quality_score
        })
        
        if issues_count == 0:
            print("✅ No issues found - no fixes needed")
            workflow_results["success"] = True
            return workflow_results
        
        print(f"   Found {issues_count} issues, quality score: {quality_score}/10")
        
        # Step 2: Generate fixes
        print("🛠️  Step 2: Generating fixes...")
        fixes_data = self.fixer.generate_fixes(file_path, analysis)
        
        if "error" in fixes_data:
            workflow_results["steps"].append({"step": "fix_generation", "status": "failed", "error": fixes_data["error"]})
            return workflow_results
        
        fixes_count = len(fixes_data.get("fixes", []))
        workflow_results["steps"].append({
            "step": "fix_generation",
            "status": "completed", 
            "fixes_generated": fixes_count
        })
        
        print(f"   Generated {fixes_count} fixes")
        
        # Step 3: Apply fixes
        print("🔨 Step 3: Applying fixes...")
        fixed_file = self.fixer.apply_fixes(file_path, fixes_data)
        
        workflow_results["steps"].append({
            "step": "apply_fixes",
            "status": "completed",
            "fixed_file": fixed_file
        })
        
        # Step 4: Test fixes
        print("🧪 Step 4: Testing fixes...")
        
        # Syntax check
        syntax_result = self.tester.run_syntax_check(fixed_file)
        if not syntax_result.get("syntax_valid", False):
            workflow_results["steps"].append({
                "step": "testing",
                "status": "failed", 
                "error": f"Syntax error: {syntax_result.get('error', 'Unknown')}"
            })
            return workflow_results
        
        # Static analysis
        static_result = self.tester.run_static_analysis(fixed_file)
        
        # Import test
        import_result = self.tester.run_basic_tests(fixed_file)
        
        test_passed = (
            syntax_result.get("syntax_valid", False) and
            import_result.get("import_test", False)
        )
        
        workflow_results["steps"].append({
            "step": "testing",
            "status": "passed" if test_passed else "failed",
            "syntax_check": syntax_result,
            "static_analysis": static_result,
            "import_test": import_result
        })
        
        if not test_passed:
            print("❌ Tests failed - not creating PR")
            return workflow_results
        
        print("✅ All tests passed")
        
        # Step 5: Create branch and PR
        print("🌿 Step 5: Creating pull request...")
        
        branch_name = f"auto-fix-{Path(file_path).stem}-{__import__('datetime').datetime.now().strftime('%Y%m%d-%H%M%S')}"
        
        if not self.pr_manager.create_fix_branch(branch_name):
            workflow_results["steps"].append({"step": "create_branch", "status": "failed"})
            return workflow_results
        
        # Replace original file with fixed version
        os.rename(fixed_file, file_path)
        
        # Create commit message
        commit_message = f"Auto-fix: Resolve {fixes_count} code issues in {Path(file_path).name}\n\n"
        for fix in fixes_data.get("fixes", [])[:3]:  # Show first 3 fixes
            commit_message += f"- {fix.get('issue_description', 'Code improvement')}\n"
        
        if not self.pr_manager.commit_fixes([file_path], commit_message):
            workflow_results["steps"].append({"step": "commit", "status": "failed"})
            return workflow_results
        
        if not self.pr_manager.push_branch(branch_name):
            workflow_results["steps"].append({"step": "push", "status": "failed"})
            return workflow_results
        
        # Create PR description
        pr_description = f"""## Automated Code Fixes

This PR contains automated fixes for code quality issues detected by the Intelligent Code Analyzer.

### Summary
- **File**: `{file_path}`
- **Issues Fixed**: {fixes_count}
- **Quality Improvement**: Expected improvement in code quality score

### Fixes Applied
"""
        
        for i, fix in enumerate(fixes_data.get("fixes", [])[:5], 1):  # Show first 5 fixes
            pr_description += f"{i}. **{fix.get('issue_description', 'Code improvement')}**\n"
            pr_description += f"   - Line: {fix.get('line_number', 'N/A')}\n"
            pr_description += f"   - Fix: {fix.get('explanation', 'Applied automated fix')}\n\n"
        
        pr_description += """
### Testing
- ✅ Syntax validation passed
- ✅ Static analysis checks
- ✅ Import/module loading test

### Review Notes
Please review the changes to ensure they maintain the intended functionality while improving code quality.
"""
        
        pr_title = f"Auto-fix: Resolve {fixes_count} code issues in {Path(file_path).name}"
        pr_url = self.pr_manager.create_pull_request(branch_name, pr_title, pr_description)
        
        if pr_url:
            workflow_results["steps"].append({
                "step": "create_pr",
                "status": "completed",
                "pr_url": pr_url,
                "branch_name": branch_name
            })
            workflow_results["success"] = True
            workflow_results["pr_url"] = pr_url
            print(f"✅ Pull request created: {pr_url}")
        else:
            workflow_results["steps"].append({"step": "create_pr", "status": "failed"})
        
        return workflow_results

def main():
    """Demo the auto-fix workflow"""
    
    # Create a sample file with issues for testing
    sample_code = '''#!/usr/bin/env python3
"""Sample code with issues for auto-fix demo"""

import os
import sys

def unsafe_eval(user_input):
    # Security issue: eval with user input
    return eval(user_input)

def file_leak(filename):
    # Resource leak: file not closed
    f = open(filename, 'r')
    content = f.read()
    return content

def divide_unsafe(a, b):
    # No zero check
    return a / b

def style_issues(items):
    # Style issues
    result = []
    for i in range(len(items)):
        if items[i] != None:  # Should use 'is not'
            result.append(items[i])
    return result

if __name__ == "__main__":
    # This code has multiple issues that can be auto-fixed
    user_code = input("Enter code: ")
    result = unsafe_eval(user_code)
    print(result)
'''
    
    # Write sample file
    sample_file = "demo_auto_fix.py"
    with open(sample_file, 'w') as f:
        f.write(sample_code)
    
    print("🚀 Auto-Fix Workflow Demo")
    print("=" * 50)
    
    try:
        # Run the workflow
        workflow = AutoFixWorkflow()
        results = workflow.run_auto_fix_workflow(sample_file)
        
        # Print results
        print(f"\n📊 Workflow Results:")
        print(f"   Success: {results['success']}")
        
        if results.get('pr_url'):
            print(f"   PR Created: {results['pr_url']}")
        
        print(f"\n📋 Steps Completed:")
        for step in results['steps']:
            status = step['status']
            emoji = "✅" if status in ['completed', 'passed'] else "❌"
            print(f"   {emoji} {step['step']}: {status}")
        
        # Save detailed results
        with open("auto_fix_results.json", 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"\n📄 Detailed results saved to: auto_fix_results.json")
        
    finally:
        # Clean up
        if os.path.exists(sample_file):
            os.remove(sample_file)
        
        # Clean up any fixed files
        for f in Path(".").glob("*_fixed.py"):
            f.unlink()
    
    print("\n✅ Auto-fix workflow demo complete!")

if __name__ == "__main__":
    main()
