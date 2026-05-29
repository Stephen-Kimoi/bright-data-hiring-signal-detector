import json
import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

load_dotenv(Path(__file__).parent.parent / ".env")

from scraper import fetch_jobs_for_company
from analyzer import analyze_jobs

app = FastAPI(title="Hiring Signal Detector")

FRONTEND_DIR = Path(__file__).parent.parent / "frontend"
WATCHLIST_PATH = Path(__file__).parent.parent / "watchlist.json"

app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")


@app.get("/", response_class=FileResponse)
def index():
    return FRONTEND_DIR / "index.html"


@app.get("/watchlist")
def get_watchlist():
    with open(WATCHLIST_PATH) as f:
        return json.load(f)


class AnalyzeRequest(BaseModel):
    company: str
    linkedin_url: str


@app.post("/analyze")
def analyze(req: AnalyzeRequest):
    try:
        jobs = fetch_jobs_for_company(req.linkedin_url)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Bright Data error: {e}")

    if not jobs:
        raise HTTPException(status_code=404, detail=f"No job postings found for {req.company}")

    try:
        brief = analyze_jobs(req.company, jobs)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Gemini error: {e}")

    return {"company": req.company, "job_count": len(jobs), "brief": brief}
