#!/usr/bin/env python3
"""
Playwright test to verify Paleo Hebrew words are clickable
"""

import asyncio
import time
from playwright.async_api import async_playwright

async def test_paleo_words_clickable():
    """Test that Paleo Hebrew words are clickable and show overlays"""
    async with async_playwright() as p:
        # Launch browser
        browser = await p.chromium.launch(headless=False)  # Set to False to see the browser
        context = await browser.new_context()
        page = await context.new_page()
        
        try:
            print("🚀 Starting Playwright test...")
            
            # Navigate to the app
            print("📱 Navigating to http://localhost:5002...")
            await page.goto("http://localhost:5002")
            await page.wait_for_load_state("networkidle")
            
            # Verify the page loaded
            title = await page.title()
            print(f"📄 Page title: {title}")
            
            # Click on Books button to show the Books section
            print("📚 Clicking on Books button...")
            books_button = await page.query_selector('button.nav-btn:has-text("Books")')
            if books_button:
                await books_button.click()
                await page.wait_for_timeout(1000)  # Wait for section to show
                print("📚 Books button clicked")
            
            # Check if Books section is now visible
            books_section = await page.query_selector('#books')
            if books_section:
                is_visible = await books_section.is_visible()
                print(f"📚 Books section visible: {is_visible}")
            
            # Wait for books to load
            await page.wait_for_selector('.books-grid .book-card', timeout=10000)
            print("📖 Books loaded")
            
            # Click on the first book (should be Genesis)
            first_book = await page.query_selector('.book-card')
            if first_book:
                book_name = await first_book.query_selector('.book-name')
                if book_name:
                    book_text = await book_name.inner_text()
                    print(f"📖 Clicking on book: {book_text}")
                
                await first_book.click()
                await page.wait_for_load_state("networkidle")
                
                # Wait for chapters to load
                await page.wait_for_selector('.chapters-grid .chapter-card', timeout=10000)
                print("📑 Chapters loaded")
                
                # Click on Chapter 1
                chapter_1 = await page.query_selector('.chapter-card')
                if chapter_1:
                    print("📑 Clicking on Chapter 1")
                    await chapter_1.click()
                    await page.wait_for_load_state("networkidle")
                    
                    # Wait for verses to load
                    await page.wait_for_selector('.verses-container .verse-card', timeout=10000)
                    print("📜 Verses loaded")
                    
                    # Look for Paleo Hebrew words
                    paleo_words = await page.query_selector_all('.paleo-word-interactive')
                    print(f"🔤 Found {len(paleo_words)} clickable Paleo Hebrew words")
                    
                    if len(paleo_words) > 0:
                        # Test clicking on the first few Paleo words
                        for i, word in enumerate(paleo_words[:3]):  # Test first 3 words
                            try:
                                word_text = await word.inner_text()
                                print(f"🔤 Testing word {i+1}: '{word_text}'")
                                
                                # Click the word
                                await word.click()
                                await page.wait_for_timeout(1000)  # Wait for overlay to appear
                                
                                # Check if overlay appeared
                                overlay = await page.query_selector('#word-overlay')
                                if overlay:
                                    is_visible = await overlay.is_visible()
                                    if is_visible:
                                        print(f"✅ Word '{word_text}' - Overlay appeared!")
                                        
                                        # Check overlay content
                                        hebrew_word = await page.query_selector('#overlay-hebrew-word')
                                        paleo_word = await page.query_selector('#overlay-paleo-word')
                                        english_word = await page.query_selector('#overlay-english-word')
                                        
                                        if hebrew_word and paleo_word and english_word:
                                            hebrew_text = await hebrew_word.inner_text()
                                            paleo_text = await paleo_word.inner_text()
                                            english_text = await english_word.inner_text()
                                            
                                            print(f"   Hebrew: {hebrew_text}")
                                            print(f"   Paleo: {paleo_text}")
                                            print(f"   English: {english_text}")
                                            
                                            if english_text and english_text != "loading..." and english_text != "Ancient Word Analysis":
                                                print(f"✅ Word has proper English translation!")
                                            else:
                                                print(f"⚠️  Word shows generic/loading text")
                                        
                                        # Close overlay by clicking outside
                                        await page.click('body')
                                        await page.wait_for_timeout(500)
                                    else:
                                        print(f"❌ Word '{word_text}' - Overlay not visible")
                                else:
                                    print(f"❌ Word '{word_text}' - Overlay element not found")
                                    
                            except Exception as e:
                                print(f"❌ Error testing word {i+1}: {e}")
                        
                        print("✅ Test completed successfully!")
                        
                        # Additional check: verify complete paleo mapping is loaded
                        mapping_loaded = await page.evaluate("() => window.COMPLETE_PALEO_ENGLISH && Object.keys(window.COMPLETE_PALEO_ENGLISH).length > 0")
                        if mapping_loaded:
                            mapping_count = await page.evaluate("() => Object.keys(window.COMPLETE_PALEO_ENGLISH).length")
                            print(f"✅ Complete Paleo mapping loaded: {mapping_count} entries")
                        else:
                            print("❌ Complete Paleo mapping not loaded")
                            
                    else:
                        print("❌ No clickable Paleo Hebrew words found")
                        
                        # Debug: check if any paleo text exists at all
                        verse_paleo = await page.query_selector_all('.verse-paleo')
                        print(f"🔍 Found {len(verse_paleo)} verse-paleo elements")
                        
                        if len(verse_paleo) > 0:
                            paleo_text = await verse_paleo[0].inner_text()
                            print(f"🔍 First verse Paleo text: {paleo_text[:100]}...")
                            
                            # Check HTML content
                            paleo_html = await verse_paleo[0].inner_html()
                            has_interactive = "paleo-word-interactive" in paleo_html
                            print(f"🔍 Contains interactive class: {has_interactive}")
            
        except Exception as e:
            print(f"❌ Test failed with error: {e}")
            
        finally:
            # Take a screenshot for debugging
            await page.screenshot(path='test_results.png')
            print("📸 Screenshot saved as test_results.png")
            
            # Keep browser open for a moment to see results
            await page.wait_for_timeout(3000)
            await browser.close()

if __name__ == "__main__":
    asyncio.run(test_paleo_words_clickable())