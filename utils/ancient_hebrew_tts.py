"""
Ancient Hebrew Text-to-Speech pronunciation mapping
Based on reconstructed Pre-Exilic Biblical Hebrew phonology (c. 1000-600 BCE)
"""

# Ancient Hebrew consonant pronunciation mapping
ANCIENT_HEBREW_SOUNDS = {
    # Stops
    'א': '',          # Glottal stop (silent or light breathing)
    'ב': 'b',         # Voiced bilabial stop
    'ג': 'g',         # Voiced velar stop
    'ד': 'd',         # Voiced dental stop
    'ט': 'th',        # Emphatic dental stop
    'כ': 'k',         # Voiceless velar stop
    'ך': 'k',         # Final kaf
    'פ': 'p',         # Voiceless bilabial stop
    'ף': 'p',         # Final pey
    'ק': 'kh',        # Emphatic velar stop (more guttural than כ)
    'ת': 't',         # Voiceless dental stop
    
    # Fricatives
    'ו': 'w',         # Voiced labio-velar approximant (ancient pronunciation)
    'ז': 'z',         # Voiced alveolar fricative
    'ח': 'kh',        # Voiceless pharyngeal fricative
    'ס': 's',         # Voiceless alveolar fricative
    'ש': 'sh',        # Voiceless postalveolar fricative
    'צ': 'ts',        # Emphatic alveolar affricate
    'ץ': 'ts',        # Final tsadey
    
    # Liquids and Nasals
    'ל': 'l',         # Lateral approximant
    'מ': 'm',         # Bilabial nasal
    'ם': 'm',         # Final mem
    'נ': 'n',         # Alveolar nasal
    'ן': 'n',         # Final nun
    'ר': 'r',         # Alveolar trill (rolled r)
    
    # Gutturals
    'ע': 'ah',        # Pharyngeal approximant (slight 'ah' sound)
    'ה': 'h',         # Glottal fricative
    
    # Semivowels
    'י': 'y',         # Palatal approximant
    
    # Punctuation and spaces
    ' ': ' ',
    '.': '.',
    ',': ',',
    ':': ':',
    ';': ';',
    '!': '!',
    '?': '?',
}

# Paleo Hebrew to ancient pronunciation mapping
PALEO_TO_ANCIENT_SOUNDS = {
    '𐤀': '',         # Aleph - glottal stop
    '𐤁': 'b',        # Bet - house
    '𐤂': 'g',        # Gimel - camel
    '𐤃': 'd',        # Dalet - door
    '𐤄': 'h',        # Hey - window/revelation
    '𐤅': 'w',        # Vav - nail/hook
    '𐤆': 'z',        # Zayin - weapon
    '𐤇': 'kh',       # Chet - fence/wall
    '𐤈': 'th',       # Tet - snake/basket
    '𐤉': 'y',        # Yod - hand
    '𐤊': 'k',        # Kaf - palm
    '𐤋': 'l',        # Lamed - staff
    '𐤌': 'm',        # Mem - water
    '𐤍': 'n',        # Nun - fish
    '𐤎': 's',        # Samekh - thorn
    '𐤏': 'ah',       # Ayin - eye
    '𐤐': 'p',        # Pey - mouth
    '𐤑': 'ts',       # Tsadey - fish hook
    '𐤒': 'kh',       # Qof - back of head
    '𐤓': 'r',        # Resh - head
    '𐤔': 'sh',       # Shin - teeth
    '𐤕': 't',        # Tav - mark/sign
    ' ': ' ',
}

# Enhanced pronunciation rules for ancient Hebrew
PRONUNCIATION_RULES = {
    # Consonant clusters and special combinations
    'שׁ': 'sh',       # Shin with dot
    'שׂ': 's',        # Sin with dot
    'בּ': 'b',        # Bet with dagesh (hard b)
    'גּ': 'g',        # Gimel with dagesh (hard g)
    'דּ': 'd',        # Dalet with dagesh (hard d)
    'כּ': 'k',        # Kaf with dagesh (hard k)
    'פּ': 'p',        # Pey with dagesh (hard p)
    'תּ': 't',        # Tav with dagesh (hard t)
    
    # Without dagesh (spirantized in post-biblical period, but not in ancient Hebrew)
    'ב': 'b',         # Ancient Hebrew kept hard consonants
    'ג': 'g',
    'ד': 'd',
    'כ': 'k',
    'פ': 'p',
    'ת': 't',
}

