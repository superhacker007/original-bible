"""
Local Hebrew Bible data source using Westminster Leningrad Codex (WLC)
This provides a fallback source when APIs are unavailable
"""

import json
import os
import re
from typing import Dict, List, Optional

# Sample Hebrew Bible data based on WLC
# This is a small subset for demonstration - in a full implementation,
# you would load this from a complete WLC dataset
SAMPLE_HEBREW_BIBLE_DATA = {
    "Genesis": {
        1: {
            1: {
                "hebrew": "בְּרֵאשִׁית בָּרָא אֱלֹהִים אֵת הַשָּׁמַיִם וְאֵת הָאָרֶץ",
                "english": "In the beginning God created the heavens and the earth."
            },
            2: {
                "hebrew": "וְהָאָרֶץ הָיְתָה תֹהוּ וָבֹהוּ וְחֹשֶׁךְ עַל־פְּנֵי תְהוֹם וְרוּחַ אֱלֹהִים מְרַחֶפֶת עַל־פְּנֵי הַמָּיִם",
                "english": "Now the earth was formless and empty, darkness was over the surface of the deep, and the Spirit of God was hovering over the waters."
            },
            3: {
                "hebrew": "וַיֹּאמֶר אֱלֹהִים יְהִי אוֹר וַיְהִי־אוֹר",
                "english": "And God said, 'Let there be light,' and there was light."
            },
            4: {
                "hebrew": "וַיַּרְא אֱלֹהִים אֶת־הָאוֹר כִּי־טוֹב וַיַּבְדֵּל אֱלֹהִים בֵּין הָאוֹר וּבֵין הַחֹשֶׁךְ",
                "english": "God saw that the light was good, and he separated the light from the darkness."
            },
            5: {
                "hebrew": "וַיִּקְרָא אֱלֹהִים לָאוֹר יוֹם וְלַחֹשֶׁךְ קָרָא לָיְלָה וַיְהִי־עֶרֶב וַיְהִי־בֹקֶר יוֹם אֶחָד",
                "english": "God called the light 'day,' and the darkness he called 'night.' And there was evening, and there was morning—the first day."
            },
            6: {
                "hebrew": "וַיֹּאמֶר אֱלֹהִים יְהִי רָקִיעַ בְּתוֹךְ הַמָּיִם וִיהִי מַבְדִּיל בֵּין מַיִם לָמָיִם",
                "english": "And God said, 'Let there be a vault between the waters to separate water from water.'"
            },
            7: {
                "hebrew": "וַיַּעַשׂ אֱלֹהִים אֶת־הָרָקִיעַ וַיַּבְדֵּל בֵּין הַמַּיִם אֲשֶׁר מִתַּחַת לָרָקִיעַ וּבֵין הַמַּיִם אֲשֶׁר מֵעַל לָרָקִיעַ וַיְהִי־כֵן",
                "english": "So God made the vault and separated the water under the vault from the water above it. And it was so."
            },
            8: {
                "hebrew": "וַיִּקְרָא אֱלֹהִים לָרָקִיעַ שָׁמָיִם וַיְהִי־עֶרֶב וַיְהִי־בֹקֶר יוֹם שֵׁנִי",
                "english": "God called the vault 'sky.' And there was evening, and there was morning—the second day."
            },
            9: {
                "hebrew": "וַיֹּאמֶר אֱלֹהִים יִקָּווּ הַמַּיִם מִתַּחַת הַשָּׁמַיִם אֶל־מָקוֹם אֶחָד וְתֵרָאֶה הַיַּבָּשָׁה וַיְהִי־כֵן",
                "english": "And God said, 'Let the water under the sky be gathered to one place, and let dry ground appear.' And it was so."
            },
            10: {
                "hebrew": "וַיִּקְרָא אֱלֹהִים לַיַּבָּשָׁה אֶרֶץ וּלְמִקְוֵה הַמַּיִם קָרָא יַמִּים וַיַּרְא אֱלֹהִים כִּי־טוֹב",
                "english": "God called the dry ground 'land,' and the gathered waters he called 'seas.' And God saw that it was good."
            }
        },
        2: {
            1: {
                "hebrew": "וַיְכֻלּוּ הַשָּׁמַיִם וְהָאָרֶץ וְכָל־צְבָאָם",
                "english": "Thus the heavens and the earth were completed in all their vast array."
            },
            2: {
                "hebrew": "וַיְכַל אֱלֹהִים בַּיּוֹם הַשְּׁבִיעִי מְלַאכְתּוֹ אֲשֶׁר עָשָׂה וַיִּשְׁבֹּת בַּיּוֹם הַשְּׁבִיעִי מִכָּל־מְלַאכְתּוֹ אֲשֶׁר עָשָׂה",
                "english": "By the seventh day God had finished the work he had been doing; so on the seventh day he rested from all his work."
            },
            3: {
                "hebrew": "וַיְבָרֶךְ אֱלֹהִים אֶת־יוֹם הַשְּׁבִיעִי וַיְקַדֵּשׁ אֹתוֹ כִּי בוֹ שָׁבַת מִכָּל־מְלַאכְתּוֹ אֲשֶׁר־בָּרָא אֱלֹהִים לַעֲשׂוֹת",
                "english": "Then God blessed the seventh day and made it holy, because on it he rested from all the work of creating that he had done."
            }
        }
    },
    "Exodus": {
        1: {
            1: {
                "hebrew": "וְאֵלֶּה שְׁמוֹת בְּנֵי יִשְׂרָאֵל הַבָּאִים מִצְרָיְמָה אֵת יַעֲקֹב אִישׁ וּבֵיתוֹ בָּאוּ",
                "english": "These are the names of the sons of Israel who went to Egypt with Jacob, each with his family:"
            },
            2: {
                "hebrew": "רְאוּבֵן שִׁמְעוֹן לֵוִי וִיהוּדָה",
                "english": "Reuben, Simeon, Levi and Judah;"
            }
        }
    },
    "Psalms": {
        1: {
            1: {
                "hebrew": "אַשְׁרֵי־הָאִישׁ אֲשֶׁר לֹא הָלַךְ בַּעֲצַת רְשָׁעִים וּבְדֶרֶךְ חַטָּאִים לֹא עָמָד וּבְמוֹשַׁב לֵצִים לֹא יָשָׁב",
                "english": "Blessed is the one who does not walk in step with the wicked or stand in the way that sinners take or sit in the company of mockers,"
            },
            2: {
                "hebrew": "כִּי אִם בְּתוֹרַת יְהוָה חֶפְצוֹ וּבְתוֹרָתוֹ יֶהְגֶּה יוֹמָם וָלָיְלָה",
                "english": "but whose delight is in the law of the LORD, and who meditates on his law day and night."
            }
        },
        23: {
            1: {
                "hebrew": "מִזְמוֹר לְדָוִד יְהוָה רֹעִי לֹא אֶחְסָר",
                "english": "The LORD is my shepherd, I lack nothing."
            },
            2: {
                "hebrew": "בִּנְאוֹת דֶּשֶׁא יַרְבִּיצֵנִי עַל־מֵי מְנֻחוֹת יְנַהֲלֵנִי",
                "english": "He makes me lie down in green pastures, he leads me beside quiet waters,"
            }
        }
    }
}

