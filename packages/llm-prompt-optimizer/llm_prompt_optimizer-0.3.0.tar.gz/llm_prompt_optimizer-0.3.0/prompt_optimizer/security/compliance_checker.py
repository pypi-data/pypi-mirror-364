"""
Compliance checking for regulatory requirements.
"""

import re
from typing import Dict, List, Optional, Set
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class ComplianceType(str, Enum):
    """Types of compliance requirements."""
    GDPR = "gdpr"
    HIPAA = "hipaa"
    PCI_DSS = "pci_dss"
    SOX = "sox"
    CCPA = "ccpa"
    FERPA = "ferpa"


class ComplianceLevel(str, Enum):
    """Compliance levels."""
    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    REQUIRES_REVIEW = "requires_review"


@dataclass
class ComplianceResult:
    """Result of compliance checking."""
    is_compliant: bool
    compliance_type: ComplianceType
    level: ComplianceLevel
    violations: List[str]
    recommendations: List[str]
    risk_score: float  # 0.0 to 1.0


class ComplianceChecker:
    """Check compliance with various regulatory requirements."""
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self._load_compliance_patterns()
        
    def _load_compliance_patterns(self):
        """Load patterns for different compliance requirements."""
        # GDPR patterns
        self.gdpr_patterns = {
            'personal_data': [
                r'\b(name|address|phone|email|ssn|passport|id)\b',
                r'\b(birth|date of birth|dob|age)\b',
                r'\b(location|gps|coordinates|address)\b',
                r'\b(ip address|mac address|device id)\b',
                r'\b(credit card|bank account|financial)\b',
            ],
            'sensitive_data': [
                r'\b(health|medical|diagnosis|treatment)\b',
                r'\b(race|ethnicity|religion|political)\b',
                r'\b(sexual|orientation|gender|identity)\b',
                r'\b(criminal|conviction|arrest|record)\b',
            ]
        }
        
        # HIPAA patterns
        self.hipaa_patterns = {
            'phi': [
                r'\b(patient|medical|diagnosis)\b',
                r'\b(treatment|medication|prescription)\b',
                r'\b(symptoms|condition|disease|illness)\b',
                r'\b(doctor|physician|nurse|hospital)\b',
                r'\b(insurance|policy|claim|benefits)\b',
                # More specific health patterns
                r'\b(health care|healthcare|medical care)\b',
                r'\b(health insurance|medical insurance)\b',
            ],
            'identifiers': [
                r'\b\d{3}-\d{2}-\d{4}\b',  # SSN
                r'\b\d{3}-\d{3}-\d{4}\b',  # Phone
                r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # Email
                r'\b\d{1,2}/\d{1,2}/\d{4}\b',  # Date
            ]
        }
        
        # PCI DSS patterns
        self.pci_patterns = {
            'card_data': [
                r'\b\d{4}-\d{4}-\d{4}-\d{4}\b',  # Credit card
                r'\b(cvv|cvc|cvv2|security code)\b',
                r'\b(expiry|expiration|exp)\b',
                r'\b(pin|password|passcode)\b',
            ],
            'context': [
                r'\b(credit card|debit card|payment card)\b',
                r'\b(card number|account number)\b',
                r'\b(payment|transaction|billing)\b',
            ]
        }
        
        # CCPA patterns
        self.ccpa_patterns = {
            'personal_info': [
                r'\b(name|address|phone|email)\b',
                r'\b(california|ca resident)\b',
                r'\b(consumer|customer|user)\b',
                r'\b(sell|sold|selling|sale)\b.*\b(personal|information|data)\b',
            ],
            'context': [
                r'\b(personal information|personal data)\b',
                r'\b(consumer data|customer data)\b',
                r'\b(data collection|data sharing)\b',
            ]
        }
        
    def check_gdpr_compliance(self, text: str, context: Optional[Dict] = None) -> ComplianceResult:
        """Check GDPR compliance of text."""
        violations = []
        risk_score = 0.0
        
        # Check for personal data
        for pattern in self.gdpr_patterns['personal_data']:
            if re.search(pattern, text, re.IGNORECASE):
                violations.append(f"Personal data detected: {pattern}")
                risk_score += 0.3
                
        # Check for sensitive data
        for pattern in self.gdpr_patterns['sensitive_data']:
            if re.search(pattern, text, re.IGNORECASE):
                violations.append(f"Sensitive data detected: {pattern}")
                risk_score += 0.5
                
        # Check for consent language (only if personal data is detected)
        if any(re.search(pattern, text, re.IGNORECASE) for pattern in self.gdpr_patterns['personal_data'] + self.gdpr_patterns['sensitive_data']):
            if not re.search(r'\b(consent|permission|authorize|agree)\b', text, re.IGNORECASE):
                violations.append("Missing consent language")
                risk_score += 0.2
            
        # Determine compliance level
        if risk_score == 0.0:
            level = ComplianceLevel.COMPLIANT
        elif risk_score >= 0.8:  # Make it more lenient
            level = ComplianceLevel.NON_COMPLIANT
        else:
            level = ComplianceLevel.REQUIRES_REVIEW
            
        # Generate recommendations
        recommendations = self._generate_gdpr_recommendations(violations, risk_score)
        
        return ComplianceResult(
            is_compliant=level == ComplianceLevel.COMPLIANT,
            compliance_type=ComplianceType.GDPR,
            level=level,
            violations=violations,
            recommendations=recommendations,
            risk_score=min(risk_score, 1.0)
        )
        
    def check_hipaa_compliance(self, text: str, context: Optional[Dict] = None) -> ComplianceResult:
        """Check HIPAA compliance of text."""
        violations = []
        risk_score = 0.0
        
        # Check for PHI
        phi_detected = False
        for pattern in self.hipaa_patterns['phi']:
            if re.search(pattern, text, re.IGNORECASE):
                phi_detected = True
                violations.append(f"PHI detected: {pattern}")
                risk_score += 0.4
                
        # Check for identifiers
        identifier_detected = False
        for pattern in self.hipaa_patterns['identifiers']:
            if re.search(pattern, text, re.IGNORECASE):
                identifier_detected = True
                violations.append(f"Personal identifier detected: {pattern}")
                risk_score += 0.6
                
        # Only flag as non-compliant if both PHI and identifiers are present
        if not (phi_detected and identifier_detected):
            risk_score = 0.0
            violations = []
                
        # Check for security measures (only if PHI is detected)
        if phi_detected and not re.search(r'\b(encrypt|secure|protect|safeguard)\b', text, re.IGNORECASE):
            violations.append("Missing security measures language")
            risk_score += 0.2
            
        # Determine compliance level
        if risk_score == 0.0:
            level = ComplianceLevel.COMPLIANT
        elif risk_score >= 0.8:
            level = ComplianceLevel.NON_COMPLIANT
        else:
            level = ComplianceLevel.REQUIRES_REVIEW
            
        # Generate recommendations
        recommendations = self._generate_hipaa_recommendations(violations, risk_score)
        
        return ComplianceResult(
            is_compliant=level == ComplianceLevel.COMPLIANT,
            compliance_type=ComplianceType.HIPAA,
            level=level,
            violations=violations,
            recommendations=recommendations,
            risk_score=min(risk_score, 1.0)
        )
        
    def check_pci_compliance(self, text: str, context: Optional[Dict] = None) -> ComplianceResult:
        """Check PCI DSS compliance of text."""
        violations = []
        risk_score = 0.0
        
        # Check for card data
        card_data_detected = False
        for pattern in self.pci_patterns['card_data']:
            if re.search(pattern, text, re.IGNORECASE):
                card_data_detected = True
                violations.append(f"Card data detected: {pattern}")
                risk_score += 0.8
                
        # Check for payment context
        payment_context = any(re.search(pattern, text, re.IGNORECASE) for pattern in self.pci_patterns['context'])
        
        # Only flag as non-compliant if there's actual card data (not just context)
        if not card_data_detected:
            risk_score = 0.0
            violations = []
                
        # Check for security measures (only if card data is detected)
        if card_data_detected and not re.search(r'\b(encrypt|tokenize|mask|secure)\b', text, re.IGNORECASE):
            violations.append("Missing security measures for card data")
            risk_score += 0.3
            
        # Determine compliance level
        if risk_score == 0.0:
            level = ComplianceLevel.COMPLIANT
        elif risk_score >= 0.5:
            level = ComplianceLevel.NON_COMPLIANT
        else:
            level = ComplianceLevel.REQUIRES_REVIEW
            
        # Generate recommendations
        recommendations = self._generate_pci_recommendations(violations, risk_score)
        
        return ComplianceResult(
            is_compliant=level == ComplianceLevel.COMPLIANT,
            compliance_type=ComplianceType.PCI_DSS,
            level=level,
            violations=violations,
            recommendations=recommendations,
            risk_score=min(risk_score, 1.0)
        )
        
    def check_ccpa_compliance(self, text: str, context: Optional[Dict] = None) -> ComplianceResult:
        """Check CCPA compliance of text."""
        violations = []
        risk_score = 0.0
        
        # Check for personal information
        personal_info_detected = False
        for pattern in self.ccpa_patterns['personal_info']:
            if re.search(pattern, text, re.IGNORECASE):
                personal_info_detected = True
                violations.append(f"Personal information detected: {pattern}")
                risk_score += 0.3
                
        # Check for data selling context
        data_selling_context = any(re.search(pattern, text, re.IGNORECASE) for pattern in self.ccpa_patterns['context'])
        
        # Check for data selling
        if re.search(r'\b(sell|sold|selling|sale)\b.*\b(personal|information|data)\b', text, re.IGNORECASE):
            violations.append("Data selling detected without opt-out")
            risk_score += 0.5
            
        # Only flag as non-compliant if there's actual personal info or data selling
        if not (personal_info_detected or data_selling_context):
            risk_score = 0.0
            violations = []
            
        # Check for opt-out language (only if personal info is detected)
        if personal_info_detected and not re.search(r'\b(opt.?out|do not sell|privacy rights)\b', text, re.IGNORECASE):
            violations.append("Missing opt-out language")
            risk_score += 0.2
            
        # Determine compliance level
        if risk_score == 0.0:
            level = ComplianceLevel.COMPLIANT
        elif risk_score >= 0.6:
            level = ComplianceLevel.NON_COMPLIANT
        else:
            level = ComplianceLevel.REQUIRES_REVIEW
            
        # Generate recommendations
        recommendations = self._generate_ccpa_recommendations(violations, risk_score)
        
        return ComplianceResult(
            is_compliant=level == ComplianceLevel.COMPLIANT,
            compliance_type=ComplianceType.CCPA,
            level=level,
            violations=violations,
            recommendations=recommendations,
            risk_score=min(risk_score, 1.0)
        )
        
    def _generate_gdpr_recommendations(self, violations: List[str], risk_score: float) -> List[str]:
        """Generate GDPR compliance recommendations."""
        recommendations = []
        
        if "Personal data detected" in str(violations):
            recommendations.append("Implement data minimization principles")
            recommendations.append("Add explicit consent mechanisms")
            
        if "Sensitive data detected" in str(violations):
            recommendations.append("Implement additional safeguards for sensitive data")
            recommendations.append("Require explicit consent for sensitive data processing")
            
        if "Missing consent language" in str(violations):
            recommendations.append("Add clear consent language")
            recommendations.append("Implement opt-in mechanisms")
            
        if risk_score >= 0.7:
            recommendations.append("Conduct Data Protection Impact Assessment (DPIA)")
            recommendations.append("Appoint a Data Protection Officer (DPO)")
            
        return recommendations
        
    def _generate_hipaa_recommendations(self, violations: List[str], risk_score: float) -> List[str]:
        """Generate HIPAA compliance recommendations."""
        recommendations = []
        
        if "PHI detected" in str(violations):
            recommendations.append("Implement administrative, physical, and technical safeguards")
            recommendations.append("Conduct regular risk assessments")
            
        if "Personal identifier detected" in str(violations):
            recommendations.append("De-identify or anonymize personal identifiers")
            recommendations.append("Implement access controls and audit logs")
            
        if "Missing security measures" in str(violations):
            recommendations.append("Add encryption and access controls")
            recommendations.append("Implement audit trails")
            
        if risk_score >= 0.8:
            recommendations.append("Conduct comprehensive security assessment")
            recommendations.append("Implement Business Associate Agreements (BAAs)")
            
        return recommendations
        
    def _generate_pci_recommendations(self, violations: List[str], risk_score: float) -> List[str]:
        """Generate PCI DSS compliance recommendations."""
        recommendations = []
        
        if "Card data detected" in str(violations):
            recommendations.append("Implement tokenization or encryption")
            recommendations.append("Use secure payment processors")
            recommendations.append("Implement data retention policies")
            
        if "Missing security measures" in str(violations):
            recommendations.append("Add encryption and security controls")
            recommendations.append("Implement access controls and monitoring")
            
        if risk_score >= 0.5:
            recommendations.append("Conduct PCI DSS assessment")
            recommendations.append("Implement security monitoring and logging")
            
        return recommendations
        
    def _generate_ccpa_recommendations(self, violations: List[str], risk_score: float) -> List[str]:
        """Generate CCPA compliance recommendations."""
        recommendations = []
        
        if "Personal information detected" in str(violations):
            recommendations.append("Implement data inventory and mapping")
            recommendations.append("Add privacy notice requirements")
            
        if "Data selling detected" in str(violations):
            recommendations.append("Implement opt-out mechanisms")
            recommendations.append("Add 'Do Not Sell My Personal Information' link")
            
        if "Missing opt-out language" in str(violations):
            recommendations.append("Add clear opt-out instructions")
            recommendations.append("Implement consumer rights mechanisms")
            
        if risk_score >= 0.6:
            recommendations.append("Conduct CCPA compliance audit")
            recommendations.append("Implement consumer request handling procedures")
            
        return recommendations
        
    def check_all_compliance(self, text: str, context: Optional[Dict] = None) -> Dict[ComplianceType, ComplianceResult]:
        """Check all compliance types for the given text."""
        results = {}
        
        results[ComplianceType.GDPR] = self.check_gdpr_compliance(text, context)
        results[ComplianceType.HIPAA] = self.check_hipaa_compliance(text, context)
        results[ComplianceType.PCI_DSS] = self.check_pci_compliance(text, context)
        results[ComplianceType.CCPA] = self.check_ccpa_compliance(text, context)
        
        return results 