"""
Audit logging for comprehensive tracking of prompt operations.
"""

import json
import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
import uuid

logger = logging.getLogger(__name__)


class AuditEventType(str, Enum):
    """Types of audit events."""
    PROMPT_CREATED = "prompt_created"
    PROMPT_MODIFIED = "prompt_modified"
    PROMPT_DELETED = "prompt_deleted"
    EXPERIMENT_CREATED = "experiment_created"
    EXPERIMENT_STARTED = "experiment_started"
    EXPERIMENT_STOPPED = "experiment_stopped"
    TEST_EXECUTED = "test_executed"
    SECURITY_CHECK = "security_check"
    COMPLIANCE_CHECK = "compliance_check"
    USER_LOGIN = "user_login"
    USER_LOGOUT = "user_logout"
    ACCESS_DENIED = "access_denied"
    CONFIGURATION_CHANGED = "configuration_changed"


class AuditLevel(str, Enum):
    """Audit levels."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class AuditEvent:
    """An audit event record."""
    event_id: str
    event_type: AuditEventType
    timestamp: datetime
    user_id: Optional[str]
    session_id: Optional[str]
    ip_address: Optional[str]
    user_agent: Optional[str]
    resource_id: Optional[str]
    resource_type: Optional[str]
    action: str
    details: Dict[str, Any]
    level: AuditLevel
    success: bool
    error_message: Optional[str] = None


class AuditLogger:
    """Comprehensive audit logging system."""
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self._setup_logging()
        
    def _setup_logging(self):
        """Setup audit logging configuration."""
        # Create audit logger
        self.audit_logger = logging.getLogger('audit')
        self.audit_logger.setLevel(logging.INFO)
        
        # Create file handler for audit logs
        audit_handler = logging.FileHandler('audit.log')
        audit_handler.setLevel(logging.INFO)
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        audit_handler.setFormatter(formatter)
        
        # Add handler to logger
        self.audit_logger.addHandler(audit_handler)
        
    def log_event(self, 
                  event_type: AuditEventType,
                  user_id: Optional[str] = None,
                  session_id: Optional[str] = None,
                  ip_address: Optional[str] = None,
                  user_agent: Optional[str] = None,
                  resource_id: Optional[str] = None,
                  resource_type: Optional[str] = None,
                  action: str = "",
                  details: Optional[Dict[str, Any]] = None,
                  level: AuditLevel = AuditLevel.INFO,
                  success: bool = True,
                  error_message: Optional[str] = None) -> str:
        """Log an audit event."""
        
        event_id = str(uuid.uuid4())
        timestamp = datetime.now(timezone.utc)
        
        event = AuditEvent(
            event_id=event_id,
            event_type=event_type,
            timestamp=timestamp,
            user_id=user_id,
            session_id=session_id,
            ip_address=ip_address,
            user_agent=user_agent,
            resource_id=resource_id,
            resource_type=resource_type,
            action=action,
            details=details or {},
            level=level,
            success=success,
            error_message=error_message
        )
        
        # Log to file
        self._log_to_file(event)
        
        # Log to database if configured
        if self.config.get('database_logging', False):
            self._log_to_database(event)
            
        return event_id
        
    def _log_to_file(self, event: AuditEvent):
        """Log event to file."""
        log_entry = {
            'event_id': event.event_id,
            'event_type': event.event_type.value,
            'timestamp': event.timestamp.isoformat(),
            'user_id': event.user_id,
            'session_id': event.session_id,
            'ip_address': event.ip_address,
            'user_agent': event.user_agent,
            'resource_id': event.resource_id,
            'resource_type': event.resource_type,
            'action': event.action,
            'details': event.details,
            'level': event.level.value,
            'success': event.success,
            'error_message': event.error_message
        }
        
        log_message = json.dumps(log_entry)
        
        if event.level == AuditLevel.ERROR or event.level == AuditLevel.CRITICAL:
            self.audit_logger.error(log_message)
        elif event.level == AuditLevel.WARNING:
            self.audit_logger.warning(log_message)
        else:
            self.audit_logger.info(log_message)
            
    def _log_to_database(self, event: AuditEvent):
        """Log event to database."""
        # This would be implemented to store in a database
        # For now, we'll just pass
        pass
        
    def log_prompt_created(self, 
                          prompt_id: str,
                          user_id: str,
                          prompt_content: str,
                          metadata: Optional[Dict] = None,
                          **kwargs) -> str:
        """Log prompt creation event."""
        return self.log_event(
            event_type=AuditEventType.PROMPT_CREATED,
            user_id=user_id,
            resource_id=prompt_id,
            resource_type="prompt",
            action="create",
            details={
                'prompt_content': prompt_content[:1000],  # Truncate for logging
                'metadata': metadata or {}
            },
            **kwargs
        )
        
    def log_prompt_modified(self,
                           prompt_id: str,
                           user_id: str,
                           old_content: str,
                           new_content: str,
                           changes: Optional[Dict] = None,
                           **kwargs) -> str:
        """Log prompt modification event."""
        return self.log_event(
            event_type=AuditEventType.PROMPT_MODIFIED,
            user_id=user_id,
            resource_id=prompt_id,
            resource_type="prompt",
            action="modify",
            details={
                'old_content': old_content[:500],
                'new_content': new_content[:500],
                'changes': changes or {}
            },
            **kwargs
        )
        
    def log_experiment_created(self,
                              experiment_id: str,
                              user_id: str,
                              experiment_config: Dict,
                              **kwargs) -> str:
        """Log experiment creation event."""
        return self.log_event(
            event_type=AuditEventType.EXPERIMENT_CREATED,
            user_id=user_id,
            resource_id=experiment_id,
            resource_type="experiment",
            action="create",
            details={
                'experiment_config': experiment_config
            },
            **kwargs
        )
        
    def log_test_executed(self,
                         test_id: str,
                         user_id: str,
                         experiment_id: str,
                         variant_name: str,
                         input_data: Dict,
                         result: Dict,
                         **kwargs) -> str:
        """Log test execution event."""
        return self.log_event(
            event_type=AuditEventType.TEST_EXECUTED,
            user_id=user_id,
            resource_id=test_id,
            resource_type="test",
            action="execute",
            details={
                'experiment_id': experiment_id,
                'variant_name': variant_name,
                'input_data': input_data,
                'result_summary': {
                    'quality_score': result.get('quality_score'),
                    'latency_ms': result.get('latency_ms'),
                    'cost_usd': result.get('cost_usd'),
                    'tokens_used': result.get('tokens_used')
                }
            },
            **kwargs
        )
        
    def log_security_check(self,
                          check_type: str,
                          user_id: str,
                          resource_id: str,
                          resource_type: str,
                          check_result: Dict,
                          **kwargs) -> str:
        """Log security check event."""
        level = AuditLevel.WARNING if check_result.get('is_flagged', False) else AuditLevel.INFO
        
        return self.log_event(
            event_type=AuditEventType.SECURITY_CHECK,
            user_id=user_id,
            resource_id=resource_id,
            resource_type=resource_type,
            action=f"security_check_{check_type}",
            details=check_result,
            level=level,
            success=not check_result.get('is_flagged', False),
            **kwargs
        )
        
    def log_compliance_check(self,
                            compliance_type: str,
                            user_id: str,
                            resource_id: str,
                            resource_type: str,
                            check_result: Dict,
                            **kwargs) -> str:
        """Log compliance check event."""
        level = AuditLevel.WARNING if not check_result.get('is_compliant', True) else AuditLevel.INFO
        
        return self.log_event(
            event_type=AuditEventType.COMPLIANCE_CHECK,
            user_id=user_id,
            resource_id=resource_id,
            resource_type=resource_type,
            action=f"compliance_check_{compliance_type}",
            details=check_result,
            level=level,
            success=check_result.get('is_compliant', True),
            **kwargs
        )
        
    def log_access_denied(self,
                         user_id: str,
                         resource_id: str,
                         resource_type: str,
                         reason: str,
                         **kwargs) -> str:
        """Log access denied event."""
        return self.log_event(
            event_type=AuditEventType.ACCESS_DENIED,
            user_id=user_id,
            resource_id=resource_id,
            resource_type=resource_type,
            action="access_denied",
            details={'reason': reason},
            level=AuditLevel.WARNING,
            success=False,
            **kwargs
        )
        
    def get_audit_trail(self,
                       user_id: Optional[str] = None,
                       resource_id: Optional[str] = None,
                       event_type: Optional[AuditEventType] = None,
                       start_time: Optional[datetime] = None,
                       end_time: Optional[datetime] = None,
                       limit: int = 100) -> List[AuditEvent]:
        """Retrieve audit trail with filters."""
        # This would query the audit log database
        # For now, return empty list
        return []
        
    def export_audit_log(self,
                        start_time: datetime,
                        end_time: datetime,
                        format: str = "json") -> str:
        """Export audit log for a time period."""
        # This would export audit logs
        # For now, return empty string
        return "" 