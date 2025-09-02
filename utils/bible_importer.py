"""
Comprehensive Bible data import system
Handles import from various sources including WLC, JSON APIs, etc.
"""

import json
import requests
import re
from typing import Dict, List, Tuple, Optional
from utils.hebrew_converter import hebrew_to_paleo, remove_nikud, get_pronunciation_guide
from utils.ancient_hebrew_tts import create_tts_text, get_word_pronunciation

class BiblicalHebrewTransliterator:
    """Enhanced transliteration for biblical Hebrew with ancient pronunciations"""
    
    # Ancient Hebrew pronunciation mapping (Pre-Exilic period c. 1000-600 BCE)
    ANCIENT_PRONUNCIATION = {
        'א': '',           # Silent aleph (glottal stop)
        'ב': 'b',          # Always hard b (no spirantization yet)
        'ג': 'g',          # Always hard g
        'ד': 'd',          # Always hard d
        'ה': 'h',          # Aspirated h
        'ו': 'w',          # Consonantal waw (not yet v)
        'ז': 'z',          # Voiced z
        'ח': 'ch',         # Pharyngeal fricative
        'ט': 't',          # Emphatic t
        'י': 'y',          # Consonantal yod
        'כ': 'k',          # Always hard k
        'ך': 'k',          # Final kaf
        'ל': 'l',          # Lateral l
        'מ': 'm',          # Bilabial m
        'ם': 'm',          # Final mem
        'נ': 'n',          # Alveolar n
        'ן': 'n',          # Final nun
        'ס': 's',          # Voiceless s
        'ע': 'a',          # Pharyngeal (slight vowel sound)
        'פ': 'p',          # Always hard p
        'ף': 'p',          # Final pey
        'צ': 'ts',         # Emphatic affricate
        'ץ': 'ts',         # Final tsade
        'ק': 'q',          # Emphatic q
        'ר': 'r',          # Trilled r
        'ש': 'sh',         # Post-alveolar fricative
        'ת': 't',          # Always hard t
    }
    
    # Common vowel patterns for ancient Hebrew reconstruction
    VOWEL_PATTERNS = {
        # Common word patterns with reconstructed ancient vowels
        'בראשית': 'ba-ra-sheet',        # In beginning
        'ברא': 'ba-ra',                  # He created
        'אלהים': 'eh-lo-heem',           # God/gods
        'את': 'eht',                     # Object marker
        'השמים': 'ha-sha-ma-yim',        # The heavens
        'ואת': 'wa-eht',                 # And (object marker)
        'הארץ': 'ha-ah-rets',            # The earth
        'והארץ': 'wa-ha-ah-rets',        # And the earth
        'היתה': 'ha-ya-tah',             # She was/became
        'תהו': 'to-hu',                  # Formless
        'ובהו': 'wa-vo-hu',              # And void
        'וחשך': 'wa-cho-shek',           # And darkness
        'על': 'ahl',                     # Upon
        'פני': 'pa-nay',                 # Face of
        'תהום': 'ta-hohm',               # Deep
        'ורוח': 'wa-ru-ach',             # And spirit/wind
        'מרחפת': 'ma-ra-che-fet',        # Hovering/brooding
        'ויאמר': 'wa-yo-mer',            # And he said
        'יהי': 'ya-hee',                 # Let there be
        'אור': 'ohr',                    # Light
        'וירא': 'wa-yar',                # And he saw
        'כי': 'kee',                     # That/for
        'טוב': 'tohv',                   # Good
        'ויבדל': 'wa-yav-dehl',          # And he separated
        'בין': 'bayn',                   # Between
        'ויקרא': 'wa-yiq-ra',            # And he called
        'לילה': 'lay-lah',               # Night
        'ויהי': 'wa-ya-hee',             # And it was
        'ערב': 'eh-rev',                 # Evening
        'בקר': 'bo-qer',                 # Morning
        'יום': 'yohm',                   # Day
        'אחד': 'eh-chad',                # One
        'רקיע': 'ra-qee-a',              # Firmament/expanse
        'בתוך': 'ba-tokh',               # In the midst
        'המים': 'ha-ma-yim',             # The waters
        'יבדיל': 'yav-deel',             # Let it separate
        'מעל': 'may-ahl',                # Above
        'מתחת': 'mi-ta-chat',            # Below
        'כן': 'kayn',                    # So/thus
    }
    
    def create_paleo_transliteration(self, hebrew_text: str) -> str:
        """
        Create Paleo Hebrew transliteration (like 'barashyt bara')
        Uses ancient pronunciation patterns
        """
        # Remove nikud first
        consonantal = remove_nikud(hebrew_text)
        
        # Check for known patterns first
        for pattern, pronunciation in self.VOWEL_PATTERNS.items():
            if pattern in consonantal:
                consonantal = consonantal.replace(pattern, pronunciation)
        
        # Word-by-word processing for remaining text
        words = consonantal.split()
        transliterated_words = []
        
        for word in words:
            if word in self.VOWEL_PATTERNS:
                transliterated_words.append(self.VOWEL_PATTERNS[word])
            else:
                # Letter-by-letter transliteration with vowel insertion
                transliterated = self._transliterate_word(word)
                transliterated_words.append(transliterated)
        
        return ' '.join(transliterated_words)
    
    def _transliterate_word(self, word: str) -> str:
        """Transliterate a single Hebrew word to ancient pronunciation"""
        if not word:
            return ''
        
        result = []
        word_length = len(word)
        
        for i, char in enumerate(word):
            # Get the consonantal sound
            sound = self.ANCIENT_PRONUNCIATION.get(char, char)
            
            if sound:  # If it's a consonant
                result.append(sound)
                
                # Add vowel if not at the end and next char is also a consonant
                if i < word_length - 1 and char in self.ANCIENT_PRONUNCIATION:
                    next_char = word[i + 1]
                    if next_char in self.ANCIENT_PRONUNCIATION:
                        # Insert appropriate vowel based on position and context
                        vowel = self._get_contextual_vowel(char, next_char, i, word_length)
                        if vowel:
                            result.append(vowel)
        
        return ''.join(result)
    
    def _get_contextual_vowel(self, current: str, next_char: str, position: int, word_length: int) -> str:
        """Determine appropriate vowel to insert between consonants"""
        # This is a simplified vowel insertion based on Hebrew phonology
        # In reality, this would require extensive linguistic analysis
        
        # Default vowels based on position and consonant type
        if position == 0:  # Beginning of word
            return 'a'
        elif position == word_length - 2:  # Before last consonant
            return 'e'
        else:  # Middle of word
            # Use 'a' for most contexts, 'e' before certain consonants
            if next_char in ['ה', 'ח', 'ע']:
                return 'a'
            elif next_char in ['י', 'ל', 'נ', 'ר']:
                return 'e'
            else:
                return 'a'

