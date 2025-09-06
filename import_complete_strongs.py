#!/usr/bin/env python3

"""
Complete Strong's Concordance Data Importer
This script imports all 14,197+ Strong's Hebrew and Greek concordance entries
"""

import json
import re
from models import db, StrongsHebrew, StrongsGreek
from app import app

def parse_hebrew_js_data():
    """Parse Hebrew Strong's dictionary from JavaScript file"""
    print("Parsing Hebrew Strong's dictionary...")
    
    hebrew_data = {}
    
    try:
        with open('strong_data/hebrew/strongs-hebrew-dictionary.js', 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Find the JavaScript object definition
        match = re.search(r'var strongsHebrewDictionary = ({.*});', content, re.DOTALL)
        if not match:
            raise ValueError("Could not find strongsHebrewDictionary object")
        
        # Extract the JSON-like object string
        js_object_str = match.group(1)
        
        # Convert JavaScript object to Python dict
        # Replace single quotes with double quotes for JSON parsing
        js_object_str = re.sub(r"'", '"', js_object_str)
        
        # Handle the object parsing manually since it's not pure JSON
        entries = re.findall(r'"H(\d+)":({[^}]*})', js_object_str)
        
        for strong_num, entry_str in entries:
            try:
                # Clean up the entry string for JSON parsing
                entry_str = entry_str.replace('\\"', '"')
                entry_dict = json.loads(entry_str)
                
                hebrew_data[f"H{strong_num}"] = {
                    'word': entry_dict.get('lemma', ''),
                    'transliteration': entry_dict.get('xlit', ''),
                    'pronunciation': entry_dict.get('pron', ''),
                    'meaning': entry_dict.get('strongs_def', ''),
                    'definition': entry_dict.get('kjv_def', ''),
                    'derivation': entry_dict.get('derivation', ''),
                }
            except json.JSONDecodeError as e:
                print(f"Error parsing H{strong_num}: {e}")
                continue
    
    except FileNotFoundError:
        print("Hebrew dictionary file not found!")
        return {}
    except Exception as e:
        print(f"Error parsing Hebrew dictionary: {e}")
        return {}
    
    print(f"Parsed {len(hebrew_data)} Hebrew entries")
    return hebrew_data

def parse_greek_js_data():
    """Parse Greek Strong's dictionary from JavaScript file"""
    print("Parsing Greek Strong's dictionary...")
    
    greek_data = {}
    
    try:
        with open('strong_data/greek/strongs-greek-dictionary.js', 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Find the JavaScript object definition
        match = re.search(r'var strongsGreekDictionary = ({.*});', content, re.DOTALL)
        if not match:
            raise ValueError("Could not find strongsGreekDictionary object")
        
        # Extract the JSON-like object string
        js_object_str = match.group(1)
        
        # Convert JavaScript object to Python dict
        js_object_str = re.sub(r"'", '"', js_object_str)
        
        # Handle the object parsing manually
        entries = re.findall(r'"G(\d+)":({[^}]*})', js_object_str)
        
        for strong_num, entry_str in entries:
            try:
                entry_str = entry_str.replace('\\"', '"')
                entry_dict = json.loads(entry_str)
                
                greek_data[f"G{strong_num}"] = {
                    'word': entry_dict.get('lemma', ''),
                    'transliteration': entry_dict.get('xlit', ''),
                    'pronunciation': entry_dict.get('pron', ''),
                    'meaning': entry_dict.get('strongs_def', ''),
                    'definition': entry_dict.get('kjv_def', ''),
                    'derivation': entry_dict.get('derivation', ''),
                }
            except json.JSONDecodeError as e:
                print(f"Error parsing G{strong_num}: {e}")
                continue
    
    except FileNotFoundError:
        print("Greek dictionary file not found!")
        return {}
    except Exception as e:
        print(f"Error parsing Greek dictionary: {e}")
        return {}
    
    print(f"Parsed {len(greek_data)} Greek entries")
    return greek_data

def import_hebrew_entries(hebrew_data):
    """Import Hebrew entries into database"""
    print("Importing Hebrew entries...")
    
    imported_count = 0
    skipped_count = 0
    
    for strong_num, data in hebrew_data.items():
        # Check if entry already exists
        existing = StrongsHebrew.query.filter_by(strong_number=strong_num).first()
        if existing:
            skipped_count += 1
            continue
        
        # Create new entry
        try:
            hebrew_entry = StrongsHebrew(
                strong_number=strong_num,
                hebrew_word=data['word'][:100],  # Truncate if too long
                transliteration=data['transliteration'][:100],
                pronunciation=data['pronunciation'][:100],
                short_definition=data['meaning'][:200],
                long_definition=(data['definition'] or data['meaning'])[:1000],
                part_of_speech=extract_part_of_speech(data.get('derivation', ''))
            )
            
            db.session.add(hebrew_entry)
            imported_count += 1
            
            if imported_count % 100 == 0:
                print(f"  Imported {imported_count} Hebrew entries...")
                db.session.commit()  # Commit in batches
            
        except Exception as e:
            print(f"Error importing {strong_num}: {e}")
            continue
    
    db.session.commit()
    print(f"Hebrew import complete: {imported_count} imported, {skipped_count} skipped")

def import_greek_entries(greek_data):
    """Import Greek entries into database"""
    print("Importing Greek entries...")
    
    imported_count = 0
    skipped_count = 0
    
    for strong_num, data in greek_data.items():
        # Check if entry already exists
        existing = StrongsGreek.query.filter_by(strong_number=strong_num).first()
        if existing:
            skipped_count += 1
            continue
        
        # Create new entry
        try:
            greek_entry = StrongsGreek(
                strong_number=strong_num,
                greek_word=data['word'][:100],  # Truncate if too long
                transliteration=data['transliteration'][:100],
                pronunciation=data['pronunciation'][:100],
                short_definition=data['meaning'][:200],
                long_definition=(data['definition'] or data['meaning'])[:1000],
                part_of_speech=extract_part_of_speech(data.get('derivation', ''))
            )
            
            db.session.add(greek_entry)
            imported_count += 1
            
            if imported_count % 100 == 0:
                print(f"  Imported {imported_count} Greek entries...")
                db.session.commit()  # Commit in batches
            
        except Exception as e:
            print(f"Error importing {strong_num}: {e}")
            continue
    
    db.session.commit()
    print(f"Greek import complete: {imported_count} imported, {skipped_count} skipped")

def extract_part_of_speech(derivation):
    """Extract part of speech from derivation text"""
    derivation = derivation.lower()
    
    if 'verb' in derivation or 'root' in derivation:
        return 'verb'
    elif 'noun' in derivation or 'name' in derivation:
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
    else:
        return 'unknown'

def main():
    """Main import function"""
    with app.app_context():
        print("=== COMPLETE STRONG'S CONCORDANCE IMPORT ===")
        print("This will import all 14,197+ Strong's entries")
        print()
        
        # Create tables if they don't exist
        db.create_all()
        
        # Parse data from JavaScript files
        hebrew_data = parse_hebrew_js_data()
        greek_data = parse_greek_js_data()
        
        total_entries = len(hebrew_data) + len(greek_data)
        print(f"Total entries to import: {total_entries}")
        print()
        
        # Import Hebrew data
        if hebrew_data:
            import_hebrew_entries(hebrew_data)
        
        # Import Greek data  
        if greek_data:
            import_greek_entries(greek_data)
        
        print()
        print("=== IMPORT COMPLETED ===")
        
        # Print summary
        hebrew_count = StrongsHebrew.query.count()
        greek_count = StrongsGreek.query.count()
        total_count = hebrew_count + greek_count
        
        print(f"Final database summary:")
        print(f"Hebrew entries: {hebrew_count:,}")
        print(f"Greek entries: {greek_count:,}")
        print(f"Total Strong's entries: {total_count:,}")
        print(f"Coverage: {round((total_count / 14197) * 100, 1)}% of complete concordance")

if __name__ == "__main__":
    main()