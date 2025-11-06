"""
Context-Specific Threat Detection Module

This module provides enhanced detection for specific threat categories that require
more targeted pattern matching beyond general violence detection.

Categories:
- School/Mass Violence Threats
- Self-Harm Methods (Expanded)
- Drug Manufacturing (Specific)
- Specific Weapons
- Workplace Violence
- Target-Specific Threats
"""

import re
from typing import Dict, List, Tuple
from dataclasses import dataclass
from enum import Enum


class ThreatCategory(Enum):
    """Specific threat categories with severity levels"""
    SCHOOL_THREAT = "school_threat"
    SELF_HARM = "self_harm"
    DRUG_MANUFACTURING = "drug_manufacturing"
    SPECIFIC_WEAPON = "specific_weapon"
    WORKPLACE_VIOLENCE = "workplace_violence"
    TARGET_THREAT = "target_threat"
    SEXUAL_VIOLENCE = "sexual_violence"
    MEDICAL_MISINFORMATION = "medical_misinformation"
    EXPLICIT_SEXUAL_CONTENT = "explicit_sexual_content"


@dataclass
class ContextThreatResult:
    """Result from context-specific threat detection"""
    detected: bool
    category: ThreatCategory = None
    severity: str = "none"  # none, medium, high, critical
    matched_patterns: List[str] = None
    confidence: float = 0.0
    explanation: str = ""
    
    def __post_init__(self):
        if self.matched_patterns is None:
            self.matched_patterns = []


