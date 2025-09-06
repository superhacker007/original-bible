from flask import Flask, jsonify, request, render_template, send_from_directory, session, redirect, url_for
from flask_cors import CORS
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
import os
import uuid

# Import models and db
from models import db, Book, Chapter, Verse, PaleoLetter, GodFact, Word
from utils.hebrew_converter import hebrew_to_paleo, get_pronunciation_guide, analyze_word_meaning
from utils.ancient_hebrew_tts import create_tts_text, get_word_pronunciation, hebrew_to_ancient_pronunciation

app = Flask(__name__)
app.config['SECRET_KEY'] = 'paleo-hebrew-bible-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///paleo_bible.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# File upload configuration
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'webm', 'mov', 'avi'}

# Initialize extensions
db.init_app(app)
CORS(app)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access the admin dashboard.'

# Simple User class for admin authentication
class User(UserMixin):
    def __init__(self, id):
        self.id = id

# Admin credentials (in production, store these in database with proper hashing)
ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD_HASH = generate_password_hash('paleo_admin_2025', method='pbkdf2:sha256')

@login_manager.user_loader
def load_user(user_id):
    if user_id == 'admin':
        return User('admin')
    return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Admin login page"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username == ADMIN_USERNAME and check_password_hash(ADMIN_PASSWORD_HASH, password):
            user = User('admin')
            login_user(user)
            return redirect(url_for('index'))
        else:
            return jsonify({'error': 'Invalid credentials'}), 401
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    """Admin logout"""
    logout_user()
    return redirect(url_for('index'))

@app.route('/import')
def import_progress():
    return render_template('import_progress.html')

@app.route('/api/test')
def test():
    return jsonify({'message': 'Paleo Hebrew Bible API is running!'})

@app.route('/api/books')
def get_books():
    """Get all books in the database"""
    books = Book.query.order_by(Book.order).all()
    return jsonify([book.to_dict() for book in books])

@app.route('/api/books/<int:book_id>')
def get_book(book_id):
    """Get a specific book with its chapters"""
    book = Book.query.get_or_404(book_id)
    book_data = book.to_dict()
    book_data['chapters'] = [chapter.to_dict() for chapter in book.chapters]
    return jsonify(book_data)

@app.route('/api/books/<int:book_id>/chapters/<int:chapter_number>')
def get_chapter(book_id, chapter_number):
    """Get a specific chapter with all its verses"""
    book = Book.query.get_or_404(book_id)
    chapter = Chapter.query.filter_by(book_id=book_id, chapter_number=chapter_number).first_or_404()
    
    chapter_data = chapter.to_dict()
    chapter_data['book'] = book.to_dict()
    chapter_data['verses'] = [verse.to_dict() for verse in chapter.verses]
    
    return jsonify(chapter_data)

@app.route('/api/books/<int:book_id>/chapters/<int:chapter_number>/navigation')
def get_chapter_navigation(book_id, chapter_number):
    """Get navigation info for a chapter (previous/next chapter across books)"""
    from models import Book, Chapter
    
    # Get current book and chapter
    current_book = Book.query.get_or_404(book_id)
    current_chapter = Chapter.query.filter_by(
        book_id=book_id, 
        chapter_number=chapter_number
    ).first_or_404()
    
    navigation = {
        'current': {
            'book_id': current_book.id,
            'book_name': current_book.name,
            'chapter_number': chapter_number
        },
        'previous': None,
        'next': None
    }
    
    # Find previous chapter
    if chapter_number > 1:
        # Previous chapter in same book
        navigation['previous'] = {
            'book_id': current_book.id,
            'book_name': current_book.name,
            'chapter_number': chapter_number - 1
        }
    else:
        # Last chapter of previous book
        prev_book = Book.query.filter(Book.order < current_book.order).order_by(Book.order.desc()).first()
        if prev_book:
            last_chapter = Chapter.query.filter_by(book_id=prev_book.id).order_by(Chapter.chapter_number.desc()).first()
            if last_chapter:
                navigation['previous'] = {
                    'book_id': prev_book.id,
                    'book_name': prev_book.name,
                    'chapter_number': last_chapter.chapter_number
                }
    
    # Find next chapter
    next_chapter_in_book = Chapter.query.filter_by(
        book_id=book_id, 
        chapter_number=chapter_number + 1
    ).first()
    
    if next_chapter_in_book:
        # Next chapter in same book
        navigation['next'] = {
            'book_id': current_book.id,
            'book_name': current_book.name,
            'chapter_number': chapter_number + 1
        }
    else:
        # First chapter of next book
        next_book = Book.query.filter(Book.order > current_book.order).order_by(Book.order.asc()).first()
        if next_book:
            first_chapter = Chapter.query.filter_by(book_id=next_book.id, chapter_number=1).first()
            if first_chapter:
                navigation['next'] = {
                    'book_id': next_book.id,
                    'book_name': next_book.name,
                    'chapter_number': 1
                }
    
    return jsonify(navigation)

