#!/usr/bin/env python3

"""
Robust Hebrew Strong's Concordance Importer
Uses line-by-line parsing to handle problematic entries
"""

import re
from models import db, StrongsHebrew
from app import app

def parse_hebrew_line_by_line():
    """Parse Hebrew dictionary line by line to avoid JSON issues"""
    print("Parsing Hebrew dictionary line by line...")
    
    hebrew_data = {}
    
    with open('strong_data/hebrew/strongs-hebrew-dictionary.js', 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Find the start of the dictionary object
    start_match = re.search(r'var strongsHebrewDictionary = \{', content)
    if not start_match:
        print("Could not find strongsHebrewDictionary")
        return {}
    
    # Extract everything after the opening brace
    dict_content = content[start_match.end():]
    
    # Split by entries - each entry starts with "H\d+":
    entries = re.split(r'(?="H\d+":)', dict_content)
    
    for entry in entries[1:]:  # Skip first empty element
        try:
            # Extract the Strong's number
            num_match = re.match(r'"H(\d+)":', entry)
            if not num_match:
                continue
                
            strong_num = f"H{num_match.group(1)}"
            
            # Extract fields using regex
            lemma_match = re.search(r'"lemma":"([^"]*)"', entry)
            xlit_match = re.search(r'"xlit":"([^"]*)"', entry)
            pron_match = re.search(r'"pron":"([^"]*)"', entry)
            derivation_match = re.search(r'"derivation":"([^"]*)"', entry)
            strongs_def_match = re.search(r'"strongs_def":"([^"]*)"', entry)
            kjv_def_match = re.search(r'"kjv_def":"([^"]*)"', entry)
            
            # Build entry data
            entry_data = {
                'lemma': lemma_match.group(1) if lemma_match else '',
                'xlit': xlit_match.group(1) if xlit_match else '',
                'pron': pron_match.group(1) if pron_match else '',
                'derivation': derivation_match.group(1) if derivation_match else '',
                'strongs_def': strongs_def_match.group(1) if strongs_def_match else '',
                'kjv_def': kjv_def_match.group(1) if kjv_def_match else ''
            }
            
            hebrew_data[strong_num] = entry_data
            
        except Exception as e:
            print(f"Error parsing entry: {e}")
            continue
    
    print(f"Parsed {len(hebrew_data)} Hebrew entries")
    return hebrew_data

def import_hebrew_robust():
    """Import Hebrew entries with robust error handling"""
    hebrew_data = parse_hebrew_line_by_line()
    
    if not hebrew_data:
        print("No Hebrew data to import")
        return
    
    print(f"Importing {len(hebrew_data)} Hebrew entries...")
    
    imported_count = 0
    error_count = 0
    
    for strong_num, entry_data in hebrew_data.items():
        try:
            # Check if entry already exists
            existing = StrongsHebrew.query.filter_by(strong_number=strong_num).first()
            if existing:
                continue
            
            # Clean and truncate data
            word = (entry_data.get('lemma', '') or '')[:100]
            transliteration = (entry_data.get('xlit', '') or '')[:100] 
            pronunciation = (entry_data.get('pron', '') or transliteration)[:100]
            short_def = (entry_data.get('strongs_def', '') or '')[:200]
            long_def = (entry_data.get('kjv_def', '') or short_def)[:1000]
            derivation = entry_data.get('derivation', '') or ''
            
            # Skip empty entries
            if not word and not short_def:
                continue
                
            # Extract part of speech
            pos = extract_part_of_speech(derivation)
            
            # Create entry
            hebrew_entry = StrongsHebrew(
                strong_number=strong_num,
                hebrew_word=word,
                transliteration=transliteration,
                pronunciation=pronunciation,
                short_definition=short_def,
                long_definition=long_def,
                part_of_speech=pos
            )
            
            db.session.add(hebrew_entry)
            imported_count += 1
            
            if imported_count % 1000 == 0:
                print(f"  Imported {imported_count} Hebrew entries...")
                db.session.commit()
            
        except Exception as e:
            error_count += 1
            if error_count <= 5:
                print(f"Error importing Hebrew {strong_num}: {e}")
            continue
    
    try:
        db.session.commit()
        print(f"Hebrew import complete: {imported_count} imported, {error_count} errors")
    except Exception as e:
        print(f"Error committing Hebrew entries: {e}")
        db.session.rollback()

def extract_part_of_speech(derivation):
    """Extract part of speech from derivation text"""
    if not derivation:
        return 'unknown'
    
    derivation = derivation.lower()
    
    if any(word in derivation for word in ['verb', 'root']):
        return 'verb'
    elif any(word in derivation for word in ['noun', 'name']):
        return 'noun'  
    elif 'adjective' in derivation:
        return 'adjective'
    elif 'adverb' in derivation:
        return 'adverb'
    elif 'preposition' in derivation:
        return 'preposition'
    elif 'conjunction' in derivation:
        return 'conjunction'
    elif 'interjection' in derivation:
        return 'interjection'
    elif 'pronoun' in derivation:
        return 'pronoun'
    elif 'particle' in derivation:
        return 'particle'
    else:
        return 'unknown'

def main():
    """Main import function for Hebrew"""
    with app.app_context():
        print("=" * 50)
        print("ROBUST HEBREW STRONG'S IMPORT")
        print("=" * 50)
        
        # Show current counts
        current_hebrew = StrongsHebrew.query.count()
        print(f"Current Hebrew entries: {current_hebrew:,}")
        
        # Import Hebrew data
        import_hebrew_robust()
        
        # Final count
        final_hebrew = StrongsHebrew.query.count()
        print(f"Final Hebrew entries: {final_hebrew:,}")
        print(f"Added: {final_hebrew - current_hebrew:,} entries")

if __name__ == "__main__":
    main()