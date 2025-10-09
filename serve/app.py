# serve/app.py
import os
import logging
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# import your pipeline helpers
# Make sure scripts is on PYTHONPATH (it should be if repo layout is standard).
try:
    from scripts.pipeline import infer_line, syllabify_devanagari  # type: ignore
except Exception as e:
    # If something in scripts.pipeline raises on import, we still want the app to start.
    infer_line = None  # type: ignore
    syllabify_devanagari = None  # type: ignore
    logging.exception("Failed to import pipeline module. /scan will return error until fixed: %s", e)


# -------- logging --------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("chand-serve")


# -------- FastAPI app --------
app = FastAPI(title="Chandas Identifier API", version="0.1")


# -------- CORS configuration (robust) --------
# Behavior:
#  - Read ALLOWED_ORIGINS env var (comma-separated). If not present, we default to
#    localhost origins plus a recommended Vercel domain placeholder.
#  - If ALLOWED_ORIGINS == "*" we allow all origins but set allow_credentials=False
#    (browsers disallow wildcard origin with credentials).
#
# Set environment variable on Render:
#   ALLOWED_ORIGINS="http://localhost:5173,http://localhost:3000,https://your-vercel-app.vercel.app"
#
_allowed_env = os.environ.get("ALLOWED_ORIGINS", "").strip()

if not _allowed_env:
    # sensible defaults for local dev + typical Vercel preview
    default_frontend = os.environ.get("VITE_API_BASE_FRONTEND", "https://chand-identifier.vercel.app")
    origins = [
        "http://localhost:5173",   # Vite dev default
        "http://localhost:3000",   # CRA default
        default_frontend           # replaceable via env
    ]
else:
    # parse comma-separated list
    origins = [o.strip() for o in _allowed_env.split(",") if o.strip()]

# handle wildcard case
if len(origins) == 1 and origins[0] == "*":
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )
else:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

logger.info("CORS origins: %s", origins)


# -------- request/response models --------
class ScanRequest(BaseModel):
    text: str
    sandhi: Optional[bool] = True


# -------- health route --------
@app.get("/")
async def root():
    return {"status": "ok", "service": "chand-identifier", "message": "ready"}


# -------- scan route --------
@app.post("/scan")
async def scan(req: ScanRequest, request: Request):
    """
    Main API: analyze the given Sanskrit line for syllable segmentation and chandas.
    Body: { "text": "...", "sandhi": true }
    """
    if not req.text or not isinstance(req.text, str) or not req.text.strip():
        raise HTTPException(status_code=400, detail="`text` must be a non-empty string.")

    if infer_line is None:
        # pipeline import failed earlier
        logger.error("Pipeline not available; cannot process /scan")
        raise HTTPException(status_code=500, detail="Pipeline not available on server. Check logs.")

    try:
        # call pipeline
        result = infer_line(req.text, use_sandhi=bool(req.sandhi))
        # ensure result is JSON-serializable
        return result
    except Exception as e:
        logger.exception("Error during infer_line for text: %s", req.text)
        # return 500 with minimal message; details are in logs
        raise HTTPException(status_code=500, detail="Internal Server Error while analyzing text.")


# -------- optional debug endpoint (syllabify only) --------
@app.post("/syllabify")
async def syllabify_endpoint(req: ScanRequest):
    if not req.text or not isinstance(req.text, str) or not req.text.strip():
        raise HTTPException(status_code=400, detail="`text` must be a non-empty string.")
    if syllabify_devanagari is None:
        raise HTTPException(status_code=500, detail="Syllabifier not available on server.")
    try:
        s = syllabify_devanagari(req.text)
        return {"text": req.text, "syllables": s, "count": len(s)}
    except Exception as e:
        logger.exception("Error in syllabify_endpoint: %s", e)
        raise HTTPException(status_code=500, detail="Internal Server Error while syllabifying text.")


# -------- startup/shutdown hooks (placeholders) --------
@app.on_event("startup")
async def startup_event():
    # If you later want to download a model on startup when enabling ML, do it here.
    # For now we intentionally do not auto-load heavy model weights.
    logger.info("Server startup complete. Pipeline available: %s", infer_line is not None)


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Server shutdown.")


# -------- uvicorn entry (if run directly) --------
if __name__ == "__main__":
    # run with: python serve/app.py  OR uvicorn serve.app:app --host 0.0.0.0 --port 8000
    import uvicorn

    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("serve.app:app", host="0.0.0.0", port=port, log_level="info")