@app.route('/api/alphabet')
def get_alphabet():
    """Get the complete Paleo Hebrew alphabet"""
    letters = PaleoLetter.query.order_by(PaleoLetter.order).all()
    return jsonify([letter.to_dict() for letter in letters])

@app.route('/api/alphabet/<string:letter>')
def get_letter(letter):
    """Get information about a specific letter"""
    paleo_letter = PaleoLetter.query.filter_by(letter=letter).first_or_404()
    return jsonify(paleo_letter.to_dict())

@app.route('/api/search')
def search_verses():
    """Search for verses containing specific text"""
    query = request.args.get('q', '').strip()
    search_type = request.args.get('type', 'all')  # 'hebrew', 'paleo', 'english', 'all'
    
    if not query:
        return jsonify({'error': 'Search query is required'}), 400
    
    verses = []
    
    if search_type in ['hebrew', 'all']:
        hebrew_results = Verse.query.filter(Verse.hebrew_text.contains(query)).all()
        verses.extend(hebrew_results)
    
    if search_type in ['paleo', 'all']:
        paleo_results = Verse.query.filter(Verse.paleo_text.contains(query)).all()
        verses.extend([v for v in paleo_results if v not in verses])
    
    if search_type in ['english', 'all']:
        english_results = Verse.query.filter(Verse.english_translation.contains(query)).all()
        verses.extend([v for v in english_results if v not in verses])
    
    # Add book and chapter info to each verse
    results = []
    for verse in verses:
        verse_data = verse.to_dict()
        chapter = Chapter.query.get(verse.chapter_id)
        book = Book.query.get(chapter.book_id)
        verse_data['book'] = book.to_dict()
        verse_data['chapter'] = chapter.to_dict()
        results.append(verse_data)
    
    return jsonify({
        'query': query,
        'search_type': search_type,
        'results': results,
        'count': len(results)
    })

@app.route('/api/convert', methods=['POST'])
def convert_text():
    """Convert Hebrew text to Paleo Hebrew"""
    data = request.json
    hebrew_text = data.get('text', '')
    
    if not hebrew_text:
        return jsonify({'error': 'Hebrew text is required'}), 400
    
    paleo_text = hebrew_to_paleo(hebrew_text)
    pronunciation = get_pronunciation_guide(hebrew_text)
    
    return jsonify({
        'hebrew': hebrew_text,
        'paleo': paleo_text,
        'pronunciation': pronunciation
    })

@app.route('/api/analyze', methods=['POST'])
def analyze_word():
    """Analyze a Paleo Hebrew word based on letter meanings"""
    data = request.json
    paleo_word = data.get('word', '')
    
    if not paleo_word:
        return jsonify({'error': 'Paleo Hebrew word is required'}), 400
    
    analysis = analyze_word_meaning(paleo_word)
    return jsonify(analysis)

@app.route('/api/pronunciation/<string:word>')
def get_pronunciation(word):
    """Get pronunciation guide for a Hebrew word"""
    pronunciation = get_pronunciation_guide(word)
    return jsonify({
        'word': word,
        'pronunciation': pronunciation
    })



