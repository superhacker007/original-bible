#!/usr/bin/env python3
"""
Quick test to verify punctuation marks are removed from Paleo text
"""

import asyncio
from playwright.async_api import async_playwright

async def test_clean_paleo():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        
        try:
            print("🧹 Testing cleaned Paleo Hebrew text...")
            
            # Navigate to the app
            await page.goto("http://localhost:5002")
            await page.wait_for_load_state("networkidle")
            
            # Navigate to Genesis 1:1
            await page.click('button.nav-btn:has-text("Books")')
            await page.wait_for_timeout(1000)
            await page.click('.book-card')
            await page.wait_for_timeout(2000)
            await page.click('.chapter-card')
            await page.wait_for_timeout(3000)
            
            # Get the first verse Paleo text
            paleo_text = await page.evaluate("() => document.querySelector('.verse-paleo').textContent")
            print(f"📜 First verse Paleo text: {paleo_text}")
            
            # Check for punctuation marks that should be removed
            has_maqqef = '־' in paleo_text
            has_sof_pasuq = '׃' in paleo_text
            
            print(f"🔍 Contains maqqef (־): {has_maqqef}")
            print(f"🔍 Contains sof pasuq (׃): {has_sof_pasuq}")
            
            if not has_maqqef and not has_sof_pasuq:
                print("✅ Perfect! No ancient punctuation marks found in Paleo text")
            else:
                print("❌ Still contains punctuation marks that should be removed")
            
            # Check a few words to make sure they're still clickable
            clickable_words = await page.query_selector_all('.paleo-word-interactive')
            print(f"🔤 Found {len(clickable_words)} clickable words")
            
            if len(clickable_words) > 0:
                print("✅ Words are still clickable after cleaning")
            else:
                print("❌ No clickable words found - cleaning may have broken functionality")
                
            await page.wait_for_timeout(2000)
            
        except Exception as e:
            print(f"❌ Error: {e}")
        finally:
            await page.screenshot(path='clean_test_results.png')
            await browser.close()

if __name__ == "__main__":
    asyncio.run(test_clean_paleo())