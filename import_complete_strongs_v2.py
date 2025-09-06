#!/usr/bin/env python3

"""
Complete Strong's Concordance Data Importer v2
This script imports all 14,197+ Strong's Hebrew and Greek concordance entries
Using a more robust parsing approach
"""

import json
import re
from models import db, StrongsHebrew, StrongsGreek
from app import app

def parse_js_to_json(file_path, var_name):
    """Convert JavaScript object to Python dictionary"""
    print(f"Parsing {file_path}...")
    
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Find the variable assignment
    pattern = rf'var {var_name} = ({{.*?}});'
    match = re.search(pattern, content, re.DOTALL)
    
    if not match:
        raise ValueError(f"Could not find {var_name} in file")
    
    js_obj = match.group(1)
    
    # Clean up the JavaScript object to make it JSON-parseable
    # Replace unescaped quotes and handle JavaScript-specific syntax
    js_obj = re.sub(r'(?<!\\)"([^"]*)"(?=:)', r'"\1"', js_obj)  # Ensure keys are quoted
    js_obj = re.sub(r':\s*"([^"]*)"([,}])', r': "\1"\2', js_obj)  # Ensure values are properly quoted
    
    try:
        # Parse as JSON
        data = json.loads(js_obj)
        print(f"Successfully parsed {len(data)} entries from {file_path}")
        return data
    except json.JSONDecodeError as e:
        print(f"JSON decode error: {e}")
        # Fall back to manual parsing
        return parse_manually(js_obj)

def parse_manually(js_obj):
    """Manually parse JavaScript object if JSON parsing fails"""
    print("Falling back to manual parsing...")
    
    data = {}
    
    # Extract entries using regex
    pattern = r'"([HG]\d+)"\s*:\s*{([^}]*)}'
    matches = re.findall(pattern, js_obj)
    
    for strong_num, entry_content in matches:
        entry_data = {}
        
        # Extract fields from entry content
        field_pattern = r'"([^"]+)"\s*:\s*"([^"]*)"'
        fields = re.findall(field_pattern, entry_content)
        
        for field_name, field_value in fields:
            entry_data[field_name] = field_value
        
        data[strong_num] = entry_data
    
    print(f"Manually parsed {len(data)} entries")
    return data

def parse_hebrew_data():
    """Parse Hebrew Strong's dictionary"""
    file_path = 'strong_data/hebrew/strongs-hebrew-dictionary.js'
    try:
        return parse_js_to_json(file_path, 'strongsHebrewDictionary')
    except Exception as e:
        print(f"Error parsing Hebrew data: {e}")
        return {}

def parse_greek_data():
    """Parse Greek Strong's dictionary"""
    file_path = 'strong_data/greek/strongs-greek-dictionary.js'
    try:
        return parse_js_to_json(file_path, 'strongsGreekDictionary')
    except Exception as e:
        print(f"Error parsing Greek data: {e}")
        return {}

def import_hebrew_entries(hebrew_data):
    """Import Hebrew entries into database"""
    print(f"Importing {len(hebrew_data)} Hebrew entries...")
    
    imported_count = 0
    error_count = 0
    
    for strong_num, entry_data in hebrew_data.items():
        try:
            # Check if entry already exists
            existing = StrongsHebrew.query.filter_by(strong_number=strong_num).first()
            if existing:
                continue
            
            # Extract data with fallbacks
            word = entry_data.get('lemma', '')[:100]
            transliteration = entry_data.get('xlit', entry_data.get('translit', ''))[:100]
            pronunciation = entry_data.get('pron', transliteration)[:100]
            short_def = entry_data.get('strongs_def', '')[:200]
            long_def = entry_data.get('kjv_def', short_def)[:1000]
            derivation = entry_data.get('derivation', '')
            
            # Create entry
            hebrew_entry = StrongsHebrew(
                strong_number=strong_num,
                hebrew_word=word,
                transliteration=transliteration,
                pronunciation=pronunciation,
                short_definition=short_def,
                long_definition=long_def,
                part_of_speech=extract_part_of_speech(derivation)
            )
            
            db.session.add(hebrew_entry)
            imported_count += 1
            
            if imported_count % 500 == 0:
                print(f"  Imported {imported_count} Hebrew entries...")
                db.session.commit()
            
        except Exception as e:
            error_count += 1
            if error_count < 10:  # Only print first 10 errors
                print(f"Error importing Hebrew {strong_num}: {e}")
            continue
    
    try:
        db.session.commit()
        print(f"Hebrew import complete: {imported_count} imported, {error_count} errors")
    except Exception as e:
        print(f"Error committing Hebrew entries: {e}")
        db.session.rollback()