@app.route('/api/tts/verse', methods=['POST'])
def get_verse_tts():
    """Get TTS pronunciation for a verse using Paleo transliteration"""
    data = request.json
    hebrew_text = data.get('hebrew', '')
    paleo_text = data.get('paleo', '')
    paleo_transliteration = data.get('paleo_transliteration', '')
    verse_id = data.get('verse_id', '')
    
    # Priority: Use paleo_transliteration first (like "barashyt bara"), then fallback
    if paleo_transliteration:
        tts_text = paleo_transliteration
        pronunciation_source = 'paleo_transliteration'
    elif paleo_text:
        tts_text = create_tts_text(paleo_text, include_vowels=True)
        pronunciation_source = 'paleo_text'
    elif hebrew_text:
        tts_text = create_tts_text(hebrew_text, include_vowels=True)
        pronunciation_source = 'hebrew_text'
    else:
        return jsonify({'error': 'No text provided'}), 400
    
    # Clean up the TTS text for better pronunciation
    tts_text_cleaned = tts_text.replace('-', ' ')  # Replace hyphens with spaces
    tts_text_cleaned = tts_text_cleaned.replace('_', ' ')  # Replace underscores with spaces
    
    return jsonify({
        'verse_id': verse_id,
        'tts_text': tts_text_cleaned,
        'original_tts_text': tts_text,
        'pronunciation_source': pronunciation_source,
        'instructions': f'Using {pronunciation_source} for most accurate ancient Hebrew pronunciation'
    })

@app.route('/api/tts/letter', methods=['POST'])
def get_letter_tts():
    """Get TTS pronunciation for a Paleo Hebrew letter"""
    data = request.json
    letter = data.get('letter', '')
    paleo_symbol = data.get('paleo_symbol', '')
    letter_name = data.get('name', '')
    
    if not (letter or paleo_symbol):
        return jsonify({'error': 'Letter or paleo symbol required'}), 400
    
    # Get the letter pronunciation
    if paleo_symbol:
        pronunciation = hebrew_to_ancient_pronunciation(paleo_symbol)
    else:
        pronunciation = hebrew_to_ancient_pronunciation(letter)
    
    # Create a phonetic spelling of the letter name for TTS
    letter_name_tts = letter_name.lower() if letter_name else pronunciation
    
    return jsonify({
        'letter': letter,
        'paleo_symbol': paleo_symbol,
        'name': letter_name,
        'sound_pronunciation': pronunciation,
        'name_pronunciation': letter_name_tts,
        'tts_instructions': f'Pronounce the letter sound as "{pronunciation}" and the name as "{letter_name_tts}"'
    })

@app.route('/api/tts/word', methods=['POST'])
def get_word_tts():
    """Get TTS pronunciation for a specific Hebrew word"""
    data = request.json
    word = data.get('word', '')
    
    if not word:
        return jsonify({'error': 'Word is required'}), 400
    
    # Get word-specific pronunciation
    pronunciation = get_word_pronunciation(word)
    ancient_sound = hebrew_to_ancient_pronunciation(word)
    
    return jsonify({
        'word': word,
        'pronunciation': pronunciation,
        'ancient_sound': ancient_sound,
        'tts_text': pronunciation
    })

# Hebrew Bible Import endpoints
from utils.bible_bulk_importer import BackgroundImportRunner

# Global import runner
background_runner = BackgroundImportRunner()

@app.route('/api/import/start', methods=['POST'])
def start_bible_import():
    """Start Hebrew Bible import process"""
    data = request.json or {}
    resume = data.get('resume', True)
    
    if background_runner.is_running:
        return jsonify({
            'error': 'Import already running',
            'status': background_runner.get_status()
        }), 400
    
    success = background_runner.start_background_import(resume=resume)
    
    if success:
        return jsonify({
            'message': 'Hebrew Bible import started',
            'resume': resume,
            'status': background_runner.get_status()
        })
    else:
        return jsonify({
            'error': 'Failed to start import'
        }), 500

@app.route('/api/import/stop', methods=['POST'])
def stop_bible_import():
    """Stop Hebrew Bible import process"""
    if not background_runner.is_running:
        return jsonify({
            'error': 'No import currently running'
        }), 400
    
    background_runner.stop_background_import()
    
    return jsonify({
        'message': 'Import stop requested',
        'status': background_runner.get_status()
    })

@app.route('/api/import/status')
def get_import_status():
    """Get current import status and progress"""
    status = background_runner.get_status()
    
    # Add database statistics
    book_count = Book.query.count()
    verse_count = Verse.query.count()
    
    status['database'] = {
        'books': book_count,
        'verses': verse_count,
        'estimated_total_verses': 23000  # Approximate total verses in Hebrew Bible
    }
    
    return jsonify(status)

