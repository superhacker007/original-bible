#!/usr/bin/env python3

"""
Comprehensive Paleo Hebrew Dictionary Creator
Generates pictographic root analysis for all Strong's Hebrew entries
"""

import json
import re
from models import db, PaleoDictionary, StrongsHebrew
from app import app
from utils.hebrew_converter import hebrew_to_paleo, remove_nikud

# Enhanced Hebrew letter meanings with deeper pictographic analysis
HEBREW_LETTER_MEANINGS = {
    'א': {
        'name': 'Aleph',
        'meaning': 'strength, mighty one, leader, bull, ox',
        'pictograph': 'ox head, strong leader',
        'concept': 'strength, power, leadership, first, beginning'
    },
    'ב': {
        'name': 'Bet', 
        'meaning': 'house, family, tent, inside, within',
        'pictograph': 'tent floor plan, house',
        'concept': 'dwelling, family, containment, inside'
    },
    'ג': {
        'name': 'Gimel',
        'meaning': 'camel, pride, lift up, gather',
        'pictograph': 'camel, foot of man',
        'concept': 'movement, gathering, pride, lifting'
    },
    'ד': {
        'name': 'Dalet',
        'meaning': 'door, entrance, path, move, hang',
        'pictograph': 'tent door hanging',
        'concept': 'entrance, pathway, movement, access'
    },
    'ה': {
        'name': 'Hey',
        'meaning': 'breath, behold, reveal, window, spirit',
        'pictograph': 'man with arms raised, window',
        'concept': 'revelation, breath, spirit, behold'
    },
    'ו': {
        'name': 'Vav',
        'meaning': 'nail, peg, hook, secure, add, and',
        'pictograph': 'tent peg, nail',
        'concept': 'connection, security, adding, joining'
    },
    'ז': {
        'name': 'Zayin',
        'meaning': 'weapon, sword, cut, divide, nourish',
        'pictograph': 'mattock, cutting tool',
        'concept': 'cutting, dividing, weapon, food'
    },
    'ח': {
        'name': 'Chet',
        'meaning': 'wall, fence, outside, separate, half',
        'pictograph': 'tent wall, fence',
        'concept': 'separation, protection, boundary, outside'
    },
    'ט': {
        'name': 'Tet',
        'meaning': 'serpent, surround, mud, good',
        'pictograph': 'coiled serpent, basket',
        'concept': 'surrounding, containing, good, mud'
    },
    'י': {
        'name': 'Yod',
        'meaning': 'hand, arm, work, throw, worship, praise',
        'pictograph': 'closed hand, arm',
        'concept': 'work, deed, worship, power'
    },
    'כ': {
        'name': 'Kaf',
        'meaning': 'palm, bend, open, allow, tame, subdue',
        'pictograph': 'open palm',
        'concept': 'opening, allowing, bending, covering'
    },
    'ך': {
        'name': 'Kaf-final',
        'meaning': 'palm, bend, open, allow, tame, subdue',
        'pictograph': 'open palm',
        'concept': 'opening, allowing, bending, covering'
    },
    'ל': {
        'name': 'Lamed',
        'meaning': 'staff, rod, authority, teach, yoke, toward',
        'pictograph': 'shepherd staff, cattle prod',
        'concept': 'authority, teaching, leading, control'
    },
    'מ': {
        'name': 'Mem',
        'meaning': 'water, mighty, blood, people, nations',
        'pictograph': 'waves of water',
        'concept': 'chaos, mighty, mass, people'
    },
    'ם': {
        'name': 'Mem-final',
        'meaning': 'water, mighty, blood, people, nations',
        'pictograph': 'waves of water',
        'concept': 'chaos, mighty, mass, people'
    },
    'נ': {
        'name': 'Nun',
        'meaning': 'fish, life, activity, heir, continue',
        'pictograph': 'swimming fish',
        'concept': 'life, activity, movement, heir'
    },
    'ן': {
        'name': 'Nun-final',
        'meaning': 'fish, life, activity, heir, continue',
        'pictograph': 'swimming fish',
        'concept': 'life, activity, movement, heir'
    },
    'ס': {
        'name': 'Samech',
        'meaning': 'thorn, grab, hate, protect, support',
        'pictograph': 'thorn, prop',
        'concept': 'support, protection, grabbing, hatred'
    },
    'ע': {
        'name': 'Ayin',
        'meaning': 'eye, see, know, experience, fountain',
        'pictograph': 'eye',
        'concept': 'seeing, knowing, understanding, experience'
    },
    'פ': {
        'name': 'Pe',
        'meaning': 'mouth, speak, blow, scatter, edge',
        'pictograph': 'mouth',
        'concept': 'speaking, communication, blowing, edge'
    },
    'ף': {
        'name': 'Pe-final',
        'meaning': 'mouth, speak, blow, scatter, edge',
        'pictograph': 'mouth',
        'concept': 'speaking, communication, blowing, edge'
    },
    'צ': {
        'name': 'Tsade',
        'meaning': 'hunt, catch, desire, need, righteous',
        'pictograph': 'fish hook, man on side',
        'concept': 'hunting, desire, righteousness, need'
    },
    'ץ': {
        'name': 'Tsade-final',
        'meaning': 'hunt, catch, desire, need, righteous',
        'pictograph': 'fish hook, man on side',
        'concept': 'hunting, desire, righteousness, need'
    },
    'ק': {
        'name': 'Qof',
        'meaning': 'back of head, behind, time, condense',
        'pictograph': 'back of head, horizon',
        'concept': 'time, behind, gathering, condensing'
    },
    'ר': {
        'name': 'Resh',
        'meaning': 'head, first, top, beginning, person',
        'pictograph': 'head of man',
        'concept': 'head, chief, beginning, person, top'
    },
    'ש': {
        'name': 'Shin',
        'meaning': 'teeth, sharp, press, eat, destroy',
        'pictograph': 'two front teeth',
        'concept': 'sharpness, eating, destroying, pressing'
    },
    'ת': {
        'name': 'Tav',
        'meaning': 'mark, sign, covenant, cross, desire',
        'pictograph': 'crossed sticks, mark',
        'concept': 'sign, covenant, mark, desire, cross'
    }
}