class BibleImporter:
    """Imports complete Bible data from various sources"""
    
    def __init__(self):
        self.transliterator = BiblicalHebrewTransliterator()
    
    def import_from_sefaria_api(self, book_name: str) -> List[Dict]:
        """
        Import Bible text from Sefaria API
        """
        try:
            # Sefaria API endpoint
            url = f"https://www.sefaria.org/api/texts/{book_name}"
            response = requests.get(url)
            
            if response.status_code == 200:
                data = response.json()
                return self._process_sefaria_data(data)
            else:
                print(f"Failed to fetch {book_name} from Sefaria: {response.status_code}")
                return []
        except Exception as e:
            print(f"Error importing from Sefaria API: {e}")
            return []
    
    def import_from_json_file(self, file_path: str) -> List[Dict]:
        """
        Import Bible text from local JSON file
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return self._process_json_data(data)
        except Exception as e:
            print(f"Error importing from JSON file: {e}")
            return []
    
    def _process_sefaria_data(self, data: Dict) -> List[Dict]:
        """Process data from Sefaria API format"""
        verses = []
        
        try:
            hebrew_text = data.get('he', [])
            english_text = data.get('text', [])
            
            for chapter_num, chapter_hebrew in enumerate(hebrew_text, 1):
                chapter_english = english_text[chapter_num - 1] if chapter_num - 1 < len(english_text) else []
                
                if isinstance(chapter_hebrew, list):
                    for verse_num, verse_hebrew in enumerate(chapter_hebrew, 1):
                        verse_english = chapter_english[verse_num - 1] if verse_num - 1 < len(chapter_english) else ""
                        
                        verse_data = self._create_verse_data(
                            chapter_num, verse_num, verse_hebrew, verse_english
                        )
                        verses.append(verse_data)
        
        except Exception as e:
            print(f"Error processing Sefaria data: {e}")
        
        return verses
    
    def _create_verse_data(self, chapter: int, verse: int, hebrew: str, english: str = "") -> Dict:
        """Create comprehensive verse data with all required fields"""
        
        # Clean Hebrew text
        hebrew_clean = hebrew.strip()
        
        # Remove nikud for consonantal text
        hebrew_consonantal = remove_nikud(hebrew_clean)
        
        # Convert to Paleo Hebrew
        paleo_text = hebrew_to_paleo(hebrew_clean)
        
        # Create transliterations
        paleo_transliteration = self.transliterator.create_paleo_transliteration(hebrew_clean)
        modern_transliteration = get_pronunciation_guide(hebrew_clean)
        
        # Create literal translation (simplified)
        literal_translation = self._create_literal_translation(hebrew_consonantal)
        
        return {
            'chapter': chapter,
            'verse': verse,
            'hebrew_text': hebrew_clean,
            'hebrew_consonantal': hebrew_consonantal,
            'paleo_text': paleo_text,
            'paleo_transliteration': paleo_transliteration,
            'modern_transliteration': modern_transliteration,
            'english_translation': english.strip(),
            'literal_translation': literal_translation,
            'strong_numbers': '',  # Would need additional parsing
            'morphology': '',      # Would need additional parsing
            'notes': ''
        }
    
    def _create_literal_translation(self, hebrew_text: str) -> str:
        """Create a basic literal translation (word-for-word)"""
        # This is a simplified implementation
        # A full implementation would use Hebrew lexicons and parsing
        
        common_words = {
            'בראשית': 'in-beginning',
            'ברא': 'created',
            'אלהים': 'God/gods',
            'את': '[obj]',
            'השמים': 'the-heavens',
            'ואת': 'and-[obj]',
            'הארץ': 'the-earth',
            'והארץ': 'and-the-earth',
            'היתה': 'was',
            'תהו': 'formless',
            'ובהו': 'and-void',
            'וחשך': 'and-darkness',
            'על': 'upon',
            'פני': 'face-of',
            'תהום': 'deep',
            'ורוח': 'and-spirit',
            'מרחפת': 'hovering',
            'ויאמר': 'and-said',
            'יהי': 'let-be',
            'אור': 'light',
            'וירא': 'and-saw',
            'כי': 'that',
            'טוב': 'good',
        }
        
        words = hebrew_text.split()
        literal_words = []
        
        for word in words:
            if word in common_words:
                literal_words.append(common_words[word])
            else:
                literal_words.append(f'[{word}]')  # Untranslated words in brackets
        
        return ' '.join(literal_words)
    
    def create_sample_genesis_data(self) -> List[Dict]:
        """Create sample Genesis chapter 1 data for testing"""
        genesis_1_data = [
            {
                'chapter': 1,
                'verse': 1,
                'hebrew': 'בְּרֵאשִׁית בָּרָא אֱלֹהִים אֵת הַשָּׁמַיִם וְאֵת הָאָרֶץ',
                'english': 'In the beginning God created the heavens and the earth.'
            },
            {
                'chapter': 1,
                'verse': 2,
                'hebrew': 'וְהָאָרֶץ הָיְתָה תֹהוּ וָבֹהוּ וְחֹשֶׁךְ עַל־פְּנֵי תְהוֹם וְרוּחַ אֱלֹהִים מְרַחֶפֶת עַל־פְּנֵי הַמָּיִם',
                'english': 'Now the earth was formless and empty, darkness was over the surface of the deep, and the Spirit of God was hovering over the waters.'
            },
            {
                'chapter': 1,
                'verse': 3,
                'hebrew': 'וַיֹּאמֶר אֱלֹהִים יְהִי אוֹר וַיְהִי־אוֹר',
                'english': 'And God said, "Let there be light," and there was light.'
            },
            {
                'chapter': 1,
                'verse': 4,
                'hebrew': 'וַיַּרְא אֱלֹהִים אֶת־הָאוֹר כִּי־טוֹב וַיַּבְדֵּל אֱלֹהִים בֵּין הָאוֹר וּבֵין הַחֹשֶׁךְ',
                'english': 'God saw that the light was good, and he separated the light from the darkness.'
            },
            {
                'chapter': 1,
                'verse': 5,
                'hebrew': 'וַיִּקְרָא אֱלֹהִים לָאוֹר יוֹם וְלַחֹשֶׁךְ קָרָא לָיְלָה וַיְהִי־עֶרֶב וַיְהִי־בֹקֶר יוֹם אֶחָד',
                'english': 'God called the light "day," and the darkness he called "night." And there was evening, and there was morning—the first day.'
            }
        ]
        
        verses = []
        for verse_info in genesis_1_data:
            verse_data = self._create_verse_data(
                verse_info['chapter'],
                verse_info['verse'],
                verse_info['hebrew'],
                verse_info['english']
            )
            verses.append(verse_data)
        
        return verses

# Example usage and testing
if __name__ == "__main__":
    importer = BibleImporter()
    
    # Test with sample Genesis data
    sample_verses = importer.create_sample_genesis_data()
    
    for verse in sample_verses:
        print(f"Genesis {verse['chapter']}:{verse['verse']}")
        print(f"Hebrew: {verse['hebrew_text']}")
        print(f"Paleo: {verse['paleo_text']}")
        print(f"Paleo Transliteration: {verse['paleo_transliteration']}")
        print(f"Modern Transliteration: {verse['modern_transliteration']}")
        print(f"English: {verse['english_translation']}")
        print(f"Literal: {verse['literal_translation']}")
        print("-" * 50)