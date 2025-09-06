#!/usr/bin/env python3
"""
Test the God Facts functionality
"""

import asyncio
from playwright.async_api import async_playwright

async def test_god_facts():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        
        try:
            print("🌟 Testing God Facts functionality...")
            
            # Navigate to the app
            await page.goto("http://localhost:5002")
            await page.wait_for_load_state("networkidle")
            
            # Click on God Facts button
            print("📖 Clicking on God Facts section...")
            await page.click('button.nav-btn:has-text("God Facts")')
            await page.wait_for_timeout(2000)
            
            # Check if facts are loaded
            facts = await page.query_selector_all('.fact-card')
            print(f"✅ Found {len(facts)} God facts")
            
            if len(facts) > 0:
                # Test clicking on a fact
                print("📋 Testing fact details...")
                read_more_btn = await page.query_selector('.read-more-btn')
                if read_more_btn:
                    await read_more_btn.click()
                    await page.wait_for_timeout(1000)
                    
                    # Check if modal appeared
                    modal = await page.query_selector('.fact-modal')
                    if modal:
                        print("✅ Fact modal opened successfully")
                        # Close modal
                        close_btn = await page.query_selector('.fact-modal-close')
                        if close_btn:
                            await close_btn.click()
                            await page.wait_for_timeout(500)
            
            # Test category filtering
            print("🏷️ Testing category filters...")
            science_btn = await page.query_selector('button.filter-btn:has-text("Science")')
            if science_btn:
                await science_btn.click()
                await page.wait_for_timeout(2000)
                
                filtered_facts = await page.query_selector_all('.fact-card')
                print(f"✅ Science filter shows {len(filtered_facts)} facts")
            
            # Test admin dashboard
            print("🔧 Testing Admin Dashboard...")
            await page.click('button.nav-btn:has-text("Admin")')
            await page.wait_for_timeout(2000)
            
            # Check admin stats
            total_facts = await page.text_content('#total-facts')
            published_facts = await page.text_content('#published-facts')
            print(f"📊 Admin stats - Total: {total_facts}, Published: {published_facts}")
            
            # Test add fact form
            add_btn = await page.query_selector('button:has-text("Add New Fact")')
            if add_btn:
                await add_btn.click()
                await page.wait_for_timeout(1000)
                
                form = await page.query_selector('#add-fact-form')
                if form and not await form.is_hidden():
                    print("✅ Add fact form opened successfully")
                    
                    # Close form
                    cancel_btn = await page.query_selector('.cancel-btn')
                    if cancel_btn:
                        await cancel_btn.click()
                        await page.wait_for_timeout(500)
            
            print("🎉 All God Facts tests completed successfully!")
            
            await page.screenshot(path='god_facts_test.png')
            await page.wait_for_timeout(3000)
            
        except Exception as e:
            print(f"❌ Test failed: {e}")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(test_god_facts())