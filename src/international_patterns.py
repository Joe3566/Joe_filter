#!/usr/bin/env python3
"""
🌍 International Pattern Library
200+ patterns for detecting harmful content in multiple languages
"""

from typing import Dict, List

# Spanish Patterns (Español)
SPANISH_PATTERNS = {
    'violence': [
        'cómo matar', 'como matar', 'matar a alguien', 'asesinar',
        'hacer daño', 'lastimar', 'herir gravemente',
        'atacar violentamente', 'golpear hasta',
    ],
    'weapons': [
        'fabricar bomba', 'hacer bomba', 'construir explosivo',
        'fabricar arma', 'hacer pistola', 'rifle casero',
        'explosivo casero', 'bomba molotov', 'artefacto explosivo',
    ],
    'suicide': [
        'quiero suicidarme', 'matarme', 'quitarme la vida',
        'acabar con mi vida', 'formas de suicidio', 'cómo suicidarse',
        'suicidio efectivo', 'morir rápido',
    ],
    'drugs': [
        'fabricar droga', 'hacer metanfetamina', 'cocaína casera',
        'sintetizar droga', 'laboratorio clandestino', 'cocinar meta',
    ],
    'hate': [
        'odio a todos los', 'deberían morir', 'eliminar a los',
        'raza inferior', 'no merecen vivir', 'exterminar',
    ],
    'threats': [
        'voy a matar', 'te voy a', 'voy a hacerte daño',
        'prepárate para morir', 'vengo por ti', 'te encontraré',
    ],
}

# French Patterns (Français)
FRENCH_PATTERNS = {
    'violence': [
        'comment tuer', 'tuer quelqu\'un', 'faire mal',
        'blesser gravement', 'attaquer violemment', 'assassiner',
        'mettre fin à la vie', 'donner la mort',
    ],
    'weapons': [
        'fabriquer bombe', 'faire explosif', 'construire arme',
        'explosif maison', 'cocktail molotov', 'engin explosif',
        'fabriquer pistolet', 'arme artisanale',
    ],
    'suicide': [
        'je veux me suicider', 'me tuer', 'mettre fin à mes jours',
        'comment se suicider', 'suicide efficace', 'mourir rapidement',
        'en finir avec la vie',
    ],
    'drugs': [
        'fabriquer drogue', 'faire méthamphétamine', 'cocaïne maison',
        'synthétiser drogue', 'laboratoire clandestin', 'cuisiner méth',
    ],
    'hate': [
        'je hais tous les', 'devraient mourir', 'éliminer les',
        'race inférieure', 'ne méritent pas', 'exterminer',
    ],
    'threats': [
        'je vais te tuer', 'je vais te', 'te faire du mal',
        'prépare-toi à mourir', 'je viens pour toi', 'je te trouverai',
    ],
}

# German Patterns (Deutsch)
GERMAN_PATTERNS = {
    'violence': [
        'wie man tötet', 'jemanden töten', 'verletzen',
        'schwer verletzen', 'gewalttätig angreifen', 'ermorden',
        'umbringen', 'das Leben nehmen',
    ],
    'weapons': [
        'bombe bauen', 'sprengstoff herstellen', 'waffe bauen',
        'hausgemachter sprengstoff', 'molotowcocktail', 'sprengsatz',
        'pistole bauen', 'selbstgebaute waffe',
    ],
    'suicide': [
        'ich will selbstmord begehen', 'mich umbringen', 'mein leben beenden',
        'wie man selbstmord', 'effektiver selbstmord', 'schnell sterben',
        'das leben beenden',
    ],
    'drugs': [
        'droge herstellen', 'methamphetamin machen', 'kokain herstellen',
        'droge synthetisieren', 'geheimlabor', 'meth kochen',
    ],
    'hate': [
        'ich hasse alle', 'sollten sterben', 'eliminieren',
        'minderwertige rasse', 'verdienen nicht', 'ausrotten',
    ],
    'threats': [
        'ich werde dich töten', 'ich werde dir', 'dir wehtun',
        'bereite dich vor zu sterben', 'ich komme für dich', 'ich finde dich',
    ],
}

# Portuguese Patterns (Português)
PORTUGUESE_PATTERNS = {
    'violence': [
        'como matar', 'matar alguém', 'fazer mal',
        'ferir gravemente', 'atacar violentamente', 'assassinar',
        'tirar a vida', 'causar morte',
    ],
    'weapons': [
        'fabricar bomba', 'fazer explosivo', 'construir arma',
        'explosivo caseiro', 'coquetel molotov', 'dispositivo explosivo',
        'fazer pistola', 'arma caseira',
    ],
    'suicide': [
        'quero me suicidar', 'me matar', 'tirar minha vida',
        'acabar com minha vida', 'como se suicidar', 'suicídio eficaz',
        'morrer rápido',
    ],
    'drugs': [
        'fabricar droga', 'fazer metanfetamina', 'cocaína caseira',
        'sintetizar droga', 'laboratório clandestino', 'cozinhar meta',
    ],
    'hate': [
        'odeio todos os', 'deveriam morrer', 'eliminar os',
        'raça inferior', 'não merecem viver', 'exterminar',
    ],
    'threats': [
        'vou te matar', 'vou te', 'fazer mal para você',
        'prepare-se para morrer', 'vou atrás de você', 'vou te encontrar',
    ],
}

