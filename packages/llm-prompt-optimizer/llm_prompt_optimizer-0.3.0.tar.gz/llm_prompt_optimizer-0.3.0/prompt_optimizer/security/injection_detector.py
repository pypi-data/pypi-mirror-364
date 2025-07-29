"""
Prompt injection detection and prevention.
"""

import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class InjectionType(str, Enum):
    """Types of prompt injection attacks."""
    IGNORE_PREVIOUS = "ignore_previous"
    ROLE_PLAYING = "role_playing"
    SYSTEM_PROMPT_LEAK = "system_prompt_leak"
    INSTRUCTION_OVERRIDE = "instruction_override"
    CONTEXT_MANIPULATION = "context_manipulation"
    ESCAPE_SEQUENCE = "escape_sequence"


@dataclass
class InjectionResult:
    """Result of injection detection."""
    is_injection: bool
    injection_types: List[InjectionType]
    confidence: float
    flagged_text: List[str]
    risk_level: str  # low, medium, high, critical
    suggestions: List[str]


class InjectionDetector:
    """Detect and prevent prompt injection attacks."""
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self._load_injection_patterns()
        
    def _load_injection_patterns(self):
        """Load patterns for different types of injection attacks."""
        self.ignore_patterns = [
            r'\b(ignore|forget|disregard|skip)\b.*\b(previous|above|earlier|before)\b.*\b(instructions?|prompts?|rules?)\b',
            r'\b(ignore|forget|disregard|skip)\b.*\b(all|everything)\b.*\b(instructions?|prompts?|rules?)\b',
            r'\b(start|begin|reset)\b.*\b(fresh|new|clean)\b.*\b(instructions?|prompts?)\b',
        ]
        
        self.role_playing_patterns = [
            r'\b(pretend|act|play|roleplay)\b.*\b(you are|you\'re|you\'ve become)\b',
            r'\b(imagine|suppose|assume)\b.*\b(you are|you\'re)\b.*\b(someone|something)\b',
            r'\b(from now on|starting now|henceforth)\b.*\b(you are|you\'re)\b',
        ]
        
        self.system_leak_patterns = [
            r'\b(system|assistant|ai|model)\b.*\b(prompt|instruction|rule|guideline)\b',
            r'\b(what are|what\'s|tell me)\b.*\b(your|the)\b.*\b(instructions?|prompts?|rules?)\b',
            r'\b(show|display|output|print)\b.*\b(instructions?|prompts?|rules?)\b',
        ]
        
        self.override_patterns = [
            r'\b(override|replace|change|modify)\b.*\b(instructions?|prompts?|rules?)\b',
            r'\b(new|different|updated)\b.*\b(instructions?|prompts?|rules?)\b',
            r'\b(use|follow|apply)\b.*\b(these|this)\b.*\b(instead|instead of)\b',
        ]
        
        self.context_patterns = [
            r'\b(ignore|forget|remove)\b.*\b(context|background|information)\b',
            r'\b(assume|pretend)\b.*\b(context|background|information)\b',
            r'\b(change|modify)\b.*\b(context|background|information)\b',
        ]
        
        self.escape_patterns = [
            r'```.*```',  # Code blocks
            r'<.*?>',     # HTML-like tags
            r'\{.*?\}',   # Curly braces
            r'\[.*?\]',   # Square brackets
            r'\(.*?\)',   # Parentheses
        ]
        
        self.suspicious_phrases = [
            'ignore all previous instructions',
            'forget everything above',
            'start fresh',
            'new instructions',
            'override previous',
            'pretend you are',
            'act as if',
            'roleplay as',
            'system prompt',
            'assistant instructions',
            'model guidelines',
        ]
        
    def detect_injection(self, text: str) -> InjectionResult:
        """Detect potential prompt injection attacks."""
        if not text:
            return InjectionResult(
                is_injection=False,
                injection_types=[],
                confidence=1.0,
                flagged_text=[],
                risk_level="low",
                suggestions=[]
            )
            
        injection_types = []
        flagged_text = []
        risk_score = 0.0
        
        text_lower = text.lower()
        
        # Check for ignore previous instructions
        if self._check_patterns(text_lower, self.ignore_patterns):
            injection_types.append(InjectionType.IGNORE_PREVIOUS)
            flagged_text.extend(self._extract_matches(text_lower, self.ignore_patterns))
            risk_score += 0.4
            
        # Check for role playing
        if self._check_patterns(text_lower, self.role_playing_patterns):
            injection_types.append(InjectionType.ROLE_PLAYING)
            flagged_text.extend(self._extract_matches(text_lower, self.role_playing_patterns))
            risk_score += 0.3
            
        # Check for system prompt leaks
        if self._check_patterns(text_lower, self.system_leak_patterns):
            injection_types.append(InjectionType.SYSTEM_PROMPT_LEAK)
            flagged_text.extend(self._extract_matches(text_lower, self.system_leak_patterns))
            risk_score += 0.5
            
        # Check for instruction overrides
        if self._check_patterns(text_lower, self.override_patterns):
            injection_types.append(InjectionType.INSTRUCTION_OVERRIDE)
            flagged_text.extend(self._extract_matches(text_lower, self.override_patterns))
            risk_score += 0.4
            
        # Check for context manipulation
        if self._check_patterns(text_lower, self.context_patterns):
            injection_types.append(InjectionType.CONTEXT_MANIPULATION)
            flagged_text.extend(self._extract_matches(text_lower, self.context_patterns))
            risk_score += 0.3
            
        # Check for escape sequences
        if self._check_patterns(text_lower, self.escape_patterns):
            injection_types.append(InjectionType.ESCAPE_SEQUENCE)
            flagged_text.extend(self._extract_matches(text_lower, self.escape_patterns))
            risk_score += 0.2
            
        # Check for suspicious phrases
        for phrase in self.suspicious_phrases:
            if phrase in text_lower:
                injection_types.append(InjectionType.INSTRUCTION_OVERRIDE)
                flagged_text.append(phrase)
                risk_score += 0.3
                
        # Determine risk level
        risk_level = self._determine_risk_level(risk_score, len(injection_types))
        
        # Generate suggestions
        suggestions = self._generate_suggestions(injection_types, risk_level)
        
        return InjectionResult(
            is_injection=len(injection_types) > 0,
            injection_types=injection_types,
            confidence=min(risk_score + 0.3, 1.0),
            flagged_text=list(set(flagged_text)),
            risk_level=risk_level,
            suggestions=suggestions
        )
        
    def _check_patterns(self, text: str, patterns: List[str]) -> bool:
        """Check if text matches any of the given patterns."""
        return any(re.search(pattern, text, re.IGNORECASE) for pattern in patterns)
        
    def _extract_matches(self, text: str, patterns: List[str]) -> List[str]:
        """Extract matching text from patterns."""
        matches = []
        for pattern in patterns:
            found = re.findall(pattern, text, re.IGNORECASE)
            matches.extend(found)
        return matches
        
    def _determine_risk_level(self, risk_score: float, injection_count: int) -> str:
        """Determine risk level based on risk score and injection count."""
        if risk_score >= 0.8 or injection_count >= 4:
            return "critical"
        elif risk_score >= 0.6 or injection_count >= 3:
            return "high"
        elif risk_score >= 0.4 or injection_count >= 2:
            return "medium"
        else:
            return "low"
            
    def _generate_suggestions(self, injection_types: List[InjectionType], risk_level: str) -> List[str]:
        """Generate suggestions for preventing injection attacks."""
        suggestions = []
        
        if InjectionType.IGNORE_PREVIOUS in injection_types:
            suggestions.append("Reject prompts that try to ignore previous instructions")
            
        if InjectionType.ROLE_PLAYING in injection_types:
            suggestions.append("Validate role-playing requests against allowed roles")
            
        if InjectionType.SYSTEM_PROMPT_LEAK in injection_types:
            suggestions.append("Block attempts to access system prompts or instructions")
            
        if InjectionType.INSTRUCTION_OVERRIDE in injection_types:
            suggestions.append("Prevent instruction overrides through input validation")
            
        if InjectionType.CONTEXT_MANIPULATION in injection_types:
            suggestions.append("Maintain context integrity and prevent manipulation")
            
        if InjectionType.ESCAPE_SEQUENCE in injection_types:
            suggestions.append("Sanitize escape sequences and special formatting")
            
        if risk_level in ["high", "critical"]:
            suggestions.append("Consider rejecting this prompt entirely")
            suggestions.append("Implement additional validation layers")
            
        return suggestions
        
    def sanitize_input(self, text: str) -> str:
        """Sanitize input to prevent injection attacks."""
        if not text:
            return text
            
        # Remove or escape suspicious patterns
        sanitized = text
        
        # Escape common injection patterns
        for pattern in self.ignore_patterns + self.role_playing_patterns:
            sanitized = re.sub(pattern, r'[REDACTED]', sanitized, flags=re.IGNORECASE)
            
        # Remove suspicious phrases
        for phrase in self.suspicious_phrases:
            sanitized = sanitized.replace(phrase, '[REDACTED]')
            
        return sanitized
        
    def validate_prompt(self, prompt: str, context: Optional[Dict] = None) -> Tuple[bool, List[str]]:
        """Validate a prompt for injection attacks."""
        result = self.detect_injection(prompt)
        
        if result.is_injection:
            return False, result.suggestions
        else:
            return True, [] 