@app.route('/api/import/reset', methods=['POST'])
def reset_import_progress():
    """Reset import progress"""
    if background_runner.is_running:
        return jsonify({
            'error': 'Cannot reset while import is running'
        }), 400
    
    background_runner.importer.reset_progress()
    
    return jsonify({
        'message': 'Import progress reset',
        'status': background_runner.get_status()
    })

@app.route('/api/stats')
def get_bible_stats():
    """Get comprehensive Bible statistics"""
    books = Book.query.all()
    stats = {
        'total_books': len(books),
        'books_with_verses': 0,
        'total_verses': 0,
        'testament_stats': {},
        'books': []
    }
    
    testament_counts = {}
    
    for book in books:
        verse_count = db.session.query(Verse).join(Chapter).filter(Chapter.book_id == book.id).count()
        
        book_info = {
            'name': book.name,
            'hebrew_name': book.hebrew_name,
            'testament': book.testament,
            'order': book.order,
            'chapters': len(book.chapters),
            'verses': verse_count
        }
        
        stats['books'].append(book_info)
        stats['total_verses'] += verse_count
        
        if verse_count > 0:
            stats['books_with_verses'] += 1
        
        # Testament statistics
        if book.testament not in testament_counts:
            testament_counts[book.testament] = {'books': 0, 'verses': 0}
        
        testament_counts[book.testament]['books'] += 1
        testament_counts[book.testament]['verses'] += verse_count
    
    stats['testament_stats'] = testament_counts
    
    return jsonify(stats)

@app.route('/api/strongs')
def get_strongs_concordance():
    """Get Strong's Concordance data with Hebrew/Greek words and their meanings"""
    from models import StrongsHebrew, StrongsGreek, PaleoDictionary
    
    # Get search parameter if provided
    search_term = request.args.get('search', '').lower()
    
    # Query Hebrew entries
    hebrew_query = StrongsHebrew.query
    if search_term:
        hebrew_query = hebrew_query.filter(
            db.or_(
                StrongsHebrew.short_definition.ilike(f'%{search_term}%'),
                StrongsHebrew.long_definition.ilike(f'%{search_term}%'),
                StrongsHebrew.transliteration.ilike(f'%{search_term}%'),
                StrongsHebrew.hebrew_word.ilike(f'%{search_term}%'),
                StrongsHebrew.strong_number.ilike(f'%{search_term}%')
            )
        )
    
    # Query Greek entries
    greek_query = StrongsGreek.query
    if search_term:
        greek_query = greek_query.filter(
            db.or_(
                StrongsGreek.short_definition.ilike(f'%{search_term}%'),
                StrongsGreek.long_definition.ilike(f'%{search_term}%'),
                StrongsGreek.transliteration.ilike(f'%{search_term}%'),
                StrongsGreek.greek_word.ilike(f'%{search_term}%'),
                StrongsGreek.strong_number.ilike(f'%{search_term}%')
            )
        )
    
    # Get the results and limit if needed
    hebrew_entries = hebrew_query.order_by(StrongsHebrew.strong_number).limit(100).all()
    greek_entries = greek_query.order_by(StrongsGreek.strong_number).limit(100).all()
    
    # Format Hebrew entries with root meanings
    hebrew_data = {}
    for entry in hebrew_entries:
        entry_dict = entry.to_dict()
        
        # Look up corresponding Paleo Dictionary entry for root meaning
        paleo_entry = PaleoDictionary.query.filter_by(strong_number=entry.strong_number).first()
        if paleo_entry:
            entry_dict['root_meaning'] = {
                'paleo_word': paleo_entry.paleo_word,
                'pictographic_analysis': paleo_entry.pictographic_analysis,
                'original_concept': paleo_entry.original_concept,
                'formation_explanation': paleo_entry.formation_explanation
            }
        else:
            entry_dict['root_meaning'] = None
            
        hebrew_data[entry.strong_number] = entry_dict
    
    # Format the response
    strongs_data = {
        'hebrew': hebrew_data,
        'greek': {entry.strong_number: entry.to_dict() for entry in greek_entries}
    }
    
    return jsonify(strongs_data)

