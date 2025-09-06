#!/usr/bin/env python3

"""
Strong's Concordance Data Importer
This script imports comprehensive Strong's Hebrew and Greek concordance data
"""

import json
import requests
from models import db, StrongsHebrew, StrongsGreek
from app import app

# Comprehensive Strong's Hebrew data
STRONGS_HEBREW_DATA = {
    # Genesis words and common Hebrew words
    "H1": {"word": "אָב", "transliteration": "ab", "meaning": "father", "definition": "father, ancestor, originator", "usage": 1205, "pos": "noun"},
    "H120": {"word": "אָדָם", "transliteration": "adam", "meaning": "man, mankind", "definition": "man, human being, mankind, Adam", "usage": 562, "pos": "noun"},
    "H127": {"word": "אֲדָמָה", "transliteration": "adamah", "meaning": "ground, land", "definition": "ground, land, earth, soil", "usage": 225, "pos": "noun"},
    "H216": {"word": "אוֹר", "transliteration": "or", "meaning": "light", "definition": "light, illumination, daylight, dawn", "usage": 120, "pos": "noun"},
    "H226": {"word": "אוֹת", "transliteration": "oth", "meaning": "sign", "definition": "sign, signal, mark, token", "usage": 79, "pos": "noun"},
    "H251": {"word": "אָח", "transliteration": "ach", "meaning": "brother", "definition": "brother, kinsman, colleague", "usage": 629, "pos": "noun"},
    "H269": {"word": "אָחוֹת", "transliteration": "achoth", "meaning": "sister", "definition": "sister, female relative", "usage": 114, "pos": "noun"},
    "H312": {"word": "אַחֵר", "transliteration": "acher", "meaning": "another, other", "definition": "another, other, different", "usage": 166, "pos": "adjective"},
    "H376": {"word": "אִישׁ", "transliteration": "ish", "meaning": "man, husband", "definition": "man, male, husband, each", "usage": 2188, "pos": "noun"},
    "H430": {"word": "אֱלֹהִים", "transliteration": "elohim", "meaning": "God, gods", "definition": "God, gods, divine beings, supreme being", "usage": 2570, "pos": "noun"},
    "H559": {"word": "אָמַר", "transliteration": "amar", "meaning": "to say, speak", "definition": "to say, speak, utter, declare", "usage": 5316, "pos": "verb"},
    "H776": {"word": "אֶרֶץ", "transliteration": "eretz", "meaning": "earth, land", "definition": "earth, land, country, ground", "usage": 2505, "pos": "noun"},
    "H802": {"word": "אִשָּׁה", "transliteration": "ishshah", "meaning": "woman, wife", "definition": "woman, wife, female", "usage": 781, "pos": "noun"},
    "H854": {"word": "אֵת", "transliteration": "eth", "meaning": "with", "definition": "with, near, together with", "usage": 890, "pos": "preposition"},
    "H935": {"word": "בּוֹא", "transliteration": "bo", "meaning": "to come, go", "definition": "to come, go, enter, arrive", "usage": 2592, "pos": "verb"},
    "H1004": {"word": "בַּיִת", "transliteration": "bayith", "meaning": "house", "definition": "house, home, household, family", "usage": 2047, "pos": "noun"},
    "H1121": {"word": "בֵּן", "transliteration": "ben", "meaning": "son", "definition": "son, child, descendant", "usage": 4906, "pos": "noun"},
    "H1254": {"word": "בָּרָא", "transliteration": "bara", "meaning": "to create", "definition": "to create, make, fashion", "usage": 54, "pos": "verb"},
    "H1288": {"word": "בָּרַךְ", "transliteration": "barak", "meaning": "to bless", "definition": "to bless, kneel, praise", "usage": 330, "pos": "verb"},
    "H1323": {"word": "בַּת", "transliteration": "bath", "meaning": "daughter", "definition": "daughter, girl, female descendant", "usage": 587, "pos": "noun"},
    "H1431": {"word": "גָּדַל", "transliteration": "gadal", "meaning": "to grow, be great", "definition": "to grow, become great, magnify", "usage": 117, "pos": "verb"},
    "H1419": {"word": "גָּדוֹל", "transliteration": "gadol", "meaning": "great, large", "definition": "great, large, big, mighty", "usage": 527, "pos": "adjective"},
    "H1471": {"word": "גּוֹי", "transliteration": "goy", "meaning": "nation", "definition": "nation, people, Gentiles", "usage": 559, "pos": "noun"},
    "H1696": {"word": "דָּבַר", "transliteration": "dabar", "meaning": "to speak", "definition": "to speak, say, declare, command", "usage": 1142, "pos": "verb"},
    "H1697": {"word": "דָּבָר", "transliteration": "dabar", "meaning": "word, matter", "definition": "word, matter, thing, commandment", "usage": 1440, "pos": "noun"},
    "H2009": {"word": "הִנֵּה", "transliteration": "hinneh", "meaning": "behold", "definition": "behold, look, see", "usage": 1061, "pos": "interjection"},
    "H2416": {"word": "חַי", "transliteration": "chay", "meaning": "living, alive", "definition": "living, alive, life, lifetime", "usage": 501, "pos": "adjective"},
    "H2822": {"word": "חֹשֶׁךְ", "transliteration": "choshek", "meaning": "darkness", "definition": "darkness, obscurity, secret place", "usage": 80, "pos": "noun"},
    "H3027": {"word": "יָד", "transliteration": "yad", "meaning": "hand", "definition": "hand, side, power, strength", "usage": 1627, "pos": "noun"},
    "H3068": {"word": "יְהוָה", "transliteration": "YHWH", "meaning": "LORD", "definition": "the proper name of the God of Israel", "usage": 6828, "pos": "noun"},
    "H3117": {"word": "יוֹם", "transliteration": "yom", "meaning": "day", "definition": "day, time, year, lifetime", "usage": 2301, "pos": "noun"},
    "H3205": {"word": "יָלַד", "transliteration": "yalad", "meaning": "to bear, bring forth", "definition": "to bear, bring forth, beget", "usage": 497, "pos": "verb"},
    "H3212": {"word": "יָלַךְ", "transliteration": "yalak", "meaning": "to go, walk", "definition": "to go, walk, come, depart", "usage": 1554, "pos": "verb"},
    "H3318": {"word": "יָצָא", "transliteration": "yatsa", "meaning": "to go out", "definition": "to go out, come forth, proceed", "usage": 1076, "pos": "verb"},
    "H3427": {"word": "יָשַׁב", "transliteration": "yashab", "meaning": "to sit, dwell", "definition": "to sit, remain, dwell, inhabit", "usage": 1088, "pos": "verb"},
    "H4325": {"word": "מַיִם", "transliteration": "mayim", "meaning": "water", "definition": "water, waters, flood", "usage": 581, "pos": "noun"},
    "H4428": {"word": "מֶלֶךְ", "transliteration": "melek", "meaning": "king", "definition": "king, ruler, sovereign", "usage": 2530, "pos": "noun"},
    "H4872": {"word": "מֹשֶׁה", "transliteration": "Mosheh", "meaning": "Moses", "definition": "Moses, the lawgiver of Israel", "usage": 766, "pos": "proper noun"},
    "H5414": {"word": "נָתַן", "transliteration": "nathan", "meaning": "to give", "definition": "to give, put, set, place", "usage": 2014, "pos": "verb"},
    "H5971": {"word": "עַם", "transliteration": "am", "meaning": "people", "definition": "people, nation, folk", "usage": 1868, "pos": "noun"},
    "H6213": {"word": "עָשָׂה", "transliteration": "asah", "meaning": "to do, make", "definition": "to do, make, accomplish, prepare", "usage": 2632, "pos": "verb"},
    "H7121": {"word": "קָרָא", "transliteration": "qara", "meaning": "to call, proclaim", "definition": "to call, cry, read, proclaim", "usage": 739, "pos": "verb"},
    "H7200": {"word": "רָאָה", "transliteration": "raah", "meaning": "to see", "definition": "to see, look, behold, perceive", "usage": 1311, "pos": "verb"},
    "H7307": {"word": "רוּחַ", "transliteration": "ruach", "meaning": "spirit, wind", "definition": "spirit, wind, breath, mind", "usage": 378, "pos": "noun"},
    "H8064": {"word": "שָׁמַיִם", "transliteration": "shamayim", "meaning": "heaven, sky", "definition": "heaven, heavens, sky, air", "usage": 421, "pos": "noun"},
    "H8085": {"word": "שָׁמַע", "transliteration": "shama", "meaning": "to hear", "definition": "to hear, listen, obey, understand", "usage": 1165, "pos": "verb"},
    "H8104": {"word": "שָׁמַר", "transliteration": "shamar", "meaning": "to keep, guard", "definition": "to keep, guard, observe, watch", "usage": 468, "pos": "verb"},
    "H8269": {"word": "שַׂר", "transliteration": "sar", "meaning": "prince, captain", "definition": "prince, captain, chief, ruler", "usage": 421, "pos": "noun"}
}

