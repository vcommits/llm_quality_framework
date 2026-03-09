# File: browser_agent_server.py
# Purpose: Runs on Node 3 (iMac) to execute heavy Playwright browser tasks.

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from playwright.async_api import async_playwright
import uvicorn
import asyncio
import base64
import os

app = FastAPI()

class BrowserTask(BaseModel):
    url: str
    prompt: str
    scenario: str = "default"

@app.post("/run_browser_task")
async def run_browser_task(task: BrowserTask):
    print(f"🚀 Received Task: {task.scenario} -> {task.url}")
    
    async with async_playwright() as p:
        # Launch browser (Headful mode for debugging on iMac, or headless=True for speed)
        browser = await p.chromium.launch(headless=False) 
        context = await browser.new_context()
        page = await context.new_page()
        
        try:
            # 1. Navigate
            await page.goto(task.url)
            await page.wait_for_load_state("networkidle")
            
            # 2. Execute Scenario (Simplified generic logic)
            # In a real agent, this would be complex logic based on 'task.scenario'
            if "chat" in task.url:
                # Example: Generic chat interface interaction
                # This selector is a placeholder; needs to be specific to the target site
                await page.get_by_role("textbox").fill(task.prompt)
                await page.get_by_role("textbox").press("Enter")
                await page.wait_for_timeout(5000) # Wait for response
            
            # 3. Capture Evidence
            screenshot_bytes = await page.screenshot()
            screenshot_b64 = base64.b64encode(screenshot_bytes).decode("utf-8")
            
            # 4. Extract Text (Simple dump)
            content = await page.content()
            
            await browser.close()
            
            return {
                "status": "success",
                "screenshot": screenshot_b64,
                "content_length": len(content),
                "message": "Task executed successfully on Node 3"
            }
            
        except Exception as e:
            await browser.close()
            print(f"❌ Error: {e}")
            raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    # Run on 0.0.0.0 to allow access from Node 1 (Pi) and Node 2 (Laptop)
    print("🖥️ Browser Agent Server running on Node 3...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
