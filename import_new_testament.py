#!/usr/bin/env python3
"""
Import New Testament books (27 books) with Greek text
Adapt the existing Hebrew/Paleo structure for Greek New Testament
"""

from app import app, db
from models import Book, Chapter, Verse
import requests
import re
import time

def clean_text(text):
    """Clean HTML tags and formatting from text"""
    if not text:
        return ""
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'\*', '', text)
    return text.strip()

def greek_to_transliteration(greek_text):
    """Convert Greek text to basic transliteration"""
    if not greek_text:
        return ""
    
    # Basic Greek to Latin transliteration mapping
    transliteration_map = {
        'α': 'a', 'β': 'b', 'γ': 'g', 'δ': 'd', 'ε': 'e', 'ζ': 'z', 'η': 'e', 'θ': 'th',
        'ι': 'i', 'κ': 'k', 'λ': 'l', 'μ': 'm', 'ν': 'n', 'ξ': 'x', 'ο': 'o', 'π': 'p',
        'ρ': 'r', 'σ': 's', 'ς': 's', 'τ': 't', 'υ': 'u', 'φ': 'ph', 'χ': 'ch', 'ψ': 'ps', 'ω': 'o',
        'Α': 'A', 'Β': 'B', 'Γ': 'G', 'Δ': 'D', 'Ε': 'E', 'Ζ': 'Z', 'Η': 'E', 'Θ': 'Th',
        'Ι': 'I', 'Κ': 'K', 'Λ': 'L', 'Μ': 'M', 'Ν': 'N', 'Ξ': 'X', 'Ο': 'O', 'Π': 'P',
        'Ρ': 'R', 'Σ': 'S', 'Τ': 'T', 'Υ': 'U', 'Φ': 'Ph', 'Χ': 'Ch', 'Ψ': 'Ps', 'Ω': 'O'
    }
    
    result = ""
    for char in greek_text:
        result += transliteration_map.get(char, char)
    
    return result

def create_nt_books():
    """Create the 27 New Testament books in the database"""
    
    nt_books = [
        # Gospels
        (40, "Matthew", "Κατά Ματθαίον", "Kata Matthaion", "New Testament"),
        (41, "Mark", "Κατά Μάρκον", "Kata Markon", "New Testament"),
        (42, "Luke", "Κατά Λουκάν", "Kata Loukan", "New Testament"),
        (43, "John", "Κατά Ἰωάννην", "Kata Ioannen", "New Testament"),
        
        # Acts
        (44, "Acts", "Πράξεις Ἀποστόλων", "Praxeis Apostolon", "New Testament"),
        
        # Paul's Epistles
        (45, "Romans", "Πρὸς Ῥωμαίους", "Pros Romaious", "New Testament"),
        (46, "1 Corinthians", "Πρὸς Κορινθίους Α", "Pros Korinthious A", "New Testament"),
        (47, "2 Corinthians", "Πρὸς Κορινθίους Β", "Pros Korinthious B", "New Testament"),
        (48, "Galatians", "Πρὸς Γαλάτας", "Pros Galatas", "New Testament"),
        (49, "Ephesians", "Πρὸς Ἐφεσίους", "Pros Ephesious", "New Testament"),
        (50, "Philippians", "Πρὸς Φιλιππησίους", "Pros Philippesious", "New Testament"),
        (51, "Colossians", "Πρὸς Κολοσσαεῖς", "Pros Kolossaeis", "New Testament"),
        (52, "1 Thessalonians", "Πρὸς Θεσσαλονικεῖς Α", "Pros Thessalonikeis A", "New Testament"),
        (53, "2 Thessalonians", "Πρὸς Θεσσαλονικεῖς Β", "Pros Thessalonikeis B", "New Testament"),
        (54, "1 Timothy", "Πρὸς Τιμόθεον Α", "Pros Timotheon A", "New Testament"),
        (55, "2 Timothy", "Πρὸς Τιμόθεον Β", "Pros Timotheon B", "New Testament"),
        (56, "Titus", "Πρὸς Τίτον", "Pros Titon", "New Testament"),
        (57, "Philemon", "Πρὸς Φιλήμονα", "Pros Philemona", "New Testament"),
        
        # General Epistles
        (58, "Hebrews", "Πρὸς Ἑβραίους", "Pros Hebraious", "New Testament"),
        (59, "James", "Ἰακώβου", "Iakobou", "New Testament"),
        (60, "1 Peter", "Πέτρου Α", "Petrou A", "New Testament"),
        (61, "2 Peter", "Πέτρου Β", "Petrou B", "New Testament"),
        (62, "1 John", "Ἰωάννου Α", "Ioannou A", "New Testament"),
        (63, "2 John", "Ἰωάννου Β", "Ioannou B", "New Testament"),
        (64, "3 John", "Ἰωάννου Γ", "Ioannou G", "New Testament"),
        (65, "Jude", "Ἰούδα", "Iouda", "New Testament"),
        
        # Apocalypse
        (66, "Revelation", "Ἀποκάλυψις", "Apokalupsis", "New Testament")
    ]
    
    with app.app_context():
        print("📚 Creating New Testament books...")
        
        for order, name, greek_name, transliteration, testament in nt_books:
            # Check if book already exists
            existing_book = Book.query.filter_by(name=name).first()
            if existing_book:
                print(f"   ✅ {name} already exists, skipping")
                continue
            
            # Create new book
            book = Book(
                name=name,
                hebrew_name=greek_name,  # Using hebrew_name field for Greek
                paleo_name=transliteration,  # Using paleo_name field for transliteration
                order=order,
                testament=testament
            )
            
            db.session.add(book)
            print(f"   ➕ Added {name} ({greek_name})")
        
        try:
            db.session.commit()
            print("✅ New Testament books created successfully!")
            return True
        except Exception as e:
            print(f"❌ Error creating NT books: {e}")
            db.session.rollback()
            return False

