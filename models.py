from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Create db instance that will be imported by app.py
db = SQLAlchemy()

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    hebrew_name = db.Column(db.String(100), nullable=False)
    paleo_name = db.Column(db.String(100), nullable=False)
    order = db.Column(db.Integer, nullable=False)
    testament = db.Column(db.String(20), nullable=False)  # 'Torah', 'Nevi\'im', 'Ketuvim'
    chapters = db.relationship('Chapter', backref='book', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'hebrew_name': self.hebrew_name,
            'paleo_name': self.paleo_name,
            'order': self.order,
            'testament': self.testament,
            'chapter_count': len(self.chapters)
        }

class Chapter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    chapter_number = db.Column(db.Integer, nullable=False)
    verses = db.relationship('Verse', backref='chapter', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'book_id': self.book_id,
            'chapter_number': self.chapter_number,
            'verse_count': len(self.verses)
        }

class Verse(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    chapter_id = db.Column(db.Integer, db.ForeignKey('chapter.id'), nullable=False)
    verse_number = db.Column(db.Integer, nullable=False)
    
    # Original texts
    hebrew_text = db.Column(db.Text, nullable=False)  # Modern Hebrew with nikud
    hebrew_consonantal = db.Column(db.Text, nullable=False)  # Hebrew without nikud
    paleo_text = db.Column(db.Text, nullable=False)  # Paleo Hebrew script
    
    # Transliterations
    paleo_transliteration = db.Column(db.Text, nullable=False)  # Ancient pronunciation (barashyt bara)
    modern_transliteration = db.Column(db.Text, nullable=False)  # Modern Hebrew pronunciation
    
    # Translations
    english_translation = db.Column(db.Text)  # English translation
    literal_translation = db.Column(db.Text)  # Word-for-word literal
    
    # Additional fields
    strong_numbers = db.Column(db.Text)  # Strong's concordance numbers
    morphology = db.Column(db.Text)  # Morphological analysis
    notes = db.Column(db.Text)  # Commentary or notes
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'chapter_id': self.chapter_id,
            'verse_number': self.verse_number,
            'hebrew_text': self.hebrew_text,
            'hebrew_consonantal': self.hebrew_consonantal,
            'paleo_text': self.paleo_text,
            'paleo_transliteration': self.paleo_transliteration,
            'modern_transliteration': self.modern_transliteration,
            'english_translation': self.english_translation,
            'literal_translation': self.literal_translation,
            'strong_numbers': self.strong_numbers,
            'morphology': self.morphology,
            'notes': self.notes
        }

class PaleoLetter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    letter = db.Column(db.String(10), nullable=False, unique=True)
    paleo_symbol = db.Column(db.String(10), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    meaning = db.Column(db.String(200), nullable=False)
    pictograph_description = db.Column(db.String(200), nullable=False)
    sound = db.Column(db.String(20), nullable=False)
    numerical_value = db.Column(db.Integer)
    order = db.Column(db.Integer, nullable=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'letter': self.letter,
            'paleo_symbol': self.paleo_symbol,
            'name': self.name,
            'meaning': self.meaning,
            'pictograph_description': self.pictograph_description,
            'sound': self.sound,
            'numerical_value': self.numerical_value,
            'order': self.order
        }

class Word(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hebrew_word = db.Column(db.String(100), nullable=False)
    paleo_word = db.Column(db.String(100), nullable=False)
    transliteration = db.Column(db.String(100), nullable=False)
    pronunciation = db.Column(db.String(100), nullable=False)
    meaning = db.Column(db.Text, nullable=False)
    root_analysis = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'hebrew_word': self.hebrew_word,
            'paleo_word': self.paleo_word,
            'transliteration': self.transliteration,
            'pronunciation': self.pronunciation,
            'meaning': self.meaning,
            'root_analysis': self.root_analysis
        }