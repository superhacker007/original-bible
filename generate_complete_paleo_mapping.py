#!/usr/bin/env python3
"""
Generate complete Paleo Hebrew to English mapping
Maps all Hebrew words from Strong's database to Paleo script with English definitions
"""

import sys
sys.path.append('.')

from app import app
from models import db, StrongsHebrew
from utils.hebrew_converter import hebrew_to_paleo, remove_nikud

def generate_complete_mapping():
    """Generate complete mapping from all Strong's Hebrew entries"""
    
    print("Generating complete Paleo Hebrew to English mapping...")
    
    with app.app_context():
        # Get all Hebrew entries
        all_entries = StrongsHebrew.query.all()
        print(f"Found {len(all_entries)} Hebrew words in database")
        
        mapping = {}
        processed_paleo_words = set()
        
        for entry in all_entries:
            try:
                # Clean Hebrew word (remove nikud)
                clean_hebrew = remove_nikud(entry.hebrew_word)
                if not clean_hebrew:
                    continue
                
                # Convert to Paleo Hebrew
                paleo_word = hebrew_to_paleo(clean_hebrew)
                if not paleo_word:
                    continue
                
                # Use the short definition as the English meaning
                english_meaning = entry.short_definition.strip()
                if not english_meaning:
                    continue
                
                # Store mapping (avoid duplicates by checking if paleo word already exists)
                if paleo_word not in processed_paleo_words:
                    mapping[paleo_word] = english_meaning
                    processed_paleo_words.add(paleo_word)
                
                # Also add common prefixed versions
                prefixes = ['ה', 'ו', 'ב', 'ל', 'מ', 'כ']  # the, and, in, to, from, like
                for prefix in prefixes:
                    prefixed_hebrew = prefix + clean_hebrew
                    prefixed_paleo = hebrew_to_paleo(prefixed_hebrew)
                    if prefixed_paleo and prefixed_paleo not in processed_paleo_words:
                        mapping[prefixed_paleo] = english_meaning
                        processed_paleo_words.add(prefixed_paleo)
                        
            except Exception as e:
                print(f"Error processing {entry.hebrew_word}: {e}")
                continue
        
        print(f"Generated {len(mapping)} Paleo word mappings")
        
        # Write to JavaScript file
        with open('static/js/complete_paleo_english.js', 'w', encoding='utf-8') as f:
            f.write('// COMPLETE Paleo Hebrew to English mapping\n')
            f.write('// Generated from Strong\'s Hebrew concordance database\n')
            f.write('// Using proper Paleo Hebrew script (Unicode block U+10900–U+1091F)\n')
            f.write('const COMPLETE_PALEO_ENGLISH = {\n')
            
            # Sort by paleo word for consistent output
            for paleo_word in sorted(mapping.keys()):
                english_word = mapping[paleo_word].replace('"', '\\"')  # Escape quotes
                f.write(f'  "{paleo_word}": "{english_word}",\n')
            
            f.write('};\n\n')
            f.write('// Export for use\n')
            f.write('window.COMPLETE_PALEO_ENGLISH = COMPLETE_PALEO_ENGLISH;\n')
        
        print(f"Complete mapping saved to static/js/complete_paleo_english.js")
        print(f"Total entries: {len(mapping)}")
        
        return len(mapping)

if __name__ == "__main__":
    total_mappings = generate_complete_mapping()
    print(f"\nGeneration complete: {total_mappings} Paleo word mappings created")