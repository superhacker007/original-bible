#!/usr/bin/env python3

"""
Paleo Hebrew Dictionary Importer
Creates comprehensive entries showing how Hebrew words are formed from pictographic roots
"""

import json
from models import db, PaleoDictionary
from app import app
from utils.hebrew_converter import hebrew_to_paleo

# Comprehensive Hebrew word data with pictographic analysis
PALEO_HEBREW_WORDS = [
    {
        "hebrew_word": "אב",
        "transliteration": "ab", 
        "english_meaning": "father",
        "strong_number": "H1",
        "root_letters": "אב",
        "letter_meanings": [
            {"letter": "א", "meaning": "strength, leader, bull's head"},
            {"letter": "ב", "meaning": "house, family, tent"}
        ],
        "pictographic_analysis": "The strength/leader (א) of the house/family (ב)",
        "original_concept": "The strong leader who heads the family household",
        "word_type": "root",
        "formation_explanation": "Father = The one with strength who leads the family house",
        "first_occurrence": "Genesis 2:24",
        "usage_examples": [
            {"reference": "Genesis 2:24", "text": "Therefore shall a man leave his father and his mother"},
            {"reference": "Exodus 20:12", "text": "Honor thy father and thy mother"}
        ],
        "frequency_count": 1205
    },
    {
        "hebrew_word": "בית",
        "transliteration": "bayit",
        "english_meaning": "house",
        "strong_number": "H1004",
        "root_letters": "בית",
        "letter_meanings": [
            {"letter": "ב", "meaning": "house, family, tent"},
            {"letter": "י", "meaning": "hand, work, throw"},
            {"letter": "ת", "meaning": "mark, sign, covenant"}
        ],
        "pictographic_analysis": "House (ב) of work/activity (י) with a sign/mark (ת)",
        "original_concept": "A dwelling place where purposeful activity happens and is marked",
        "word_type": "root",
        "formation_explanation": "House = A place of family activity that bears the mark of its inhabitants",
        "first_occurrence": "Genesis 7:1",
        "usage_examples": [
            {"reference": "Genesis 7:1", "text": "Come thou and all thy house into the ark"},
            {"reference": "Joshua 24:15", "text": "As for me and my house, we will serve the LORD"}
        ],
        "frequency_count": 2047
    },
    {
        "hebrew_word": "אלהים", 
        "transliteration": "elohim",
        "english_meaning": "God, gods",
        "strong_number": "H430",
        "root_letters": "אלהים",
        "letter_meanings": [
            {"letter": "א", "meaning": "strength, mighty one"},
            {"letter": "ל", "meaning": "authority, shepherd staff"},
            {"letter": "ה", "meaning": "breath, reveal, window"}, 
            {"letter": "י", "meaning": "hand, power, work"},
            {"letter": "ם", "meaning": "mighty waters, chaos (plural)"}
        ],
        "pictographic_analysis": "The mighty one (א) with authority (ל) who reveals (ה) power (י) over chaos (ם)",
        "original_concept": "The supreme being with ultimate authority who reveals divine power",
        "word_type": "compound",
        "formation_explanation": "God = The mighty authority who reveals His powerful control over all chaos",
        "first_occurrence": "Genesis 1:1",
        "usage_examples": [
            {"reference": "Genesis 1:1", "text": "In the beginning God created the heaven and the earth"},
            {"reference": "Deuteronomy 6:4", "text": "Hear, O Israel: The LORD our God is one LORD"}
        ],
        "frequency_count": 2570
    },
    {
        "hebrew_word": "יהוה",
        "transliteration": "YHWH", 
        "english_meaning": "LORD (Yahweh)",
        "strong_number": "H3068",
        "root_letters": "יהוה",
        "letter_meanings": [
            {"letter": "י", "meaning": "hand, power, work"},
            {"letter": "ה", "meaning": "breath, behold, reveal"},
            {"letter": "ו", "meaning": "nail, secure, add"},
            {"letter": "ה", "meaning": "breath, behold, reveal"}
        ],
        "pictographic_analysis": "Hand/power (י) that reveals (ה) security/covenant (ו) and reveals again (ה)",
        "original_concept": "The eternal God who reveals His power through covenant relationship",
        "word_type": "proper_name",
        "formation_explanation": "YHWH = The God who works powerfully, reveals Himself, secures covenant, and continues revealing",
        "first_occurrence": "Genesis 2:4",
        "usage_examples": [
            {"reference": "Genesis 2:4", "text": "These are the generations of the heavens when the LORD God created them"},
            {"reference": "Exodus 3:14", "text": "And God said unto Moses, I AM THAT I AM"}
        ],
        "frequency_count": 6828
    },
    {
        "hebrew_word": "ברא",
        "transliteration": "bara",
        "english_meaning": "create",
        "strong_number": "H1254", 
        "root_letters": "ברא",
        "letter_meanings": [
            {"letter": "ב", "meaning": "house, inside"},
            {"letter": "ר", "meaning": "head, first, beginning"},
            {"letter": "א", "meaning": "strength, mighty"}
        ],
        "pictographic_analysis": "To bring inside (ב) the first/head (ר) strength (א)",
        "original_concept": "To bring forth the first/chief strength from within - creating from nothing", 
        "word_type": "root",
        "formation_explanation": "Create = To bring the prime strength from within to manifest something new",
        "first_occurrence": "Genesis 1:1",
        "usage_examples": [
            {"reference": "Genesis 1:1", "text": "In the beginning God created the heaven and the earth"},
            {"reference": "Genesis 1:27", "text": "So God created man in his own image"}
        ],
        "frequency_count": 54
    },
    {
        "hebrew_word": "שלום",
        "transliteration": "shalom",
        "english_meaning": "peace, wholeness",
        "strong_number": "H7965",
        "root_letters": "שלום", 
        "letter_meanings": [
            {"letter": "ש", "meaning": "consume, destroy, teeth"},
            {"letter": "ל", "meaning": "authority, control, staff"},
            {"letter": "ו", "meaning": "add, secure, nail"},
            {"letter": "ם", "meaning": "mighty waters, chaos"}
        ],
        "pictographic_analysis": "Authority (ל) that consumes/destroys (ש) and secures (ו) against chaos (ם)",
        "original_concept": "The state where destructive forces are controlled and security is established",
        "word_type": "root",
        "formation_explanation": "Peace = Authority that destroys chaos and secures wholeness",
        "first_occurrence": "Genesis 15:15",
        "usage_examples": [
            {"reference": "Numbers 6:26", "text": "The LORD lift up his countenance upon thee, and give thee peace"},
            {"reference": "Isaiah 9:6", "text": "And his name shall be called... The Prince of Peace"}
        ],
        "frequency_count": 236
    },
    {
        "hebrew_word": "דבר",
        "transliteration": "dabar",
        "english_meaning": "word, matter, thing",
        "strong_number": "H1697",
        "root_letters": "דבר",
        "letter_meanings": [
            {"letter": "ד", "meaning": "door, path, move"},
            {"letter": "ב", "meaning": "house, inside, family"},  
            {"letter": "ר", "meaning": "head, first, chief"}
        ],
        "pictographic_analysis": "What moves (ד) from inside the house (ב) of the head/mind (ר)",
        "original_concept": "The expression that comes forth from within the mind or heart",
        "word_type": "root", 
        "formation_explanation": "Word = That which moves from inside the head/authority to communicate",
        "first_occurrence": "Genesis 11:1",
        "usage_examples": [
            {"reference": "Genesis 15:1", "text": "The word of the LORD came unto Abram"},
            {"reference": "Psalm 119:105", "text": "Thy word is a lamp unto my feet"}
        ],
        "frequency_count": 1440
    },
    {
        "hebrew_word": "אדם",
        "transliteration": "adam",
        "english_meaning": "man, mankind",  
        "strong_number": "H120",
        "root_letters": "אדם",
        "letter_meanings": [
            {"letter": "א", "meaning": "strength, leader"},
            {"letter": "ד", "meaning": "door, path, move"},
            {"letter": "ם", "meaning": "mighty waters, chaos"}
        ],
        "pictographic_analysis": "The strong one (א) who moves/walks (ד) through chaos/life (ם)",
        "original_concept": "The being with strength who walks through the chaos of earthly existence",
        "word_type": "root",
        "formation_explanation": "Man = The strong one who journeys through the chaotic waters of life",
        "first_occurrence": "Genesis 1:26",
        "usage_examples": [
            {"reference": "Genesis 1:26", "text": "Let us make man in our image"},
            {"reference": "Genesis 2:7", "text": "And the LORD God formed man of the dust"}
        ],
        "frequency_count": 562
    },
    {
        "hebrew_word": "אור",
        "transliteration": "or",
        "english_meaning": "light",
        "strong_number": "H216",
        "root_letters": "אור", 
        "letter_meanings": [
            {"letter": "א", "meaning": "strength, mighty"},
            {"letter": "ו", "meaning": "add, secure, nail"},
            {"letter": "ר", "meaning": "head, first, beginning"}
        ],
        "pictographic_analysis": "The mighty strength (א) that secures (ו) the first/beginning (ר)",
        "original_concept": "The powerful force that establishes and reveals the beginning of things",
        "word_type": "root",
        "formation_explanation": "Light = The mighty power that secures the first revelation of creation",
        "first_occurrence": "Genesis 1:3", 
        "usage_examples": [
            {"reference": "Genesis 1:3", "text": "And God said, Let there be light: and there was light"},
            {"reference": "Psalm 27:1", "text": "The LORD is my light and my salvation"}
        ],
        "frequency_count": 120
    },
    {
        "hebrew_word": "חכמה",
        "transliteration": "chokmah", 
        "english_meaning": "wisdom",
        "strong_number": "H2451",
        "root_letters": "חכמה",
        "letter_meanings": [
            {"letter": "ח", "meaning": "wall, fence, outside"},
            {"letter": "כ", "meaning": "palm, bend, allow"},
            {"letter": "ם", "meaning": "mighty waters, chaos"},
            {"letter": "ה", "meaning": "breath, reveal, behold"}
        ], 
        "pictographic_analysis": "The wall/boundary (ח) that bends/controls (כ) chaos (ם) to reveal (ה)",
        "original_concept": "The divine boundary that controls chaotic forces and reveals truth",
        "word_type": "root",
        "formation_explanation": "Wisdom = The boundary that controls chaos and reveals divine understanding",
        "first_occurrence": "Exodus 28:3",
        "usage_examples": [
            {"reference": "Proverbs 1:7", "text": "The fear of the LORD is the beginning of knowledge"},
            {"reference": "Proverbs 8:22", "text": "The LORD possessed me in the beginning of his way"}
        ],
        "frequency_count": 149
    }
]

