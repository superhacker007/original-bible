#!/usr/bin/env python3

from playwright.sync_api import sync_playwright
import time

def test_strongs_button():
    with sync_playwright() as p:
        # Launch browser
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        
        # Navigate to the app
        page.goto("http://127.0.0.1:5001")
        
        # Wait for page to load
        page.wait_for_load_state("networkidle")
        
        print("Page loaded, looking for Strong's button...")
        
        # Find and click the Strong's button
        strongs_button = page.locator("button:has-text('Strong\\'s')")
        print(f"Found Strong's button: {strongs_button.is_visible()}")
        
        # Take a screenshot before clicking
        page.screenshot(path="before_click.png")
        
        # Click the Strong's button
        strongs_button.click()
        
        # Wait a bit for the section to load
        time.sleep(2)
        
        # Take a screenshot after clicking
        page.screenshot(path="after_click.png")
        
        # Check if the Strong's section is visible
        strongs_section = page.locator("#strongs")
        print(f"Strong's section visible: {strongs_section.is_visible()}")
        
        # Check if the section has active class
        has_active = strongs_section.get_attribute("class")
        print(f"Strong's section classes: {has_active}")
        
        # Check for any console errors
        page.on("console", lambda msg: print(f"Console {msg.type}: {msg.text}"))
        
        # Wait for the loading to complete and check results
        time.sleep(3)
        
        # Check if results loaded
        results_div = page.locator("#strongs-results")
        results_content = results_div.inner_text()
        print(f"Strong's results content: {results_content[:100]}...")
        
        # Take final screenshot
        page.screenshot(path="final_state.png")
        
        browser.close()

if __name__ == "__main__":
    test_strongs_button()