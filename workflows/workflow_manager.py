"""Workflow manager for orchestrating different analysis workflows"""

from typing import Dict, Any, Optional
from enum import Enum
from core.base import AnalysisResult
from core.interfaces import ICodeAnalyzer, IFixGenerator, ITestRunner, IPRManager
from core.config import Config
from core.exceptions import AnalysisError
from analyzers.unified_analyzer import UnifiedAnalyzer

class WorkflowType(Enum):
    """Available workflow types"""
    ANALYSIS_ONLY = "analysis_only"
    AUTO_FIX = "auto_fix"
    STRANDS_COORDINATED = "strands_coordinated"

class WorkflowManager:
    """Manages different workflow types and orchestrates execution"""
    
    def __init__(self, config: Config = None):
        self.config = config or Config.from_env()
        self.analyzer = UnifiedAnalyzer(self.config.to_dict())
    
    def execute_workflow(self, 
                        file_path: str, 
                        workflow_type: WorkflowType,
                        **kwargs) -> Dict[str, Any]:
        """Execute specified workflow type"""
        
        try:
            if workflow_type == WorkflowType.ANALYSIS_ONLY:
                return self._execute_analysis_workflow(file_path, **kwargs)
            elif workflow_type == WorkflowType.AUTO_FIX:
                return self._execute_auto_fix_workflow(file_path, **kwargs)
            elif workflow_type == WorkflowType.STRANDS_COORDINATED:
                return self._execute_strands_workflow(file_path, **kwargs)
            else:
                raise ValueError(f"Unknown workflow type: {workflow_type}")
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'workflow_type': workflow_type.value
            }
    
    def _execute_analysis_workflow(self, file_path: str, **kwargs) -> Dict[str, Any]:
        """Execute analysis-only workflow"""
        
        analysis_result = self.analyzer.analyze_file(file_path)
        
        return {
            'success': True,
            'workflow_type': WorkflowType.ANALYSIS_ONLY.value,
            'analysis': {
                'file_path': analysis_result.file_path,
                'language': analysis_result.language,
                'quality_score': analysis_result.quality_score,
                'issues_found': len(analysis_result.issues),
                'issues': analysis_result.issues,
                'recommendations': analysis_result.recommendations,
                'metadata': analysis_result.metadata
            }
        }
    
    def _execute_auto_fix_workflow(self, file_path: str, **kwargs) -> Dict[str, Any]:
        """Execute auto-fix workflow"""
        # Import here to avoid circular imports
        from .auto_fix_workflow import AutoFixWorkflow
        
        auto_fix = AutoFixWorkflow(self.config)
        return auto_fix.execute(file_path, **kwargs)
    
    def _execute_strands_workflow(self, file_path: str, **kwargs) -> Dict[str, Any]:
        """Execute Strands coordinated workflow"""
        # Import here to avoid circular imports
        from .strands_workflow import StrandsWorkflow
        
        strands = StrandsWorkflow(self.config)
        return strands.execute(file_path, **kwargs)
    
    def get_workflow_info(self, workflow_type: WorkflowType) -> Dict[str, Any]:
        """Get information about a workflow type"""
        
        workflow_info = {
            WorkflowType.ANALYSIS_ONLY: {
                'name': 'Analysis Only',
                'description': 'Comprehensive code analysis without fixes',
                'features': ['Static analysis', 'LLM analysis', 'Quality scoring', 'Issue identification']
            },
            WorkflowType.AUTO_FIX: {
                'name': 'Auto-Fix',
                'description': 'Complete workflow with automated fixes and PR creation',
                'features': ['Analysis', 'Fix generation', 'Testing', 'PR creation']
            },
            WorkflowType.STRANDS_COORDINATED: {
                'name': 'Strands Coordinated',
                'description': 'Multi-agent coordinated workflow',
                'features': ['Agent coordination', 'Specialized analysis', 'Workflow orchestration']
            }
        }
        
        return workflow_info.get(workflow_type, {})
    
    def validate_workflow_requirements(self, workflow_type: WorkflowType) -> Dict[str, bool]:
        """Validate requirements for workflow type"""
        
        requirements = {
            'aws_credentials': self._check_aws_credentials(),
            'git_available': self._check_git_available(),
            'github_cli': self._check_github_cli()
        }
        
        workflow_requirements = {
            WorkflowType.ANALYSIS_ONLY: ['aws_credentials'],
            WorkflowType.AUTO_FIX: ['aws_credentials', 'git_available', 'github_cli'],
            WorkflowType.STRANDS_COORDINATED: ['aws_credentials', 'git_available']
        }
        
        needed = workflow_requirements.get(workflow_type, [])
        return {req: requirements[req] for req in needed}
    
    def _check_aws_credentials(self) -> bool:
        """Check if AWS credentials are available"""
        try:
            import boto3
            boto3.client('bedrock-runtime', region_name=self.config.aws_region)
            return True
        except:
            return False
    
    def _check_git_available(self) -> bool:
        """Check if Git is available"""
        from core.utils import ProcessUtils
        result = ProcessUtils.run_command(['git', '--version'])
        return result['success']
    
    def _check_github_cli(self) -> bool:
        """Check if GitHub CLI is available"""
        from core.utils import ProcessUtils
        result = ProcessUtils.run_command(['gh', '--version'])
        return result['success']