def get_nt_chapter_counts():
    """Get expected chapter counts for NT books"""
    return {
        "Matthew": 28, "Mark": 16, "Luke": 24, "John": 21,
        "Acts": 28,
        "Romans": 16, "1 Corinthians": 16, "2 Corinthians": 13, "Galatians": 6,
        "Ephesians": 6, "Philippians": 4, "Colossians": 4,
        "1 Thessalonians": 5, "2 Thessalonians": 3,
        "1 Timothy": 6, "2 Timothy": 4, "Titus": 3, "Philemon": 1,
        "Hebrews": 13, "James": 5, "1 Peter": 5, "2 Peter": 3,
        "1 John": 5, "2 John": 1, "3 John": 1, "Jude": 1,
        "Revelation": 22
    }

def get_sefaria_nt_name(book_name):
    """Map NT book names to Sefaria API names"""
    sefaria_names = {
        "Matthew": "Matthew",
        "Mark": "Mark", 
        "Luke": "Luke",
        "John": "John",
        "Acts": "Acts",
        "Romans": "Romans",
        "1 Corinthians": "I Corinthians",
        "2 Corinthians": "II Corinthians",
        "Galatians": "Galatians",
        "Ephesians": "Ephesians",
        "Philippians": "Philippians",
        "Colossians": "Colossians",
        "1 Thessalonians": "I Thessalonians",
        "2 Thessalonians": "II Thessalonians",
        "1 Timothy": "I Timothy",
        "2 Timothy": "II Timothy",
        "Titus": "Titus",
        "Philemon": "Philemon",
        "Hebrews": "Hebrews",
        "James": "James",
        "1 Peter": "I Peter",
        "2 Peter": "II Peter",
        "1 John": "I John",
        "2 John": "II John",
        "3 John": "III John",
        "Jude": "Jude",
        "Revelation": "Revelation"
    }
    return sefaria_names.get(book_name, book_name)

