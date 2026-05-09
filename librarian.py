import uvicorn, logging, json, os
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from storage_sentry import StorageSentry

app = FastAPI(title="Ghidorah Librarian")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
sentry = StorageSentry()

@app.post("/api/v1/sessions/upload")
async def upload(weightclass: str, session_id: str, file: UploadFile = File(...)):
    try:
        content = await file.read()
        data = json.loads(content)
        return await sentry.save_session(session_id, weightclass, data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health():
    return {"status": "ONLINE", "node": "NODE_1_LIBRARIAN", "version": "8.9.9"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8081)