# Comprehensive Strong's Greek data  
STRONGS_GREEK_DATA = {
    # New Testament words and common Greek words
    "G1": {"word": "Ἀ", "transliteration": "a", "meaning": "alpha", "definition": "first letter of Greek alphabet", "usage": 4, "pos": "letter"},
    "G2": {"word": "Ἀαρών", "transliteration": "Aaron", "meaning": "Aaron", "definition": "Aaron, brother of Moses", "usage": 5, "pos": "proper noun"},
    "G26": {"word": "ἀγάπη", "transliteration": "agape", "meaning": "love", "definition": "love, affection, good will", "usage": 116, "pos": "noun"},
    "G32": {"word": "ἄγγελος", "transliteration": "angelos", "meaning": "angel", "definition": "angel, messenger", "usage": 175, "pos": "noun"},
    "G40": {"word": "ἅγιος", "transliteration": "hagios", "meaning": "holy", "definition": "holy, saint, sacred", "usage": 233, "pos": "adjective"},
    "G80": {"word": "ἀδελφός", "transliteration": "adelphos", "meaning": "brother", "definition": "brother, fellow believer", "usage": 343, "pos": "noun"},
    "G444": {"word": "ἄνθρωπος", "transliteration": "anthropos", "meaning": "man, human", "definition": "man, human being, person", "usage": 550, "pos": "noun"},
    "G1135": {"word": "γυνή", "transliteration": "gyne", "meaning": "woman, wife", "definition": "woman, wife, female", "usage": 221, "pos": "noun"},
    "G2316": {"word": "θεός", "transliteration": "theos", "meaning": "God", "definition": "God, deity, divine being", "usage": 1317, "pos": "noun"},
    "G2424": {"word": "Ἰησοῦς", "transliteration": "Iesous", "meaning": "Jesus", "definition": "Jesus, the Christ, the Son of God", "usage": 917, "pos": "proper noun"},
    "G2962": {"word": "κύριος", "transliteration": "kyrios", "meaning": "Lord, master", "definition": "Lord, master, owner, sir", "usage": 717, "pos": "noun"},
    "G5547": {"word": "Χριστός", "transliteration": "Christos", "meaning": "Christ", "definition": "Christ, Messiah, the Anointed One", "usage": 529, "pos": "proper noun"},
    "G40": {"word": "ἅγιος", "transliteration": "hagios", "meaning": "holy", "definition": "holy, set apart, sacred", "usage": 233, "pos": "adjective"},
    "G1342": {"word": "δίκαιος", "transliteration": "dikaios", "meaning": "righteous", "definition": "righteous, just, upright", "usage": 79, "pos": "adjective"},
    "G4151": {"word": "πνεῦμα", "transliteration": "pneuma", "meaning": "spirit", "definition": "spirit, breath, wind, ghost", "usage": 379, "pos": "noun"},
    "G4172": {"word": "πόλις", "transliteration": "polis", "meaning": "city", "definition": "city, town, citizenship", "usage": 163, "pos": "noun"},
    "G932": {"word": "βασιλεία", "transliteration": "basileia", "meaning": "kingdom", "definition": "kingdom, rule, reign", "usage": 162, "pos": "noun"},
    "G5590": {"word": "ψυχή", "transliteration": "psyche", "meaning": "soul", "definition": "soul, life, mind, heart", "usage": 103, "pos": "noun"},
    "G2222": {"word": "ζωή", "transliteration": "zoe", "meaning": "life", "definition": "life, lifetime, existence", "usage": 135, "pos": "noun"},
    "G2288": {"word": "θάνατος", "transliteration": "thanatos", "meaning": "death", "definition": "death, dying, mortality", "usage": 120, "pos": "noun"},
    "G1537": {"word": "ἐκ", "transliteration": "ek", "meaning": "out of, from", "definition": "out of, from, by, away from", "usage": 914, "pos": "preposition"},
    "G1722": {"word": "ἐν", "transliteration": "en", "meaning": "in", "definition": "in, on, at, by, with", "usage": 2752, "pos": "preposition"},
    "G1519": {"word": "εἰς", "transliteration": "eis", "meaning": "into, to", "definition": "into, to, toward, for", "usage": 1767, "pos": "preposition"},
    "G3056": {"word": "λόγος", "transliteration": "logos", "meaning": "word", "definition": "word, saying, speech, account", "usage": 330, "pos": "noun"},
    "G4102": {"word": "πίστις", "transliteration": "pistis", "meaning": "faith", "definition": "faith, belief, trust, fidelity", "usage": 244, "pos": "noun"},
    "G1680": {"word": "ἐλπίς", "transliteration": "elpis", "meaning": "hope", "definition": "hope, expectation, trust", "usage": 53, "pos": "noun"},
    "G25": {"word": "ἀγαπάω", "transliteration": "agapao", "meaning": "to love", "definition": "to love, have affection for", "usage": 143, "pos": "verb"},
    "G1097": {"word": "γινώσκω", "transliteration": "ginosko", "meaning": "to know", "definition": "to know, understand, perceive", "usage": 222, "pos": "verb"},
    "G2064": {"word": "ἔρχομαι", "transliteration": "erchomai", "meaning": "to come, go", "definition": "to come, go, arrive, appear", "usage": 634, "pos": "verb"},
    "G3004": {"word": "λέγω", "transliteration": "lego", "meaning": "to say", "definition": "to say, speak, call, tell", "usage": 2354, "pos": "verb"},
    "G4160": {"word": "ποιέω", "transliteration": "poieo", "meaning": "to make, do", "definition": "to make, do, cause, work", "usage": 568, "pos": "verb"},
    "G1510": {"word": "εἰμί", "transliteration": "eimi", "meaning": "to be", "definition": "to be, exist, happen, be present", "usage": 2462, "pos": "verb"},
    "G2192": {"word": "ἔχω", "transliteration": "echo", "meaning": "to have, hold", "definition": "to have, hold, possess, be", "usage": 708, "pos": "verb"},
    "G1492": {"word": "εἴδω", "transliteration": "eido", "meaning": "to see, know", "definition": "to see, behold, know, understand", "usage": 666, "pos": "verb"},
    "G1325": {"word": "δίδωμι", "transliteration": "didomi", "meaning": "to give", "definition": "to give, grant, put, place", "usage": 415, "pos": "verb"},
    "G2036": {"word": "ἔπω", "transliteration": "epo", "meaning": "to say, speak", "definition": "to say, speak, tell, command", "usage": 2036, "pos": "verb"}
}