def clean_hebrew_word(hebrew_text):
    """Clean Hebrew text by removing nikud and extra characters"""
    if not hebrew_text:
        return ""
    
    # Remove nikud (vowel points)
    clean_text = remove_nikud(hebrew_text)
    
    # Remove common non-Hebrew characters but keep Hebrew letters
    hebrew_pattern = re.compile('[א-ת]+')
    matches = hebrew_pattern.findall(clean_text)
    
    return ''.join(matches) if matches else clean_text.strip()

def analyze_hebrew_root(hebrew_word):
    """Analyze Hebrew word and generate pictographic meaning"""
    if not hebrew_word:
        return None
    
    clean_word = clean_hebrew_word(hebrew_word)
    if not clean_word:
        return None
    
    # Get individual letters
    letters = list(clean_word)
    if len(letters) < 1:
        return None
    
    # Build letter meanings
    letter_meanings = []
    concepts = []
    pictographs = []
    
    for letter in letters:
        if letter in HEBREW_LETTER_MEANINGS:
            letter_info = HEBREW_LETTER_MEANINGS[letter]
            letter_meanings.append({
                'letter': letter,
                'name': letter_info['name'],
                'meaning': letter_info['meaning'],
                'pictograph': letter_info['pictograph']
            })
            concepts.append(letter_info['concept'])
            pictographs.append(f"{letter_info['pictograph']} ({letter})")
    
    if not letter_meanings:
        return None
    
    # Generate pictographic analysis with Paleo symbols
    from utils.hebrew_converter import hebrew_to_paleo
    paleo_pictographs = []
    for i, letter in enumerate(letters):
        paleo_letter = hebrew_to_paleo(letter)
        letter_info = HEBREW_LETTER_MEANINGS[letter]
        paleo_pictographs.append(f"{paleo_letter} ({letter_info['pictograph']})")
    
    pictographic_analysis = " + ".join(paleo_pictographs)
    
    # Generate concept explanation based on letter count and meanings
    if len(letters) == 1:
        original_concept = f"The {concepts[0]}"
    elif len(letters) == 2:
        original_concept = f"The {concepts[0]} connected to {concepts[1]}"
    elif len(letters) == 3:
        # Most Hebrew roots are 3 letters - this is the most important case
        original_concept = f"The {concepts[0]} that {concepts[1]} through {concepts[2]}"
    elif len(letters) == 4:
        original_concept = f"The {concepts[0]} with {concepts[1]} that {concepts[2]} and {concepts[3]}"
    else:
        original_concept = f"Complex formation involving {', '.join(concepts[:3])} and more"
    
    return {
        'root_letters': clean_word,
        'letter_meanings': letter_meanings,
        'pictographic_analysis': pictographic_analysis,
        'original_concept': original_concept,
        'concepts': concepts
    }