def import_greek_entries(greek_data):
    """Import Greek entries into database"""
    print(f"Importing {len(greek_data)} Greek entries...")
    
    imported_count = 0
    error_count = 0
    
    for strong_num, entry_data in greek_data.items():
        try:
            # Check if entry already exists
            existing = StrongsGreek.query.filter_by(strong_number=strong_num).first()
            if existing:
                continue
            
            # Extract data with fallbacks
            word = entry_data.get('lemma', '')[:100]
            transliteration = entry_data.get('xlit', entry_data.get('translit', ''))[:100]
            pronunciation = entry_data.get('pron', transliteration)[:100]
            short_def = entry_data.get('strongs_def', '')[:200]
            long_def = entry_data.get('kjv_def', short_def)[:1000]
            derivation = entry_data.get('derivation', '')
            
            # Create entry
            greek_entry = StrongsGreek(
                strong_number=strong_num,
                greek_word=word,
                transliteration=transliteration,
                pronunciation=pronunciation,
                short_definition=short_def,
                long_definition=long_def,
                part_of_speech=extract_part_of_speech(derivation)
            )
            
            db.session.add(greek_entry)
            imported_count += 1
            
            if imported_count % 500 == 0:
                print(f"  Imported {imported_count} Greek entries...")
                db.session.commit()
            
        except Exception as e:
            error_count += 1
            if error_count < 10:  # Only print first 10 errors
                print(f"Error importing Greek {strong_num}: {e}")
            continue
    
    try:
        db.session.commit()
        print(f"Greek import complete: {imported_count} imported, {error_count} errors")
    except Exception as e:
        print(f"Error committing Greek entries: {e}")
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
    """Main import function"""
    with app.app_context():
        print("=" * 60)
        print("COMPLETE STRONG'S CONCORDANCE IMPORT")
        print("Importing all Hebrew and Greek Strong's entries")
        print("=" * 60)
        print()
        
        # Create tables if they don't exist
        db.create_all()
        
        # Show current counts
        current_hebrew = StrongsHebrew.query.count()
        current_greek = StrongsGreek.query.count()
        print(f"Current database state:")
        print(f"  Hebrew entries: {current_hebrew:,}")
        print(f"  Greek entries: {current_greek:,}")
        print(f"  Total entries: {current_hebrew + current_greek:,}")
        print()
        
        # Parse data files
        hebrew_data = parse_hebrew_data()
        greek_data = parse_greek_data()
        
        total_to_import = len(hebrew_data) + len(greek_data)
        print(f"Entries available for import: {total_to_import:,}")
        print()
        
        # Import data
        if hebrew_data:
            import_hebrew_entries(hebrew_data)
        
        if greek_data:
            import_greek_entries(greek_data)
        
        # Final summary
        final_hebrew = StrongsHebrew.query.count()
        final_greek = StrongsGreek.query.count()
        final_total = final_hebrew + final_greek
        
        print()
        print("=" * 60)
        print("IMPORT COMPLETED")
        print("=" * 60)
        print(f"Final database state:")
        print(f"  Hebrew entries: {final_hebrew:,}")
        print(f"  Greek entries: {final_greek:,}")
        print(f"  Total entries: {final_total:,}")
        print()
        print(f"Expected complete Strong's: ~14,197 entries")
        print(f"Coverage: {round((final_total / 14197) * 100, 1)}%")
        
        if final_total > 13000:
            print("✅ EXCELLENT: Near-complete Strong's concordance loaded!")
        elif final_total > 10000:
            print("✅ GOOD: Substantial Strong's concordance loaded!")
        else:
            print("⚠️  PARTIAL: Only partial Strong's concordance loaded")

if __name__ == "__main__":
    main()