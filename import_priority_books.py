#!/usr/bin/env python3
"""
Priority import for major books that need completion
Focus on Torah books and major prophets first
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

def import_book_chapters(book_name, sefaria_name, start_chapter=1, end_chapter=None):
    """Import specific chapters for a book"""
    
    with app.app_context():
        book = Book.query.filter_by(name=book_name).first()
        if not book:
            print(f"❌ Book {book_name} not found")
            return 0
        
        print(f"\n📖 Importing {book_name} chapters {start_chapter}-{end_chapter or 'end'}...")
        
        importer = BibleImporter()
        total_imported = 0
        
        # Determine end chapter if not specified
        if not end_chapter:
            chapter_counts = {
                'Exodus': 40, 'Leviticus': 27, 'Numbers': 36, 'Deuteronomy': 34,
                'Joshua': 24, 'Judges': 21, 'Samuel I': 31, 'Samuel II': 24,
                'Kings I': 22, 'Kings II': 25, 'Isaiah': 66, 'Jeremiah': 52,
                'Psalms': 150, 'Proverbs': 31
            }
            end_chapter = chapter_counts.get(book_name, 50)
        
        for chapter_num in range(start_chapter, end_chapter + 1):
            try:
                # Check if chapter already has verses
                chapter = Chapter.query.filter_by(
                    book_id=book.id,
                    chapter_number=chapter_num
                ).first()
                
                if chapter and Verse.query.filter_by(chapter_id=chapter.id).count() > 0:
                    print(f"  ✅ Chapter {chapter_num} already complete")
                    continue
                
                # Get chapter from Sefaria
                url = f"https://www.sefaria.org/api/texts/{sefaria_name}.{chapter_num}"
                response = requests.get(url, timeout=10)
                
                if response.status_code != 200:
                    print(f"  ❌ Failed to fetch {book_name} {chapter_num}: HTTP {response.status_code}")
                    continue
                
                data = response.json()
                hebrew_verses = data.get('he', [])
                english_verses = data.get('text', [])
                
                if not hebrew_verses:
                    print(f"  ⏭️ No verses for {book_name} {chapter_num}")
                    continue
                
                # Create chapter if needed
                if not chapter:
                    chapter = Chapter(
                        book_id=book.id,
                        chapter_number=chapter_num,
                        verse_count=len(hebrew_verses)
                    )
                    db.session.add(chapter)
                    db.session.flush()
                
                # Add verses
                verses_added = 0
                for verse_num, hebrew_verse in enumerate(hebrew_verses, 1):
                    english_verse = english_verses[verse_num - 1] if verse_num - 1 < len(english_verses) else ""
                    
                    hebrew_clean = clean_sefaria_text(hebrew_verse)
                    english_clean = clean_sefaria_text(english_verse)
                    
                    if not hebrew_clean:
                        continue
                    
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
                    verses_added += 1
                
                chapter.verse_count = verses_added
                db.session.commit()
                
                total_imported += verses_added
                print(f"  📝 Added {verses_added} verses to {book_name} {chapter_num}")
                
                time.sleep(0.3)  # Be nice to the API
                
            except Exception as e:
                print(f"  ❌ Error with {book_name} {chapter_num}: {e}")
                continue
        
        print(f"✅ {book_name} complete: {total_imported} verses imported")
        return total_imported

# Priority books to complete
priority_imports = [
    ('Exodus', 'Exodus', 1, 40),
    ('Leviticus', 'Leviticus', 1, 27), 
    ('Numbers', 'Numbers', 2, 36),  # Skip chapter 1 since it exists
    ('Deuteronomy', 'Deuteronomy', 2, 34),  # Skip chapter 1
    ('Joshua', 'Joshua', 2, 24),  # Skip chapter 1
    ('Psalms', 'Psalms', 2, 50),  # Start with first 50 psalms
]

if __name__ == "__main__":
    print("🚀 Starting priority Bible import...")
    
    total_verses = 0
    for book_name, sefaria_name, start, end in priority_imports:
        verses_imported = import_book_chapters(book_name, sefaria_name, start, end)
        total_verses += verses_imported
        print(f"Running total: {total_verses} verses imported")
    
    print(f"\n🎉 Priority import complete! Total: {total_verses} verses imported")
    
    # Show final stats
    with app.app_context():
        final_count = Verse.query.count()
        print(f"📊 Total verses in database: {final_count}")