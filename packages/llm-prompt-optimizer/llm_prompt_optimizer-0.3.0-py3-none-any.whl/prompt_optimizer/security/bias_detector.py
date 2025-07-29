"""
Bias detection for prompts and responses.
"""

import re
from typing import Dict, List, Optional, Set
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class BiasType(str, Enum):
    """Types of bias that can be detected."""
    GENDER = "gender"
    RACIAL = "racial"
    AGE = "age"
    RELIGIOUS = "religious"
    CULTURAL = "cultural"
    ECONOMIC = "economic"
    POLITICAL = "political"
    PROFESSIONAL = "professional"
    LANGUAGE = "language"


@dataclass
class BiasResult:
    """Result of bias detection."""
    has_bias: bool
    bias_types: List[BiasType]
    biased_terms: List[str]
    confidence: float
    suggestions: List[str]
    bias_score: float  # 0.0 to 1.0


class BiasDetector:
    """Detect various types of bias in prompts and responses."""
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self._load_bias_patterns()
        
    def _load_bias_patterns(self):
        """Load patterns for different types of bias."""
        self.gender_patterns = {
            'stereotypes': [
                r'\b(emotional|hysterical|bossy|aggressive)\b.*\b(woman|women|female|girl)\b',
                r'\b(man|men|male|boy)\b.*\b(strong|tough|assertive|leader)\b',
                r'\b(nurse|teacher|secretary)\b.*\b(she|her|woman)\b',
                r'\b(engineer|doctor|CEO|boss)\b.*\b(he|his|man)\b',
                r'\b(women are emotional and men are logical)\b',
                r'\b(females are|males are)\b.*\b(emotional|logical)\b',
            ],
            'exclusionary': [
                r'\b(he|him|his)\b(?!.*\b(she|her|they|them)\b)',
                r'\b(man|men|male)\b(?!.*\b(woman|women|female|person|people)\b)',
            ]
        }
        
        self.racial_patterns = {
            'stereotypes': [
                r'\b(athletic|musical|rhythmic)\b.*\b(black|african)\b',
                r'\b(studious|academic|mathematical)\b.*\b(asian|chinese|japanese)\b',
                r'\b(lazy|poor|criminal)\b.*\b(minority|ethnic)\b',
                r'\b(black people are athletic and asian people are studious)\b',
                r'\b(african americans are|asians are)\b.*\b(athletic|studious)\b',
            ],
            'exclusionary': [
                r'\b(white|caucasian)\b.*\b(default|normal|standard)\b',
                r'\b(american)\b(?!.*\b(african|asian|hispanic|native)\b)',
            ]
        }
        
        self.age_patterns = {
            'stereotypes': [
                r'\b(old|elderly|senior)\b.*\b(technology|computer|smartphone)\b',
                r'\b(young|teen|teenager)\b.*\b(immature|irresponsible|rebellious)\b',
                r'\b(millennial|gen z)\b.*\b(lazy|entitled|snowflake)\b',
                r'\b(old people can\'t use technology)\b',
                r'\b(young people are|old people are)\b.*\b(immature|technology)\b',
            ]
        }
        
        self.religious_patterns = {
            'stereotypes': [
                r'\b(muslim|islam)\b.*\b(terrorist|extremist|violent)\b',
                r'\b(christian|christianity)\b.*\b(conservative|traditional|close-minded)\b',
                r'\b(jewish|judaism)\b.*\b(money|wealth|business)\b',
            ]
        }
        
        self.economic_patterns = {
            'stereotypes': [
                r'\b(poor|poverty)\b.*\b(lazy|unmotivated|uneducated)\b',
                r'\b(rich|wealthy)\b.*\b(greedy|selfish|privileged)\b',
                r'\b(middle class)\b.*\b(average|mediocre|ordinary)\b',
            ]
        }
        
        self.professional_patterns = {
            'stereotypes': [
                r'\b(doctor|physician)\b.*\b(he|his|man)\b',
                r'\b(nurse|caregiver)\b.*\b(she|her|woman)\b',
                r'\b(engineer|programmer)\b.*\b(nerd|geek|introvert)\b',
                r'\b(salesperson|marketer)\b.*\b(pushy|aggressive|manipulative)\b',
                r'\b(doctors are men and nurses are women)\b',
                r'\b(doctors are|nurses are)\b.*\b(men|women)\b',
            ]
        }
        
    def detect_bias(self, text: str) -> BiasResult:
        """Detect bias in the given text."""
        if not text:
            return BiasResult(
                has_bias=False,
                bias_types=[],
                biased_terms=[],
                confidence=1.0,
                suggestions=[],
                bias_score=0.0
            )
            
        bias_types = []
        biased_terms = []
        bias_score = 0.0
        
        # Check for gender bias
        gender_bias = self._check_gender_bias(text)
        if gender_bias['has_bias']:
            bias_types.append(BiasType.GENDER)
            biased_terms.extend(gender_bias['terms'])
            bias_score += gender_bias['score']
            
        # Check for racial bias
        racial_bias = self._check_racial_bias(text)
        if racial_bias['has_bias']:
            bias_types.append(BiasType.RACIAL)
            biased_terms.extend(racial_bias['terms'])
            bias_score += racial_bias['score']
            
        # Check for age bias
        age_bias = self._check_age_bias(text)
        if age_bias['has_bias']:
            bias_types.append(BiasType.AGE)
            biased_terms.extend(age_bias['terms'])
            bias_score += age_bias['score']
            
        # Check for religious bias
        religious_bias = self._check_religious_bias(text)
        if religious_bias['has_bias']:
            bias_types.append(BiasType.RELIGIOUS)
            biased_terms.extend(religious_bias['terms'])
            bias_score += religious_bias['score']
            
        # Check for economic bias
        economic_bias = self._check_economic_bias(text)
        if economic_bias['has_bias']:
            bias_types.append(BiasType.ECONOMIC)
            biased_terms.extend(economic_bias['terms'])
            bias_score += economic_bias['score']
            
        # Check for professional bias
        professional_bias = self._check_professional_bias(text)
        if professional_bias['has_bias']:
            bias_types.append(BiasType.PROFESSIONAL)
            biased_terms.extend(professional_bias['terms'])
            bias_score += professional_bias['score']
            
        # Generate suggestions
        suggestions = self._generate_suggestions(bias_types, biased_terms)
        
        return BiasResult(
            has_bias=len(bias_types) > 0,
            bias_types=bias_types,
            biased_terms=list(set(biased_terms)),
            confidence=min(bias_score + 0.3, 1.0),
            suggestions=suggestions,
            bias_score=min(bias_score, 1.0)
        )
        
    def _check_gender_bias(self, text: str) -> Dict:
        """Check for gender bias in text."""
        text_lower = text.lower()
        has_bias = False
        terms = []
        score = 0.0
        
        # Check stereotypes
        for pattern in self.gender_patterns['stereotypes']:
            if re.search(pattern, text_lower, re.IGNORECASE):
                has_bias = True
                matches = re.findall(pattern, text_lower, re.IGNORECASE)
                # Handle both strings and tuples from regex groups
                for match in matches:
                    if isinstance(match, tuple):
                        terms.extend([m for m in match if m])
                    else:
                        terms.append(match)
                score += 0.3
                
        # Check exclusionary language
        for pattern in self.gender_patterns['exclusionary']:
            if re.search(pattern, text_lower, re.IGNORECASE):
                has_bias = True
                matches = re.findall(pattern, text_lower, re.IGNORECASE)
                # Handle both strings and tuples from regex groups
                for match in matches:
                    if isinstance(match, tuple):
                        terms.extend([m for m in match if m])
                    else:
                        terms.append(match)
                score += 0.2
                
        return {
            'has_bias': has_bias,
            'terms': terms,
            'score': score
        }
        
    def _check_racial_bias(self, text: str) -> Dict:
        """Check for racial bias in text."""
        text_lower = text.lower()
        has_bias = False
        terms = []
        score = 0.0
        
        for pattern in self.racial_patterns['stereotypes']:
            if re.search(pattern, text_lower, re.IGNORECASE):
                has_bias = True
                matches = re.findall(pattern, text_lower, re.IGNORECASE)
                # Handle both strings and tuples from regex groups
                for match in matches:
                    if isinstance(match, tuple):
                        terms.extend([m for m in match if m])
                    else:
                        terms.append(match)
                score += 0.4
                
        for pattern in self.racial_patterns['exclusionary']:
            if re.search(pattern, text_lower, re.IGNORECASE):
                has_bias = True
                matches = re.findall(pattern, text_lower, re.IGNORECASE)
                # Handle both strings and tuples from regex groups
                for match in matches:
                    if isinstance(match, tuple):
                        terms.extend([m for m in match if m])
                    else:
                        terms.append(match)
                score += 0.3
                
        return {
            'has_bias': has_bias,
            'terms': terms,
            'score': score
        }
        
    def _check_age_bias(self, text: str) -> Dict:
        """Check for age bias in text."""
        text_lower = text.lower()
        has_bias = False
        terms = []
        score = 0.0
        
        for pattern in self.age_patterns['stereotypes']:
            if re.search(pattern, text_lower, re.IGNORECASE):
                has_bias = True
                matches = re.findall(pattern, text_lower, re.IGNORECASE)
                # Handle both strings and tuples from regex groups
                for match in matches:
                    if isinstance(match, tuple):
                        terms.extend([m for m in match if m])
                    else:
                        terms.append(match)
                score += 0.3
                
        return {
            'has_bias': has_bias,
            'terms': terms,
            'score': score
        }
        
    def _check_religious_bias(self, text: str) -> Dict:
        """Check for religious bias in text."""
        text_lower = text.lower()
        has_bias = False
        terms = []
        score = 0.0
        
        for pattern in self.religious_patterns['stereotypes']:
            if re.search(pattern, text_lower, re.IGNORECASE):
                has_bias = True
                matches = re.findall(pattern, text_lower, re.IGNORECASE)
                # Handle both strings and tuples from regex groups
                for match in matches:
                    if isinstance(match, tuple):
                        terms.extend([m for m in match if m])
                    else:
                        terms.append(match)
                score += 0.4
                
        return {
            'has_bias': has_bias,
            'terms': terms,
            'score': score
        }
        
    def _check_economic_bias(self, text: str) -> Dict:
        """Check for economic bias in text."""
        text_lower = text.lower()
        has_bias = False
        terms = []
        score = 0.0
        
        for pattern in self.economic_patterns['stereotypes']:
            if re.search(pattern, text_lower, re.IGNORECASE):
                has_bias = True
                matches = re.findall(pattern, text_lower, re.IGNORECASE)
                # Handle both strings and tuples from regex groups
                for match in matches:
                    if isinstance(match, tuple):
                        terms.extend([m for m in match if m])
                    else:
                        terms.append(match)
                score += 0.3
                
        return {
            'has_bias': has_bias,
            'terms': terms,
            'score': score
        }
        
    def _check_professional_bias(self, text: str) -> Dict:
        """Check for professional bias in text."""
        text_lower = text.lower()
        has_bias = False
        terms = []
        score = 0.0
        
        for pattern in self.professional_patterns['stereotypes']:
            if re.search(pattern, text_lower, re.IGNORECASE):
                has_bias = True
                matches = re.findall(pattern, text_lower, re.IGNORECASE)
                # Handle both strings and tuples from regex groups
                for match in matches:
                    if isinstance(match, tuple):
                        terms.extend([m for m in match if m])
                    else:
                        terms.append(match)
                score += 0.2
                
        return {
            'has_bias': has_bias,
            'terms': terms,
            'score': score
        }
        
    def _generate_suggestions(self, bias_types: List[BiasType], biased_terms: List[str]) -> List[str]:
        """Generate suggestions for reducing bias."""
        suggestions = []
        
        if BiasType.GENDER in bias_types:
            suggestions.append("Use gender-neutral language (they/them, person, individual)")
            suggestions.append("Avoid gender stereotypes in role descriptions")
            
        if BiasType.RACIAL in bias_types:
            suggestions.append("Be specific about cultural contexts rather than making assumptions")
            suggestions.append("Avoid racial stereotypes and generalizations")
            
        if BiasType.AGE in bias_types:
            suggestions.append("Focus on skills and experience rather than age")
            suggestions.append("Avoid age-based assumptions about capabilities")
            
        if BiasType.RELIGIOUS in bias_types:
            suggestions.append("Respect diverse religious perspectives")
            suggestions.append("Avoid religious stereotypes")
            
        if BiasType.ECONOMIC in bias_types:
            suggestions.append("Focus on individual circumstances rather than economic generalizations")
            suggestions.append("Avoid assumptions based on economic status")
            
        if BiasType.PROFESSIONAL in bias_types:
            suggestions.append("Focus on skills and qualifications rather than stereotypes")
            suggestions.append("Use inclusive language for all professions")
            
        if len(biased_terms) > 0:
            suggestions.append(f"Review and revise terms: {', '.join(biased_terms[:5])}")
            
        return suggestions 