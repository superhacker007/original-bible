"""
Simple initialization with enhanced verse structure
"""

from app import app, db
from models import Book, Chapter, Verse, PaleoLetter
from data.paleo_alphabet import paleo_alphabet_data
from utils.bible_importer import BibleImporter
import os

def init_fresh_database():
    """Initialize fresh database with enhanced verse structure"""
    
    # Remove existing database
    if os.path.exists('paleo_bible.db'):
        os.remove('paleo_bible.db')
        print("🗑️ Removed existing database")
    
    with app.app_context():
        print("🔧 Creating fresh database...")
        db.create_all()
        
        # Initialize alphabet
        print("📜 Adding Paleo Hebrew alphabet...")
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
        
        # Create sample books
        print("📚 Adding sample books...")
        books_data = [
            {'name': 'Genesis', 'hebrew_name': 'בראשית', 'paleo_name': '𐤁𐤓𐤀𐤔𐤉𐤕', 'order': 1, 'testament': 'Torah'},
            {'name': 'Exodus', 'hebrew_name': 'שמות', 'paleo_name': '𐤔𐤌𐤅𐤕', 'order': 2, 'testament': 'Torah'},
            {'name': 'Leviticus', 'hebrew_name': 'ויקרא', 'paleo_name': '𐤅𐤉𐤒𐤓𐤀', 'order': 3, 'testament': 'Torah'}
        ]
        
        for book_data in books_data:
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
        
        db.session.commit()
        
        # Add Genesis chapters
        genesis = Book.query.filter_by(name='Genesis').first()
        for i in range(1, 51):  # Genesis has 50 chapters
            chapter = Chapter(book_id=genesis.id, chapter_number=i)
            db.session.add(chapter)
        
        db.session.commit()
        
        # Add enhanced Genesis verses
        print("📖 Adding enhanced Genesis verses...")
        importer = BibleImporter()
        sample_verses = importer.create_sample_genesis_data()
        
        for verse_data in sample_verses:
            chapter = Chapter.query.filter_by(
                book_id=genesis.id,
                chapter_number=verse_data['chapter']
            ).first()
            
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
        
        db.session.commit()
        
        print("✅ Database initialized successfully!")
        print(f"📚 Books: {Book.query.count()}")
        print(f"📖 Chapters: {Chapter.query.count()}")  
        print(f"📝 Verses: {Verse.query.count()}")
        print(f"🔤 Letters: {PaleoLetter.query.count()}")
        
        # Test a verse
        test_verse = Verse.query.first()
        if test_verse:
            print("\n🧪 Sample verse:")
            print(f"Hebrew: {test_verse.hebrew_text}")
            print(f"Paleo: {test_verse.paleo_text}")
            print(f"Paleo Transliteration: {test_verse.paleo_transliteration}")
            print(f"English: {test_verse.english_translation}")

if __name__ == '__main__':
    init_fresh_database()