#!/usr/bin/env python3
"""Test the Paleo Hebrew regex"""

import re

# Test Paleo Hebrew characters
paleo_text = "𐤁𐤓𐤀𐤔𐤉𐤕 𐤁𐤓𐤀"
words = paleo_text.split()

print(f"Original text: {paleo_text}")
print(f"Split words: {words}")

# Check Unicode ranges
for word in words:
    print(f"\nWord: '{word}'")
    print(f"Length: {len(word)}")
    
    for i, char in enumerate(word):
        unicode_val = ord(char)
        print(f"  Char {i}: '{char}' -> U+{unicode_val:04X}")
        
        # Check if it's in Paleo Hebrew range
        is_paleo = 0x10900 <= unicode_val <= 0x1091F
        print(f"    In Paleo range (U+10900-U+1091F): {is_paleo}")
    
    # Test the regex
    regex_match = bool(re.match(r'^[\u10900-\u1091F]+$', word))
    print(f"  Matches regex ^[\\u10900-\\u1091F]+$: {regex_match}")

# Test individual Paleo characters
print(f"\n=== Individual Character Tests ===")
paleo_chars = ['𐤀', '𐤁', '𐤂', '𐤃', '𐤄', '𐤅']
for char in paleo_chars:
    unicode_val = ord(char)
    regex_match = bool(re.match(r'^[\u10900-\u1091F]+$', char))
    print(f"'{char}' (U+{unicode_val:04X}): {regex_match}")