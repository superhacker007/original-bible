"""
Docker-optimized initialization
Creates database structure and imports priority books from Sefaria API
"""

import os
import sys
import time
import requests
from app import app, db
from models import Book, Chapter, Verse, PaleoLetter
from data.paleo_alphabet import paleo_alphabet_data
from utils.bible_importer import BibleImporter
from utils.hebrew_converter import hebrew_to_paleo, remove_nikud

def init_docker_database():
    """Initialize database for Docker deployment"""
    
    print("🐳 Docker Bible Database Initialization")
    print("=====================================")
    
    with app.app_context():
        print("🔧 Creating database tables...")
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
        
        db.session.commit()
        
        # Add essential books structure
        print("📚 Creating book structure...")
        priority_books = [
            {'name': 'Genesis', 'hebrew_name': 'בראשית', 'paleo_name': '𐤁𐤓𐤀𐤔𐤉𐤕', 'order': 1, 'testament': 'Torah', 'chapters': 50},
            {'name': 'Exodus', 'hebrew_name': 'שמות', 'paleo_name': '𐤔𐤌𐤅𐤕', 'order': 2, 'testament': 'Torah', 'chapters': 40},
            {'name': 'Leviticus', 'hebrew_name': 'ויקרא', 'paleo_name': '𐤅𐤉𐤒𐤓𐤀', 'order': 3, 'testament': 'Torah', 'chapters': 27},
            {'name': 'Numbers', 'hebrew_name': 'במדבר', 'paleo_name': '𐤁𐤌𐤃𐤁𐤓', 'order': 4, 'testament': 'Torah', 'chapters': 36},
            {'name': 'Deuteronomy', 'hebrew_name': 'דברים', 'paleo_name': '𐤃𐤁𐤓𐤉𐤌', 'order': 5, 'testament': 'Torah', 'chapters': 34},
        ]
        
        for book_data in priority_books:
            existing_book = Book.query.filter_by(name=book_data['name']).first()
            if not existing_book:
                book = Book(
                    name=book_data['name'],
                    hebrew_name=book_data['hebrew_name'],
                    paleo_name=book_data['paleo_name'],
                    order=book_data['order'],
                    testament=book_data['testament']
                )
                db.session.add(book)
                db.session.commit()
                
                # Add chapters for this book
                for i in range(1, book_data['chapters'] + 1):
                    chapter = Chapter(book_id=book.id, chapter_number=i)
                    db.session.add(chapter)
                
                db.session.commit()
        
        # Import Genesis 1 from Sefaria as sample
        print("🌍 Importing Genesis 1 from Sefaria API...")
        try:
            import_genesis_chapter_1()
        except Exception as e:
            print(f"⚠️ Warning: Could not import from Sefaria: {e}")
            print("📝 Creating sample verses instead...")
            create_sample_verses()
        
        # Final statistics
        print("\n✅ Docker initialization complete!")
        print(f"📚 Books: {Book.query.count()}")
        print(f"📖 Chapters: {Chapter.query.count()}")
        print(f"📝 Verses: {Verse.query.count()}")
        print(f"🔤 Letters: {PaleoLetter.query.count()}")

def import_genesis_chapter_1():
    """Import Genesis chapter 1 from Sefaria API"""
    
    url = "https://www.sefaria.org/api/texts/Genesis.1"
    response = requests.get(url, timeout=10)
    
    if response.status_code != 200:
        raise Exception(f"Sefaria API returned {response.status_code}")
    
    data = response.json()
    hebrew_verses = data.get('he', [])
    english_verses = data.get('text', [])
    
    if not hebrew_verses or not english_verses:
        raise Exception("No verse data in response")
    
    genesis = Book.query.filter_by(name='Genesis').first()
    chapter_1 = Chapter.query.filter_by(book_id=genesis.id, chapter_number=1).first()
    
    importer = BibleImporter()
    
    for i, (hebrew_text, english_text) in enumerate(zip(hebrew_verses, english_verses), 1):
        if isinstance(hebrew_text, str) and isinstance(english_text, str):
            
            # Clean and process Hebrew text
            hebrew_consonantal = remove_nikud(hebrew_text)
            paleo_text = hebrew_to_paleo(hebrew_consonantal)
            
            # Create transliterations
            paleo_transliteration = importer.transliterate_paleo(paleo_text)
            modern_transliteration = importer.transliterate_hebrew(hebrew_consonantal)
            
            verse = Verse(
                chapter_id=chapter_1.id,
                verse_number=i,
                hebrew_text=hebrew_text,
                hebrew_consonantal=hebrew_consonantal,
                paleo_text=paleo_text,
                paleo_transliteration=paleo_transliteration,
                modern_transliteration=modern_transliteration,
                english_translation=english_text,
                literal_translation=english_text,  # Use same for now
                strong_numbers='',
                morphology='',
                notes=f'Imported from Sefaria API'
            )
            db.session.add(verse)
    
    db.session.commit()
    print(f"✅ Imported {len(hebrew_verses)} verses from Genesis 1")

def create_sample_verses():
    """Create sample verses if Sefaria import fails"""
    
    genesis = Book.query.filter_by(name='Genesis').first()
    chapter_1 = Chapter.query.filter_by(book_id=genesis.id, chapter_number=1).first()
    
    sample_verses = [
        {
            'verse': 1,
            'hebrew': 'בְּרֵאשִׁ֖ית בָּרָ֣א אֱלֹהִ֑ים אֵ֥ת הַשָּׁמַ֖יִם וְאֵ֥ת הָאָֽרֶץ׃',
            'english': 'In the beginning God created the heavens and the earth.'
        },
        {
            'verse': 2,
            'hebrew': 'וְהָאָ֗רֶץ הָיְתָ֥ה תֹ֙הוּ֙ וָבֹ֔הוּ וְחֹ֖שֶׁךְ עַל־פְּנֵ֣י תְה֑וֹם וְר֣וּחַ אֱלֹהִ֔ים מְרַחֶ֖פֶת עַל־פְּנֵ֥י הַמָּֽיִם׃',
            'english': 'The earth was without form, and void; and darkness was on the face of the deep. And the Spirit of God was hovering over the face of the waters.'
        },
        {
            'verse': 3,
            'hebrew': 'וַיֹּ֥אמֶר אֱלֹהִ֖ים יְהִ֣י א֑וֹר וַֽיְהִי־אֽוֹר׃',
            'english': 'Then God said, "Let there be light"; and there was light.'
        }
    ]
    
    importer = BibleImporter()
    
    for verse_data in sample_verses:
        hebrew_text = verse_data['hebrew']
        hebrew_consonantal = remove_nikud(hebrew_text)
        paleo_text = hebrew_to_paleo(hebrew_consonantal)
        
        verse = Verse(
            chapter_id=chapter_1.id,
            verse_number=verse_data['verse'],
            hebrew_text=hebrew_text,
            hebrew_consonantal=hebrew_consonantal,
            paleo_text=paleo_text,
            paleo_transliteration=importer.transliterate_paleo(paleo_text),
            modern_transliteration=importer.transliterate_hebrew(hebrew_consonantal),
            english_translation=verse_data['english'],
            literal_translation=verse_data['english'],
            strong_numbers='',
            morphology='',
            notes='Sample verse'
        )
        db.session.add(verse)
    
    db.session.commit()
    print(f"✅ Created {len(sample_verses)} sample verses")

if __name__ == '__main__':
    init_docker_database()