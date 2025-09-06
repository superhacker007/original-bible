"""
Hebrew to Paleo Hebrew converter utility
"""

# Mapping from modern Hebrew letters to Paleo Hebrew symbols
# Only the 22 Hebrew letters (plus final forms) - no punctuation in ancient scripts
HEBREW_TO_PALEO = {
    'א': '𐤀',  # Aleph
    'ב': '𐤁',  # Bet
    'ג': '𐤂',  # Gimel
    'ד': '𐤃',  # Dalet
    'ה': '𐤄',  # Hey
    'ו': '𐤅',  # Vav
    'ז': '𐤆',  # Zayin
    'ח': '𐤇',  # Chet
    'ט': '𐤈',  # Tet
    'י': '𐤉',  # Yod
    'כ': '𐤊',  # Kaf
    'ך': '𐤊',  # Final Kaf
    'ל': '𐤋',  # Lamed
    'מ': '𐤌',  # Mem
    'ם': '𐤌',  # Final Mem
    'נ': '𐤍',  # Nun
    'ן': '𐤍',  # Final Nun
    'ס': '𐤎',  # Samekh
    'ע': '𐤏',  # Ayin
    'פ': '𐤐',  # Pey
    'ף': '𐤐',  # Final Pey
    'צ': '𐤑',  # Tsadey
    'ץ': '𐤑',  # Final Tsadey
    'ק': '𐤒',  # Qof
    'ר': '𐤓',  # Resh
    'ש': '𐤔',  # Shin
    'ת': '𐤕',  # Tav
    ' ': ' ',   # Space (preserve word separation)
}

# Reverse mapping for Paleo to Hebrew
PALEO_TO_HEBREW = {v: k for k, v in HEBREW_TO_PALEO.items() if k not in ['ך', 'ם', 'ן', 'ף', 'ץ']}

def hebrew_to_paleo(hebrew_text):
    """
    Convert Hebrew text to Paleo Hebrew script using only the 22 Hebrew letters
    
    Args:
        hebrew_text (str): Hebrew text with or without nikud
    
    Returns:
        str: Text converted to Paleo Hebrew script (only the 22 letters + spaces)
    """
    # Remove nikud (vowel points) - they didn't exist in ancient times
    hebrew_no_nikud = remove_nikud(hebrew_text)
    
    # Convert each character, only keeping Hebrew letters and spaces
    paleo_text = ''
    for char in hebrew_no_nikud:
        if char in HEBREW_TO_PALEO:
            paleo_text += HEBREW_TO_PALEO[char]
        elif char.isspace():
            paleo_text += ' '
        # Skip all other characters (punctuation, numbers, etc.)
    
    return paleo_text

def paleo_to_hebrew(paleo_text):
    """
    Convert Paleo Hebrew script back to modern Hebrew
    
    Args:
        paleo_text (str): Paleo Hebrew text
    
    Returns:
        str: Text converted to modern Hebrew script
    """
    hebrew_text = ''
    for char in paleo_text:
        hebrew_text += PALEO_TO_HEBREW.get(char, char)
    
    return hebrew_text

def remove_nikud(hebrew_text):
    """
    Remove nikud (vowel points) and Hebrew punctuation marks from Hebrew text
    Removes all non-consonantal marks that didn't exist in ancient Paleo Hebrew
    
    Args:
        hebrew_text (str): Hebrew text with nikud and punctuation
    
    Returns:
        str: Hebrew text with only consonantal letters
    """
    # Unicode ranges for Hebrew nikud/vowel points and punctuation to remove
    nikud_ranges = [
        (0x0591, 0x05BD),  # Hebrew accents
        (0x05BF, 0x05BF),  # Hebrew point rafe
        (0x05C1, 0x05C2),  # Hebrew points shin/sin
        (0x05C4, 0x05C5),  # Hebrew punctuation
        (0x05C7, 0x05C7),  # Hebrew point qamats qatan
    ]
    
    # Specific Hebrew punctuation marks that didn't exist in ancient times
    ancient_punctuation = [
        0x05BE,  # Hebrew punctuation maqaf (־)
        0x05C3,  # Hebrew punctuation sof pasuq (׃)
        0x05C0,  # Hebrew punctuation paseq
        0x05C6,  # Hebrew punctuation nun hafukha
    ]
    
    result = ''
    for char in hebrew_text:
        char_code = ord(char)
        
        # Skip ancient punctuation marks that didn't exist in Paleo Hebrew
        if char_code in ancient_punctuation:
            continue
            
        # Skip nikud (vowel points and cantillation marks)
        is_nikud = any(start <= char_code <= end for start, end in nikud_ranges)
        if not is_nikud:
            result += char
    
    return result

def get_pronunciation_guide(hebrew_word):
    """
    Generate a basic pronunciation guide for a Hebrew word
    
    Args:
        hebrew_word (str): Hebrew word
    
    Returns:
        str: Basic pronunciation guide
    """
    # This is a simplified transliteration
    # In a full implementation, you'd want a more sophisticated system
    transliteration_map = {
        'א': '',      # Silent or glottal stop
        'ב': 'b',
        'ג': 'g',
        'ד': 'd',
        'ה': 'h',
        'ו': 'v',
        'ז': 'z',
        'ח': 'ch',
        'ט': 't',
        'י': 'y',
        'כ': 'k',
        'ל': 'l',
        'מ': 'm',
        'נ': 'n',
        'ס': 's',
        'ע': '',      # Guttural, often silent
        'פ': 'p',
        'צ': 'ts',
        'ק': 'q',
        'ר': 'r',
        'ש': 'sh',
        'ת': 't',
        ' ': ' '
    }
    
    clean_word = remove_nikud(hebrew_word)
    pronunciation = ''
    
    for char in clean_word:
        pronunciation += transliteration_map.get(char, char)
    
    return pronunciation.strip()

def analyze_word_meaning(paleo_word):
    """
    Analyze a Paleo Hebrew word based on its individual letter meanings
    
    Args:
        paleo_word (str): Word in Paleo Hebrew script
    
    Returns:
        dict: Analysis of the word including letter meanings
    """
    from flask import current_app
    
    with current_app.app_context():
        from models import PaleoLetter
        
        analysis = {
            'word': paleo_word,
            'letters': [],
            'possible_meaning': ''
        }
        
        for char in paleo_word:
            if char != ' ':  # Skip spaces
                letter = PaleoLetter.query.filter_by(paleo_symbol=char).first()
                if letter:
                    analysis['letters'].append({
                        'symbol': char,
                        'name': letter.name,
                        'meaning': letter.meaning,
                        'pictograph': letter.pictograph_description
                    })
        
        return analysis