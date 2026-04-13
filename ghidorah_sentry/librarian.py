import os
import uvicorn
import logging
import json
import re
from fastapi import FastAPI, File, UploadFile, HTTPException
from storage_sentry import StorageSentry

app = FastAPI(title="Ghidorah Sentry Librarian")
sentry = StorageSentry()

class SentryParser:
    @staticmethod
    def parse(text: str):
        tags = re.findall(r'#(\w+)', text)
        is_search = text.startswith('/')
        is_exec = text.startswith('!')
        clean = re.sub(r'#\w+', '', text).strip()
        if is_search or is_exec: clean = clean[1:].strip()
        return {"text": clean, "tags": tags, "mode": "SEARCH" if is_search else "EXEC" if is_exec else "PROMPT"}

@app.post("/api/v1/sessions/upload")
async def upload(weightclass: str, session_id: str, file: UploadFile = File(...)):
    try:
        content = await file.read()
        data = json.loads(content)
        return await sentry.save_session(session_id, weightclass, data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/sentry/parse")
async def parse_prompt(payload: dict):
    return SentryParser.parse(payload.get("text", ""))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
