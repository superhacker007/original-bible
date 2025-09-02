#!/usr/bin/env python3
"""
Import complete Genesis from Sefaria API to demonstrate full chapter import
"""

from app import app, db
from models import Book, Chapter, Verse
from utils.bible_importer import BibleImporter
import requests

def test_sefaria_api():
    """Test Sefaria API directly"""
    print("🔍 Testing Sefaria API access...")
    
    # Test different book formats
    test_books = [
        "Genesis",
        "Genesis.1", 
        "Bereshit",
        "Torah/Genesis"
    ]
    
    for book_name in test_books:
        try:
            url = f"https://www.sefaria.org/api/texts/{book_name}"
            print(f"Testing: {url}")
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ SUCCESS for {book_name}")
                print(f"   Keys available: {list(data.keys())}")
                
                if 'he' in data:
                    hebrew_chapters = data['he']
                    print(f"   Hebrew chapters: {len(hebrew_chapters)}")
                    if len(hebrew_chapters) > 0 and len(hebrew_chapters[0]) > 0:
                        print(f"   First verse sample: {hebrew_chapters[0][0][:50]}...")
                        
                if 'text' in data:
                    english_chapters = data['text'] 
                    print(f"   English chapters: {len(english_chapters)}")
                    if len(english_chapters) > 0 and len(english_chapters[0]) > 0:
                        print(f"   First English verse: {english_chapters[0][0][:50]}...")
                
                # If successful, use this format
                return book_name, data
                
            else:
                print(f"❌ Failed {book_name}: HTTP {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error testing {book_name}: {e}")
    
    return None, None

def import_complete_genesis():
    """Import complete Genesis with all chapters"""
    
    with app.app_context():
        print("📖 Starting complete Genesis import...")
        
        # Test Sefaria API first
        working_format, sample_data = test_sefaria_api()
        
        if not working_format:
            print("❌ Could not connect to Sefaria API")
            return False
            
        print(f"✅ Using format: {working_format}")
        
        # Get Genesis book from database
        genesis = Book.query.filter_by(name='Genesis').first()
        if not genesis:
            print("❌ Genesis book not found in database")
            return False
            
        # Initialize importer
        importer = BibleImporter()
        
        print("🚀 Importing complete Genesis...")
        
        # Let's debug the Sefaria data processing
        print("🔍 Debug: Calling Sefaria API directly...")
        import requests
        url = f"https://www.sefaria.org/api/texts/{working_format}"
        response = requests.get(url, timeout=10)
        raw_data = response.json()
        
        print(f"📊 Raw data structure:")
        print(f"   Hebrew chapters: {len(raw_data.get('he', []))}")
        print(f"   English chapters: {len(raw_data.get('text', []))}")
        
        if len(raw_data.get('he', [])) > 0:
            first_chapter = raw_data['he'][0]
            print(f"   First chapter verses: {len(first_chapter) if isinstance(first_chapter, list) else 'Not a list'}")
            if isinstance(first_chapter, list) and len(first_chapter) > 0:
                print(f"   First verse sample: {first_chapter[0][:100]}...")
        
        # Now try the importer
        verses_data = importer._process_sefaria_data(raw_data)
        
        if not verses_data:
            print("❌ No data received from Sefaria processing")
            return False
            
        print(f"📝 Received {len(verses_data)} verses")
        
        # Import verses to database
        imported_count = 0
        chapters_created = set()
        
        for verse_data in verses_data:
            try:
                chapter_num = verse_data['chapter']
                verse_num = verse_data['verse']
                
                # Find or create chapter
                chapter = Chapter.query.filter_by(
                    book_id=genesis.id,
                    chapter_number=chapter_num
                ).first()
                
                if not chapter:
                    chapter = Chapter(
                        book_id=genesis.id,
                        chapter_number=chapter_num,
                        verse_count=0  # Will be updated
                    )
                    db.session.add(chapter)
                    db.session.flush()  # Get ID
                    chapters_created.add(chapter_num)
                
                # Check if verse already exists
                existing_verse = Verse.query.filter_by(
                    chapter_id=chapter.id,
                    verse_number=verse_num
                ).first()
                
                if existing_verse:
                    print(f"⏭️  Skipping Genesis {chapter_num}:{verse_num} (already exists)")
                    continue
                
                # Create new verse
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
                imported_count += 1
                
                if imported_count % 50 == 0:
                    print(f"📝 Imported {imported_count} verses...")
                    
            except Exception as e:
                print(f"❌ Error importing verse {chapter_num}:{verse_num}: {e}")
                continue
        
        # Commit all changes
        try:
            db.session.commit()
            print(f"✅ Successfully imported {imported_count} Genesis verses")
            print(f"📚 Chapters created/updated: {sorted(chapters_created)}")
            
            # Update chapter verse counts
            for chapter_num in chapters_created:
                chapter = Chapter.query.filter_by(
                    book_id=genesis.id,
                    chapter_number=chapter_num
                ).first()
                if chapter:
                    verse_count = Verse.query.filter_by(chapter_id=chapter.id).count()
                    chapter.verse_count = verse_count
                    
            db.session.commit()
            return True
            
        except Exception as e:
            print(f"❌ Error committing to database: {e}")
            db.session.rollback()
            return False

if __name__ == "__main__":
    success = import_complete_genesis()
    if success:
        print("🎉 Complete Genesis import finished successfully!")
    else:
        print("💥 Genesis import failed!")