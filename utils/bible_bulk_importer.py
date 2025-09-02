"""
Comprehensive Hebrew Bible Bulk Import System
Supports multiple data sources with rate limiting, progress tracking, and resumability
"""

import json
import requests
import time
import os
import threading
import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import quote

from models import db, Book, Chapter, Verse
from utils.bible_importer import BibleImporter
from utils.local_hebrew_source import LocalHebrewBibleSource, create_expanded_local_source
from data.bible_books import HEBREW_BIBLE_BOOKS

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bible_import.log'),
        logging.StreamHandler()
    ]
)

class ImportProgress:
    """Track import progress and provide resumability"""
    
    def __init__(self, progress_file='import_progress.json'):
        self.progress_file = progress_file
        self.progress_data = self._load_progress()
        self._lock = threading.Lock()
    
    def _load_progress(self) -> Dict:
        """Load existing progress from file"""
        if os.path.exists(self.progress_file):
            try:
                with open(self.progress_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logging.warning(f"Could not load progress file: {e}")
        
        return {
            'started_at': None,
            'last_updated': None,
            'books_completed': [],
            'books_in_progress': {},
            'total_books': len(HEBREW_BIBLE_BOOKS),
            'total_verses_imported': 0,
            'errors': [],
            'status': 'not_started'
        }
    
    def _save_progress(self):
        """Save current progress to file"""
        try:
            self.progress_data['last_updated'] = datetime.now().isoformat()
            with open(self.progress_file, 'w') as f:
                json.dump(self.progress_data, f, indent=2)
        except Exception as e:
            logging.error(f"Could not save progress: {e}")
    
    def start_import(self):
        """Mark import as started"""
        with self._lock:
            self.progress_data['started_at'] = datetime.now().isoformat()
            self.progress_data['status'] = 'in_progress'
            self._save_progress()
    
    def complete_book(self, book_name: str, verses_imported: int):
        """Mark a book as completed"""
        with self._lock:
            if book_name not in self.progress_data['books_completed']:
                self.progress_data['books_completed'].append(book_name)
            
            if book_name in self.progress_data['books_in_progress']:
                del self.progress_data['books_in_progress'][book_name]
            
            self.progress_data['total_verses_imported'] += verses_imported
            self._save_progress()
    
    def start_book(self, book_name: str):
        """Mark a book as in progress"""
        with self._lock:
            self.progress_data['books_in_progress'][book_name] = {
                'started_at': datetime.now().isoformat(),
                'verses_imported': 0
            }
            self._save_progress()
    
    def add_error(self, error_info: Dict):
        """Add an error to the progress log"""
        with self._lock:
            self.progress_data['errors'].append({
                **error_info,
                'timestamp': datetime.now().isoformat()
            })
            self._save_progress()
    
    def complete_import(self):
        """Mark import as completed"""
        with self._lock:
            self.progress_data['status'] = 'completed'
            self.progress_data['completed_at'] = datetime.now().isoformat()
            self._save_progress()
    
    def get_remaining_books(self) -> List[str]:
        """Get list of books that haven't been completed"""
        completed = set(self.progress_data['books_completed'])
        all_books = {book['name'] for book in HEBREW_BIBLE_BOOKS}
        return list(all_books - completed)
    
    def get_status(self) -> Dict:
        """Get current import status"""
        with self._lock:
            remaining_books = self.get_remaining_books()
            return {
                **self.progress_data,
                'books_remaining': len(remaining_books),
                'progress_percentage': (len(self.progress_data['books_completed']) / self.progress_data['total_books']) * 100
            }

class HebrewBibleDataSource:
    """Base class for Hebrew Bible data sources"""
    
    def __init__(self, name: str, rate_limit_delay: float = 1.0):
        self.name = name
        self.rate_limit_delay = rate_limit_delay
        self.last_request_time = 0
    
    def _rate_limit(self):
        """Implement rate limiting between requests"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.rate_limit_delay:
            time.sleep(self.rate_limit_delay - time_since_last)
        self.last_request_time = time.time()
    
    def fetch_book_data(self, book_name: str, sefaria_name: str = None) -> List[Dict]:
        """Fetch book data - to be implemented by subclasses"""
        raise NotImplementedError

class SefariaDataSource(HebrewBibleDataSource):
    """Sefaria API data source"""
    
    def __init__(self):
        super().__init__("Sefaria", rate_limit_delay=1.5)  # Be respectful to Sefaria's servers
        self.base_url = "https://www.sefaria.org/api"
    
    def fetch_book_data(self, book_name: str, sefaria_name: str = None) -> List[Dict]:
        """Fetch Hebrew Bible data from Sefaria API"""
        if not sefaria_name:
            sefaria_name = book_name
        
        logging.info(f"Fetching {book_name} from Sefaria...")
        self._rate_limit()
        
        try:
            # Try direct book fetch first
            url = f"{self.base_url}/texts/{quote(sefaria_name)}"
            response = requests.get(url, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                return self._process_sefaria_response(data, book_name)
            elif response.status_code == 404:
                # Try alternative naming
                alternative_names = self._get_alternative_names(sefaria_name)
                for alt_name in alternative_names:
                    self._rate_limit()
                    alt_url = f"{self.base_url}/texts/{quote(alt_name)}"
                    alt_response = requests.get(alt_url, timeout=30)
                    if alt_response.status_code == 200:
                        data = alt_response.json()
                        return self._process_sefaria_response(data, book_name)
            
            logging.warning(f"Could not fetch {book_name} from Sefaria: {response.status_code}")
            return []
            
        except Exception as e:
            logging.error(f"Error fetching {book_name} from Sefaria: {e}")
            return []
    
    def _get_alternative_names(self, book_name: str) -> List[str]:
        """Get alternative names for books that might have different naming in Sefaria"""
        alternatives = {
            'Samuel I': ['I Samuel', '1 Samuel', 'Samuel 1'],
            'Samuel II': ['II Samuel', '2 Samuel', 'Samuel 2'],
            'Kings I': ['I Kings', '1 Kings', 'Kings 1'],
            'Kings II': ['II Kings', '2 Kings', 'Kings 2'],
            'Chronicles I': ['I Chronicles', '1 Chronicles', 'Chronicles 1'],
            'Chronicles II': ['II Chronicles', '2 Chronicles', 'Chronicles 2'],
            'Song of Songs': ['Song of Solomon', 'Canticles', 'Shir HaShirim']
        }
        return alternatives.get(book_name, [])
    
    def _process_sefaria_response(self, data: Dict, book_name: str) -> List[Dict]:
        """Process Sefaria API response into verse data"""
        verses = []
        
        try:
            hebrew_text = data.get('he', [])
            english_text = data.get('text', [])
            
            # Handle single chapter books
            if isinstance(hebrew_text[0], str):
                hebrew_text = [hebrew_text]
                english_text = [english_text] if english_text else [[]]
            
            for chapter_num, chapter_hebrew in enumerate(hebrew_text, 1):
                chapter_english = english_text[chapter_num - 1] if chapter_num - 1 < len(english_text) else []
                
                if isinstance(chapter_hebrew, list):
                    for verse_num, verse_hebrew in enumerate(chapter_hebrew, 1):
                        verse_english = ""
                        if isinstance(chapter_english, list) and verse_num - 1 < len(chapter_english):
                            verse_english = chapter_english[verse_num - 1]
                        
                        verses.append({
                            'chapter': chapter_num,
                            'verse': verse_num,
                            'hebrew': verse_hebrew,
                            'english': verse_english
                        })
        
        except Exception as e:
            logging.error(f"Error processing Sefaria data for {book_name}: {e}")
        
        return verses

class BulkHebrewBibleImporter:
    """Main bulk import system for Hebrew Bible"""
    
    def __init__(self):
        self.bible_importer = BibleImporter()
        self.progress = ImportProgress()
        self.data_sources = [
            SefariaDataSource(),
            create_expanded_local_source(),  # Fallback to local data
        ]
        self._stop_import = False
    
    def import_complete_bible(self, resume: bool = True, max_workers: int = 1) -> bool:
        """
        Import the complete Hebrew Bible
        
        Args:
            resume: Whether to resume from previous progress
            max_workers: Number of concurrent workers (default 1 for politeness to APIs)
        """
        if not resume:
            self.progress = ImportProgress()  # Reset progress
        
        self.progress.start_import()
        logging.info("Starting complete Hebrew Bible import...")
        
        try:
            # Get books to import (remaining if resuming)
            if resume:
                books_to_import = self._get_books_to_import_resume()
            else:
                books_to_import = self._get_books_to_import_ordered()
            
            if not books_to_import:
                logging.info("All books already imported!")
                return True
            
            logging.info(f"Importing {len(books_to_import)} books...")
            
            # Import books in order (Torah first, then Prophets, then Writings)
            success_count = 0
            
            if max_workers == 1:
                # Sequential import for better API politeness
                for book_info in books_to_import:
                    if self._stop_import:
                        break
                    
                    success = self._import_single_book(book_info)
                    if success:
                        success_count += 1
                    
                    # Small delay between books
                    time.sleep(2)
            else:
                # Parallel import (use cautiously)
                with ThreadPoolExecutor(max_workers=max_workers) as executor:
                    future_to_book = {
                        executor.submit(self._import_single_book, book_info): book_info 
                        for book_info in books_to_import
                    }
                    
                    for future in as_completed(future_to_book):
                        if self._stop_import:
                            break
                        
                        book_info = future_to_book[future]
                        try:
                            success = future.result()
                            if success:
                                success_count += 1
                        except Exception as e:
                            logging.error(f"Error importing {book_info['name']}: {e}")
            
            if not self._stop_import:
                self.progress.complete_import()
                logging.info(f"Import completed! Successfully imported {success_count}/{len(books_to_import)} books")
            
            return success_count == len(books_to_import)
            
        except Exception as e:
            logging.error(f"Critical error during import: {e}")
            self.progress.add_error({
                'type': 'critical_error',
                'message': str(e),
                'book': 'general'
            })
            return False
    
    def _get_books_to_import_resume(self) -> List[Dict]:
        """Get books to import when resuming"""
        remaining_books = set(self.progress.get_remaining_books())
        return [book for book in HEBREW_BIBLE_BOOKS if book['name'] in remaining_books]
    
    def _get_books_to_import_ordered(self) -> List[Dict]:
        """Get all books in proper import order (Torah, Prophets, Writings)"""
        return sorted(HEBREW_BIBLE_BOOKS, key=lambda x: x['order'])
    
    def _import_single_book(self, book_info: Dict) -> bool:
        """Import a single book"""
        book_name = book_info['name']
        
        try:
            self.progress.start_book(book_name)
            logging.info(f"Starting import of {book_name}...")
            
            # Try each data source until we get data
            verse_data = []
            for source in self.data_sources:
                try:
                    verse_data = source.fetch_book_data(book_name, book_name)
                    if verse_data:
                        logging.info(f"Successfully fetched {len(verse_data)} verses from {source.name}")
                        break
                except Exception as e:
                    logging.warning(f"Failed to fetch from {source.name}: {e}")
                    continue
            
            if not verse_data:
                logging.error(f"No data sources available for {book_name}")
                self.progress.add_error({
                    'type': 'no_data',
                    'message': 'No data sources returned data',
                    'book': book_name
                })
                return False
            
            # Import verses to database
            imported_count = self._import_verses_to_db(book_name, verse_data)
            
            if imported_count > 0:
                self.progress.complete_book(book_name, imported_count)
                logging.info(f"Successfully imported {book_name} with {imported_count} verses")
                return True
            else:
                logging.warning(f"No verses imported for {book_name}")
                return False
                
        except Exception as e:
            logging.error(f"Error importing {book_name}: {e}")
            self.progress.add_error({
                'type': 'import_error',
                'message': str(e),
                'book': book_name
            })
            return False
    
    def _import_verses_to_db(self, book_name: str, verse_data: List[Dict]) -> int:
        """Import verse data to database"""
        from app import app
        
        with app.app_context():
            # Get the book
            book = Book.query.filter_by(name=book_name).first()
            if not book:
                logging.error(f"Book {book_name} not found in database")
                return 0
            
            imported_count = 0
            batch_size = 100
            batch_verses = []
            
            for verse_info in verse_data:
                try:
                    # Process verse data through BibleImporter
                    processed_verse = self.bible_importer._create_verse_data(
                        verse_info['chapter'],
                        verse_info['verse'],
                        verse_info['hebrew'],
                        verse_info.get('english', '')
                    )
                    
                    # Get chapter
                    chapter = Chapter.query.filter_by(
                        book_id=book.id,
                        chapter_number=processed_verse['chapter']
                    ).first()
                    
                    if not chapter:
                        logging.warning(f"Chapter {processed_verse['chapter']} not found for {book_name}")
                        continue
                    
                    # Check if verse already exists
                    existing_verse = Verse.query.filter_by(
                        chapter_id=chapter.id,
                        verse_number=processed_verse['verse']
                    ).first()
                    
                    if existing_verse:
                        logging.debug(f"Verse {book_name} {processed_verse['chapter']}:{processed_verse['verse']} already exists")
                        continue
                    
                    # Create new verse
                    verse = Verse(
                        chapter_id=chapter.id,
                        verse_number=processed_verse['verse'],
                        hebrew_text=processed_verse['hebrew_text'],
                        hebrew_consonantal=processed_verse['hebrew_consonantal'],
                        paleo_text=processed_verse['paleo_text'],
                        paleo_transliteration=processed_verse['paleo_transliteration'],
                        modern_transliteration=processed_verse['modern_transliteration'],
                        english_translation=processed_verse['english_translation'],
                        literal_translation=processed_verse['literal_translation'],
                        strong_numbers=processed_verse.get('strong_numbers', ''),
                        morphology=processed_verse.get('morphology', ''),
                        notes=processed_verse.get('notes', '')
                    )
                    
                    batch_verses.append(verse)
                    
                    # Commit in batches
                    if len(batch_verses) >= batch_size:
                        db.session.add_all(batch_verses)
                        db.session.commit()
                        imported_count += len(batch_verses)
                        batch_verses = []
                        logging.debug(f"Imported {imported_count} verses so far...")
                
                except Exception as e:
                    logging.error(f"Error processing verse {verse_info}: {e}")
                    continue
            
            # Commit remaining verses
            if batch_verses:
                db.session.add_all(batch_verses)
                db.session.commit()
                imported_count += len(batch_verses)
            
            return imported_count
    
    def stop_import(self):
        """Stop the import process"""
        self._stop_import = True
        logging.info("Import stop requested...")
    
    def get_progress(self) -> Dict:
        """Get current import progress"""
        return self.progress.get_status()
    
    def reset_progress(self):
        """Reset import progress"""
        self.progress = ImportProgress()
        if os.path.exists('import_progress.json'):
            os.remove('import_progress.json')
        logging.info("Import progress reset")

# Background import runner
class BackgroundImportRunner:
    """Run Hebrew Bible import in background"""
    
    def __init__(self):
        self.importer = BulkHebrewBibleImporter()
        self.import_thread = None
        self.is_running = False
    
    def start_background_import(self, resume: bool = True) -> bool:
        """Start import in background thread"""
        if self.is_running:
            logging.warning("Import already running")
            return False
        
        def run_import():
            try:
                self.is_running = True
                logging.info("Starting background Hebrew Bible import...")
                success = self.importer.import_complete_bible(resume=resume)
                logging.info(f"Background import completed with success: {success}")
            except Exception as e:
                logging.error(f"Background import failed: {e}")
            finally:
                self.is_running = False
        
        self.import_thread = threading.Thread(target=run_import, daemon=True)
        self.import_thread.start()
        return True
    
    def stop_background_import(self):
        """Stop background import"""
        if self.is_running:
            self.importer.stop_import()
            logging.info("Stopping background import...")
    
    def get_status(self) -> Dict:
        """Get import status"""
        return {
            'is_running': self.is_running,
            'progress': self.importer.get_progress()
        }

if __name__ == "__main__":
    # Test the import system
    import argparse
    
    parser = argparse.ArgumentParser(description='Hebrew Bible Bulk Importer')
    parser.add_argument('--resume', action='store_true', help='Resume previous import')
    parser.add_argument('--reset', action='store_true', help='Reset progress and start fresh')
    parser.add_argument('--workers', type=int, default=1, help='Number of concurrent workers')
    
    args = parser.parse_args()
    
    importer = BulkHebrewBibleImporter()
    
    if args.reset:
        importer.reset_progress()
    
    success = importer.import_complete_bible(resume=args.resume, max_workers=args.workers)
    print(f"Import completed with success: {success}")