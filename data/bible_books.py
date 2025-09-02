"""
Complete Hebrew Bible (Tanakh) book definitions
39 books total: Torah (5), Nevi'im (21), Ketuvim (13)
"""

HEBREW_BIBLE_BOOKS = [
    # TORAH (תורה) - 5 books
    {
        'name': 'Genesis',
        'hebrew_name': 'בראשית',
        'paleo_name': '𐤁𐤓𐤀𐤔𐤉𐤕',
        'order': 1,
        'testament': 'Torah',
        'abbreviation': 'Gen',
        'hebrew_abbreviation': 'בר',
        'chapters': 50
    },
    {
        'name': 'Exodus',
        'hebrew_name': 'שמות',
        'paleo_name': '𐤔𐤌𐤅𐤕',
        'order': 2,
        'testament': 'Torah',
        'abbreviation': 'Exo',
        'hebrew_abbreviation': 'שמ',
        'chapters': 40
    },
    {
        'name': 'Leviticus',
        'hebrew_name': 'ויקרא',
        'paleo_name': '𐤅𐤉𐤒𐤓𐤀',
        'order': 3,
        'testament': 'Torah',
        'abbreviation': 'Lev',
        'hebrew_abbreviation': 'ויק',
        'chapters': 27
    },
    {
        'name': 'Numbers',
        'hebrew_name': 'במדבר',
        'paleo_name': '𐤁𐤌𐤃𐤁𐤓',
        'order': 4,
        'testament': 'Torah',
        'abbreviation': 'Num',
        'hebrew_abbreviation': 'במד',
        'chapters': 36
    },
    {
        'name': 'Deuteronomy',
        'hebrew_name': 'דברים',
        'paleo_name': '𐤃𐤁𐤓𐤉𐤌',
        'order': 5,
        'testament': 'Torah',
        'abbreviation': 'Deu',
        'hebrew_abbreviation': 'דבר',
        'chapters': 34
    },
    
    # NEVI'IM (נביאים) - Prophets - 21 books
    # Former Prophets (4 books)
    {
        'name': 'Joshua',
        'hebrew_name': 'יהושע',
        'paleo_name': '𐤉𐤄𐤅𐤔𐤏',
        'order': 6,
        'testament': 'Nevi\'im',
        'abbreviation': 'Jos',
        'hebrew_abbreviation': 'יהש',
        'chapters': 24
    },
    {
        'name': 'Judges',
        'hebrew_name': 'שופטים',
        'paleo_name': '𐤔𐤅𐤐𐤈𐤉𐤌',
        'order': 7,
        'testament': 'Nevi\'im',
        'abbreviation': 'Jdg',
        'hebrew_abbreviation': 'שפט',
        'chapters': 21
    },
    {
        'name': 'Samuel I',
        'hebrew_name': 'שמואל א',
        'paleo_name': '𐤔𐤌𐤅𐤀𐤋 𐤀',
        'order': 8,
        'testament': 'Nevi\'im',
        'abbreviation': '1Sa',
        'hebrew_abbreviation': 'שמא',
        'chapters': 31
    },
    {
        'name': 'Samuel II',
        'hebrew_name': 'שמואל ב',
        'paleo_name': '𐤔𐤌𐤅𐤀𐤋 𐤁',
        'order': 9,
        'testament': 'Nevi\'im',
        'abbreviation': '2Sa',
        'hebrew_abbreviation': 'שמב',
        'chapters': 24
    },
    {
        'name': 'Kings I',
        'hebrew_name': 'מלכים א',
        'paleo_name': '𐤌𐤋𐤊𐤉𐤌 𐤀',
        'order': 10,
        'testament': 'Nevi\'im',
        'abbreviation': '1Ki',
        'hebrew_abbreviation': 'מלא',
        'chapters': 22
    },
    {
        'name': 'Kings II',
        'hebrew_name': 'מלכים ב',
        'paleo_name': '𐤌𐤋𐤊𐤉𐤌 𐤁',
        'order': 11,
        'testament': 'Nevi\'im',
        'abbreviation': '2Ki',
        'hebrew_abbreviation': 'מלב',
        'chapters': 25
    },
    
    # Latter Prophets (15 books)
    # Major Prophets
    {
        'name': 'Isaiah',
        'hebrew_name': 'ישעיהו',
        'paleo_name': '𐤉𐤔𐤏𐤉𐤄𐤅',
        'order': 12,
        'testament': 'Nevi\'im',
        'abbreviation': 'Isa',
        'hebrew_abbreviation': 'יש',
        'chapters': 66
    },
    {
        'name': 'Jeremiah',
        'hebrew_name': 'ירמיהו',
        'paleo_name': '𐤉𐤓𐤌𐤉𐤄𐤅',
        'order': 13,
        'testament': 'Nevi\'im',
        'abbreviation': 'Jer',
        'hebrew_abbreviation': 'יר',
        'chapters': 52
    },
    {
        'name': 'Ezekiel',
        'hebrew_name': 'יחזקאל',
        'paleo_name': '𐤉𐤇𐤆𐤒𐤀𐤋',
        'order': 14,
        'testament': 'Nevi\'im',
        'abbreviation': 'Eze',
        'hebrew_abbreviation': 'יח',
        'chapters': 48
    },
    
    # Minor Prophets (12 books)
    {
        'name': 'Hosea',
        'hebrew_name': 'הושע',
        'paleo_name': '𐤄𐤅𐤔𐤏',
        'order': 15,
        'testament': 'Nevi\'im',
        'abbreviation': 'Hos',
        'hebrew_abbreviation': 'הו',
        'chapters': 14
    },
    {
        'name': 'Joel',
        'hebrew_name': 'יואל',
        'paleo_name': '𐤉𐤅𐤀𐤋',
        'order': 16,
        'testament': 'Nevi\'im',
        'abbreviation': 'Joe',
        'hebrew_abbreviation': 'יואל',
        'chapters': 3
    },
    {
        'name': 'Amos',
        'hebrew_name': 'עמוס',
        'paleo_name': '𐤏𐤌𐤅𐤎',
        'order': 17,
        'testament': 'Nevi\'im',
        'abbreviation': 'Amo',
        'hebrew_abbreviation': 'עמ',
        'chapters': 9
    },
    {
        'name': 'Obadiah',
        'hebrew_name': 'עובדיה',
        'paleo_name': '𐤏𐤅𐤁𐤃𐤉𐤄',
        'order': 18,
        'testament': 'Nevi\'im',
        'abbreviation': 'Oba',
        'hebrew_abbreviation': 'עוב',
        'chapters': 1
    },
    {
        'name': 'Jonah',
        'hebrew_name': 'יונה',
        'paleo_name': '𐤉𐤅𐤍𐤄',
        'order': 19,
        'testament': 'Nevi\'im',
        'abbreviation': 'Jon',
        'hebrew_abbreviation': 'יונה',
        'chapters': 4
    },
    {
        'name': 'Micah',
        'hebrew_name': 'מיכה',
        'paleo_name': '𐤌𐤉𐤊𐤄',
        'order': 20,
        'testament': 'Nevi\'im',
        'abbreviation': 'Mic',
        'hebrew_abbreviation': 'מיכה',
        'chapters': 7
    },
    {
        'name': 'Nahum',
        'hebrew_name': 'נחום',
        'paleo_name': '𐤍𐤇𐤅𐤌',
        'order': 21,
        'testament': 'Nevi\'im',
        'abbreviation': 'Nah',
        'hebrew_abbreviation': 'נח',
        'chapters': 3
    },
    {
        'name': 'Habakkuk',
        'hebrew_name': 'חבקוק',
        'paleo_name': '𐤇𐤁𐤒𐤅𐤒',
        'order': 22,
        'testament': 'Nevi\'im',
        'abbreviation': 'Hab',
        'hebrew_abbreviation': 'חב',
        'chapters': 3
    },
    {
        'name': 'Zephaniah',
        'hebrew_name': 'צפניה',
        'paleo_name': '𐤑𐤐𐤍𐤉𐤄',
        'order': 23,
        'testament': 'Nevi\'im',
        'abbreviation': 'Zep',
        'hebrew_abbreviation': 'צפ',
        'chapters': 3
    },
    {
        'name': 'Haggai',
        'hebrew_name': 'חגי',
        'paleo_name': '𐤇𐤂𐤉',
        'order': 24,
        'testament': 'Nevi\'im',
        'abbreviation': 'Hag',
        'hebrew_abbreviation': 'חג',
        'chapters': 2
    },
    {
        'name': 'Zechariah',
        'hebrew_name': 'זכריה',
        'paleo_name': '𐤆𐤊𐤓𐤉𐤄',
        'order': 25,
        'testament': 'Nevi\'im',
        'abbreviation': 'Zec',
        'hebrew_abbreviation': 'זכ',
        'chapters': 14
    },
    {
        'name': 'Malachi',
        'hebrew_name': 'מלאכי',
        'paleo_name': '𐤌𐤋𐤀𐤊𐤉',
        'order': 26,
        'testament': 'Nevi\'im',
        'abbreviation': 'Mal',
        'hebrew_abbreviation': 'מלא',
        'chapters': 4
    },
    
    # KETUVIM (כתובים) - Writings - 13 books
    {
        'name': 'Psalms',
        'hebrew_name': 'תהלים',
        'paleo_name': '𐤕𐤄𐤋𐤉𐤌',
        'order': 27,
        'testament': 'Ketuvim',
        'abbreviation': 'Psa',
        'hebrew_abbreviation': 'תה',
        'chapters': 150
    },
    {
        'name': 'Proverbs',
        'hebrew_name': 'משלי',
        'paleo_name': '𐤌𐤔𐤋𐤉',
        'order': 28,
        'testament': 'Ketuvim',
        'abbreviation': 'Pro',
        'hebrew_abbreviation': 'משל',
        'chapters': 31
    },
    {
        'name': 'Job',
        'hebrew_name': 'איוב',
        'paleo_name': '𐤀𐤉𐤅𐤁',
        'order': 29,
        'testament': 'Ketuvim',
        'abbreviation': 'Job',
        'hebrew_abbreviation': 'איב',
        'chapters': 42
    },
    {
        'name': 'Song of Songs',
        'hebrew_name': 'שיר השירים',
        'paleo_name': '𐤔𐤉𐤓 𐤄𐤔𐤉𐤓𐤉𐤌',
        'order': 30,
        'testament': 'Ketuvim',
        'abbreviation': 'Sng',
        'hebrew_abbreviation': 'שיר',
        'chapters': 8
    },
    {
        'name': 'Ruth',
        'hebrew_name': 'רות',
        'paleo_name': '𐤓𐤅𐤕',
        'order': 31,
        'testament': 'Ketuvim',
        'abbreviation': 'Rut',
        'hebrew_abbreviation': 'רות',
        'chapters': 4
    },
    {
        'name': 'Lamentations',
        'hebrew_name': 'איכה',
        'paleo_name': '𐤀𐤉𐤊𐤄',
        'order': 32,
        'testament': 'Ketuvim',
        'abbreviation': 'Lam',
        'hebrew_abbreviation': 'איכה',
        'chapters': 5
    },
    {
        'name': 'Ecclesiastes',
        'hebrew_name': 'קהלת',
        'paleo_name': '𐤒𐤄𐤋𐤕',
        'order': 33,
        'testament': 'Ketuvim',
        'abbreviation': 'Ecc',
        'hebrew_abbreviation': 'קה',
        'chapters': 12
    },
    {
        'name': 'Esther',
        'hebrew_name': 'אסתר',
        'paleo_name': '𐤀𐤎𐤕𐤓',
        'order': 34,
        'testament': 'Ketuvim',
        'abbreviation': 'Est',
        'hebrew_abbreviation': 'אסת',
        'chapters': 10
    },
    {
        'name': 'Daniel',
        'hebrew_name': 'דניאל',
        'paleo_name': '𐤃𐤍𐤉𐤀𐤋',
        'order': 35,
        'testament': 'Ketuvim',
        'abbreviation': 'Dan',
        'hebrew_abbreviation': 'דני',
        'chapters': 12
    },
    {
        'name': 'Ezra',
        'hebrew_name': 'עזרא',
        'paleo_name': '𐤏𐤆𐤓𐤀',
        'order': 36,
        'testament': 'Ketuvim',
        'abbreviation': 'Ezr',
        'hebrew_abbreviation': 'עז',
        'chapters': 10
    },
    {
        'name': 'Nehemiah',
        'hebrew_name': 'נחמיה',
        'paleo_name': '𐤍𐤇𐤌𐤉𐤄',
        'order': 37,
        'testament': 'Ketuvim',
        'abbreviation': 'Neh',
        'hebrew_abbreviation': 'נח',
        'chapters': 13
    },
    {
        'name': 'Chronicles I',
        'hebrew_name': 'דברי הימים א',
        'paleo_name': '𐤃𐤁𐤓𐤉 𐤄𐤉𐤌𐤉𐤌 𐤀',
        'order': 38,
        'testament': 'Ketuvim',
        'abbreviation': '1Ch',
        'hebrew_abbreviation': 'דהא',
        'chapters': 29
    },
    {
        'name': 'Chronicles II',
        'hebrew_name': 'דברי הימים ב',
        'paleo_name': '𐤃𐤁𐤓𐤉 𐤄𐤉𐤌𐤉𐤌 𐤁',
        'order': 39,
        'testament': 'Ketuvim',
        'abbreviation': '2Ch',
        'hebrew_abbreviation': 'דהב',
        'chapters': 36
    }
]

# Calculate total chapters in Hebrew Bible
TOTAL_CHAPTERS = sum(book['chapters'] for book in HEBREW_BIBLE_BOOKS)
print(f"Total chapters in Hebrew Bible: {TOTAL_CHAPTERS}")  # Should be around 929 chapters

# Book order mapping for different traditions
CHRISTIAN_ORDER_MAPPING = {
    # Maps Hebrew Bible order to Christian Old Testament order
    # This would be used if we want to display books in Christian order
}

# Testament summaries
TESTAMENT_INFO = {
    'Torah': {
        'hebrew_name': 'תורה',
        'paleo_name': '𐤕𐤅𐤓𐤄',
        'description': 'The Five Books of Moses - Law',
        'books': 5
    },
    'Nevi\'im': {
        'hebrew_name': 'נביאים',
        'paleo_name': '𐤍𐤁𐤉𐤀𐤉𐤌',
        'description': 'Prophets - Former and Latter',
        'books': 21
    },
    'Ketuvim': {
        'hebrew_name': 'כתובים',
        'paleo_name': '𐤊𐤕𐤅𐤁𐤉𐤌',
        'description': 'Writings - Wisdom and Historical',
        'books': 13
    }
}