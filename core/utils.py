"""Utility functions for the code analyzer"""

import os
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional
import boto3
from .exceptions import ConfigurationError

class FileUtils:
    """File operation utilities"""
    
    @staticmethod
    def read_file(file_path: str) -> str:
        """Read file content safely"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            raise FileNotFoundError(f"Could not read file {file_path}: {e}")
    
    @staticmethod
    def write_file(file_path: str, content: str) -> None:
        """Write file content safely"""
        try:
            Path(file_path).parent.mkdir(parents=True, exist_ok=True)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
        except Exception as e:
            raise IOError(f"Could not write file {file_path}: {e}")
    
    @staticmethod
    def detect_language(file_path: str) -> Optional[str]:
        """Detect programming language from file extension"""
        ext_map = {
            '.py': 'python', '.js': 'javascript', '.ts': 'typescript',
            '.java': 'java', '.go': 'go', '.rs': 'rust'
        }
        return ext_map.get(Path(file_path).suffix.lower())
    
    @staticmethod
    def find_files(directory: str, extensions: List[str], recursive: bool = True) -> List[str]:
        """Find files with specified extensions"""
        path = Path(directory)
        pattern = "**/*" if recursive else "*"
        
        files = []
        for ext in extensions:
            files.extend([str(f) for f in path.glob(f"{pattern}{ext}")])
        
        return files

class GitUtils:
    """Git operation utilities"""
    
    @staticmethod
    def run_git_command(command: List[str], cwd: str = ".") -> Dict[str, Any]:
        """Run git command safely"""
        try:
            result = subprocess.run(
                ['git'] + command,
                cwd=cwd,
                capture_output=True,
                text=True,
                check=True,
                timeout=30
            )
            return {'success': True, 'output': result.stdout, 'error': result.stderr}
        except subprocess.CalledProcessError as e:
            return {'success': False, 'error': e.stderr, 'returncode': e.returncode}
        except subprocess.TimeoutExpired:
            return {'success': False, 'error': 'Git command timeout'}
    
    @staticmethod
    def create_branch(branch_name: str, cwd: str = ".") -> bool:
        """Create and checkout new branch"""
        # Ensure on main branch
        GitUtils.run_git_command(['checkout', 'main'], cwd)
        GitUtils.run_git_command(['pull', 'origin', 'main'], cwd)
        
        # Create new branch
        result = GitUtils.run_git_command(['checkout', '-b', branch_name], cwd)
        return result['success']
    
    @staticmethod
    def commit_files(files: List[str], message: str, cwd: str = ".") -> bool:
        """Commit files with message"""
        # Add files
        for file_path in files:
            result = GitUtils.run_git_command(['add', file_path], cwd)
            if not result['success']:
                return False
        
        # Commit
        result = GitUtils.run_git_command(['commit', '-m', message], cwd)
        return result['success']
    
    @staticmethod
    def push_branch(branch_name: str, cwd: str = ".") -> bool:
        """Push branch to remote"""
        result = GitUtils.run_git_command(['push', '-u', 'origin', branch_name], cwd)
        return result['success']

class LLMUtils:
    """LLM operation utilities"""
    
    def __init__(self, region: str = "us-west-2", model_id: str = "anthropic.claude-3-sonnet-20240229-v1:0"):
        try:
            self.bedrock = boto3.client('bedrock-runtime', region_name=region)
            self.model_id = model_id
        except Exception as e:
            raise ConfigurationError(f"Failed to initialize AWS Bedrock client: {e}")
    
    def generate_response(self, prompt: str, max_tokens: int = 2000) -> str:
        """Generate LLM response"""
        try:
            response = self.bedrock.invoke_model(
                modelId=self.model_id,
                body=json.dumps({
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": max_tokens,
                    "messages": [{"role": "user", "content": prompt}]
                })
            )
            
            result = json.loads(response['body'].read())
            return result['content'][0]['text']
            
        except Exception as e:
            raise RuntimeError(f"LLM generation failed: {e}")
    
    def parse_json_response(self, response: str) -> Dict[str, Any]:
        """Parse JSON from LLM response"""
        try:
            # Find JSON in response
            start = response.find('{')
            end = response.rfind('}') + 1
            
            if start >= 0 and end > start:
                json_str = response[start:end]
                return json.loads(json_str)
            
            raise ValueError("No valid JSON found in response")
            
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in response: {e}")

class ProcessUtils:
    """Process execution utilities"""
    
    @staticmethod
    def run_command(command: List[str], timeout: int = 30, cwd: str = ".") -> Dict[str, Any]:
        """Run command safely with timeout"""
        try:
            result = subprocess.run(
                command,
                cwd=cwd,
                capture_output=True,
                text=True,
                timeout=timeout,
                check=False
            )
            
            return {
                'success': result.returncode == 0,
                'returncode': result.returncode,
                'stdout': result.stdout,
                'stderr': result.stderr
            }
            
        except subprocess.TimeoutExpired:
            return {'success': False, 'error': 'Command timeout'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