@app.route('/api/strongs/<string:strong_number>')
def get_strong_number(strong_number):
    """Get detailed information for a specific Strong's number"""
    from models import StrongsHebrew, StrongsGreek, PaleoDictionary
    
    strong_number = strong_number.upper()
    
    # Try Hebrew first
    if strong_number.startswith('H'):
        entry = StrongsHebrew.query.filter_by(strong_number=strong_number).first()
        if entry:
            entry_dict = entry.to_dict()
            
            # Look up corresponding Paleo Dictionary entry for root meaning
            paleo_entry = PaleoDictionary.query.filter_by(strong_number=strong_number).first()
            if paleo_entry:
                entry_dict['root_meaning'] = {
                    'paleo_word': paleo_entry.paleo_word,
                    'pictographic_analysis': paleo_entry.pictographic_analysis,
                    'original_concept': paleo_entry.original_concept,
                    'formation_explanation': paleo_entry.formation_explanation
                }
            else:
                entry_dict['root_meaning'] = None
                
            return jsonify(entry_dict)
    
    # Try Greek
    elif strong_number.startswith('G'):
        entry = StrongsGreek.query.filter_by(strong_number=strong_number).first()
        if entry:
            return jsonify(entry.to_dict())
    
    # If not found
    return jsonify({'error': f'Strong\'s number {strong_number} not found'}), 404

@app.route('/api/paleo-dictionary')
def get_paleo_dictionary():
    """Get Paleo Hebrew Dictionary entries with pictographic analysis"""
    from models import PaleoDictionary
    
    # Get search parameter if provided
    search_term = request.args.get('search', '').lower()
    
    # Query entries
    query = PaleoDictionary.query
    if search_term:
        query = query.filter(
            db.or_(
                PaleoDictionary.hebrew_word.ilike(f'%{search_term}%'),
                PaleoDictionary.strong_number.ilike(f'%{search_term}%'),
                PaleoDictionary.transliteration.ilike(f'%{search_term}%'),
                PaleoDictionary.english_meaning.ilike(f'%{search_term}%'),
                PaleoDictionary.pictographic_analysis.ilike(f'%{search_term}%'),
                PaleoDictionary.original_concept.ilike(f'%{search_term}%')
            )
        )
    
    # Get results ordered by transliteration, increased limit for better matching
    entries = query.order_by(PaleoDictionary.transliteration).limit(200).all()
    
    # Format response
    dictionary_data = {
        'entries': [entry.to_dict() for entry in entries],
        'count': len(entries),
        'search_term': search_term if search_term else None
    }
    
    return jsonify(dictionary_data)

@app.route('/api/paleo-dictionary/<string:word>')
def get_paleo_word_analysis(word):
    """Get detailed pictographic analysis for a specific Hebrew word"""
    from models import PaleoDictionary
    
    # Try to find by Hebrew word or transliteration
    entry = PaleoDictionary.query.filter(
        db.or_(
            PaleoDictionary.hebrew_word == word,
            PaleoDictionary.transliteration.ilike(word),
            PaleoDictionary.paleo_word == word
        )
    ).first()
    
    if entry:
        return jsonify(entry.to_dict())
    else:
        return jsonify({'error': f'Word "{word}" not found in Paleo Dictionary'}), 404

