"""Configuration management for the code analyzer"""

import os
from typing import Dict, Any, Optional
from dataclasses import dataclass, field

@dataclass
class Config:
    """Configuration class with defaults"""
    
    # AWS/LLM Configuration
    aws_region: str = "us-west-2"
    model_id: str = "anthropic.claude-3-sonnet-20240229-v1:0"
    max_tokens: int = 2000
    
    # Analysis Configuration
    supported_extensions: list = field(default_factory=lambda: ['.py', '.js', '.ts', '.java', '.go', '.rs'])
    quality_threshold: int = 6
    max_issues_to_fix: int = 10
    
    # Git Configuration
    default_branch: str = "main"
    branch_prefix: str = "auto-fix"
    
    # Tool Configuration
    static_analysis_timeout: int = 30
    test_timeout: int = 60
    
    @classmethod
    def from_env(cls) -> 'Config':
        """Create config from environment variables"""
        return cls(
            aws_region=os.getenv('AWS_DEFAULT_REGION', cls.aws_region),
            model_id=os.getenv('STRANDS_MODEL_ID', cls.model_id),
            max_tokens=int(os.getenv('STRANDS_MAX_TOKENS', cls.max_tokens)),
            quality_threshold=int(os.getenv('QUALITY_THRESHOLD', cls.quality_threshold)),
            default_branch=os.getenv('DEFAULT_BRANCH', cls.default_branch)
        )
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'Config':
        """Create config from dictionary"""
        return cls(**{k: v for k, v in config_dict.items() if hasattr(cls, k)})
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary"""
        return {
            'aws_region': self.aws_region,
            'model_id': self.model_id,
            'max_tokens': self.max_tokens,
            'supported_extensions': self.supported_extensions,
            'quality_threshold': self.quality_threshold,
            'max_issues_to_fix': self.max_issues_to_fix,
            'default_branch': self.default_branch,
            'branch_prefix': self.branch_prefix,
            'static_analysis_timeout': self.static_analysis_timeout,
            'test_timeout': self.test_timeout
        }
