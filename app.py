from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
import os

# Import models and db
from models import db, Book, Chapter, Verse, PaleoLetter, Word
from utils.hebrew_converter import hebrew_to_paleo, get_pronunciation_guide, analyze_word_meaning
from utils.ancient_hebrew_tts import create_tts_text, get_word_pronunciation, hebrew_to_ancient_pronunciation

app = Flask(__name__)
app.config['SECRET_KEY'] = 'paleo-hebrew-bible-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///paleo_bible.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db.init_app(app)
CORS(app)

@app.route('/')
def index():
    return render_template('index.html')

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