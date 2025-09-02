#!/usr/bin/env python3
"""
Import complete Hebrew Bible - ALL chapters for ALL books
This will systematically go through every book and import all missing chapters
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
    # Remove HTML tags like <big>, <sup>, <i>, etc.
    text = re.sub(r'<[^>]+>', '', text)
    # Remove footnote markers and formatting
    text = re.sub(r'\*', '', text)
    return text.strip()

def get_book_chapter_count(book_name):
    """Get the expected number of chapters for each book"""
    chapter_counts = {
        'Genesis': 50, 'Exodus': 40, 'Leviticus': 27, 'Numbers': 36, 'Deuteronomy': 34,
        'Joshua': 24, 'Judges': 21, 'Ruth': 4, 'Samuel I': 31, 'Samuel II': 24,
        'Kings I': 22, 'Kings II': 25, 'Chronicles I': 29, 'Chronicles II': 36,
        'Ezra': 10, 'Nehemiah': 13, 'Esther': 10, 'Job': 42, 'Psalms': 150,
        'Proverbs': 31, 'Ecclesiastes': 12, 'Song of Songs': 8, 'Isaiah': 66,
        'Jeremiah': 52, 'Lamentations': 5, 'Ezekiel': 48, 'Daniel': 12,
        'Hosea': 14, 'Joel': 3, 'Amos': 9, 'Obadiah': 1, 'Jonah': 4,
        'Micah': 7, 'Nahum': 3, 'Habakkuk': 3, 'Zephaniah': 3, 'Haggai': 2,
        'Zechariah': 14, 'Malachi': 4
    }
    return chapter_counts.get(book_name, 1)

def get_sefaria_book_name(book_name):
    """Map our book names to Sefaria API names"""
    sefaria_names = {
        'Genesis': 'Genesis',
        'Exodus': 'Exodus',
        'Leviticus': 'Leviticus',
        'Numbers': 'Numbers',
        'Deuteronomy': 'Deuteronomy',
        'Joshua': 'Joshua',
        'Judges': 'Judges',
        'Ruth': 'Ruth',
        'Samuel I': 'I Samuel',
        'Samuel II': 'II Samuel',
        'Kings I': 'I Kings',
        'Kings II': 'II Kings',
        'Chronicles I': 'I Chronicles',
        'Chronicles II': 'II Chronicles',
        'Ezra': 'Ezra',
        'Nehemiah': 'Nehemiah',
        'Esther': 'Esther',
        'Job': 'Job',
        'Psalms': 'Psalms',
        'Proverbs': 'Proverbs',
        'Ecclesiastes': 'Ecclesiastes',
        'Song of Songs': 'Song of Songs',
        'Isaiah': 'Isaiah',
        'Jeremiah': 'Jeremiah',
        'Lamentations': 'Lamentations',
        'Ezekiel': 'Ezekiel',
        'Daniel': 'Daniel',
        'Hosea': 'Hosea',
        'Joel': 'Joel',
        'Amos': 'Amos',
        'Obadiah': 'Obadiah',
        'Jonah': 'Jonah',
        'Micah': 'Micah',
        'Nahum': 'Nahum',
        'Habakkuk': 'Habakkuk',
        'Zephaniah': 'Zephaniah',
        'Haggai': 'Haggai',
        'Zechariah': 'Zechariah',
        'Malachi': 'Malachi'
    }
    return sefaria_names.get(book_name, book_name)

def import_complete_book(book, max_chapters=None):
    """Import all chapters for a specific book"""
    
    book_name = book.name
    sefaria_name = get_sefaria_book_name(book_name)
    expected_chapters = get_book_chapter_count(book_name)
    
    if max_chapters:
        expected_chapters = min(expected_chapters, max_chapters)
    
    print(f"\n📖 Importing complete {book_name} ({expected_chapters} chapters)...")
    
    # Initialize importer
    importer = BibleImporter()
    
    total_verses_imported = 0
    chapters_processed = 0
    
    # Process each chapter
    for chapter_num in range(1, expected_chapters + 1):
        try:
            print(f"  📄 Processing {book_name} Chapter {chapter_num}...")
            
            # Check if chapter already has verses
            chapter = Chapter.query.filter_by(
                book_id=book.id,
                chapter_number=chapter_num
            ).first()
            
            if chapter:
                existing_verse_count = Verse.query.filter_by(chapter_id=chapter.id).count()
                if existing_verse_count > 0:
                    print(f"    ✅ Chapter {chapter_num} already has {existing_verse_count} verses, skipping")
                    continue
            
            # Get chapter data from Sefaria
            chapter_url = f"https://www.sefaria.org/api/texts/{sefaria_name}.{chapter_num}"
            
            try:
                response = requests.get(chapter_url, timeout=15)
                if response.status_code != 200:
                    print(f"    ❌ Failed to fetch {book_name} {chapter_num}: HTTP {response.status_code}")
                    continue
                    
                chapter_data = response.json()
                hebrew_verses = chapter_data.get('he', [])
                english_verses = chapter_data.get('text', [])
                
                if not hebrew_verses:
                    print(f"    ⏭️ No Hebrew verses found for {book_name} {chapter_num}")
                    continue
                
                print(f"    📝 Found {len(hebrew_verses)} verses")
                
                # Create chapter if it doesn't exist
                if not chapter:
                    chapter = Chapter(
                        book_id=book.id,
                        chapter_number=chapter_num
                    )
                    db.session.add(chapter)
                    db.session.flush()
                    print(f"    ➕ Created chapter {chapter_num}")
                
                # Process each verse
                verses_added = 0
                for verse_num in range(1, len(hebrew_verses) + 1):
                    try:
                        hebrew_verse = hebrew_verses[verse_num - 1]
                        english_verse = english_verses[verse_num - 1] if verse_num - 1 < len(english_verses) else ""
                        
                        # Clean the text
                        hebrew_clean = clean_sefaria_text(hebrew_verse)
                        english_clean = clean_sefaria_text(english_verse)
                        
                        if not hebrew_clean:
                            continue
                        
                        # Create verse data
                        verse_data = importer._create_verse_data(
                            chapter_num, verse_num, hebrew_clean, english_clean
                        )
                        
                        # Create verse
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
                        
                    except Exception as e:
                        print(f"    ⚠️  Error processing verse {chapter_num}:{verse_num}: {e}")
                        continue
                
                # Commit the chapter
                db.session.commit()
                
                total_verses_imported += verses_added
                chapters_processed += 1
                
                print(f"    ✅ Added {verses_added} verses to {book_name} {chapter_num}")
                
                # Brief pause to be nice to Sefaria API
                time.sleep(0.5)
                
            except Exception as e:
                print(f"    ❌ Error fetching {book_name} {chapter_num}: {e}")
                continue
                
        except Exception as e:
            print(f"  ❌ Error processing {book_name} chapter {chapter_num}: {e}")
            continue
    
    print(f"📊 {book_name} complete: {chapters_processed} chapters, {total_verses_imported} verses imported")
    return total_verses_imported, chapters_processed

def import_all_remaining_books():
    """Import all remaining chapters for all books"""
    
    with app.app_context():
        print("🚀 Starting complete Hebrew Bible import...")
        print("📚 This will systematically import ALL missing chapters for ALL books")
        
        # Get all books
        books = Book.query.order_by(Book.order).all()
        
        total_books_processed = 0
        total_verses_imported = 0
        total_chapters_processed = 0
        
        for book in books:
            try:
                # Check current verse count
                current_verses = db.session.query(Verse).join(Chapter).filter(
                    Chapter.book_id == book.id
                ).count()
                
                expected_chapters = get_book_chapter_count(book.name)
                
                print(f"\n{'='*60}")
                print(f"📖 {book.name} ({book.hebrew_name})")
                print(f"   Current verses: {current_verses}")
                print(f"   Expected chapters: {expected_chapters}")
                
                # Skip if it's already complete (rough estimate)
                if book.name == 'Genesis' and current_verses > 900:
                    print(f"   ✅ {book.name} appears complete, skipping")
                    continue
                    
                # Import the book
                verses_imported, chapters_processed = import_complete_book(book)
                
                total_books_processed += 1
                total_verses_imported += verses_imported
                total_chapters_processed += chapters_processed
                
                print(f"✅ {book.name} processing complete")
                
            except Exception as e:
                print(f"❌ Error processing {book.name}: {e}")
                continue
        
        print(f"\n🎉 COMPLETE BIBLE IMPORT FINISHED!")
        print(f"📚 Books processed: {total_books_processed}")
        print(f"📄 Chapters processed: {total_chapters_processed}")
        print(f"📝 Verses imported: {total_verses_imported}")
        
        # Final statistics
        final_verse_count = Verse.query.count()
        final_book_count = db.session.query(Book).join(Chapter).join(Verse).distinct(Book.id).count()
        
        print(f"\n📊 FINAL DATABASE STATISTICS:")
        print(f"   Total verses in database: {final_verse_count}")
        print(f"   Books with verses: {final_book_count}/39")
        print(f"   Completion: {(final_verse_count/23000)*100:.1f}%")

if __name__ == "__main__":
    import_all_remaining_books()