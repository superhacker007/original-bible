#!/usr/bin/env python3
"""
Create basic New Testament structure with chapters
Add placeholder content for all 27 NT books
"""

from app import app, db
from models import Book, Chapter, Verse

def get_nt_chapter_counts():
    """Get expected chapter counts for NT books"""
    return {
        "Matthew": 28, "Mark": 16, "Luke": 24, "John": 21,
        "Acts": 28,
        "Romans": 16, "1 Corinthians": 16, "2 Corinthians": 13, "Galatians": 6,
        "Ephesians": 6, "Philippians": 4, "Colossians": 4,
        "1 Thessalonians": 5, "2 Thessalonians": 3,
        "1 Timothy": 6, "2 Timothy": 4, "Titus": 3, "Philemon": 1,
        "Hebrews": 13, "James": 5, "1 Peter": 5, "2 Peter": 3,
        "1 John": 5, "2 John": 1, "3 John": 1, "Jude": 1,
        "Revelation": 22
    }

def get_sample_verses():
    """Get some sample NT verses for each book type"""
    return {
        "Matthew": [
            "Βίβλος γενέσεως Ἰησοῦ Χριστοῦ υἱοῦ Δαυὶδ υἱοῦ Ἀβραάμ.",
            "Ἀβραὰμ ἐγέννησεν τὸν Ἰσαάκ, Ἰσαὰκ δὲ ἐγέννησεν τὸν Ἰακώβ."
        ],
        "Romans": [
            "Παῦλος δοῦλος Χριστοῦ Ἰησοῦ, κλητὸς ἀπόστολος.",
            "ἀφωρισμένος εἰς εὐαγγέλιον θεοῦ."
        ],
        "Revelation": [
            "Ἀποκάλυψις Ἰησοῦ Χριστοῦ, ἣν ἔδωκεν αὐτῷ ὁ θεός.",
            "δεῖξαι τοῖς δούλοις αὐτοῦ ἃ δεῖ γενέσθαι ἐν τάχει."
        ],
        "default": [
            "Κείμενον παραδείγματος ἐν τῇ Ἑλληνικῇ γλώσσῃ.",
            "Δεύτερον στίχον τοῦ παραδείγματος."
        ]
    }

def greek_to_transliteration(greek_text):
    """Convert Greek text to basic transliteration"""
    if not greek_text:
        return ""
    
    # Basic Greek to Latin transliteration mapping
    transliteration_map = {
        'α': 'a', 'β': 'b', 'γ': 'g', 'δ': 'd', 'ε': 'e', 'ζ': 'z', 'η': 'e', 'θ': 'th',
        'ι': 'i', 'κ': 'k', 'λ': 'l', 'μ': 'm', 'ν': 'n', 'ξ': 'x', 'ο': 'o', 'π': 'p',
        'ρ': 'r', 'σ': 's', 'ς': 's', 'τ': 't', 'υ': 'u', 'φ': 'ph', 'χ': 'ch', 'ψ': 'ps', 'ω': 'o',
        'Α': 'A', 'Β': 'B', 'Γ': 'G', 'Δ': 'D', 'Ε': 'E', 'Ζ': 'Z', 'Η': 'E', 'Θ': 'Th',
        'Ι': 'I', 'Κ': 'K', 'Λ': 'L', 'Μ': 'M', 'Ν': 'N', 'Ξ': 'X', 'Ο': 'O', 'Π': 'P',
        'Ρ': 'R', 'Σ': 'S', 'Τ': 'T', 'Υ': 'U', 'Φ': 'Ph', 'Χ': 'Ch', 'Ψ': 'Ps', 'Ω': 'O'
    }
    
    result = ""
    for char in greek_text:
        result += transliteration_map.get(char, char)
    
    return result

def create_nt_chapters_and_verses():
    """Create chapters and sample verses for all NT books"""
    
    with app.app_context():
        print("🚀 Creating New Testament chapters and verses...")
        
        # Get all NT books
        nt_books = Book.query.filter_by(testament='New Testament').order_by(Book.order).all()
        chapter_counts = get_nt_chapter_counts()
        sample_verses = get_sample_verses()
        
        total_chapters = 0
        total_verses = 0
        
        for book in nt_books:
            book_name = book.name
            expected_chapters = chapter_counts.get(book_name, 1)
            
            print(f"\n📖 Processing {book_name} ({expected_chapters} chapters)...")
            
            # Get sample verses for this book
            verses_to_use = sample_verses.get(book_name, sample_verses['default'])
            
            # Create chapters
            for chapter_num in range(1, expected_chapters + 1):
                # Check if chapter already exists
                existing_chapter = Chapter.query.filter_by(
                    book_id=book.id,
                    chapter_number=chapter_num
                ).first()
                
                if not existing_chapter:
                    chapter = Chapter(
                        book_id=book.id,
                        chapter_number=chapter_num
                    )
                    db.session.add(chapter)
                    db.session.flush()
                    total_chapters += 1
                else:
                    chapter = existing_chapter
                
                # Check if chapter has verses
                existing_verse_count = Verse.query.filter_by(chapter_id=chapter.id).count()
                
                if existing_verse_count == 0:
                    # Add sample verses (usually 2-5 verses per chapter)
                    verses_in_chapter = min(len(verses_to_use), 3) if chapter_num > 1 else len(verses_to_use)
                    
                    for verse_num in range(1, verses_in_chapter + 1):
                        greek_text = verses_to_use[(verse_num - 1) % len(verses_to_use)]
                        transliteration = greek_to_transliteration(greek_text)
                        
                        # Simple English translation placeholder
                        english_text = f"English translation for {book_name} {chapter_num}:{verse_num}"
                        
                        verse = Verse(
                            chapter_id=chapter.id,
                            verse_number=verse_num,
                            hebrew_text=greek_text,  # Using hebrew_text field for Greek
                            hebrew_consonantal=greek_text,  # Consonantal version
                            paleo_text=transliteration,  # Using paleo_text for transliteration
                            paleo_transliteration=transliteration,
                            modern_transliteration=transliteration,
                            english_translation=english_text,
                            literal_translation=english_text
                        )
                        
                        db.session.add(verse)
                        total_verses += 1
                    
                    print(f"  ➕ Chapter {chapter_num}: {verses_in_chapter} verses")
                else:
                    print(f"  ✅ Chapter {chapter_num}: {existing_verse_count} verses (existing)")
        
        try:
            db.session.commit()
            print(f"\n🎉 New Testament structure created successfully!")
            print(f"📄 Total chapters created: {total_chapters}")
            print(f"📝 Total verses created: {total_verses}")
            
            # Final stats
            all_nt_verses = db.session.query(Verse).join(Chapter).join(Book).filter(
                Book.testament == 'New Testament'
            ).count()
            
            all_nt_chapters = db.session.query(Chapter).join(Book).filter(
                Book.testament == 'New Testament'
            ).count()
            
            print(f"📊 Final NT totals: {all_nt_chapters} chapters, {all_nt_verses} verses")
            
            return True
            
        except Exception as e:
            print(f"❌ Error creating NT structure: {e}")
            db.session.rollback()
            return False

if __name__ == "__main__":
    success = create_nt_chapters_and_verses()
    if success:
        print("✅ New Testament structure creation completed!")
    else:
        print("❌ New Testament structure creation failed!")