"""
Enhanced Bible initialization with complete Tanakh
Imports all 39 books of the Hebrew Bible with enhanced verse data
"""

from models import db, PaleoLetter, Book, Chapter, Verse
from data.paleo_alphabet import paleo_alphabet_data
from data.bible_books import HEBREW_BIBLE_BOOKS, TESTAMENT_INFO
from utils.bible_importer import BibleImporter
import requests
import json
import time
from datetime import datetime

class CompleteBibleInitializer:
    """Initialize complete Hebrew Bible with all verse data"""
    
    def __init__(self):
        self.importer = BibleImporter()
        self.books_imported = 0
        self.chapters_imported = 0
        self.verses_imported = 0
    
    def init_all_data(self):
        """Initialize all Bible data including alphabet, books, and verses"""
        print("=== COMPLETE BIBLE INITIALIZATION ===")
        print(f"Starting at: {datetime.now()}")
        print()
        
        # Initialize alphabet
        self.init_alphabet()
        
        # Initialize all 39 books
        self.init_all_books()
        
        # Import enhanced Genesis sample data
        self.init_enhanced_genesis()
        
        print("\n=== INITIALIZATION COMPLETE ===")
        print(f"Books imported: {self.books_imported}")
        print(f"Chapters imported: {self.chapters_imported}")
        print(f"Verses imported: {self.verses_imported}")
        print(f"Completed at: {datetime.now()}")
    
    def init_alphabet(self):
        """Initialize Paleo Hebrew alphabet"""
        print("📜 Initializing Paleo Hebrew alphabet...")
        
        for letter_data in paleo_alphabet_data:
            existing = PaleoLetter.query.filter_by(letter=letter_data['letter']).first()
            if not existing:
                letter = PaleoLetter(
                    letter=letter_data['letter'],
                    paleo_symbol=letter_data['paleo_symbol'],
                    name=letter_data['name'],
                    meaning=letter_data['meaning'],
                    pictograph_description=letter_data['pictograph_description'],
                    sound=letter_data['sound'],
                    numerical_value=letter_data['numerical_value'],
                    order=letter_data['order']
                )
                db.session.add(letter)
        
        db.session.commit()
        print(f"✅ Added {len(paleo_alphabet_data)} Paleo Hebrew letters")
    
    def init_all_books(self):
        """Initialize all 39 Hebrew Bible books"""
        print("\n📚 Initializing Hebrew Bible books...")
        print(f"Total books to create: {len(HEBREW_BIBLE_BOOKS)}")
        
        for book_data in HEBREW_BIBLE_BOOKS:
            existing = Book.query.filter_by(name=book_data['name']).first()
            if not existing:
                book = Book(
                    name=book_data['name'],
                    hebrew_name=book_data['hebrew_name'],
                    paleo_name=book_data['paleo_name'],
                    order=book_data['order'],
                    testament=book_data['testament']
                )
                db.session.add(book)
                self.books_imported += 1
                
                # Create empty chapters for each book
                for chapter_num in range(1, book_data['chapters'] + 1):
                    chapter = Chapter(
                        book=book,
                        chapter_number=chapter_num
                    )
                    db.session.add(chapter)
                    self.chapters_imported += 1
        
        db.session.commit()
        print(f"✅ Created {self.books_imported} books and {self.chapters_imported} chapters")
    
    def init_enhanced_genesis(self):
        """Initialize Genesis with enhanced verse data"""
        print("\n📖 Initializing enhanced Genesis data...")
        
        genesis = Book.query.filter_by(name='Genesis').first()
        if not genesis:
            print("❌ Genesis book not found!")
            return
        
        # Get sample Genesis data from importer
        sample_verses = self.importer.create_sample_genesis_data()
        
        for verse_data in sample_verses:
            chapter = Chapter.query.filter_by(
                book_id=genesis.id, 
                chapter_number=verse_data['chapter']
            ).first()
            
            if chapter:
                # Check if verse already exists
                existing_verse = Verse.query.filter_by(
                    chapter_id=chapter.id,
                    verse_number=verse_data['verse']
                ).first()
                
                if not existing_verse:
                    verse = Verse(
                        chapter_id=chapter.id,
                        verse_number=verse_data['verse'],
                        hebrew_text=verse_data['hebrew_text'],
                        hebrew_consonantal=verse_data['hebrew_consonantal'],
                        paleo_text=verse_data['paleo_text'],
                        paleo_transliteration=verse_data['paleo_transliteration'],
                        modern_transliteration=verse_data['modern_transliteration'],
                        english_translation=verse_data['english_translation'],
                        literal_translation=verse_data['literal_translation'],
                        strong_numbers=verse_data.get('strong_numbers', ''),
                        morphology=verse_data.get('morphology', ''),
                        notes=verse_data.get('notes', '')
                    )
                    db.session.add(verse)
                    self.verses_imported += 1
        
        db.session.commit()
        print(f"✅ Added {self.verses_imported} enhanced Genesis verses")
    
    def import_book_from_api(self, book_name: str, sefaria_name: str = None):
        """
        Import a complete book from Sefaria API
        
        Args:
            book_name: Name in our database (e.g., 'Genesis')
            sefaria_name: Name in Sefaria API (e.g., 'Genesis') - defaults to book_name
        """
        if not sefaria_name:
            sefaria_name = book_name
        
        print(f"\n📥 Importing {book_name} from Sefaria API...")
        
        book = Book.query.filter_by(name=book_name).first()
        if not book:
            print(f"❌ Book {book_name} not found in database!")
            return
        
        try:
            verses_data = self.importer.import_from_sefaria_api(sefaria_name)
            
            if not verses_data:
                print(f"❌ No data retrieved for {book_name}")
                return
            
            imported_count = 0
            for verse_data in verses_data:
                chapter = Chapter.query.filter_by(
                    book_id=book.id,
                    chapter_number=verse_data['chapter']
                ).first()
                
                if chapter:
                    # Check if verse already exists
                    existing_verse = Verse.query.filter_by(
                        chapter_id=chapter.id,
                        verse_number=verse_data['verse']
                    ).first()
                    
                    if not existing_verse:
                        verse = Verse(
                            chapter_id=chapter.id,
                            verse_number=verse_data['verse'],
                            hebrew_text=verse_data['hebrew_text'],
                            hebrew_consonantal=verse_data['hebrew_consonantal'],
                            paleo_text=verse_data['paleo_text'],
                            paleo_transliteration=verse_data['paleo_transliteration'],
                            modern_transliteration=verse_data['modern_transliteration'],
                            english_translation=verse_data['english_translation'],
                            literal_translation=verse_data['literal_translation'],
                            strong_numbers=verse_data.get('strong_numbers', ''),
                            morphology=verse_data.get('morphology', ''),
                            notes=verse_data.get('notes', '')
                        )
                        db.session.add(verse)
                        imported_count += 1
                        
                        # Commit every 100 verses to avoid memory issues
                        if imported_count % 100 == 0:
                            db.session.commit()
                            print(f"  📝 Imported {imported_count} verses...")
            
            db.session.commit()
            print(f"✅ Successfully imported {imported_count} verses for {book_name}")
            self.verses_imported += imported_count
            
        except Exception as e:
            print(f"❌ Error importing {book_name}: {e}")
    
    def import_torah_books(self):
        """Import all Torah books (Genesis through Deuteronomy)"""
        torah_books = [
            ('Genesis', 'Genesis'),
            ('Exodus', 'Exodus'),
            ('Leviticus', 'Leviticus'),
            ('Numbers', 'Numbers'),
            ('Deuteronomy', 'Deuteronomy')
        ]
        
        print("\n🕊️ Importing Torah (Five Books of Moses)...")
        
        for book_name, sefaria_name in torah_books:
            self.import_book_from_api(book_name, sefaria_name)
            time.sleep(1)  # Be nice to the API
    
    def create_test_verses(self):
        """Create additional test verses for demonstration"""
        print("\n🧪 Creating additional test verses...")
        
        # Enhanced Genesis 1:6-10 for testing
        test_verses = [
            {
                'chapter': 1, 'verse': 6,
                'hebrew': 'וַיֹּאמֶר אֱלֹהִים יְהִי רָקִיעַ בְּתוֹךְ הַמָּיִם וִיהִי מַבְדִּיל בֵּין מַיִם לָמָיִם',
                'english': 'And God said, "Let there be a vault between the waters to separate water from water."'
            },
            {
                'chapter': 1, 'verse': 7,
                'hebrew': 'וַיַּעַשׂ אֱלֹהִים אֶת־הָרָקִיעַ וַיַּבְדֵּל בֵּין הַמַּיִם אֲשֶׁר מִתַּחַת לָרָקִיעַ וּבֵין הַמַּיִם אֲשֶׁר מֵעַל לָרָקִיעַ וַיְהִי־כֵן',
                'english': 'So God made the vault and separated the water under the vault from the water above it. And it was so.'
            }
        ]
        
        genesis = Book.query.filter_by(name='Genesis').first()
        if genesis:
            for verse_info in test_verses:
                verse_data = self.importer._create_verse_data(
                    verse_info['chapter'],
                    verse_info['verse'],
                    verse_info['hebrew'],
                    verse_info['english']
                )
                
                chapter = Chapter.query.filter_by(
                    book_id=genesis.id,
                    chapter_number=verse_info['chapter']
                ).first()
                
                if chapter:
                    existing_verse = Verse.query.filter_by(
                        chapter_id=chapter.id,
                        verse_number=verse_info['verse']
                    ).first()
                    
                    if not existing_verse:
                        verse = Verse(
                            chapter_id=chapter.id,
                            verse_number=verse_info['verse'],
                            hebrew_text=verse_data['hebrew_text'],
                            hebrew_consonantal=verse_data['hebrew_consonantal'],
                            paleo_text=verse_data['paleo_text'],
                            paleo_transliteration=verse_data['paleo_transliteration'],
                            modern_transliteration=verse_data['modern_transliteration'],
                            english_translation=verse_data['english_translation'],
                            literal_translation=verse_data['literal_translation'],
                        )
                        db.session.add(verse)
                        self.verses_imported += 1
            
            db.session.commit()
            print(f"✅ Added {len(test_verses)} test verses")

def main():
    """Main initialization function"""
    from app import app
    
    with app.app_context():
        # Create all tables
        db.create_all()
        
        # Initialize complete Bible
        initializer = CompleteBibleInitializer()
        initializer.init_all_data()
        
        # Create additional test verses
        initializer.create_test_verses()
        
        print("\n🎉 COMPLETE BIBLE INITIALIZATION FINISHED!")
        print(f"📊 Final Statistics:")
        print(f"   📚 Books: {initializer.books_imported}")
        print(f"   📖 Chapters: {initializer.chapters_imported}")
        print(f"   📝 Verses: {initializer.verses_imported}")

if __name__ == '__main__':
    main()