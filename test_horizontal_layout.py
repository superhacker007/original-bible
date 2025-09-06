#!/usr/bin/env python3

from playwright.sync_api import sync_playwright
import time

def test_horizontal_layout():
    with sync_playwright() as p:
        # Launch browser
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        
        # Navigate to the app
        page.goto("http://127.0.0.1:5001")
        
        # Wait for page to load
        page.wait_for_load_state("networkidle")
        
        print("=" * 60)
        print("TESTING HORIZONTAL PALEO HEBREW LAYOUT")
        print("=" * 60)
        
        # Click the Strong's button
        strongs_button = page.locator("button:has-text('Strong\\'s')")
        strongs_button.click()
        
        # Wait for section to load
        time.sleep(3)
        
        # Take screenshot of overview
        page.screenshot(path="horizontal_overview.png")
        
        # Test search for H430 (Elohim)
        search_input = page.locator("#strongs-search")
        search_input.fill("H430")
        search_button = page.locator("#strongs .search-btn")
        search_button.click()
        
        time.sleep(2)
        
        # Take screenshot of H430 horizontal layout
        page.screenshot(path="horizontal_elohim.png")
        print("📸 H430 (Elohim) horizontal layout captured")
        
        # Test search for H3068 (YHWH)
        search_input.fill("H3068")
        search_button.click()
        
        time.sleep(2)
        
        # Take screenshot of H3068 horizontal layout
        page.screenshot(path="horizontal_yhwh.png")
        print("📸 H3068 (YHWH) horizontal layout captured")
        
        # Test another Hebrew word - H1 (father)
        search_input.fill("H1")
        search_button.click()
        
        time.sleep(2)
        
        # Take screenshot of H1 horizontal layout
        page.screenshot(path="horizontal_father.png")
        print("📸 H1 (father) horizontal layout captured")
        
        # Test Greek tab to see no arrows when no Paleo
        greek_tab = page.locator("#strongs .tab-btn:has-text('Greek')")
        greek_tab.click()
        
        time.sleep(1)
        
        search_input.fill("G2316")
        search_button.click()
        
        time.sleep(2)
        
        # Take screenshot of Greek layout (should show no Paleo Hebrew)
        page.screenshot(path="horizontal_greek.png")
        print("📸 G2316 (Greek) layout captured")
        
        browser.close()
        
        print()
        print("=" * 60)
        print("HORIZONTAL LAYOUT TEST COMPLETED")
        print("=" * 60)
        print("✅ Layout changes made:")
        print("  • Changed from vertical to horizontal arrangement")
        print("  • Added arrow separators (→) between elements")
        print("  • Hebrew → Paleo Hebrew → Transliteration")
        print("  • Greek → Transliteration (no Paleo Hebrew)")
        print()
        print("📸 Screenshots saved:")
        print("  • horizontal_overview.png - General view")
        print("  • horizontal_elohim.png - H430 Elohim")
        print("  • horizontal_yhwh.png - H3068 YHWH")
        print("  • horizontal_father.png - H1 Father")
        print("  • horizontal_greek.png - G2316 Greek")

if __name__ == "__main__":
    test_horizontal_layout()