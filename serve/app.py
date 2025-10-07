# serve/app.py
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from scripts.pipeline import infer_line

app = FastAPI(title="ChandaShastra MVP API")

# CORS: allow your UI (dev) origin(s).
# For development you can allow all origins with ["*"], but for production use specific origins.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5173", "http://localhost:5173", "http://127.0.0.1:3000", "http://localhost:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],  # allows POST, OPTIONS, GET, etc.
    allow_headers=["*"],
)

class InReq(BaseModel):
    text: str
    sandhi: bool = True

@app.post("/scan")
def scan(req: InReq):
    """
    Accepts JSON: { "text": "...", "sandhi": true/false }
    Returns pipeline result.
    """
    out = infer_line(req.text, use_sandhi=req.sandhi)
    return out
