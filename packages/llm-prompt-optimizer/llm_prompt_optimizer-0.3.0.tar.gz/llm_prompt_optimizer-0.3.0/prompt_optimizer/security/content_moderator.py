"""
Content moderation for prompts and responses.
"""

import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class ContentCategory(str, Enum):
    """Categories of content that can be flagged."""
    VIOLENCE = "violence"
    HATE_SPEECH = "hate_speech"
    SEXUAL_CONTENT = "sexual_content"
    HARMFUL_INSTRUCTIONS = "harmful_instructions"
    PERSONAL_INFO = "personal_info"
    SPAM = "spam"
    MISINFORMATION = "misinformation"


class SeverityLevel(str, Enum):
    """Severity levels for flagged content."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class ModerationResult:
    """Result of content moderation."""
    is_flagged: bool
    categories: List[ContentCategory]
    severity: SeverityLevel
    confidence: float
    flagged_text: List[str]
    recommendations: List[str]
    risk_score: float  # 0.0 to 1.0


class ContentModerator:
    """Content moderation system for prompts and responses."""
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self._load_patterns()
        
    def _load_patterns(self):
        """Load moderation patterns and keywords."""
        self.violence_patterns = [
            r'\b(kill|murder|assassinate|bomb|explode|shoot|stab)\b',
            r'\b(violence|attack|harm|hurt|injure)\b',
            r'\b(weapon|gun|knife|bomb|explosive)\b',
        ]
        
        self.hate_speech_patterns = [
            r'\b(hate|racist|sexist|homophobic|transphobic)\b',
            r'\b(discriminate|prejudice|bigot)\b',
            r'\b(superior|inferior|master|slave)\b',
        ]
        
        self.sexual_patterns = [
            r'\b(sex|sexual|porn|nude|naked)\b',
            r'\b(erotic|intimate|seduce)\b',
        ]
        
        self.harmful_instructions = [
            r'\b(how to kill|how to harm|how to hurt)\b',
            r'\b(instructions for|guide to|tutorial for)\b.*\b(violence|harm)\b',
            r'\b(bypass|hack|exploit|cheat)\b',
        ]
        
        self.personal_info_patterns = [
            r'\b\d{3}-\d{2}-\d{4}\b',  # SSN
            r'\b\d{4}-\d{4}-\d{4}-\d{4}\b',  # Credit card
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # Email
            r'\b\d{3}-\d{3}-\d{4}\b',  # Phone
        ]
        
        self.bias_patterns = [
            r'\b(women are emotional and men are logical)\b',
            r'\b(black people are athletic and asian people are studious)\b',
            r'\b(old people can\'t use technology)\b',
            r'\b(doctors are men and nurses are women)\b',
            r'\b(females are|males are)\b.*\b(emotional|logical)\b',
            r'\b(african americans are|asians are)\b.*\b(athletic|studious)\b',
            r'\b(young people are|old people are)\b.*\b(immature|technology)\b',
            r'\b(doctors are|nurses are)\b.*\b(men|women)\b',
        ]
        
    def moderate_text(self, text: str) -> ModerationResult:
        """Moderate a piece of text for inappropriate content."""
        if not text:
            return ModerationResult(
                is_flagged=False,
                categories=[],
                severity=SeverityLevel.LOW,
                confidence=1.0,
                flagged_text=[],
                recommendations=[],
                risk_score=0.0
            )
            
        categories = []
        flagged_text = []
        risk_score = 0.0
        
        # Check for violence
        if self._check_patterns(text, self.violence_patterns):
            categories.append(ContentCategory.VIOLENCE)
            flagged_text.extend(self._extract_matches(text, self.violence_patterns))
            risk_score += 0.3
            
        # Check for hate speech
        if self._check_patterns(text, self.hate_speech_patterns):
            categories.append(ContentCategory.HATE_SPEECH)
            flagged_text.extend(self._extract_matches(text, self.hate_speech_patterns))
            risk_score += 0.4
            
        # Check for sexual content
        if self._check_patterns(text, self.sexual_patterns):
            categories.append(ContentCategory.SEXUAL_CONTENT)
            flagged_text.extend(self._extract_matches(text, self.sexual_patterns))
            risk_score += 0.2
            
        # Check for harmful instructions
        if self._check_patterns(text, self.harmful_instructions):
            categories.append(ContentCategory.HARMFUL_INSTRUCTIONS)
            flagged_text.extend(self._extract_matches(text, self.harmful_instructions))
            risk_score += 0.5
            
        # Check for personal information
        if self._check_patterns(text, self.personal_info_patterns):
            categories.append(ContentCategory.PERSONAL_INFO)
            flagged_text.extend(self._extract_matches(text, self.personal_info_patterns))
            risk_score += 0.3
            
        # Check for bias
        if self._check_patterns(text, self.bias_patterns):
            categories.append(ContentCategory.HATE_SPEECH)  # Use hate speech category for bias
            flagged_text.extend(self._extract_matches(text, self.bias_patterns))
            risk_score += 0.4
            
        # Determine severity
        severity = self._determine_severity(risk_score, len(categories))
        
        # Generate recommendations
        recommendations = self._generate_recommendations(categories, severity)
        
        return ModerationResult(
            is_flagged=len(categories) > 0,
            categories=categories,
            severity=severity,
            confidence=min(risk_score + 0.5, 1.0),
            flagged_text=list(set(flagged_text)),
            recommendations=recommendations,
            risk_score=min(risk_score, 1.0)
        )
        
    def _check_patterns(self, text: str, patterns: List[str]) -> bool:
        """Check if text matches any of the given patterns."""
        text_lower = text.lower()
        return any(re.search(pattern, text_lower, re.IGNORECASE) for pattern in patterns)
        
    def _extract_matches(self, text: str, patterns: List[str]) -> List[str]:
        """Extract matching text from patterns."""
        matches = []
        text_lower = text.lower()
        for pattern in patterns:
            found = re.findall(pattern, text_lower, re.IGNORECASE)
            matches.extend(found)
        return matches
        
    def _determine_severity(self, risk_score: float, category_count: int) -> SeverityLevel:
        """Determine severity level based on risk score and category count."""
        if risk_score >= 0.8 or category_count >= 4:
            return SeverityLevel.CRITICAL
        elif risk_score >= 0.6 or category_count >= 3:
            return SeverityLevel.HIGH
        elif risk_score >= 0.4 or category_count >= 2:
            return SeverityLevel.MEDIUM
        else:
            return SeverityLevel.LOW
            
    def _generate_recommendations(self, categories: List[ContentCategory], severity: SeverityLevel) -> List[str]:
        """Generate recommendations based on flagged categories."""
        recommendations = []
        
        if ContentCategory.VIOLENCE in categories:
            recommendations.append("Consider removing or softening violent language")
            
        if ContentCategory.HATE_SPEECH in categories:
            recommendations.append("Review for potentially discriminatory content")
            
        if ContentCategory.HARMFUL_INSTRUCTIONS in categories:
            recommendations.append("This prompt may generate harmful content - review carefully")
            
        if ContentCategory.PERSONAL_INFO in categories:
            recommendations.append("Remove or anonymize personal information")
            
        if severity in [SeverityLevel.HIGH, SeverityLevel.CRITICAL]:
            recommendations.append("Consider rejecting this prompt due to high risk")
            
        return recommendations
        
    def moderate_prompt(self, prompt: str, context: Optional[Dict] = None) -> ModerationResult:
        """Moderate a prompt specifically."""
        result = self.moderate_text(prompt)
        
        # Add prompt-specific checks
        if "ignore previous instructions" in prompt.lower():
            result.categories.append(ContentCategory.HARMFUL_INSTRUCTIONS)
            result.flagged_text.append("ignore previous instructions")
            result.risk_score = min(result.risk_score + 0.2, 1.0)
            result.recommendations.append("Detected potential prompt injection attempt")
            
        return result
        
    def moderate_response(self, response: str, original_prompt: str) -> ModerationResult:
        """Moderate a response in context of the original prompt."""
        result = self.moderate_text(response)
        
        # Check for prompt leakage
        if original_prompt.lower() in response.lower():
            result.categories.append(ContentCategory.PERSONAL_INFO)
            result.flagged_text.append("prompt leakage detected")
            result.risk_score = min(result.risk_score + 0.1, 1.0)
            result.recommendations.append("Response contains original prompt - potential security issue")
            
        return result 