# Italian Patterns (Italiano)
ITALIAN_PATTERNS = {
    'violence': [
        'come uccidere', 'uccidere qualcuno', 'fare male',
        'ferire gravemente', 'attaccare violentemente', 'assassinare',
        'togliere la vita', 'causare morte',
    ],
    'weapons': [
        'fabbricare bomba', 'fare esplosivo', 'costruire arma',
        'esplosivo fatto in casa', 'molotov', 'ordigno esplosivo',
        'fare pistola', 'arma artigianale',
    ],
    'suicide': [
        'voglio suicidarmi', 'uccidermi', 'togliermi la vita',
        'finire la mia vita', 'come suicidarsi', 'suicidio efficace',
        'morire velocemente',
    ],
}

# Russian Patterns (Русский)
RUSSIAN_PATTERNS = {
    'violence': [
        'как убить', 'убить кого-то', 'причинить боль',
        'серьезно ранить', 'напасть насильно', 'убийство',
        'лишить жизни', 'причинить смерть',
    ],
    'weapons': [
        'сделать бомбу', 'изготовить взрывчатку', 'построить оружие',
        'самодельная бомба', 'коктейль молотова', 'взрывное устройство',
        'сделать пистолет', 'самодельное оружие',
    ],
    'suicide': [
        'хочу покончить с собой', 'убить себя', 'лишить себя жизни',
        'закончить свою жизнь', 'как совершить самоубийство', 'быстро умереть',
    ],
    'hate': [
        'ненавижу всех', 'должны умереть', 'уничтожить',
        'низшая раса', 'не заслуживают жить', 'истребить',
    ],
}

# Chinese Patterns (中文)
CHINESE_PATTERNS = {
    'violence': [
        '如何杀人', '杀死某人', '伤害', '严重伤害',
        '暴力攻击', '谋杀', '夺取生命', '致死',
    ],
    'weapons': [
        '制造炸弹', '做爆炸物', '制造武器', '自制炸弹',
        '燃烧瓶', '爆炸装置', '制造枪', '自制武器',
    ],
    'suicide': [
        '我想自杀', '杀死自己', '结束生命', '自我了断',
        '如何自杀', '有效自杀', '快速死亡',
    ],
    'drugs': [
        '制造毒品', '制作冰毒', '合成毒品', '地下实验室',
    ],
    'hate': [
        '恨所有', '应该死', '消灭', '低等种族',
        '不配活', '根除',
    ],
}

# Japanese Patterns (日本語)
JAPANESE_PATTERNS = {
    'violence': [
        '殺す方法', '人を殺す', '傷つける', '重傷を負わせる',
        '暴力的に攻撃', '殺人', '命を奪う',
    ],
    'weapons': [
        '爆弾の作り方', '爆発物を作る', '武器を作る', '自家製爆弾',
        '火炎瓶', '爆発装置', '銃を作る',
    ],
    'suicide': [
        '自殺したい', '自分を殺す', '命を終わらせる',
        '自殺する方法', '効果的な自殺', '早く死ぬ',
    ],
}

# Arabic Patterns (العربية)
ARABIC_PATTERNS = {
    'violence': [
        'كيف تقتل', 'قتل شخص', 'إيذاء', 'جرح خطير',
        'هجوم عنيف', 'قتل', 'إزهاق الروح',
    ],
    'weapons': [
        'صنع قنبلة', 'صنع متفجرات', 'بناء سلاح', 'قنبلة منزلية',
        'قنبلة حارقة', 'جهاز متفجر', 'صنع مسدس',
    ],
    'suicide': [
        'أريد الانتحار', 'قتل نفسي', 'إنهاء حياتي',
        'كيفية الانتحار', 'انتحار فعال', 'الموت بسرعة',
    ],
}

# Compile all patterns
ALL_INTERNATIONAL_PATTERNS = {
    'spanish': SPANISH_PATTERNS,
    'french': FRENCH_PATTERNS,
    'german': GERMAN_PATTERNS,
    'portuguese': PORTUGUESE_PATTERNS,
    'italian': ITALIAN_PATTERNS,
    'russian': RUSSIAN_PATTERNS,
    'chinese': CHINESE_PATTERNS,
    'japanese': JAPANESE_PATTERNS,
    'arabic': ARABIC_PATTERNS,
}

# Pattern statistics
TOTAL_PATTERNS = sum(
    len(patterns)
    for lang_patterns in ALL_INTERNATIONAL_PATTERNS.values()
    for patterns in lang_patterns.values()
)