@app.route('/api/paleo-dictionary/analyze/<string:hebrew_word>')  
def analyze_hebrew_word(hebrew_word):
    """Analyze any Hebrew word by breaking it down into pictographic components"""
    from models import PaleoLetter, StrongsHebrew
    from utils.hebrew_converter import hebrew_to_paleo, remove_nikud
    
    # Clean the Hebrew word
    clean_hebrew = remove_nikud(hebrew_word)
    paleo_word = hebrew_to_paleo(clean_hebrew)
    
    # Try to find English definition from Strong's Hebrew
    english_definition = None
    long_definition = None
    transliteration = None
    
    # Look for exact match first
    strongs_entry = StrongsHebrew.query.filter_by(hebrew_word=clean_hebrew).first()
    if not strongs_entry:
        # Try matching with original word (with nikud)
        strongs_entry = StrongsHebrew.query.filter_by(hebrew_word=hebrew_word).first()
    if not strongs_entry:
        # Search through all Strong's entries for exact match after removing nikud
        all_strongs = StrongsHebrew.query.all()
        for entry in all_strongs:
            if remove_nikud(entry.hebrew_word) == clean_hebrew:
                strongs_entry = entry
                break
    if not strongs_entry:
        # Try removing definite article 'ה' prefix if present
        if clean_hebrew.startswith('ה') and len(clean_hebrew) > 1:
            root_word = clean_hebrew[1:]  # Remove the ה prefix
            # Try direct match first
            strongs_entry = StrongsHebrew.query.filter_by(hebrew_word=root_word).first()
            if not strongs_entry:
                # Search through all Strong's entries, applying remove_nikud to find match
                all_strongs = StrongsHebrew.query.all()
                for entry in all_strongs:
                    if remove_nikud(entry.hebrew_word) == root_word:
                        strongs_entry = entry
                        break
    if not strongs_entry:
        # Try removing common prefixes and suffixes
        prefixes = ['ו', 'כ', 'ל', 'מ', 'ב']  # and, like, to, from, in
        suffixes = ['ים', 'ות', 'יה', 'נה', 'יו']  # plural and other endings
        
        test_word = clean_hebrew
        for prefix in prefixes:
            if test_word.startswith(prefix) and len(test_word) > 1:
                test_word = test_word[1:]
                strongs_entry = StrongsHebrew.query.filter_by(hebrew_word=test_word).first()
                if strongs_entry:
                    break
        
        if not strongs_entry:
            for suffix in suffixes:
                if test_word.endswith(suffix) and len(test_word) > len(suffix):
                    test_word = test_word[:-len(suffix)]
                    strongs_entry = StrongsHebrew.query.filter_by(hebrew_word=test_word).first()
                    if strongs_entry:
                        break
    if not strongs_entry:
        # Try partial matches for compound words
        strongs_entries = StrongsHebrew.query.filter(
            db.or_(
                StrongsHebrew.hebrew_word.like(f'%{clean_hebrew}%'),
                StrongsHebrew.hebrew_word.like(f'{clean_hebrew}%'),
                StrongsHebrew.hebrew_word.like(f'%{clean_hebrew}')
            )
        ).limit(5).all()
        if strongs_entries:
            strongs_entry = strongs_entries[0]  # Take first match
    
    if strongs_entry:
        english_definition = strongs_entry.short_definition
        long_definition = strongs_entry.long_definition
        transliteration = strongs_entry.transliteration
    
    # If still no definition found, create a basic one
    if not english_definition:
        english_definition = f"Hebrew word formed from {len(clean_hebrew)} letters"
    if not long_definition:
        long_definition = f"Ancient Hebrew word written as {clean_hebrew} in Hebrew script"
    
    # Analyze each letter
    analysis = {
        'hebrew_word': hebrew_word,
        'clean_hebrew': clean_hebrew,
        'paleo_word': paleo_word,
        'letter_analysis': [],
        'suggested_meaning': '',
        'english_definition': english_definition,
        'long_definition': long_definition,
        'transliteration': transliteration
    }
    
    meaning_parts = []
    
    for i, char in enumerate(clean_hebrew):
        if char != ' ':  # Skip spaces
            letter = PaleoLetter.query.filter_by(letter=char).first()
            if letter:
                letter_data = {
                    'position': i + 1,
                    'hebrew_letter': char,
                    'paleo_symbol': letter.paleo_symbol,
                    'name': letter.name,
                    'meaning': letter.meaning,
                    'pictograph': letter.pictograph_description
                }
                analysis['letter_analysis'].append(letter_data)
                meaning_parts.append(letter.meaning.split(',')[0])  # Take first meaning
    
    # Create suggested meaning
    if meaning_parts:
        analysis['suggested_meaning'] = ' + '.join(meaning_parts)
    
    return jsonify(analysis)

# Helper functions for file uploads
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_uploaded_file(file):
    """Save uploaded file and return filename"""
    if file and allowed_file(file.filename):
        # Generate unique filename
        ext = file.filename.rsplit('.', 1)[1].lower()
        filename = f"{uuid.uuid4()}.{ext}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        # Create upload directory if it doesn't exist
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        
        file.save(filepath)
        return filename
    return None

# God Facts API endpoints
@app.route('/api/god-facts')
def get_god_facts():
    """Get all God facts with optional filtering"""
    category = request.args.get('category', 'all')
    status = request.args.get('status', 'published')
    limit = min(int(request.args.get('limit', 20)), 100)
    offset = int(request.args.get('offset', 0))
    
    query = GodFact.query
    
    if status != 'all':
        query = query.filter_by(status=status)
    
    if category != 'all':
        query = query.filter_by(category=category)
    
    # Order by featured first, then by creation date
    query = query.order_by(GodFact.featured.desc(), GodFact.created_at.desc())
    
    total = query.count()
    facts = query.offset(offset).limit(limit).all()
    
    return jsonify({
        'facts': [fact.to_dict() for fact in facts],
        'total': total,
        'offset': offset,
        'limit': limit,
        'has_more': offset + limit < total
    })

