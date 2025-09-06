#!/usr/bin/env python3
"""
Debug script to check what's happening with makePaleoWordsInteractive function
"""

import asyncio
from playwright.async_api import async_playwright

async def debug_paleo_words():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        
        # Enable console logging
        page.on("console", lambda msg: print(f"🖥️  CONSOLE: {msg.type}: {msg.text}"))
        page.on("pageerror", lambda error: print(f"❌ PAGE ERROR: {error}"))
        
        try:
            print("🚀 Starting debug session...")
            
            # Navigate to the app
            await page.goto("http://localhost:5002")
            await page.wait_for_load_state("networkidle")
            
            # Click Books button
            await page.click('button.nav-btn:has-text("Books")')
            await page.wait_for_timeout(1000)
            
            # Click on Genesis
            await page.click('.book-card')
            await page.wait_for_timeout(2000)
            
            # Click Chapter 1
            await page.click('.chapter-card')
            await page.wait_for_timeout(3000)
            
            # Check what's happening with the makePaleoWordsInteractive function
            print("🔍 Checking JavaScript functions and data...")
            
            # Check if the function exists
            function_exists = await page.evaluate("() => typeof makePaleoWordsInteractive === 'function'")
            print(f"makePaleoWordsInteractive function exists: {function_exists}")
            
            # Check if the mapping is loaded
            mapping_exists = await page.evaluate("() => typeof window.COMPLETE_PALEO_ENGLISH === 'object' && window.COMPLETE_PALEO_ENGLISH !== null")
            print(f"COMPLETE_PALEO_ENGLISH loaded: {mapping_exists}")
            
            if mapping_exists:
                mapping_count = await page.evaluate("() => Object.keys(window.COMPLETE_PALEO_ENGLISH).length")
                print(f"Mapping entries: {mapping_count}")
                
                # Test one word
                test_word = await page.evaluate("() => Object.keys(window.COMPLETE_PALEO_ENGLISH)[0]")
                test_definition = await page.evaluate("(word) => window.COMPLETE_PALEO_ENGLISH[word]", test_word)
                print(f"Sample mapping: '{test_word}' -> '{test_definition}'")
            
            # Check the verse HTML content
            print("\n🔍 Checking verse HTML...")
            verse_count = await page.evaluate("() => document.querySelectorAll('.verse-paleo').length")
            print(f"Found {verse_count} verse-paleo elements")
            
            if verse_count > 0:
                # Get the first verse's HTML and text
                first_verse_html = await page.evaluate("() => document.querySelector('.verse-paleo').innerHTML")
                first_verse_text = await page.evaluate("() => document.querySelector('.verse-paleo').textContent")
                
                print(f"First verse text: {first_verse_text[:100]}...")
                print(f"First verse HTML contains 'paleo-word-interactive': {'paleo-word-interactive' in first_verse_html}")
                
                # Test the makePaleoWordsInteractive function directly
                print("\n🧪 Testing makePaleoWordsInteractive function...")
                test_result = await page.evaluate("""
                    () => {
                        try {
                            const samplePaleo = '𐤁𐤓𐤀𐤔𐤉𐤕 𐤁𐤓𐤀';
                            const sampleHebrew = 'בראשית ברא';
                            const result = makePaleoWordsInteractive(samplePaleo, sampleHebrew, {id: 'test'});
                            return {
                                success: true,
                                result: result,
                                containsInteractive: result.includes('paleo-word-interactive')
                            };
                        } catch (error) {
                            return {
                                success: false,
                                error: error.message
                            };
                        }
                    }
                """)
                
                print(f"Function test result: {test_result}")
                
                # Check the actual verse processing
                print("\n🔍 Checking actual verse data...")
                verse_data = await page.evaluate("""
                    () => {
                        const verses = document.querySelectorAll('.verse-card');
                        if (verses.length > 0) {
                            const firstVerse = verses[0];
                            const paleoDiv = firstVerse.querySelector('.verse-paleo');
                            const hebrewDiv = firstVerse.querySelector('.verse-hebrew');
                            
                            if (paleoDiv && hebrewDiv) {
                                return {
                                    paleoText: paleoDiv.textContent.trim(),
                                    hebrewText: hebrewDiv.textContent.trim(),
                                    paleoHTML: paleoDiv.innerHTML,
                                    hasInteractiveSpans: paleoDiv.querySelectorAll('.paleo-word-interactive').length
                                };
                            }
                        }
                        return null;
                    }
                """)
                
                if verse_data:
                    print(f"Verse paleo text: {verse_data['paleoText'][:50]}...")
                    print(f"Verse hebrew text: {verse_data['hebrewText'][:50]}...")
                    print(f"Interactive spans found: {verse_data['hasInteractiveSpans']}")
                    
                    if verse_data['hasInteractiveSpans'] == 0:
                        print("❌ No interactive spans found - makePaleoWordsInteractive is not working!")
                        print(f"HTML sample: {verse_data['paleoHTML'][:200]}...")
            
            await page.wait_for_timeout(10000)  # Wait to see the page
            
        except Exception as e:
            print(f"❌ Error: {e}")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(debug_paleo_words())