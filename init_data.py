from models import db, PaleoLetter, Book, Chapter, Verse
from data.paleo_alphabet import paleo_alphabet_data

def init_alphabet():
    """Initialize the Paleo Hebrew alphabet data"""
    print("Initializing Paleo Hebrew alphabet...")
    
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
    print(f"Added {len(paleo_alphabet_data)} Paleo Hebrew letters to database")

def init_sample_books():
    """Initialize sample biblical books"""
    print("Initializing sample biblical books...")
    
    sample_books = [
        {
            'name': 'Genesis',
            'hebrew_name': 'בראשית',
            'paleo_name': '𐤁𐤓𐤀𐤔𐤉𐤕',
            'order': 1,
            'testament': 'Torah'
        },
        {
            'name': 'Exodus',
            'hebrew_name': 'שמות',
            'paleo_name': '𐤔𐤌𐤅𐤕',
            'order': 2,
            'testament': 'Torah'
        },
        {
            'name': 'Leviticus',
            'hebrew_name': 'ויקרא',
            'paleo_name': '𐤅𐤉𐤒𐤓𐤀',
            'order': 3,
            'testament': 'Torah'
        }
    ]
    
    for book_data in sample_books:
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
    print(f"Added {len(sample_books)} sample books to database")

def init_sample_genesis():
    """Initialize Genesis 1:1 as sample verse"""
    print("Adding Genesis 1:1 sample verse...")
    
    genesis = Book.query.filter_by(name='Genesis').first()
    if genesis:
        chapter1 = Chapter.query.filter_by(book_id=genesis.id, chapter_number=1).first()
        if not chapter1:
            chapter1 = Chapter(book_id=genesis.id, chapter_number=1)
            db.session.add(chapter1)
            db.session.flush()  # To get the chapter ID
        
        verse1 = Verse.query.filter_by(chapter_id=chapter1.id, verse_number=1).first()
        if not verse1:
            verse1 = Verse(
                chapter_id=chapter1.id,
                verse_number=1,
                hebrew_text='בְּרֵאשִׁית בָּרָא אֱלֹהִים אֵת הַשָּׁמַיִם וְאֵת הָאָרֶץ',
                paleo_text='𐤁𐤓𐤀𐤔𐤉𐤕 𐤁𐤓𐤀 𐤀𐤋𐤄𐤉𐤌 𐤀𐤕 𐤄𐤔𐤌𐤉𐤌 𐤅𐤀𐤕 𐤄𐤀𐤓𐤑',
                transliteration='bereshit bara elohim et hashamayim ve\'et ha\'aretz',
                english_translation='In the beginning God created the heavens and the earth.'
            )
            db.session.add(verse1)
    
    db.session.commit()
    print("Added Genesis 1:1 sample verse")

def init_all():
    """Initialize all data"""
    init_alphabet()
    init_sample_books()
    init_sample_genesis()
    print("Database initialization complete!")

if __name__ == '__main__':
    from app import app
    with app.app_context():
        db.create_all()
        init_all()