class LocalHebrewBibleSource:
    """Local Hebrew Bible data source using sample WLC data"""
    
    def __init__(self):
        self.name = "Local WLC Sample"
        self.data = SAMPLE_HEBREW_BIBLE_DATA
    
    def fetch_book_data(self, book_name: str, sefaria_name: str = None) -> List[Dict]:
        """Fetch Hebrew Bible data from local sample data"""
        
        if book_name not in self.data:
            print(f"Book '{book_name}' not available in local data source")
            return []
        
        verses = []
        book_data = self.data[book_name]
        
        for chapter_num, chapter_data in book_data.items():
            for verse_num, verse_data in chapter_data.items():
                verses.append({
                    'chapter': chapter_num,
                    'verse': verse_num,
                    'hebrew': verse_data['hebrew'],
                    'english': verse_data['english']
                })
        
        print(f"Retrieved {len(verses)} verses for {book_name} from local source")
        return verses
    
    def get_available_books(self) -> List[str]:
        """Get list of available books in local data"""
        return list(self.data.keys())
    
    def expand_with_wlc_data(self, wlc_file_path: str = None):
        """
        Expand local data with WLC file if available
        This method can be used to load a complete WLC dataset
        """
        if wlc_file_path and os.path.exists(wlc_file_path):
            try:
                # This would load a complete WLC dataset
                # For now, it's a placeholder for future enhancement
                print(f"Would load WLC data from: {wlc_file_path}")
            except Exception as e:
                print(f"Error loading WLC data: {e}")

