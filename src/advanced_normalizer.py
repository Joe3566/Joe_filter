#!/usr/bin/env python3
"""
🔧 Advanced Text Normalization
Handles leet-speak, unicode tricks, spacing, and other obfuscation techniques
"""

import re
import unicodedata
from typing import Dict, List, Set


class AdvancedTextNormalizer:
    """Advanced text normalization to detect obfuscated harmful content"""
    
    def __init__(self):
        # Comprehensive leet-speak mapping
        self.leetspeak_map = {
            '0': 'o', '1': 'i', '3': 'e', '4': 'a', '5': 's',
            '6': 'g', '7': 't', '8': 'b', '9': 'g',
            '@': 'a', '$': 's', '!': 'i', '|': 'i', '€': 'e',
            '£': 'l', '¥': 'y', '+': 't', '×': 'x',
            '§': 's', '¶': 'p', '©': 'c', '®': 'r',
            '°': 'o', '±': 'i', '²': '2', '³': '3',
            'µ': 'u', '¹': '1', '¼': '1', '½': '1', '¾': '3',
            # Advanced leetspeak
            '()': 'o', '[]': 'i', '{}': 'o', '<>': 'o',
            '/\\/\\': 'm', '\\/\\/': 'w', '|)': 'd', '|3': 'b',
            '|<': 'k', '|_': 'l', '|\\/|': 'm', '|\\|': 'n',
            '|O': 'p', '|2': 'r', '(_)': 'u', '\\/': 'v',
            '\\|/': 'y', '><': 'x', '7H': 'th', 'pH': 'f',
        }
        
        # Common character substitutions
        self.substitution_map = {
            # Lookalike characters
            'а': 'a', 'е': 'e', 'о': 'o', 'р': 'p', 'с': 'c',  # Cyrillic
            'і': 'i', 'х': 'x', 'у': 'y', 'ѕ': 's', 'һ': 'h',
            'ј': 'j', 'ԁ': 'd', 'ɡ': 'g', 'ӏ': 'l', 'ո': 'n',
            # Greek lookalikes
            'α': 'a', 'β': 'b', 'ε': 'e', 'ι': 'i', 'ο': 'o',
            'ρ': 'p', 'σ': 's', 'τ': 't', 'υ': 'u', 'χ': 'x',
            # Mathematical/special lookalikes
            '∩': 'n', '⊂': 'c', '⊃': 'u', '∨': 'v', '∧': 'a',
            '⊗': 'o', '⊕': 'o', '∅': 'o', '∈': 'e', '∋': 'e',
            # Fullwidth characters
            'Ａ': 'a', 'Ｂ': 'b', 'Ｃ': 'c', 'Ｄ': 'd', 'Ｅ': 'e',
            'Ｆ': 'f', 'Ｇ': 'g', 'Ｈ': 'h', 'Ｉ': 'i', 'Ｊ': 'j',
        }
        
        # Invisible/zero-width characters
        self.invisible_chars = {
            '\u200b',  # Zero width space
            '\u200c',  # Zero width non-joiner
            '\u200d',  # Zero width joiner
            '\u2060',  # Word joiner
            '\ufeff',  # Zero width no-break space
            '\u00ad',  # Soft hyphen
        }
        
        # Homoglyph detection patterns
        self.homoglyph_patterns = [
            (r'[кḱǩḵƙķ]', 'k'),
            (r'[ɑαа]', 'a'),
            (r'[ḇḃƀ]', 'b'),
            (r'[çćčċƈ]', 'c'),
            (r'[ďḍḋđ]', 'd'),
            (r'[éèêëēėęěĕəәеɛ]', 'e'),
            (r'[íìîïīįĭıі]', 'i'),
            (r'[óòôöōőøǿоο]', 'o'),
            (r'[úùûüūůűų]', 'u'),
            (r'[ýÿŷ]', 'y'),
        ]
    
    def normalize(self, text: str) -> str:
        """Apply all normalization techniques"""
        # 1. Unicode normalization
        text = self.normalize_unicode(text)
        
        # 2. Remove invisible characters
        text = self.remove_invisible_chars(text)
        
        # 3. Normalize spacing
        text = self.normalize_spacing(text)
        
        # 4. Decode leetspeak
        text = self.decode_leetspeak(text)
        
        # 5. Replace homoglyphs
        text = self.replace_homoglyphs(text)
        
        # 6. Normalize case
        text = text.lower()
        
        # 7. Remove excessive punctuation
        text = self.normalize_punctuation(text)
        
        return text
    
    def normalize_unicode(self, text: str) -> str:
        """Normalize unicode to standard form"""
        # NFD normalization separates accents from characters
        text = unicodedata.normalize('NFD', text)
        # Remove accent marks (combining characters)
        text = ''.join(char for char in text 
                      if unicodedata.category(char) != 'Mn')
        return text
    
    def remove_invisible_chars(self, text: str) -> str:
        """Remove zero-width and invisible characters"""
        return ''.join(char for char in text 
                      if char not in self.invisible_chars)
    
    def normalize_spacing(self, text: str) -> str:
        """Normalize excessive spacing and punctuation insertion"""
        # Remove spaces between letters (e.g., "b o m b" -> "bomb")
        # But preserve word boundaries
        text = re.sub(r'(?<=\w)\s+(?=\w)', '', text)
        
        # Normalize multiple spaces to single space
        text = re.sub(r'\s+', ' ', text)
        
        # Remove punctuation inserted between letters
        # e.g., "k.i.l.l" -> "kill"
        text = re.sub(r'(?<=\w)[.,;:!?-]+(?=\w)', '', text)
        
        return text.strip()
    
    def decode_leetspeak(self, text: str) -> str:
        """Convert leetspeak to normal text"""
        result = text.lower()
        
        # Handle multi-character leetspeak first
        for leet, normal in sorted(self.leetspeak_map.items(), 
                                   key=lambda x: -len(x[0])):
            if len(leet) > 1:
                result = result.replace(leet, normal)
        
        # Then single-character replacements
        translation_table = str.maketrans(
            {k: v for k, v in self.leetspeak_map.items() if len(k) == 1}
        )
        result = result.translate(translation_table)
        
        return result
    
    def replace_homoglyphs(self, text: str) -> str:
        """Replace visually similar characters"""
        # Apply direct substitutions
        for fake, real in self.substitution_map.items():
            text = text.replace(fake, real)
        
        # Apply pattern-based replacements
        for pattern, replacement in self.homoglyph_patterns:
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
        
        return text
    
    def normalize_punctuation(self, text: str) -> str:
        """Normalize excessive punctuation"""
        # Remove repeated punctuation
        text = re.sub(r'([!?.,;:]){2,}', r'\1', text)
        
        # Remove punctuation at word boundaries that might be obfuscation
        # But keep sentence-ending punctuation
        text = re.sub(r'(?<=\w)[!?.,;:]+(?=\s|$)', '', text)
        
        return text
    
    def get_normalization_variants(self, text: str) -> List[str]:
        """Generate multiple normalized variants for better detection"""
        variants = [text]
        
        # Original normalized
        variants.append(self.normalize(text))
        
        # Without punctuation
        no_punct = re.sub(r'[^\w\s]', '', text)
        variants.append(self.normalize(no_punct))
        
        # Lowercase only
        variants.append(text.lower())
        
        # Remove all spaces
        variants.append(re.sub(r'\s+', '', self.normalize(text)))
        
        # Unique variants only
        return list(set(variants))
    
    def detect_obfuscation_techniques(self, text: str) -> Dict[str, bool]:
        """Detect which obfuscation techniques are being used"""
        techniques = {
            'leetspeak': False,
            'excessive_spacing': False,
            'invisible_chars': False,
            'homoglyphs': False,
            'mixed_case': False,
            'punctuation_insertion': False,
            'unicode_tricks': False,
        }
        
        # Detect leetspeak
        if any(char in text for char in '0134578@$!|'):
            techniques['leetspeak'] = True
        
        # Detect excessive spacing
        if re.search(r'\w\s+\w\s+\w', text):
            techniques['excessive_spacing'] = True
        
        # Detect invisible characters
        if any(char in text for char in self.invisible_chars):
            techniques['invisible_chars'] = True
        
        # Detect homoglyphs
        if any(char in text for char in self.substitution_map.keys()):
            techniques['homoglyphs'] = True
        
        # Detect mixed case obfuscation
        if re.search(r'[a-z][A-Z][a-z]|[A-Z][a-z][A-Z]', text):
            techniques['mixed_case'] = True
        
        # Detect punctuation insertion
        if re.search(r'\w[.,;:!?-]+\w', text):
            techniques['punctuation_insertion'] = True
        
        # Detect unicode tricks
        try:
            if text != text.encode('ascii', 'ignore').decode('ascii'):
                techniques['unicode_tricks'] = True
        except:
            techniques['unicode_tricks'] = True
        
        return techniques