class ContextSpecificThreatDetector:
    """Detects context-specific threats with high precision"""
    
    def __init__(self):
        self.patterns = self._initialize_patterns()
    
    def _initialize_patterns(self) -> Dict[ThreatCategory, Dict]:
        """Initialize all context-specific threat patterns"""
        
        return {
            ThreatCategory.SCHOOL_THREAT: {
                'severity': 'critical',
                'patterns': [
                    # Direct school violence threats
                    r'\bshoot\s+up\s+(the\s+)?school\b',
                    r'\battack\s+(the\s+)?school\b',
                    r'\bschool\s+shooting\b',
                    r'\bbring\s+(a\s+)?gun\s+to\s+school\b',
                    r'\bmass\s+shooting\s+at\s+(the\s+)?school\b',
                    r'\bactive\s+shooter\s+(at\s+)?(the\s+)?school\b',
                    r'\bcolumbine\s+style\b',
                    r'\battack\s+students\b',
                    r'\bkill\s+(my\s+)?classmates\b',
                    r'\bshoot\s+(my\s+)?teacher\b',
                    r'\bbomb\s+(the\s+)?school\b',
                    r'\bexplosive\s+(at|in)\s+school\b',
                    r'\bshoot\s+everyone\s+(at|in)\s+school\b',
                    r'\bkill\s+everyone\s+(at|in)\s+school\b',
                    # Variations
                    r'\bcampus\s+shooting\b',
                    r'\buniversity\s+(massacre|shooting|attack)\b',
                    r'\bcollege\s+(massacre|shooting|attack)\b',
                ]
            },
            
            ThreatCategory.SELF_HARM: {
                'severity': 'critical',
                'patterns': [
                    # Methods and tools
                    r'\bcut\s+myself\s+with\b',
                    r'\bhurt\s+myself\s+with\b',
                    r'\boverdose\s+on\b',
                    r'\bhang\s+myself\b',
                    r'\bjump\s+off\s+(a|the)\b',
                    r'\bcarbon\s+monoxide\b',
                    r'\bwrist\s+cutting\b',
                    r'\bself\s+injury\b',
                    r'\bslit\s+my\s+(wrists?|throat)\b',
                    # Specific methods
                    r'\btake\s+all\s+(the|my)\s+pills\b',
                    r'\bdrink\s+bleach\b',
                    r'\bswallow\s+(pills|poison)\b',
                    r'\bnoose\b.*\bmyself\b',
                    r'\bself\s+harm\s+(methods?|techniques?|ways?)\b',
                    r'\bhow\s+to\s+(cut|harm|hurt)\s+myself\b',
                    r'\bpainless\s+suicide\b',
                    r'\bsuicide\s+(method|technique|way)\b',
                    r'\bend\s+my\s+life\b',
                    r'\bways?\s+to\s+(commit|do)\s+suicide\b',
                    r'\bcommit\s+suicide\b',
                    r'\bkill\s+myself\b',
                    # Intent with tools
                    r'\b(razor|blade|knife)\s+to\s+(cut|harm)\s+myself\b',
                    # Encouragement and promotion (CRITICAL ADDITION)
                    r'\b(write|create|make)\s+(a\s+)?(poem|story|song|essay|content)\s+(that\s+)?(encourages?|promotes?|glorifies?|celebrates?)\s+(self-?harm|suicide|cutting)\b',
                    r'\b(story|poem|content)\s+(promoting|glorifying|celebrating|encouraging)\s+(self-?harm|suicide|cutting|self-?injury)\b',
                    r'\bencourage(s|d|ing)?\s+(people\s+to\s+)?(self-?harm|hurt\s+themselves|cut|suicide)\b',
                    r'\bpromote(s|d|ing)?\s+(self-?harm|suicide|cutting)\b',
                    r'\bglorif(y|ies|ied|ying)\s+(self-?harm|suicide|cutting|self-?injury)\b',
                    r'\bcelebrat(e|es|ed|ing)\s+(self-?harm|suicide|cutting)\b',
                    r'\bself-?harm\s+(is|as)\s+(good|beautiful|art)\b',
                    r'\b(poem|story|content)\s+(about|encouraging|promoting)\s+(suicide|self-?harm)\b',
                    r'\bsuicide\s+(is|as)\s+(the\s+)?(solution|answer|good|best)\b',
                    r'\b(make|write|create)\s+(something|content)\s+(that\s+)?(encourages?|promotes?)\b',
                ]
            },
            
            ThreatCategory.DRUG_MANUFACTURING: {
                'severity': 'high',
                'patterns': [
                    # Meth production
                    r'\bcook\s+meth(amphetamine)?\b',
                    r'\bmeth\s+lab\b',
                    r'\bshake\s+and\s+bake\s+(meth|method)\b',
                    r'\bone\s+pot\s+method\b',
                    r'\bpseudoephedrine\s+(reduction|synthesis)\b',
                    r'\bred\s+phosphorus\s+(method|meth)\b',
                    # Other drugs
                    r'\bsynthesize\s+(mdma|lsd|dmt|pcp)\b',
                    r'\bextract\s+dmt\b',
                    r'\bmake\s+(lsd|crack)\b',
                    r'\bgrow\s+opium\b',
                    r'\bcrack\s+cocaine\s+(production|making|cook|instructions?)\b',
                    r'\bhomebrew\s+(meth|amphetamine|mdma)\b',
                    r'\bmake\s+crack\s+cocaine\b',
                    r'\binstruction(s)?\s+to\s+make\s+(crack|meth|cocaine)\b',
                    # Specific chemicals/processes
                    r'\banhydrous\s+ammonia\b.*\bmeth\b',
                    r'\blithium\s+strips\b.*\bmeth\b',
                    r'\bephedrine\s+(extraction|reduction)\b',
                    r'\bfentanyl\s+(synthesis|analog)\b',
                    r'\bclandestine\s+lab\b',
                    # Instructions
                    r'\bhow\s+to\s+(cook|make|synthesize|produce)\s+(meth|mdma|lsd|crack)\b',
                    r'\bdrug\s+(synthesis|production)\s+(guide|tutorial|instructions)\b',
                ]
            },
            
            ThreatCategory.SPECIFIC_WEAPON: {
                'severity': 'high',
                'patterns': [
                    # Specific firearms
                    r'\bar-?15\b',
                    r'\bak-?47\b',
                    r'\bak-?74\b',
                    r'\bassault\s+rifle\b',
                    r'\bsemi-?automatic\s+(rifle|weapon|gun)\b',
                    r'\bfully?\s+automatic\b',
                    r'\bhigh\s+capacity\s+magazine\b',
                    r'\bdrum\s+magazine\b',
                    r'\bbump\s+stock\b',
                    r'\bsilencer\b',
                    r'\bsuppressor\b',
                    # Explosives
                    r'\bpipe\s+bomb\b',
                    r'\bpressure\s+cooker\s+bomb\b',
                    r'\bnail\s+bomb\b',
                    r'\bcar\s+bomb\b',
                    r'\bc-?4\s+explosive\b',
                    r'\btnt\b.*\b(bomb|explosive)\b',
                    r'\bimo\s+(bomb|explosive)\b',
                    r'\bmolotov\s+cocktail\b',
                    # IEDs and components
                    r'\bied\s+(construction|making|building)\b',
                    r'\bhomemade\s+(explosive|bomb)\b',
                    r'\bfertilizer\s+bomb\b',
                    r'\banfo\s+(explosive|bomb)\b',
                    # Specific models
                    r'\bglock\s+\d+\b',
                    r'\bdesert\s+eagle\b',
                    r'\buzi\b',
                    r'\bmac-?10\b',
                ]
            },
            
            ThreatCategory.WORKPLACE_VIOLENCE: {
                'severity': 'critical',
                'patterns': [
                    # Direct workplace threats
                    r'\bshoot\s+up\s+(the\s+)?office\b',
                    r'\bkill\s+(my\s+)?boss\b',
                    r'\battack\s+(my\s+)?coworkers?\b',
                    r'\bbring\s+(a\s+)?(gun|weapon)\s+to\s+work\b',
                    r'\bgoing\s+postal\b',
                    r'\bworkplace\s+(shooting|violence|attack)\b',
                    # Targeting management
                    r'\bshoot\s+(my\s+)?(manager|supervisor)\b',
                    r'\bharm\s+(my\s+)?(boss|manager|supervisor)\b',
                    r'\bget\s+revenge\s+(on|at)\s+work\b',
                    # Specific scenarios
                    r'\bshoot\s+everyone\s+(at|in)\s+(the\s+)?(office|work)\b',
                    r'\bmassacre\s+(at|in)\s+(the\s+)?(office|workplace)\b',
                    r'\bbomb\s+(the\s+)?(office|workplace)\b',
                ]
            },
            
            ThreatCategory.TARGET_THREAT: {
                'severity': 'critical',
                'patterns': [
                    # Government/political targets
                    r'\bkill\s+(the\s+)?president\b',
                    r'\bassassinate\s+(the\s+)?(president|governor|mayor)\b',
                    r'\battack\s+(the\s+)?(white\s+house|capitol|congress)\b',
                    r'\bbomb\s+(the\s+)?(white\s+house|capitol|pentagon)\b',
                    r'\bshoot\s+(the\s+)?(president|vp|vice\s+president)\b',
                    # Mass casualty targets
                    r'\bshoot\s+up\s+(the|a)\s+(mall|theater|church|mosque|synagogue|temple)\b',
                    r'\bmassacre\s+at\s+(the|a)\b',
                    r'\bbomb\s+(the|a)\s+(mall|airport|station|stadium|shopping)\b',
                    r'\bterrorist\s+attack\s+(on|at)\b',
                    r'\bplant\s+(a\s+)?bomb\s+(at|in)\b',
                    r'\bexplosive\s+(at|in)\s+(the|a)\s+(mall|airport)\b',
                    # Specific venues
                    r'\battack\s+(the|a)\s+(concert|festival|parade|rally)\b',
                    r'\bshoot\s+up\s+(the|a)\s+(concert|movie|event)\b',
                    # Transportation
                    r'\bhijack\s+(a|the)\s+(plane|aircraft|bus|train)\b',
                    r'\bblow\s+up\s+(a|the)\s+(plane|bus|train)\b',
                ]
            },
            
            ThreatCategory.SEXUAL_VIOLENCE: {
                'severity': 'critical',
                'patterns': [
                    # Sexual assault/rape
                    r'\bsexual\s+assault\s+(scene|scenario|description)\b',
                    r'\bdescribe\s+(a\s+)?sexual\s+assault\b',
                    r'\bwrite\s+(a\s+)?rape\s+(scene|story)\b',
                    r'\bdescribe\s+(a\s+)?rape\b',
                    r'\bhow\s+to\s+(rape|sexually\s+assault)\b',
                    r'\bforced\s+sex\s+(scene|scenario)\b',
                    r'\bnon-?consensual\s+sex\s+(scene|story)\b',
                    r'\bviolent\s+sex\s+scene\b',
                    # Child exploitation
                    r'\bchild\s+(sexual|porn(ography)?|exploitation)\b',
                    r'\bpedophil(ia|e)\b',
                    r'\bminor\s+(sexual|nude|explicit)\b',
                    r'\bunderage\s+(sex|sexual|nude)\b',
                    r'\bcsam\b',  # Child Sexual Abuse Material
                    r'\bcp\b.*\b(content|material|images)\b',
                    r'\bchild\s+abuse\s+material\b',
                    r'\bexploit(ing)?\s+(child|minor|kid)\b',
                    # Sexual exploitation
                    r'\bsex\s+trafficking\b',
                    r'\bsexual\s+slavery\b',
                    r'\bforce(d)?\s+(into|to)\s+(prostitution|sex)\b',
                    r'\bgroom(ing)?\s+(child|minor|kid)\b',
                    # Explicit harmful content
                    r'\bsexualize\s+(child|minor|kid)\b',
                    r'\berotic\s+(child|minor|kid)\b',
                    r'\bincest\s+(scene|story|scenario)\b',
                    # Coercion
                    r'\bblackmail\s+(for|into)\s+sex\b',
                    r'\bcoerce\s+(into|for)\s+sex\b',
                    r'\bdate\s+rape\s+drug\b',
                    r'\brohypnol\b',
                    r'\bdrug\s+(someone|her|him)\s+(for|to)\s+sex\b',
                ]
            },
            
            ThreatCategory.EXPLICIT_SEXUAL_CONTENT: {
                'severity': 'high',
                'patterns': [
                    # Explicit content generation requests
                    r'\b(generate|write|create|make|produce)\s+(explicit|pornographic|erotic|sexual)\s+(content|dialogue|scene|story|material)\b',
                    r'\b(generate|write|create)\s+(porn|pornography|erotica)\b',
                    r'\bexplicit\s+sexual\s+(content|dialogue|scene|material)\b',
                    r'\bpornographic\s+(content|material|scene|story)\b',
                    r'\berotic\s+(content|story|scene|material)\b',
                    r'\bsexual\s+(scene|dialogue|content)\s+(explicit|graphic|detailed)\b',
                    # Explicit scenario requests
                    r'\b(write|describe|generate)\s+(a\s+)?sex\s+(scene|act|scenario)\b',
                    r'\bdetailed\s+sexual\s+(activity|acts|content)\b',
                    r'\bgraphic\s+sexual\s+(content|description|scene)\b',
                    r'\bnsfw\s+(content|material|story)\b',
                    # Adult content requests
                    r'\badult\s+(content|material)\s+(explicit|graphic)\b',
                    r'\b(generate|create)\s+sexual\s+(scenarios?|content|material)\b',
                    r'\bexplicit\s+(adult|mature)\s+content\b',
                ]
            },
            
            ThreatCategory.MEDICAL_MISINFORMATION: {
                'severity': 'high',
                'patterns': [
                    # Vaccine misinformation
                    r'\bvaccines?\s+(cause|caused|causes)\s+(autism|cancer|death)\b',
                    r'\bvaccine\s+contains?\s+(microchips?|trackers?|5g|tracking)\b',
                    r'\bvaccines?\s+contain\s+(microchips?|trackers?)\b',
                    r'\bdon\'?t\s+vaccinate\s+(your\s+)?(child|kid|baby|kids)\b',
                    r'\banti-?vax\s+(truth|facts|proof)\b',
                    r'\bvaccines?\s+(are|is)\s+(poison|toxic|dangerous)\b',
                    r'\bvaccin(e|es?|ation)\s.*\b(poison|dangerous|toxic|harmful)\b',
                    # COVID misinformation
                    r'\bcovid\s+(is\s+(a\s+)?)?(hoax|fake|lie|conspiracy)\b',
                    r'\bcovid\s+(doesn\'?t|does\s+not)\s+exist\b',
                    r'\bdrink\s+bleach\s+(to\s+)?(cure|treat|prevent|for|covid)\b',
                    r'\bbleach\s+(cure|cures?|to\s+cure|for\s+(covid|treatment))\b',
                    r'\bivermectin\s+cures\s+covid\b',
                    r'\bhydroxychloroquine\s+cures\s+covid\b',
                    # Dangerous alternative medicine
                    r'\bcure\s+cancer\s+(with|using)\s+(essential\s+oils?|herbs?|natural)\b',
                    r'\bdon\'?t\s+need\s+(insulin|medication|treatment)\b',
                    r'\bstop\s+taking\s+(your\s+)?(insulin|medication|pills)\b',
                    r'\b(prayer|faith)\s+(cures?|heals?|instead|and\s+)\b',
                    r'\bpray\s+instead\s+of\s+(medication|treatment)\b',
                    # Harmful medical advice
                    r'\bperform\s+(surgery|operation)\s+(at\s+)?home\b',
                    r'\bself-?treat\s+(cancer|infection|disease)\b',
                    r'\bavoid\s+(doctors?|hospitals?|medical\s+care)\b',
                    r'\bmedical\s+system\s+(is\s+)?(lying|corrupt|fake)\b',
                    # Specific dangerous treatments
                    r'\bdrink(ing)?\s+(hydrogen\s+)?peroxide\s+(cures?|treats?|to\s+cure)\b',
                    r'\bperoxide\s+(cure|cures?|to\s+cure)\b',
                    r'\bbleach\s+(therapy|protocol|solution)\b',
                    r'\bmms\s+(miracle\s+mineral\s+solution)\b',
                    r'\bturpentine\s+(cure|treatment|therapy)\b',
                    # Pregnancy/childbirth misinformation
                    r'\bhome\s+abortion\s+(method|procedure|instructions)\b',
                    r'\babortion\s+(method|procedure)\s+at\s+home\b',
                    r'\babortion\s+methods?\s+(that\s+)?(work|at\s+home)\b',
                    r'\bhow\s+to\s+abort\s+at\s+home\b',
                    r'\bunassisted\s+(childbirth|home\s+birth)\s+(is|are)\s+safe\b',
                    r'\bskip\s+prenatal\s+care\b',
                    # Anti-science medical claims
                    r'\bgerm\s+theory\s+(is\s+)?(false|wrong|fake)\b',
                    r'\bviruses?\s+(don\'?t|do\s+not)\s+exist\b',
                    r'\bchemotherapy\s+(kills|poisons?)\b',
                    # Eating disorders promotion
                    r'\bpro-?ana\s+(tips|tricks|advice)\b',
                    r'\bhow\s+to\s+(starve|purge)\s+yourself\b',
                    r'\beating\s+disorder\s+(guide|tips|advice)\b',
                ]
            },
        }
    
    def detect(self, text: str) -> ContextThreatResult:
        """
        Detect context-specific threats in text
        
        Args:
            text: Text to analyze
            
        Returns:
            ContextThreatResult with detection details (first match only)
        """
        if not text or len(text.strip()) < 5:
            return ContextThreatResult(detected=False)
        
        text_lower = text.lower()
        
        # Check each category
        for category, config in self.patterns.items():
            patterns = config['patterns']
            severity = config['severity']
            matched = []
            
            for pattern in patterns:
                if re.search(pattern, text_lower, re.IGNORECASE):
                    matched.append(pattern)
            
            if matched:
                # Calculate confidence based on number of matches
                confidence = min(0.95, 0.70 + (len(matched) * 0.05))
                
                explanation = self._generate_explanation(category, len(matched))
                
                return ContextThreatResult(
                    detected=True,
                    category=category,
                    severity=severity,
                    matched_patterns=matched[:5],  # Limit to first 5
                    confidence=confidence,
                    explanation=explanation
                )
        
        return ContextThreatResult(detected=False)
    
    def detect_all_categories(self, text: str) -> List[ContextThreatResult]:
        """
        Detect ALL context-specific threats in text (checks all categories)
        
        Args:
            text: Text to analyze
            
        Returns:
            List of ContextThreatResult for all detected categories
        """
        if not text or len(text.strip()) < 5:
            return []
        
        text_lower = text.lower()
        results = []
        
        # Check ALL categories
        for category, config in self.patterns.items():
            patterns = config['patterns']
            severity = config['severity']
            matched = []
            
            for pattern in patterns:
                if re.search(pattern, text_lower, re.IGNORECASE):
                    matched.append(pattern)
            
            if matched:
                # Calculate confidence based on number of matches
                confidence = min(0.95, 0.70 + (len(matched) * 0.05))
                
                explanation = self._generate_explanation(category, len(matched))
                
                results.append(ContextThreatResult(
                    detected=True,
                    category=category,
                    severity=severity,
                    matched_patterns=matched[:5],  # Limit to first 5
                    confidence=confidence,
                    explanation=explanation
                ))
        
        return results
    
    def _generate_explanation(self, category: ThreatCategory, match_count: int) -> str:
        """Generate human-readable explanation for detection"""
        
        explanations = {
            ThreatCategory.SCHOOL_THREAT: 
                f"Detected specific school violence threat ({match_count} indicators). "
                "This type of content poses immediate safety concerns.",
            
            ThreatCategory.SELF_HARM:
                f"Detected specific self-harm content with method details ({match_count} indicators). "
                "This requires immediate intervention.",
            
            ThreatCategory.DRUG_MANUFACTURING:
                f"Detected specific drug manufacturing instructions ({match_count} indicators). "
                "This content describes illegal drug production methods.",
            
            ThreatCategory.SPECIFIC_WEAPON:
                f"Detected references to specific weapons or explosives ({match_count} indicators). "
                "Content includes detailed weapon/explosive information.",
            
            ThreatCategory.WORKPLACE_VIOLENCE:
                f"Detected workplace violence threat ({match_count} indicators). "
                "This poses immediate safety concerns for workplace environment.",
            
            ThreatCategory.TARGET_THREAT:
                f"Detected threat against specific target/venue ({match_count} indicators). "
                "This represents a credible threat requiring immediate attention.",
            
            ThreatCategory.SEXUAL_VIOLENCE:
                f"Detected sexual violence content ({match_count} indicators). "
                "This content describes sexual assault, exploitation, or abuse and requires immediate blocking.",
            
            ThreatCategory.EXPLICIT_SEXUAL_CONTENT:
                f"Detected explicit sexual content request ({match_count} indicators). "
                "This request asks for pornographic, explicit, or adult sexual content generation.",
            
            ThreatCategory.MEDICAL_MISINFORMATION:
                f"Detected dangerous medical misinformation ({match_count} indicators). "
                "This content promotes harmful medical advice or misinformation that could endanger health.",
        }
        
        return explanations.get(category, "Context-specific threat detected.")
    
    def get_statistics(self) -> Dict:
        """Get statistics about loaded patterns"""
        stats = {}
        total_patterns = 0
        
        for category, config in self.patterns.items():
            pattern_count = len(config['patterns'])
            total_patterns += pattern_count
            stats[category.value] = {
                'pattern_count': pattern_count,
                'severity': config['severity']
            }
        
        stats['total_patterns'] = total_patterns
        return stats


# Example usage and testing
if __name__ == "__main__":
    detector = ContextSpecificThreatDetector()
    
    print("Context-Specific Threat Detector")
    print("=" * 50)
    print(f"Total patterns loaded: {detector.get_statistics()['total_patterns']}")
    print()
    
    # Test cases
    test_cases = [
        "I'm going to shoot up the school tomorrow",
        "How can I cut myself with a razor blade?",
        "Instructions to cook meth at home",
        "Where can I buy an AR-15?",
        "I want to kill my boss",
        "How to assassinate the president",
        "Safe text about going to school",
    ]
    
    print("Testing threat detection:")
    print("-" * 50)
    
    for text in test_cases:
        result = detector.detect(text)
        print(f"\nText: {text}")
        print(f"Detected: {result.detected}")
        if result.detected:
            print(f"Category: {result.category.value}")
            print(f"Severity: {result.severity}")
            print(f"Confidence: {result.confidence:.2f}")
            print(f"Explanation: {result.explanation}")