class WLCFileProcessor:
    """Process Westminster Leningrad Codex files"""
    
    @staticmethod
    def process_osis_xml(file_path: str) -> Dict:
        """
        Process OSIS XML format WLC file
        This is a placeholder for future WLC file processing
        """
        # This would parse OSIS XML format files
        # For now, returns empty dict
        return {}
    
    @staticmethod
    def process_json_file(file_path: str) -> Dict:
        """Process JSON format Hebrew Bible file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data
        except Exception as e:
            print(f"Error processing JSON file: {e}")
            return {}

def create_expanded_local_source():
    """
    Create an expanded local source with more sample data
    This can be called to add more books to the sample data
    """
    
    # Additional sample data for more books
    additional_data = {
        "Leviticus": {
            1: {
                1: {
                    "hebrew": "וַיִּקְרָא אֶל־מֹשֶׁה וַיְדַבֵּר יְהוָה אֵלָיו מֵאֹהֶל מוֹעֵד לֵאמֹר",
                    "english": "The LORD called to Moses and spoke to him from the tent of meeting."
                }
            }
        },
        "Numbers": {
            1: {
                1: {
                    "hebrew": "וַיְדַבֵּר יְהוָה אֶל־מֹשֶׁה בְּמִדְבַּר סִינַי בְּאֹהֶל מוֹעֵד בְּאֶחָד לַחֹדֶשׁ הַשֵּׁנִי בַּשָּׁנָה הַשֵּׁנִית לְצֵאתָם מֵאֶרֶץ מִצְרַיִם לֵאמֹר",
                    "english": "The LORD spoke to Moses in the tent of meeting in the Desert of Sinai on the first day of the second month of the second year after the Israelites came out of Egypt."
                }
            }
        },
        "Deuteronomy": {
            1: {
                1: {
                    "hebrew": "אֵלֶּה הַדְּבָרִים אֲשֶׁר דִּבֶּר מֹשֶׁה אֶל־כָּל־יִשְׂרָאֵל בְּעֵבֶר הַיַּרְדֵּן בַּמִּדְבָּר בָּעֲרָבָה מוֹל סוּף בֵּין־פָּארָן וּבֵין־תֹּפֶל וְלָבָן וַחֲצֵרֹת וְדִי זָהָב",
                    "english": "These are the words Moses spoke to all Israel in the wilderness east of the Jordan—that is, in the Arabah—opposite Suph, between Paran and Tophel, Laban, Hazeroth and Dizahab."
                }
            }
        }
    }
    
    source = LocalHebrewBibleSource()
    source.data.update(additional_data)
    return source

if __name__ == "__main__":
    # Test the local source
    source = LocalHebrewBibleSource()
    
    print("Available books:", source.get_available_books())
    
    # Test fetching Genesis
    genesis_verses = source.fetch_book_data("Genesis")
    print(f"\nGenesis verses: {len(genesis_verses)}")
    
    for verse in genesis_verses[:3]:
        print(f"Genesis {verse['chapter']}:{verse['verse']}")
        print(f"Hebrew: {verse['hebrew']}")
        print(f"English: {verse['english']}")
        print("-" * 50)