def import_strongs_hebrew():
    """Import Hebrew Strong's data into database"""
    print("Importing Hebrew Strong's concordance data...")
    
    for strong_num, data in STRONGS_HEBREW_DATA.items():
        # Check if entry already exists
        existing = StrongsHebrew.query.filter_by(strong_number=strong_num).first()
        if existing:
            print(f"Hebrew {strong_num} already exists, skipping...")
            continue
            
        # Create new entry
        hebrew_entry = StrongsHebrew(
            strong_number=strong_num,
            hebrew_word=data['word'],
            transliteration=data['transliteration'],
            pronunciation=data['transliteration'],  # Use transliteration as pronunciation
            short_definition=data['meaning'],
            long_definition=data['definition'],
            usage_count=data['usage'],
            part_of_speech=data['pos']
        )
        
        db.session.add(hebrew_entry)
        print(f"Added Hebrew {strong_num}: {data['word']} ({data['transliteration']})")
    
    db.session.commit()
    print(f"Hebrew import complete. Added {len(STRONGS_HEBREW_DATA)} entries.")

def import_strongs_greek():
    """Import Greek Strong's data into database"""
    print("Importing Greek Strong's concordance data...")
    
    for strong_num, data in STRONGS_GREEK_DATA.items():
        # Check if entry already exists
        existing = StrongsGreek.query.filter_by(strong_number=strong_num).first()
        if existing:
            print(f"Greek {strong_num} already exists, skipping...")
            continue
            
        # Create new entry
        greek_entry = StrongsGreek(
            strong_number=strong_num,
            greek_word=data['word'],
            transliteration=data['transliteration'],
            pronunciation=data['transliteration'],  # Use transliteration as pronunciation
            short_definition=data['meaning'],
            long_definition=data['definition'],
            usage_count=data['usage'],
            part_of_speech=data['pos']
        )
        
        db.session.add(greek_entry)
        print(f"Added Greek {strong_num}: {data['word']} ({data['transliteration']})")
    
    db.session.commit()
    print(f"Greek import complete. Added {len(STRONGS_GREEK_DATA)} entries.")

def main():
    """Main import function"""
    with app.app_context():
        print("Starting Strong's Concordance import...")
        
        # Create tables if they don't exist
        db.create_all()
        
        # Import Hebrew data
        import_strongs_hebrew()
        
        # Import Greek data
        import_strongs_greek()
        
        print("Strong's Concordance import completed successfully!")
        
        # Print summary
        hebrew_count = StrongsHebrew.query.count()
        greek_count = StrongsGreek.query.count()
        print(f"\nDatabase summary:")
        print(f"Hebrew entries: {hebrew_count}")
        print(f"Greek entries: {greek_count}")
        print(f"Total Strong's entries: {hebrew_count + greek_count}")

if __name__ == "__main__":
    main()