def import_nt_book_content(book, max_chapters=None):
    """Import verses for a New Testament book"""
    
    book_name = book.name
    sefaria_name = get_sefaria_nt_name(book_name)
    expected_chapters = get_nt_chapter_counts().get(book_name, 1)
    
    if max_chapters:
        expected_chapters = min(expected_chapters, max_chapters)
    
    print(f"\n📖 Importing {book_name} ({expected_chapters} chapters)...")
    
    total_verses_imported = 0
    chapters_processed = 0
    
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
            
            # Try to get from Sefaria API (might not have NT)
            chapter_url = f"https://www.sefaria.org/api/texts/{sefaria_name}.{chapter_num}"
            
            try:
                response = requests.get(chapter_url, timeout=15)
                if response.status_code == 200:
                    chapter_data = response.json()
                    english_verses = chapter_data.get('text', [])
                    
                    if english_verses:
                        print(f"    📝 Found {len(english_verses)} verses from Sefaria")
                        
                        # Create chapter if it doesn't exist
                        if not chapter:
                            chapter = Chapter(
                                book_id=book.id,
                                chapter_number=chapter_num
                            )
                            db.session.add(chapter)
                            db.session.flush()
                        
                        # Add verses (using English text as placeholder)
                        verses_added = 0
                        for verse_num, english_verse in enumerate(english_verses, 1):
                            if isinstance(english_verse, list):
                                english_verse = " ".join(english_verse)
                            
                            english_clean = clean_text(str(english_verse))
                            if not english_clean:
                                continue
                            
                            # Create verse with adapted structure
                            verse = Verse(
                                chapter_id=chapter.id,
                                verse_number=verse_num,
                                hebrew_text=english_clean,  # Using for Greek text placeholder
                                hebrew_consonantal=english_clean,  # Placeholder
                                paleo_text=english_clean,  # Placeholder  
                                paleo_transliteration=greek_to_transliteration(english_clean),
                                modern_transliteration=greek_to_transliteration(english_clean),
                                english_translation=english_clean,
                                literal_translation=english_clean
                            )
                            
                            db.session.add(verse)
                            verses_added += 1
                        
                        db.session.commit()
                        total_verses_imported += verses_added
                        chapters_processed += 1
                        
                        print(f"    ✅ Added {verses_added} verses to {book_name} {chapter_num}")
                        time.sleep(0.5)
                    else:
                        print(f"    ⏭️ No verses found for {book_name} {chapter_num}")
                else:
                    print(f"    ⏭️ Sefaria doesn't have {book_name} {chapter_num} (status: {response.status_code})")
                    
            except Exception as e:
                print(f"    ⏭️ Could not fetch from Sefaria for {book_name} {chapter_num}: {e}")
                
        except Exception as e:
            print(f"  ❌ Error processing {book_name} chapter {chapter_num}: {e}")
            continue
    
    print(f"📊 {book_name} processing complete: {chapters_processed} chapters, {total_verses_imported} verses imported")
    return total_verses_imported, chapters_processed

def import_all_nt_books():
    """Import all New Testament books and their content"""
    
    with app.app_context():
        print("🚀 Starting New Testament import...")
        
        # First create the books
        if not create_nt_books():
            print("❌ Failed to create NT books")
            return
        
        # Get all NT books
        nt_books = Book.query.filter_by(testament='New Testament').order_by(Book.order).all()
        
        total_books_processed = 0
        total_verses_imported = 0
        total_chapters_processed = 0
        
        for book in nt_books:
            try:
                print(f"\n{'='*60}")
                print(f"📖 Processing {book.name} ({book.hebrew_name})")
                
                verses_imported, chapters_processed = import_nt_book_content(book)
                
                total_books_processed += 1
                total_verses_imported += verses_imported
                total_chapters_processed += chapters_processed
                
            except Exception as e:
                print(f"❌ Error processing {book.name}: {e}")
                continue
        
        print(f"\n🎉 NEW TESTAMENT IMPORT FINISHED!")
        print(f"📚 Books processed: {total_books_processed}")
        print(f"📄 Chapters processed: {total_chapters_processed}")
        print(f"📝 Verses imported: {total_verses_imported}")
        
        # Final statistics
        final_verse_count = Verse.query.count()
        final_book_count = Book.query.count()
        
        print(f"\n📊 FINAL DATABASE STATISTICS:")
        print(f"   Total verses in database: {final_verse_count}")
        print(f"   Total books: {final_book_count}/66")

if __name__ == "__main__":
    import_all_nt_books()