# Language detection keywords (for identifying language)
LANGUAGE_INDICATORS = {
    'spanish': ['cómo', 'qué', 'dónde', 'cuándo', 'por qué', 'sí', 'no', 'muy'],
    'french': ['comment', 'où', 'quand', 'pourquoi', 'oui', 'non', 'très', 'avec'],
    'german': ['wie', 'was', 'wo', 'wann', 'warum', 'ja', 'nein', 'sehr', 'und'],
    'portuguese': ['como', 'onde', 'quando', 'por que', 'sim', 'não', 'muito'],
    'italian': ['come', 'dove', 'quando', 'perché', 'sì', 'no', 'molto', 'con'],
    'russian': ['как', 'что', 'где', 'когда', 'почему', 'да', 'нет', 'очень'],
    'chinese': ['怎么', '什么', '哪里', '什么时候', '为什么', '是', '不', '很'],
    'japanese': ['どう', '何', 'どこ', 'いつ', 'なぜ', 'はい', 'いいえ'],
    'arabic': ['كيف', 'ما', 'أين', 'متى', 'لماذا', 'نعم', 'لا', 'جدا'],
}


class InternationalPatternDetector:
    """Detector for international harmful content"""
    
    def __init__(self):
        self.patterns = ALL_INTERNATIONAL_PATTERNS
        self.indicators = LANGUAGE_INDICATORS
    
    def detect_language(self, text: str) -> List[str]:
        """Detect which languages are present in text"""
        text_lower = text.lower()
        detected = []
        
        for lang, indicators in self.indicators.items():
            if any(ind in text_lower for ind in indicators):
                detected.append(lang)
        
        # If no specific indicators, assume multilingual or English
        if not detected:
            detected.append('english')
        
        return detected
    
    def check_patterns(self, text: str, languages: List[str] = None) -> Dict:
        """Check text against international patterns"""
        if languages is None:
            languages = self.detect_language(text)
        
        text_lower = text.lower()
        matches = {
            'detected': False,
            'languages': [],
            'categories': [],
            'patterns': [],
            'severity': 'none',
        }
        
        for lang in languages:
            if lang == 'english':
                continue
                
            if lang not in self.patterns:
                continue
            
            lang_patterns = self.patterns[lang]
            
            for category, patterns in lang_patterns.items():
                for pattern in patterns:
                    if pattern in text_lower:
                        matches['detected'] = True
                        matches['languages'].append(lang)
                        matches['categories'].append(category)
                        matches['patterns'].append(pattern)
                        
                        # Set severity
                        if category in ['violence', 'weapons', 'suicide', 'threats']:
                            matches['severity'] = 'critical'
                        elif category in ['drugs', 'hate']:
                            matches['severity'] = 'high'
        
        # Remove duplicates
        matches['languages'] = list(set(matches['languages']))
        matches['categories'] = list(set(matches['categories']))
        
        return matches
    
    def get_stats(self) -> Dict:
        """Get statistics about pattern coverage"""
        stats = {
            'total_languages': len(self.patterns),
            'total_categories': 0,
            'total_patterns': TOTAL_PATTERNS,
            'languages': {},
        }
        
        for lang, categories in self.patterns.items():
            pattern_count = sum(len(p) for p in categories.values())
            stats['languages'][lang] = {
                'categories': len(categories),
                'patterns': pattern_count,
            }
            stats['total_categories'] += len(categories)
        
        return stats


# Demo
if __name__ == "__main__":
    print("🌍 International Pattern Library\n")
    print("=" * 80)
    
    detector = InternationalPatternDetector()
    stats = detector.get_stats()
    
    print(f"\n📊 Coverage Statistics:")
    print(f"  Total Languages: {stats['total_languages']}")
    print(f"  Total Patterns: {stats['total_patterns']}")
    print(f"\n  Per Language:")
    for lang, data in stats['languages'].items():
        print(f"    {lang.capitalize()}: {data['patterns']} patterns, {data['categories']} categories")
    
    print(f"\n\n🧪 Testing Detection:\n")
    
    test_cases = [
        ("Cómo fabricar una bomba casera", "Spanish"),
        ("Comment faire explosif", "French"),
        ("Wie man eine Bombe baut", "German"),
        ("如何制造炸弹", "Chinese"),
        ("Quero me suicidar", "Portuguese"),
    ]
    
    for text, expected_lang in test_cases:
        detected = detector.check_patterns(text)
        print(f"  Text: {text}")
        print(f"  Expected: {expected_lang}")
        print(f"  Result: {'🚫 FLAGGED' if detected['detected'] else '✅ SAFE'}")
        if detected['detected']:
            print(f"    Languages: {', '.join(detected['languages'])}")
            print(f"    Categories: {', '.join(detected['categories'])}")
            print(f"    Severity: {detected['severity']}")
        print("-" * 80)
