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
        # Clean paleo text by removing ancient punctuation marks
        clean_paleo_text = self.paleo_text
        if clean_paleo_text:
            # Remove maqqef (־) and sof pasuq (׃) and other ancient punctuation
            ancient_punctuation = ['־', '׃', '׀', '׆']
            for punct in ancient_punctuation:
                clean_paleo_text = clean_paleo_text.replace(punct, '')
        
        return {
            'id': self.id,
            'chapter_id': self.chapter_id,
            'verse_number': self.verse_number,
            'hebrew_text': self.hebrew_text,
            'hebrew_consonantal': self.hebrew_consonantal,
            'paleo_text': clean_paleo_text,
            'paleo_transliteration': self.paleo_transliteration,
            'modern_transliteration': self.modern_transliteration,
            'english_translation': self.english_translation,
            'literal_translation': self.literal_translation,
            'strong_numbers': self.strong_numbers,
            'morphology': self.morphology,
            'notes': self.notes
        }

class GodFact(db.Model):
    """Model for storing amazing facts that prove God is real"""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=False)  # science, history, prophecy, miracles, creation
    source = db.Column(db.String(500))  # Reference/source
    
    # Media files (optional)
    image_filename = db.Column(db.String(255))
    video_filename = db.Column(db.String(255))
    
    # Status and metadata
    status = db.Column(db.String(20), default='draft')  # draft, published
    views = db.Column(db.Integer, default=0)
    featured = db.Column(db.Boolean, default=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'category': self.category,
            'source': self.source,
            'image_filename': self.image_filename,
            'video_filename': self.video_filename,
            'status': self.status,
            'views': self.views,
            'featured': self.featured,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'image_url': f'/uploads/{self.image_filename}' if self.image_filename else None,
            'video_url': f'/uploads/{self.video_filename}' if self.video_filename else None
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

class StrongsHebrew(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    strong_number = db.Column(db.String(20), nullable=False, unique=True)  # H1, H2, etc.
    hebrew_word = db.Column(db.String(100), nullable=False)
    transliteration = db.Column(db.String(100), nullable=False)
    pronunciation = db.Column(db.String(100))
    short_definition = db.Column(db.String(200), nullable=False)
    long_definition = db.Column(db.Text)
    usage_count = db.Column(db.Integer, default=0)
    root_word = db.Column(db.String(100))
    part_of_speech = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'strong_number': self.strong_number,
            'word': self.hebrew_word,
            'transliteration': self.transliteration,
            'pronunciation': self.pronunciation,
            'meaning': self.short_definition,
            'definition': self.long_definition or self.short_definition,
            'usage_count': self.usage_count,
            'root_word': self.root_word,
            'part_of_speech': self.part_of_speech
        }

class StrongsGreek(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    strong_number = db.Column(db.String(20), nullable=False, unique=True)  # G1, G2, etc.
    greek_word = db.Column(db.String(100), nullable=False)
    transliteration = db.Column(db.String(100), nullable=False)
    pronunciation = db.Column(db.String(100))
    short_definition = db.Column(db.String(200), nullable=False)
    long_definition = db.Column(db.Text)
    usage_count = db.Column(db.Integer, default=0)
    root_word = db.Column(db.String(100))
    part_of_speech = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'strong_number': self.strong_number,
            'word': self.greek_word,
            'transliteration': self.transliteration,
            'pronunciation': self.pronunciation,
            'meaning': self.short_definition,
            'definition': self.long_definition or self.short_definition,
            'usage_count': self.usage_count,
            'root_word': self.root_word,
            'part_of_speech': self.part_of_speech
        }
class PaleoDictionary(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hebrew_word = db.Column(db.String(100), nullable=False, index=True)
    paleo_word = db.Column(db.String(100), nullable=False)
    transliteration = db.Column(db.String(100), nullable=False, index=True)
    english_meaning = db.Column(db.String(200), nullable=False)
    strong_number = db.Column(db.String(20), index=True)  # Link to Strong's if available
    
    # Root analysis
    root_letters = db.Column(db.String(50), nullable=False)  # Individual letters like "אבג"
    letter_meanings = db.Column(db.Text)  # JSON string of letter meanings
    pictographic_analysis = db.Column(db.Text, nullable=False)
    original_concept = db.Column(db.Text, nullable=False)
    
    # Word formation
    word_type = db.Column(db.String(50))  # root, derived, compound
    root_word = db.Column(db.String(100))  # If derived from another word
    formation_explanation = db.Column(db.Text)
    
    # Biblical usage
    first_occurrence = db.Column(db.String(100))  # Genesis 1:1, etc.
    usage_examples = db.Column(db.Text)  # JSON string of examples
    frequency_count = db.Column(db.Integer, default=0)
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        import json
        return {
            'id': self.id,
            'hebrew_word': self.hebrew_word,
            'paleo_word': self.paleo_word,
            'transliteration': self.transliteration,
            'english_meaning': self.english_meaning,
            'strong_number': self.strong_number,
            'root_letters': self.root_letters,
            'letter_meanings': json.loads(self.letter_meanings) if self.letter_meanings else [],
            'pictographic_analysis': self.pictographic_analysis,
            'original_concept': self.original_concept,
            'word_type': self.word_type,
            'root_word': self.root_word,
            'formation_explanation': self.formation_explanation,
            'first_occurrence': self.first_occurrence,
            'usage_examples': json.loads(self.usage_examples) if self.usage_examples else [],
            'frequency_count': self.frequency_count
        }