# Ancient Hebrew vowel approximations for TTS
ANCIENT_VOWELS = {
    # Long vowels
    'a:': 'ah',       # Long a (qamats)
    'e:': 'ay',       # Long e (tsere)
    'i:': 'ee',       # Long i (hireq gadol)
    'o:': 'oh',       # Long o (holem)
    'u:': 'oo',       # Long u (shuruq)
    
    # Short vowels
    'a': 'ah',        # Short a (patach)
    'e': 'eh',        # Short e (segol)
    'i': 'ih',        # Short i (hireq)
    'o': 'oh',        # Short o
    'u': 'uh',        # Short u (qibbuts)
    
    # Reduced vowels (schwas)
    '@': 'uh',        # Shwa
}

def hebrew_to_ancient_pronunciation(text):
    """
    Convert Hebrew or Paleo Hebrew text to ancient pronunciation for TTS
    
    Args:
        text (str): Hebrew or Paleo Hebrew text
    
    Returns:
        str: Phonetic representation for TTS
    """
    result = ''
    
    # Determine if text is Paleo Hebrew or regular Hebrew
    is_paleo = any(char in PALEO_TO_ANCIENT_SOUNDS for char in text)
    
    if is_paleo:
        # Use Paleo Hebrew mapping
        for char in text:
            result += PALEO_TO_ANCIENT_SOUNDS.get(char, char)
    else:
        # Use regular Hebrew mapping with ancient pronunciation rules
        i = 0
        while i < len(text):
            # Check for two-character combinations first
            if i < len(text) - 1:
                two_char = text[i:i+2]
                if two_char in PRONUNCIATION_RULES:
                    result += PRONUNCIATION_RULES[two_char]
                    i += 2
                    continue
            
            # Single character
            char = text[i]
            result += ANCIENT_HEBREW_SOUNDS.get(char, char)
            i += 1
    
    # Clean up the result
    result = result.replace('  ', ' ')  # Remove double spaces
    result = result.strip()
    
    return result

def add_ancient_vowels(consonantal_text):
    """
    Add reconstructed ancient vowels to consonantal text for better TTS
    This is a simplified reconstruction based on common patterns
    
    Args:
        consonantal_text (str): Text with consonants only
    
    Returns:
        str: Text with added vowel approximations
    """
    # This is a simplified approach - in reality, vowel reconstruction
    # requires extensive linguistic knowledge and context
    
    # Common ancient Hebrew patterns
    patterns = {
        # Common word patterns with reconstructed vowels
        'שלום': 'sha-lohm',      # Peace
        'אלהים': 'eh-lo-heem',   # God
        'ברא': 'ba-rah',         # Created
        'השמים': 'ha-sha-ma-yim', # The heavens
        'הארץ': 'ha-ah-rets',    # The earth
    }
    
    # Check for known patterns first
    for pattern, pronunciation in patterns.items():
        if pattern in consonantal_text:
            consonantal_text = consonantal_text.replace(pattern, pronunciation)
    
    return consonantal_text

def create_tts_text(hebrew_text, include_vowels=True):
    """
    Create TTS-friendly text from Hebrew input
    
    Args:
        hebrew_text (str): Hebrew text to convert
        include_vowels (bool): Whether to attempt vowel reconstruction
    
    Returns:
        str: TTS-ready pronunciation text
    """
    # First convert to ancient pronunciation
    pronunciation = hebrew_to_ancient_pronunciation(hebrew_text)
    
    # Add vowels if requested
    if include_vowels:
        pronunciation = add_ancient_vowels(pronunciation)
    
    # Make adjustments for better TTS
    pronunciation = pronunciation.replace('kh', 'ch')  # Better TTS pronunciation
    pronunciation = pronunciation.replace('ts', 'ts')   # Keep ts sound
    pronunciation = pronunciation.replace('ah', 'a')    # Simplify for TTS
    
    return pronunciation

# Sample pronunciations for common words
SAMPLE_WORDS = {
    'בראשית': 'beh-ray-sheet',     # In the beginning
    'אלהים': 'eh-lo-heem',         # God
    'ברא': 'ba-rah',               # Created
    'את': 'eht',                   # (object marker)
    'השמים': 'ha-sha-ma-yim',      # The heavens
    'ואת': 'weh-eht',              # And (object marker)
    'הארץ': 'ha-ah-rets',          # The earth
    
    # Paleo Hebrew equivalents
    '𐤁𐤓𐤀𐤔𐤉𐤕': 'beh-ray-sheet',
    '𐤀𐤋𐤄𐤉𐤌': 'eh-lo-heem',
    '𐤁𐤓𐤀': 'ba-rah',
}

def get_word_pronunciation(word):
    """
    Get pronunciation for a specific word, with fallback to letter-by-letter
    
    Args:
        word (str): Hebrew word
    
    Returns:
        str: Pronunciation for TTS
    """
    # Check if we have a specific pronunciation for this word
    if word in SAMPLE_WORDS:
        return SAMPLE_WORDS[word]
    
    # Fall back to letter-by-letter conversion
    return create_tts_text(word, include_vowels=True)