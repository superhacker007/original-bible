"""
Test new database structure
"""

from app import app, db
from models import Book, Chapter, Verse, PaleoLetter
from utils.bible_importer import BibleImporter

def test_new_db():
    with app.app_context():
        print("Creating tables...")
        db.create_all()
        
        print("Testing Bible importer...")
        importer = BibleImporter()
        
        # Test sample Genesis data
        sample_verses = importer.create_sample_genesis_data()
        
        print("Sample verse data structure:")
        if sample_verses:
            verse = sample_verses[0]
            for key, value in verse.items():
                print(f"  {key}: {value}")
        
        print("Database test complete!")

if __name__ == '__main__':
    test_new_db()