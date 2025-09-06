"""
Paleo Dictionary Database Model
"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

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