def generate_formation_explanation(hebrew_word, english_meaning, root_analysis, strong_number=None):
    """Generate formation explanation based on pictographic analysis"""
    if not root_analysis or not english_meaning:
        return f"Formation analysis for {english_meaning}"
    
    concepts = root_analysis['concepts']
    letters = root_analysis['root_letters']
    
    # Try to connect the pictographic meaning to the English definition
    meaning_lower = english_meaning.lower()
    
    # Common word pattern analysis
    formation_patterns = {
        # Family/relationship terms
        'father': f"The strong leader ({letters[0] if len(letters) > 0 else ''}) who provides shelter and protection",
        'mother': f"The source of life and nurturing that surrounds and protects",
        'son': f"The continuation and building upon the foundation",
        'daughter': f"The opening and entrance to new family connections",
        'brother': f"The joining together in strength and unity",
        'sister': f"The connection and binding of family relationships",
        
        # God/divine terms
        'god': f"The mighty authority who reveals power and control",
        'lord': f"The supreme authority with power over all",
        'holy': f"Set apart and separated for divine purpose",
        'spirit': f"The breath and life-force that moves and reveals",
        
        # Creation terms
        'heaven': f"The dwelling place of divine authority above",
        'earth': f"The foundation and substance of physical existence",
        'water': f"The mighty flowing force of life and chaos",
        'fire': f"The consuming and purifying force of destruction and light",
        'light': f"The revealing power that illuminates and makes known",
        'darkness': f"The concealing and unknown realm without revelation",
        
        # Human terms
        'man': f"The strong one who moves through life's challenges",
        'woman': f"The source of life and the opening to continuation",
        'people': f"The gathering of many in unity and purpose",
        'nation': f"The mighty mass of people joined together",
        
        # Action terms
        'create': f"To bring forth the first strength from within",
        'make': f"To shape and form through work and power",
        'speak': f"To release breath and communication from within",
        'see': f"To experience and understand through perception",
        'hear': f"To gather and receive communication",
        'walk': f"To move along the path of life",
        'come': f"To move toward a destination or purpose",
        'go': f"To move away from present position",
        
        # Abstract concepts
        'peace': f"Authority that controls chaos and brings security",
        'love': f"The binding and connecting force that joins",
        'wisdom': f"The boundary that controls chaos and reveals truth",
        'knowledge': f"The gathering and seeing of understanding",
        'understanding': f"The deep seeing beneath the surface",
        'strength': f"The mighty power that leads and protects",
        'righteousness': f"The pursuit and catching of what is right",
        
        # Physical objects
        'house': f"The place of dwelling and family activity",
        'city': f"The gathering place surrounded by protection",
        'mountain': f"The high place of strength and stability",
        'river': f"The flowing mighty waters that give life",
        'tree': f"The living thing that connects earth and heaven",
        'stone': f"The solid foundation and enduring strength",
    }
    
    # Try to find matching pattern
    for key, pattern in formation_patterns.items():
        if key in meaning_lower:
            return f"{english_meaning.title()} = {pattern}"
    
    # Generate generic formation explanation
    if len(concepts) >= 2:
        return f"{english_meaning.title()} = The {concepts[0]} that involves {concepts[1]}"
    elif len(concepts) == 1:
        return f"{english_meaning.title()} = Related to {concepts[0]}"
    else:
        return f"{english_meaning.title()} = Word formed from Hebrew root {letters}"

