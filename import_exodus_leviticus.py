#!/usr/bin/env python3
"""
Simple import for Exodus and Leviticus - the two completely missing books
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

def import_book_complete(book_name, sefaria_name, total_chapters):
    """Import all chapters for a book"""
    
    with app.app_context():
        book = Book.query.filter_by(name=book_name).first()
        if not book:
            print(f"❌ Book {book_name} not found")
            return 0
        
        print(f"\n📖 Importing complete {book_name} ({total_chapters} chapters)...")
        
        importer = BibleImporter()
        total_imported = 0
        
        for chapter_num in range(1, total_chapters + 1):
            try:
                print(f"  📄 Chapter {chapter_num}...")
                
                # Check if chapter already exists and has verses
                chapter = Chapter.query.filter_by(
                    book_id=book.id,
                    chapter_number=chapter_num
                ).first()
                
                if chapter and len(chapter.verses) > 0:
                    print(f"    ✅ Already has {len(chapter.verses)} verses")
                    continue
                
                # Get chapter from Sefaria
                url = f"https://www.sefaria.org/api/texts/{sefaria_name}.{chapter_num}"
                response = requests.get(url, timeout=15)
                
                if response.status_code != 200:
                    print(f"    ❌ HTTP {response.status_code}")
                    continue
                
                data = response.json()
                hebrew_verses = data.get('he', [])
                english_verses = data.get('text', [])
                
                if not hebrew_verses:
                    print(f"    ⏭️ No Hebrew verses found")
                    continue
                
                # Create chapter if it doesn't exist
                if not chapter:
                    chapter = Chapter(
                        book_id=book.id,
                        chapter_number=chapter_num
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
                
                print(f"    ✅ Added {verses_added} verses")
                time.sleep(0.5)  # Be nice to API
                
            except Exception as e:
                print(f"    ❌ Error: {e}")
                continue
        
        print(f"📊 {book_name} complete: {total_imported} verses imported")
        return total_imported

if __name__ == "__main__":
    print("🚀 Importing Exodus and Leviticus...")
    
    # Import the two missing Torah books
    exodus_verses = import_book_complete('Exodus', 'Exodus', 40)
    leviticus_verses = import_book_complete('Leviticus', 'Leviticus', 27)
    
    total = exodus_verses + leviticus_verses
    print(f"\n🎉 Import complete!")
    print(f"📝 Exodus: {exodus_verses} verses")
    print(f"📝 Leviticus: {leviticus_verses} verses")
    print(f"📊 Total imported: {total} verses")
    
    # Show final database stats
    with app.app_context():
        final_count = Verse.query.count()
        books_with_verses = db.session.query(Book).join(Chapter).join(Verse).distinct(Book.id).count()
        print(f"📈 Total verses in database: {final_count}")
        print(f"📚 Books with verses: {books_with_verses}/39")