"""
Background Bible import script
Continuously imports Bible verses while the Flask app runs
"""

import time
import threading
import json
from datetime import datetime
from app import app, db
from models import Book, Chapter, Verse
from utils.bible_importer import BibleImporter
from data.bible_books import HEBREW_BIBLE_BOOKS

class BackgroundBibleImporter:
    def __init__(self):
        self.importer = BibleImporter()
        self.is_running = False
        self.is_paused = False
        self.current_book = None
        self.current_chapter = None
        self.total_imported = 0
        self.start_time = None
        
    def start_import(self):
        """Start the background import process"""
        if self.is_running:
            print("Import already running!")
            return
            
        self.is_running = True
        self.is_paused = False
        self.start_time = datetime.now()
        
        # Start import in a separate thread
        import_thread = threading.Thread(target=self._import_worker, daemon=True)
        import_thread.start()
        
        print("🚀 Background Bible import started!")
    
    def _import_worker(self):
        """Main import worker function"""
        with app.app_context():
            try:
                # Start with more sample Genesis verses
                self._import_sample_genesis()
                
                # Then import other sample books
                self._import_sample_books()
                
                print("✅ Sample import completed!")
                
            except Exception as e:
                print(f"❌ Import error: {e}")
            finally:
                self.is_running = False
                print("📊 Background import finished.")
    
    def _import_sample_genesis(self):
        """Import extended Genesis sample"""
        print("📖 Importing extended Genesis sample...")
        
        # Extended Genesis 1 verses
        genesis_verses = [
            {
                'chapter': 1, 'verse': 6,
                'hebrew': 'וַיֹּאמֶר אֱלֹהִים יְהִי רָקִיעַ בְּתוֹךְ הַמָּיִם וִיהִי מַבְדִּיל בֵּין מַיִם לָמָיִם',
                'english': 'And God said, "Let there be a vault between the waters to separate water from water."'
            },
            {
                'chapter': 1, 'verse': 7,
                'hebrew': 'וַיַּעַשׂ אֱלֹהִים אֶת־הָרָקִיעַ וַיַּבְדֵּל בֵּין הַמַּיִם אֲשֶׁר מִתַּחַת לָרָקִיעַ וּבֵין הַמַּיִם אֲשֶׁר מֵעַל לָרָקִיעַ וַיְהִי־כֵן',
                'english': 'So God made the vault and separated the water under the vault from the water above it. And it was so.'
            },
            {
                'chapter': 1, 'verse': 8,
                'hebrew': 'וַיִּקְרָא אֱלֹהִים לָרָקִיעַ שָׁמָיִם וַיְהִי־עֶרֶב וַיְהִי־בֹקֶר יוֹם שֵׁנִי',
                'english': 'God called the vault "sky." And there was evening, and there was morning—the second day.'
            },
            {
                'chapter': 1, 'verse': 9,
                'hebrew': 'וַיֹּאמֶר אֱלֹהִים יִקָּווּ הַמַּיִם מִתַּחַת הַשָּׁמַיִם אֶל־מָקוֹם אֶחָד וְתֵרָאֶה הַיַּבָּשָׁה וַיְהִי־כֵן',
                'english': 'And God said, "Let the water under the sky be gathered to one place, and let dry ground appear." And it was so.'
            },
            {
                'chapter': 1, 'verse': 10,
                'hebrew': 'וַיִּקְרָא אֱלֹהִים לַיַּבָּשָׁה אֶרֶץ וּלְמִקְוֵה הַמַּיִם קָרָא יַמִּים וַיַּרְא אֱלֹהִים כִּי־טוֹב',
                'english': 'God called the dry ground "land," and the gathered waters he called "seas." And God saw that it was good.'
            }
        ]
        
        genesis = Book.query.filter_by(name='Genesis').first()
        if not genesis:
            print("❌ Genesis book not found!")
            return
        
        for verse_info in genesis_verses:
            if not self.is_running or self.is_paused:
                break
                
            self.current_book = 'Genesis'
            self.current_chapter = f'Chapter {verse_info["chapter"]}'
            
            # Check if verse already exists
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
                    # Create verse data
                    verse_data = self.importer._create_verse_data(
                        verse_info['chapter'],
                        verse_info['verse'],
                        verse_info['hebrew'],
                        verse_info['english']
                    )
                    
                    # Create verse
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
                    db.session.commit()
                    
                    self.total_imported += 1
                    print(f"📝 Imported Genesis {verse_info['chapter']}:{verse_info['verse']} - {verse_data['paleo_transliteration'][:50]}...")
                    
                    # Simulate processing time
                    time.sleep(0.5)
    
    def _import_sample_books(self):
        """Import sample verses from other books"""
        print("📚 Importing sample verses from other books...")
        
        # Sample verses from different books
        sample_verses = [
            {
                'book': 'Exodus', 'chapter': 3, 'verse': 14,
                'hebrew': 'וַיֹּאמֶר אֱלֹהִים אֶל־מֹשֶׁה אֶהְיֶה אֲשֶׁר אֶהְיֶה וַיֹּאמֶר כֹּה תֹאמַר לִבְנֵי יִשְׂרָאֵל אֶהְיֶה שְׁלָחַנִי אֲלֵיכֶם',
                'english': 'God said to Moses, "I AM WHO I AM. This is what you are to say to the Israelites: I AM has sent me to you."'
            },
            {
                'book': 'Leviticus', 'chapter': 19, 'verse': 18,
                'hebrew': 'לֹא־תִקֹּם וְלֹא־תִטֹּר אֶת־בְּנֵי עַמֶּךָ וְאָהַבְתָּ לְרֵעֲךָ כָּמוֹךָ אֲנִי יְהוָה',
                'english': 'Do not seek revenge or bear a grudge against anyone among your people, but love your neighbor as yourself. I am the LORD.'
            }
        ]
        
        for verse_info in sample_verses:
            if not self.is_running or self.is_paused:
                break
                
            self.current_book = verse_info['book']
            self.current_chapter = f'Chapter {verse_info["chapter"]}'
            
            book = Book.query.filter_by(name=verse_info['book']).first()
            if book:
                chapter = Chapter.query.filter_by(
                    book_id=book.id,
                    chapter_number=verse_info['chapter']
                ).first()
                
                if chapter:
                    existing_verse = Verse.query.filter_by(
                        chapter_id=chapter.id,
                        verse_number=verse_info['verse']
                    ).first()
                    
                    if not existing_verse:
                        # Create verse data
                        verse_data = self.importer._create_verse_data(
                            verse_info['chapter'],
                            verse_info['verse'],
                            verse_info['hebrew'],
                            verse_info['english']
                        )
                        
                        # Create verse
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
                        db.session.commit()
                        
                        self.total_imported += 1
                        print(f"📝 Imported {verse_info['book']} {verse_info['chapter']}:{verse_info['verse']} - {verse_data['paleo_transliteration'][:50]}...")
                        
                        # Simulate processing time
                        time.sleep(0.5)
    
    def get_status(self):
        """Get current import status"""
        return {
            'is_running': self.is_running,
            'is_paused': self.is_paused,
            'current_book': self.current_book,
            'current_chapter': self.current_chapter,
            'total_imported': self.total_imported,
            'start_time': self.start_time.isoformat() if self.start_time else None
        }

# Global importer instance
background_importer = BackgroundBibleImporter()

def start_background_import():
    """Start the background import process"""
    background_importer.start_import()

if __name__ == '__main__':
    print("🚀 Starting background Bible import...")
    start_background_import()
    
    # Keep the script running
    try:
        while background_importer.is_running:
            time.sleep(1)
        print("✅ Background import completed!")
    except KeyboardInterrupt:
        print("\n⏹️ Import stopped by user")
        background_importer.is_running = False