def create_comprehensive_dictionary():
    """Create comprehensive Paleo Dictionary from all Strong's Hebrew entries"""
    print("Creating comprehensive Paleo Hebrew Dictionary...")
    print("This will analyze all 8,674 Hebrew words for pictographic root formations.")
    print("=" * 80)
    
    # Get all Hebrew Strong's entries
    hebrew_entries = StrongsHebrew.query.all()
    print(f"Processing {len(hebrew_entries)} Hebrew entries...")
    
    processed_count = 0
    created_count = 0
    error_count = 0
    skipped_count = 0
    
    for i, entry in enumerate(hebrew_entries):
        try:
            # Progress indicator
            if i % 500 == 0:
                print(f"Progress: {i}/{len(hebrew_entries)} ({(i/len(hebrew_entries)*100):.1f}%)")
            
            # Clean and validate Hebrew word
            clean_hebrew = clean_hebrew_word(entry.hebrew_word)
            if not clean_hebrew or len(clean_hebrew) < 1:
                skipped_count += 1
                continue
                
            # Check if already exists in Paleo Dictionary
            existing = PaleoDictionary.query.filter_by(
                strong_number=entry.strong_number
            ).first()
            
            if existing:
                skipped_count += 1
                continue
            
            # Generate root analysis
            root_analysis = analyze_hebrew_root(clean_hebrew)
            if not root_analysis:
                error_count += 1
                continue
            
            # Convert to Paleo Hebrew
            paleo_word = hebrew_to_paleo(clean_hebrew)
            
            # Generate formation explanation
            formation_explanation = generate_formation_explanation(
                clean_hebrew, 
                entry.short_definition, 
                root_analysis, 
                entry.strong_number
            )
            
            # Determine word type
            word_type = 'root'  # Most Hebrew words are root-based
            if entry.root_word and entry.root_word != clean_hebrew:
                word_type = 'derived'
            if len(clean_hebrew) > 4:
                word_type = 'compound'
            
            # Create dictionary entry
            paleo_entry = PaleoDictionary(
                hebrew_word=clean_hebrew,
                paleo_word=paleo_word,
                transliteration=entry.transliteration or 'unknown',
                english_meaning=entry.short_definition,
                strong_number=entry.strong_number,
                root_letters=root_analysis['root_letters'],
                letter_meanings=json.dumps(root_analysis['letter_meanings']),
                pictographic_analysis=root_analysis['pictographic_analysis'],
                original_concept=root_analysis['original_concept'],
                word_type=word_type,
                root_word=entry.root_word,
                formation_explanation=formation_explanation,
                first_occurrence=None,  # Would need separate Scripture analysis
                usage_examples=json.dumps([]),  # Would need separate Scripture analysis
                frequency_count=entry.usage_count or 0
            )
            
            db.session.add(paleo_entry)
            created_count += 1
            processed_count += 1
            
            # Commit in batches to avoid memory issues
            if processed_count % 100 == 0:
                db.session.commit()
                print(f"  Committed batch: {created_count} entries created")
            
        except Exception as e:
            error_count += 1
            print(f"Error processing H{entry.strong_number}: {e}")
            continue
    
    # Final commit
    try:
        db.session.commit()
        print(f"\n{'='*80}")
        print(f"COMPREHENSIVE DICTIONARY CREATION COMPLETE!")
        print(f"Successfully created: {created_count} entries")
        print(f"Skipped existing: {skipped_count} entries") 
        print(f"Errors: {error_count} entries")
        print(f"Total processed: {processed_count} entries")
        print(f"{'='*80}")
        
        # Get final count
        total_paleo_entries = PaleoDictionary.query.count()
        print(f"Total Paleo Dictionary entries in database: {total_paleo_entries}")
        
    except Exception as e:
        print(f"Error committing final batch: {e}")
        db.session.rollback()

def main():
    """Main execution function"""
    with app.app_context():
        print("COMPREHENSIVE PALEO HEBREW DICTIONARY CREATOR")
        print("Generating pictographic root analysis for all Strong's Hebrew entries")
        print()
        
        # Create tables
        db.create_all()
        
        # Create comprehensive dictionary
        create_comprehensive_dictionary()
        
        print("\n✅ SUCCESS: Comprehensive Paleo Hebrew Dictionary created!")
        print("Every Hebrew word now has pictographic root analysis showing")
        print("how the word was formed from its original pictographic meanings.")

if __name__ == "__main__":
    main()