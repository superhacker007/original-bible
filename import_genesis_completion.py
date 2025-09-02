#!/usr/bin/env python3
"""
Complete Genesis import - chapters 32-50
Fix the missing verses in the remaining Genesis chapters
"""

from app import app, db
from models import Book, Chapter, Verse
from utils.bible_importer import BibleImporter
import requests
import re
import time

def clean_sefaria_text(text):
    """Clean Sefaria HTML tags and formatting"""
    if not text:
        return ""
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'\*', '', text)
    return text.strip()

def import_genesis_chapters(start_chapter=32, end_chapter=50):
    """Import Genesis chapters 32-50 with verses"""
    
    with app.app_context():
        print(f"📖 Completing Genesis chapters {start_chapter}-{end_chapter}...")
        
        # Get Genesis book
        genesis = Book.query.filter_by(name='Genesis').first()
        if not genesis:
            print("❌ Genesis book not found")
            return 0
        
        importer = BibleImporter()
        total_imported = 0
        
        for chapter_num in range(start_chapter, end_chapter + 1):
            try:
                print(f"  📄 Processing Genesis Chapter {chapter_num}...")
                
                # Get chapter from database
                chapter = Chapter.query.filter_by(
                    book_id=genesis.id,
                    chapter_number=chapter_num
                ).first()
                
                # Check if chapter already has verses
                if chapter:
                    existing_verse_count = Verse.query.filter_by(chapter_id=chapter.id).count()
                    if existing_verse_count > 0:
                        print(f"    ✅ Chapter {chapter_num} already has {existing_verse_count} verses, skipping")
                        continue
                
                # Get chapter from Sefaria API
                url = f"https://www.sefaria.org/api/texts/Genesis.{chapter_num}"
                response = requests.get(url, timeout=15)
                
                if response.status_code != 200:
                    print(f"    ❌ Failed to fetch Genesis {chapter_num}: HTTP {response.status_code}")
                    continue
                
                data = response.json()
                hebrew_verses = data.get('he', [])
                english_verses = data.get('text', [])
                
                if not hebrew_verses:
                    print(f"    ⏭️ No Hebrew verses found for Genesis {chapter_num}")
                    continue
                
                print(f"    📝 Found {len(hebrew_verses)} verses")
                
                # Create chapter if it doesn't exist
                if not chapter:
                    chapter = Chapter(
                        book_id=genesis.id,
                        chapter_number=chapter_num
                    )
                    db.session.add(chapter)
                    db.session.flush()
                    print(f"    ➕ Created chapter {chapter_num}")
                
                # Add verses
                verses_added = 0
                for verse_num, hebrew_verse in enumerate(hebrew_verses, 1):
                    english_verse = english_verses[verse_num - 1] if verse_num - 1 < len(english_verses) else ""
                    
                    hebrew_clean = clean_sefaria_text(hebrew_verse)
                    english_clean = clean_sefaria_text(english_verse)
                    
                    if not hebrew_clean:
                        continue
                    
                    # Create verse data using importer
                    verse_data = importer._create_verse_data(
                        chapter_num, verse_num, hebrew_clean, english_clean
                    )
                    
                    # Create and add verse
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
                    verses_added += 1
                
                # Commit the chapter
                db.session.commit()
                total_imported += verses_added
                
                print(f"    ✅ Added {verses_added} verses to Genesis {chapter_num}")
                time.sleep(0.3)  # Be nice to API
                
            except Exception as e:
                print(f"    ❌ Error processing Genesis {chapter_num}: {e}")
                continue
        
        print(f"\n🎉 Genesis completion finished!")
        print(f"📝 Total verses imported: {total_imported}")
        
        # Final Genesis statistics
        total_genesis_verses = db.session.query(Verse).join(Chapter).filter(
            Chapter.book_id == genesis.id
        ).count()
        
        genesis_chapters = Chapter.query.filter_by(book_id=genesis.id).count()
        
        print(f"📊 Final Genesis stats:")
        print(f"   Chapters: {genesis_chapters}/50")
        print(f"   Total verses: {total_genesis_verses}")
        
        return total_imported

if __name__ == "__main__":
    verses_imported = import_genesis_chapters()
    print(f"\n✅ Genesis completion script finished: {verses_imported} verses imported")