#!/usr/bin/env python3
"""
Import complete Genesis from Sefaria API - FIXED VERSION
Handles the actual Sefaria format where each element is a complete verse (not chapters)
"""

from app import app, db
from models import Book, Chapter, Verse
from utils.bible_importer import BibleImporter
import requests
import re

def clean_sefaria_text(text):
    """Clean Sefaria HTML tags and formatting"""
    # Remove HTML tags like <big>, <sup>, <i>, etc.
    text = re.sub(r'<[^>]+>', '', text)
    # Remove footnote markers and formatting
    text = re.sub(r'\*', '', text)
    return text.strip()

def import_genesis_from_sefaria():
    """Import complete Genesis using proper Sefaria format understanding"""
    
    with app.app_context():
        print("📖 Starting FIXED Genesis import...")
        
        # Get Genesis book from database
        genesis = Book.query.filter_by(name='Genesis').first()
        if not genesis:
            print("❌ Genesis book not found in database")
            return False
        
        print("🌐 Fetching Genesis data from Sefaria...")
        
        # Get complete Genesis data
        url = "https://www.sefaria.org/api/texts/Genesis"
        response = requests.get(url, timeout=30)
        
        if response.status_code != 200:
            print(f"❌ Failed to fetch Genesis: HTTP {response.status_code}")
            return False
            
        data = response.json()
        hebrew_chapters = data.get('he', [])
        english_chapters = data.get('text', [])
        
        print(f"📊 Received {len(hebrew_chapters)} Hebrew chapters")
        print(f"📊 Received {len(english_chapters)} English chapters")
        
        # Initialize importer for text processing
        importer = BibleImporter()
        
        total_imported = 0
        chapters_created = set()
        
        # Process each chapter
        for chapter_num in range(1, min(len(hebrew_chapters), len(english_chapters)) + 1):
            print(f"\n📖 Processing Genesis Chapter {chapter_num}...")
            
            # Get chapter data by requesting specific chapter
            chapter_url = f"https://www.sefaria.org/api/texts/Genesis.{chapter_num}"
            chapter_response = requests.get(chapter_url, timeout=10)
            
            if chapter_response.status_code != 200:
                print(f"❌ Failed to fetch Genesis {chapter_num}: HTTP {chapter_response.status_code}")
                continue
                
            chapter_data = chapter_response.json()
            hebrew_verses = chapter_data.get('he', [])
            english_verses = chapter_data.get('text', [])
            
            print(f"   Found {len(hebrew_verses)} Hebrew verses")
            print(f"   Found {len(english_verses)} English verses")
            
            if not hebrew_verses:
                print(f"   ⏭️  Skipping chapter {chapter_num} (no Hebrew verses)")
                continue
            
            # Find or create chapter in database
            chapter = Chapter.query.filter_by(
                book_id=genesis.id,
                chapter_number=chapter_num
            ).first()
            
            if not chapter:
                chapter = Chapter(
                    book_id=genesis.id,
                    chapter_number=chapter_num,
                    verse_count=len(hebrew_verses)
                )
                db.session.add(chapter)
                db.session.flush()
                chapters_created.add(chapter_num)
                print(f"   ✅ Created chapter {chapter_num}")
            
            # Process each verse in the chapter
            for verse_num in range(1, len(hebrew_verses) + 1):
                try:
                    hebrew_verse = hebrew_verses[verse_num - 1]
                    english_verse = english_verses[verse_num - 1] if verse_num - 1 < len(english_verses) else ""
                    
                    # Clean the text
                    hebrew_clean = clean_sefaria_text(hebrew_verse)
                    english_clean = clean_sefaria_text(english_verse)
                    
                    # Check if verse already exists
                    existing_verse = Verse.query.filter_by(
                        chapter_id=chapter.id,
                        verse_number=verse_num
                    ).first()
                    
                    if existing_verse:
                        print(f"   ⏭️  Verse {chapter_num}:{verse_num} exists, updating...")
                        # Update existing verse
                        verse_data = importer._create_verse_data(
                            chapter_num, verse_num, hebrew_clean, english_clean
                        )
                        
                        existing_verse.hebrew_text = verse_data['hebrew_text']
                        existing_verse.hebrew_consonantal = verse_data['hebrew_consonantal']
                        existing_verse.paleo_text = verse_data['paleo_text']
                        existing_verse.paleo_transliteration = verse_data['paleo_transliteration']
                        existing_verse.modern_transliteration = verse_data['modern_transliteration']
                        existing_verse.english_translation = verse_data['english_translation']
                        existing_verse.literal_translation = verse_data['literal_translation']
                        
                    else:
                        # Create new verse
                        verse_data = importer._create_verse_data(
                            chapter_num, verse_num, hebrew_clean, english_clean
                        )
                        
                        verse = Verse(
                            chapter_id=chapter.id,
                            verse_number=verse_num,
                            hebrew_text=verse_data['hebrew_text'],
                            hebrew_consonantal=verse_data['hebrew_consonantal'], 
                            paleo_text=verse_data['paleo_text'],
                            paleo_transliteration=verse_data['paleo_transliteration'],
                            modern_transliteration=verse_data['modern_transliteration'],
                            english_translation=verse_data['english_translation'],
                            literal_translation=verse_data['literal_translation']
                        )
                        
                        db.session.add(verse)
                        print(f"   ➕ Added verse {chapter_num}:{verse_num}")
                    
                    total_imported += 1
                    
                except Exception as e:
                    print(f"   ❌ Error processing verse {chapter_num}:{verse_num}: {e}")
                    continue
            
            # Commit after each chapter
            try:
                db.session.commit()
                print(f"   ✅ Committed chapter {chapter_num} ({len(hebrew_verses)} verses)")
            except Exception as e:
                print(f"   ❌ Error committing chapter {chapter_num}: {e}")
                db.session.rollback()
                continue
        
        print(f"\n🎉 Genesis import completed!")
        print(f"   📚 Chapters processed: {sorted(chapters_created) if chapters_created else 'Updated existing'}")
        print(f"   📝 Total verses processed: {total_imported}")
        
        # Update chapter verse counts
        for chapter_num in range(1, 51):  # Genesis has 50 chapters
            chapter = Chapter.query.filter_by(
                book_id=genesis.id,
                chapter_number=chapter_num
            ).first()
            if chapter:
                verse_count = Verse.query.filter_by(chapter_id=chapter.id).count()
                if verse_count > 0:
                    chapter.verse_count = verse_count
                    print(f"   📊 Chapter {chapter_num}: {verse_count} verses")
        
        db.session.commit()
        return True

if __name__ == "__main__":
    success = import_genesis_from_sefaria()
    if success:
        print("🎉 Complete Genesis import finished successfully!")
    else:
        print("💥 Genesis import failed!")