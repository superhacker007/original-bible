#!/usr/bin/env python3

from playwright.sync_api import sync_playwright
import time

def test_strongs_database():
    with sync_playwright() as p:
        # Launch browser
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        
        # Navigate to the app
        page.goto("http://127.0.0.1:5001")
        
        # Wait for page to load
        page.wait_for_load_state("networkidle")
        
        print("Page loaded, testing Strong's concordance...")
        
        # Click the Strong's button
        strongs_button = page.locator("button:has-text('Strong\\'s')")
        strongs_button.click()
        
        # Wait for section to load
        time.sleep(2)
        
        # Check if results loaded
        results_div = page.locator("#strongs-results")
        results_content = results_div.inner_text()
        print(f"Strong's results loaded: {'Loading' not in results_content}")
        print(f"Results preview: {results_content[:200]}...")
        
        # Test search functionality
        search_input = page.locator("#strongs-search")
        search_input.fill("God")
        
        # Use more specific selector for Strong's search button
        search_button = page.locator("#strongs .search-btn")
        search_button.click()
        
        # Wait for search results
        time.sleep(2)
        
        # Check search results
        search_results_content = results_div.inner_text()
        print(f"Search results for 'God': {search_results_content[:200]}...")
        
        # Test Greek tab
        greek_tab = page.locator("button:has-text('Greek')")
        greek_tab.click()
        
        time.sleep(1)
        
        # Check Greek results
        greek_results_content = results_div.inner_text()
        print(f"Greek results: {greek_results_content[:200]}...")
        
        # Clear search and go back to Hebrew
        search_input.fill("")
        hebrew_tab = page.locator("button:has-text('Hebrew')")
        hebrew_tab.click()
        # Use the same specific selector for search button
        page.locator("#strongs .search-btn").click()
        
        time.sleep(2)
        
        # Check Hebrew results again
        final_results = results_div.inner_text()
        print(f"Final Hebrew results: {final_results[:200]}...")
        
        # Take final screenshot
        page.screenshot(path="strongs_database_test.png")
        
        browser.close()
        
        print("Strong's concordance database test completed!")

if __name__ == "__main__":
    test_strongs_database()