def import_paleo_dictionary_words():
    """Import Paleo Hebrew dictionary entries"""
    print("Importing Paleo Hebrew Dictionary entries...")
    
    imported_count = 0
    error_count = 0
    
    for word_data in PALEO_HEBREW_WORDS:
        try:
            # Check if word already exists
            existing = PaleoDictionary.query.filter_by(
                hebrew_word=word_data['hebrew_word']
            ).first()
            
            if existing:
                print(f"Word {word_data['hebrew_word']} already exists, skipping...")
                continue
            
            # Convert Hebrew to Paleo Hebrew
            paleo_word = hebrew_to_paleo(word_data['hebrew_word'])
            
            # Create dictionary entry
            paleo_entry = PaleoDictionary(
                hebrew_word=word_data['hebrew_word'],
                paleo_word=paleo_word,
                transliteration=word_data['transliteration'],
                english_meaning=word_data['english_meaning'],
                strong_number=word_data.get('strong_number'),
                root_letters=word_data['root_letters'],
                letter_meanings=json.dumps(word_data['letter_meanings']),
                pictographic_analysis=word_data['pictographic_analysis'],
                original_concept=word_data['original_concept'],
                word_type=word_data['word_type'],
                root_word=word_data.get('root_word'),
                formation_explanation=word_data['formation_explanation'],
                first_occurrence=word_data.get('first_occurrence'),
                usage_examples=json.dumps(word_data.get('usage_examples', [])),
                frequency_count=word_data.get('frequency_count', 0)
            )
            
            db.session.add(paleo_entry)
            imported_count += 1
            
            print(f"Added: {word_data['hebrew_word']} → {paleo_word} ({word_data['transliteration']})")
            
        except Exception as e:
            error_count += 1
            print(f"Error importing {word_data.get('hebrew_word', 'unknown')}: {e}")
            continue
    
    try:
        db.session.commit()
        print(f"\nPaleo Dictionary import complete!")
        print(f"Successfully imported: {imported_count} words")
        print(f"Errors: {error_count}")
    except Exception as e:
        print(f"Error committing to database: {e}")
        db.session.rollback()

def main():
    """Main import function"""
    with app.app_context():
        print("=" * 60)
        print("PALEO HEBREW DICTIONARY IMPORT")
        print("Creating comprehensive pictographic word analysis")
        print("=" * 60)
        print()
        
        # Create tables
        db.create_all()
        
        # Import dictionary entries
        import_paleo_dictionary_words()
        
        # Summary
        total_entries = PaleoDictionary.query.count()
        print(f"\nFinal database summary:")
        print(f"Total Paleo Dictionary entries: {total_entries}")
        
        if total_entries > 0:
            print(f"\n✅ SUCCESS: Paleo Hebrew Dictionary created!")
            print("Each entry shows how Hebrew words are formed from pictographic roots")
        else:
            print(f"\n⚠️ No entries were imported")

if __name__ == "__main__":
    main()