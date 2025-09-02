#!/usr/bin/env python3
"""
Debug Sefaria API response structure
"""

import requests
import json

def debug_sefaria():
    """Check actual Sefaria response structure"""
    
    print("🔍 Debugging Sefaria API response...")
    
    url = "https://www.sefaria.org/api/texts/Genesis"
    response = requests.get(url, timeout=10)
    data = response.json()
    
    print(f"📊 Response keys: {list(data.keys())}")
    
    # Check Hebrew data structure
    he_data = data.get('he', [])
    print(f"\n📖 Hebrew data:")
    print(f"   Type: {type(he_data)}")
    print(f"   Length: {len(he_data) if hasattr(he_data, '__len__') else 'No length'}")
    
    if isinstance(he_data, list) and len(he_data) > 0:
        print(f"   First element type: {type(he_data[0])}")
        if isinstance(he_data[0], str):
            print(f"   First element (first 200 chars): {he_data[0][:200]}")
        elif isinstance(he_data[0], list):
            print(f"   First chapter length: {len(he_data[0])}")
            if len(he_data[0]) > 0:
                print(f"   First verse: {he_data[0][0][:100]}")
    
    # Check English data structure  
    en_data = data.get('text', [])
    print(f"\n🔤 English data:")
    print(f"   Type: {type(en_data)}")
    print(f"   Length: {len(en_data) if hasattr(en_data, '__len__') else 'No length'}")
    
    if isinstance(en_data, list) and len(en_data) > 0:
        print(f"   First element type: {type(en_data[0])}")
        if isinstance(en_data[0], str):
            print(f"   First element (first 200 chars): {en_data[0][:200]}")
        elif isinstance(en_data[0], list):
            print(f"   First chapter length: {len(en_data[0])}")
            if len(en_data[0]) > 0:
                print(f"   First verse: {en_data[0][0][:100]}")
    
    # Try different API formats
    print(f"\n🔄 Trying alternative API formats...")
    
    alternatives = [
        "Genesis.1",  # Specific chapter
        "Bereshit",   # Hebrew name
        "Genesis/1",  # With chapter
    ]
    
    for alt in alternatives:
        try:
            alt_url = f"https://www.sefaria.org/api/texts/{alt}"
            alt_response = requests.get(alt_url, timeout=5)
            
            if alt_response.status_code == 200:
                alt_data = alt_response.json()
                print(f"✅ {alt}: SUCCESS")
                print(f"   Hebrew type: {type(alt_data.get('he', []))}")
                print(f"   Hebrew length: {len(alt_data.get('he', [])) if hasattr(alt_data.get('he', []), '__len__') else 'No length'}")
                
                he_alt = alt_data.get('he', [])
                if isinstance(he_alt, list) and len(he_alt) > 0:
                    print(f"   First Hebrew verse: {he_alt[0][:100] if isinstance(he_alt[0], str) else 'Not string'}")
            else:
                print(f"❌ {alt}: HTTP {alt_response.status_code}")
                
        except Exception as e:
            print(f"❌ {alt}: Error - {e}")
    
    # Save sample data for analysis
    with open('sefaria_genesis_sample.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 Full response saved to 'sefaria_genesis_sample.json'")

if __name__ == "__main__":
    debug_sefaria()