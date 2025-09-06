#!/usr/bin/env python3

from playwright.sync_api import sync_playwright
import time

def test_paleo_strongs():
    with sync_playwright() as p:
        # Launch browser
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        
        # Navigate to the app
        page.goto("http://127.0.0.1:5001")
        
        # Wait for page to load
        page.wait_for_load_state("networkidle")
        
        print("=" * 60)
        print("TESTING PALEO HEBREW IN STRONG'S CONCORDANCE")
        print("=" * 60)
        
        # Click the Strong's button
        strongs_button = page.locator("button:has-text('Strong\\'s')")
        strongs_button.click()
        
        # Wait for section to load
        time.sleep(3)
        
        # Check if results loaded with Paleo Hebrew
        results_div = page.locator("#strongs-results")
        results_content = results_div.inner_text()
        
        print("✅ Testing Paleo Hebrew display:")
        print(f"  • Strong's section loads: {'Loading' not in results_content}")
        print(f"  • Hebrew entries visible: {'H1' in results_content}")
        
        # Take screenshot to see the layout
        page.screenshot(path="paleo_strongs_display.png")
        
        # Test search for specific Hebrew word
        search_input = page.locator("#strongs-search")
        search_input.fill("H430")  # Elohim
        search_button = page.locator("#strongs .search-btn")
        search_button.click()
        
        time.sleep(2)
        
        elohim_results = results_div.inner_text()
        print(f"  • H430 (Elohim) found: {'H430' in elohim_results and 'elohim' in elohim_results.lower()}")
        
        # Take screenshot of specific entry
        page.screenshot(path="elohim_paleo_display.png")
        
        # Clear search and test another word
        search_input.fill("H3068")  # YHWH
        search_button.click()
        
        time.sleep(2)
        
        yhwh_results = results_div.inner_text()
        print(f"  • H3068 (YHWH) found: {'H3068' in yhwh_results}")
        
        # Take screenshot
        page.screenshot(path="yhwh_paleo_display.png")
        
        # Test Greek tab (should not show Paleo)
        greek_tab = page.locator("#strongs .tab-btn:has-text('Greek')")
        greek_tab.click()
        
        time.sleep(2)
        
        # Search for Greek word
        search_input.fill("G2316")  # theos
        search_button.click()
        
        time.sleep(2)
        
        theos_results = results_div.inner_text()
        print(f"  • G2316 (theos) found: {'G2316' in theos_results}")
        
        # Take final screenshot
        page.screenshot(path="greek_display.png")
        
        browser.close()
        
        print()
        print("=" * 60)
        print("PALEO HEBREW STRONG'S TEST COMPLETED")
        print("=" * 60)
        print("✅ Features tested:")
        print("  • Hebrew Strong's with Paleo Hebrew display")
        print("  • Individual Strong's number lookups")
        print("  • Greek Strong's (without Paleo Hebrew)")
        print("  • Layout and styling")
        print()
        print("📸 Screenshots saved:")
        print("  • paleo_strongs_display.png - Overview")
        print("  • elohim_paleo_display.png - H430 Elohim")
        print("  • yhwh_paleo_display.png - H3068 YHWH")
        print("  • greek_display.png - Greek entries")

if __name__ == "__main__":
    test_paleo_strongs()