# Demo function
def demo_normalizer():
    """Demonstrate normalization capabilities"""
    normalizer = AdvancedTextNormalizer()
    
    test_cases = [
        ("H0w t0 m4k3 @ b0mb", "Leetspeak"),
        ("How to make a b o m b", "Spacing obfuscation"),
        ("k.i.l.l someone", "Punctuation insertion"),
        ("КІᏞᏞsomeone", "Homoglyphs (Cyrillic/Cherokee)"),
        ("KILL\u200bSOMEONE", "Zero-width space"),
        ("kIlL sOmEoNe", "Mixed case"),
        ("b0mb\u200c\u200dwith\u200bsp@ces", "Combined tricks"),
        ("ᖯ⊕ʍᖲ", "Unicode special characters"),
    ]
    
    print("🔧 Advanced Text Normalization Demo\n")
    print("=" * 80)
    
    for text, description in test_cases:
        normalized = normalizer.normalize(text)
        techniques = normalizer.detect_obfuscation_techniques(text)
        active_techniques = [k for k, v in techniques.items() if v]
        
        print(f"\n📝 {description}")
        print(f"   Original:   {repr(text)}")
        print(f"   Normalized: {normalized}")
        print(f"   Techniques: {', '.join(active_techniques) if active_techniques else 'None'}")
        print("-" * 80)


if __name__ == "__main__":
    demo_normalizer()
