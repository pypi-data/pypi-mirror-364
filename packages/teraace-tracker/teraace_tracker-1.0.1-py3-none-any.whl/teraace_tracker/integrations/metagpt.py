"""MetaGPT integration for Teraace Agentic Tracker.

MetaGPT is a multi-agent framework that assigns different roles to GPTs
to form a collaborative software entity for complex tasks.
"""

from typing import Any, Dict, List, Optional, Union
from .base import BaseTracker


class MetaGPTTracker(BaseTracker):
    """Tracker for MetaGPT multi-agent software development."""
    
    def __init__(self, agent_name: str = "metagpt_agent", **kwargs):
        """Initialize MetaGPT tracker."""
        super().__init__(agent_name=agent_name, framework_name="metagpt", **kwargs)
        self._tracked_teams = {}
        self._tracked_roles = {}
    
    def track_team_creation(self, team: Any, team_config: Dict[str, Any]) -> None:
        """Track MetaGPT team creation.
        
        Args:
            team: The MetaGPT team instance
            team_config: Configuration for the team
        """
        team_data = {
            'team_name': team_config.get('name', 'unknown'),
            'investment': team_config.get('investment', 0.0),
            'n_round': team_config.get('n_round', 10),
            'role_count': len(team_config.get('roles', [])),
            'roles': [role.get('name', 'unknown') for role in team_config.get('roles', [])],
            'project_type': team_config.get('project_type', 'software')
        }
        
        self._emit_event(
            event_type='team_creation',
            data=team_data,
            metadata={'framework': self.framework_name}
        )
        
        # Store team for tracking
        team_id = id(team)
        self._tracked_teams[team_id] = team   
 
    def track_role_creation(self, role: Any, role_config: Dict[str, Any]) -> None:
        """Track creation of a MetaGPT role.
        
        Args:
            role: The MetaGPT role instance
            role_config: Configuration for the role
        """
        role_data = {
            'role_name': role_config.get('name', 'unknown'),
            'role_type': role.__class__.__name__,
            'profile': role_config.get('profile', ''),
            'goal': role_config.get('goal', ''),
            'constraints': role_config.get('constraints', []),
            'desc': role_config.get('desc', ''),
            'is_human': role_config.get('is_human', False)
        }
        
        self._emit_event(
            event_type='role_creation',
            data=role_data,
            metadata={'framework': self.framework_name}
        )
        
        # Store role for tracking
        role_id = id(role)
        self._tracked_roles[role_id] = role
    
    def track_action_execution(self, role: Any, action: Any, action_input: Dict[str, Any], action_output: Any) -> None:
        """Track action execution by MetaGPT roles.
        
        Args:
            role: The role executing the action
            action: The action being executed
            action_input: Input to the action
            action_output: Output from the action
        """
        action_data = {
            'role_name': getattr(role, 'name', 'unknown'),
            'role_type': role.__class__.__name__,
            'action_name': getattr(action, 'name', action.__class__.__name__),
            'action_type': action.__class__.__name__,
            'input_keys': list(action_input.keys()) if isinstance(action_input, dict) else [],
            'has_output': action_output is not None,
            'output_type': type(action_output).__name__ if action_output is not None else None
        }
        
        self._emit_event(
            event_type='action_execution',
            data=action_data,
            metadata={'framework': self.framework_name}
        )
    
    def track_document_creation(self, role: Any, document: Dict[str, Any]) -> None:
        """Track document creation in MetaGPT.
        
        Args:
            role: The role creating the document
            document: The document being created
        """
        doc_data = {
            'role_name': getattr(role, 'name', 'unknown'),
            'document_type': document.get('type', 'unknown'),
            'document_name': document.get('name', ''),
            'content_length': len(document.get('content', '')),
            'has_diagrams': document.get('has_diagrams', False),
            'format': document.get('format', 'text')
        }
        
        self._emit_event(
            event_type='document_creation',
            data=doc_data,
            metadata={'framework': self.framework_name}
        )
    
    def track_code_generation(self, role: Any, code_info: Dict[str, Any]) -> None:
        """Track code generation by MetaGPT roles.
        
        Args:
            role: The role generating code
            code_info: Information about the generated code
        """
        code_data = {
            'role_name': getattr(role, 'name', 'unknown'),
            'file_name': code_info.get('file_name', ''),
            'language': code_info.get('language', 'python'),
            'lines_of_code': code_info.get('lines_of_code', 0),
            'functions_count': code_info.get('functions_count', 0),
            'classes_count': code_info.get('classes_count', 0),
            'has_tests': code_info.get('has_tests', False)
        }
        
        self._emit_event(
            event_type='code_generation',
            data=code_data,
            metadata={'framework': self.framework_name}
        )
    
    def track_review_process(self, reviewer: Any, reviewee: Any, review_result: Dict[str, Any]) -> None:
        """Track code/document review process.
        
        Args:
            reviewer: The role doing the review
            reviewee: The role being reviewed
            review_result: Result of the review
        """
        review_data = {
            'reviewer_name': getattr(reviewer, 'name', 'unknown'),
            'reviewee_name': getattr(reviewee, 'name', 'unknown'),
            'review_type': review_result.get('type', 'unknown'),
            'approval_status': review_result.get('approved', False),
            'feedback_count': len(review_result.get('feedback', [])),
            'severity_level': review_result.get('severity', 'low')
        }
        
        self._emit_event(
            event_type='review_process',
            data=review_data,
            metadata={'framework': self.framework_name}
        )
    
    def track_project_iteration(self, team: Any, iteration_number: int, iteration_result: Dict[str, Any]) -> None:
        """Track project iteration completion.
        
        Args:
            team: The team completing the iteration
            iteration_number: The iteration number
            iteration_result: Result of the iteration
        """
        iteration_data = {
            'team_name': getattr(team, 'name', 'unknown'),
            'iteration_number': iteration_number,
            'documents_created': iteration_result.get('documents_created', 0),
            'code_files_generated': iteration_result.get('code_files_generated', 0),
            'reviews_completed': iteration_result.get('reviews_completed', 0),
            'issues_resolved': iteration_result.get('issues_resolved', 0),
            'iteration_status': iteration_result.get('status', 'completed')
        }
        
        self._emit_event(
            event_type='project_iteration',
            data=iteration_data,
            metadata={'framework': self.framework_name}
        )
    
    def auto_track_team(self, team: Any, config: Dict[str, Any] = None) -> Any:
        """Automatically track a MetaGPT team.
        
        Args:
            team: The MetaGPT team instance
            config: Optional team configuration
            
        Returns:
            The same team (for chaining)
        """
        team_id = id(team)
        self._tracked_teams[team_id] = team
        
        # Track team creation if config is provided
        if config:
            self.track_team_creation(team, config)
        
        return team
    
    def extract_model_info(self, *args, **kwargs) -> str:
        """Extract model information from MetaGPT team."""
        return kwargs.get('model', 'gpt-4')
    
    def _emit_event(self, event_type: str, data: Dict[str, Any], metadata: Dict[str, Any] = None):
        """Emit a tracking event."""
        # This is a placeholder - in a real implementation, this would emit to the tracking system
        pass