@app.route('/api/god-facts/<int:fact_id>')
def get_god_fact(fact_id):
    """Get a specific God fact and increment view count"""
    fact = GodFact.query.get_or_404(fact_id)
    
    # Increment view count
    fact.views += 1
    db.session.commit()
    
    return jsonify(fact.to_dict())

@app.route('/api/god-facts', methods=['POST'])
@login_required
def create_god_fact():
    """Create a new God fact"""
    try:
        title = request.form.get('title')
        content = request.form.get('content')
        category = request.form.get('category')
        source = request.form.get('source', '')
        status = request.form.get('status', 'draft')
        
        if not all([title, content, category]):
            return jsonify({'error': 'Title, content, and category are required'}), 400
        
        # Handle file uploads
        image_filename = None
        video_filename = None
        
        if 'image' in request.files:
            image_file = request.files['image']
            image_filename = save_uploaded_file(image_file)
        
        if 'video' in request.files:
            video_file = request.files['video']
            video_filename = save_uploaded_file(video_file)
        
        # Create new fact
        fact = GodFact(
            title=title,
            content=content,
            category=category,
            source=source,
            status=status,
            image_filename=image_filename,
            video_filename=video_filename
        )
        
        db.session.add(fact)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'God fact created successfully',
            'fact': fact.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/god-facts/<int:fact_id>', methods=['PUT'])
@login_required
def update_god_fact(fact_id):
    """Update a God fact"""
    try:
        fact = GodFact.query.get_or_404(fact_id)
        
        # Update fields
        if request.form.get('title'):
            fact.title = request.form.get('title')
        if request.form.get('content'):
            fact.content = request.form.get('content')
        if request.form.get('category'):
            fact.category = request.form.get('category')
        if request.form.get('source'):
            fact.source = request.form.get('source')
        if request.form.get('status'):
            fact.status = request.form.get('status')
        
        # Handle file uploads
        if 'image' in request.files:
            image_file = request.files['image']
            if image_file.filename:  # New file uploaded
                image_filename = save_uploaded_file(image_file)
                if image_filename:
                    fact.image_filename = image_filename
        
        if 'video' in request.files:
            video_file = request.files['video']
            if video_file.filename:  # New file uploaded
                video_filename = save_uploaded_file(video_file)
                if video_filename:
                    fact.video_filename = video_filename
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'God fact updated successfully',
            'fact': fact.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/god-facts/<int:fact_id>', methods=['DELETE'])
@login_required
def delete_god_fact(fact_id):
    """Delete a God fact"""
    try:
        fact = GodFact.query.get_or_404(fact_id)
        
        # Delete associated files
        if fact.image_filename:
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], fact.image_filename)
            if os.path.exists(image_path):
                os.remove(image_path)
        
        if fact.video_filename:
            video_path = os.path.join(app.config['UPLOAD_FOLDER'], fact.video_filename)
            if os.path.exists(video_path):
                os.remove(video_path)
        
        db.session.delete(fact)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'God fact deleted successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/facts-stats')
@login_required
def get_facts_stats():
    """Get statistics for admin dashboard"""
    total_facts = GodFact.query.count()
    published_facts = GodFact.query.filter_by(status='published').count()
    draft_facts = GodFact.query.filter_by(status='draft').count()
    
    return jsonify({
        'total': total_facts,
        'published': published_facts,
        'drafts': draft_facts,
        'categories': {
            'science': GodFact.query.filter_by(category='science').count(),
            'history': GodFact.query.filter_by(category='history').count(),
            'prophecy': GodFact.query.filter_by(category='prophecy').count(),
            'miracles': GodFact.query.filter_by(category='miracles').count(),
            'creation': GodFact.query.filter_by(category='creation').count()
        }
    })

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    """Serve uploaded files"""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') != 'production'
    
    with app.app_context():
        db.create_all()
        
        # Initialize data if database is empty
        if PaleoLetter.query.count() == 0:
            from init_data import init_all
            print("Initializing database with sample data...")
            init_all()
    
    app.run(debug=debug, host='0.0.0.0', port=port)