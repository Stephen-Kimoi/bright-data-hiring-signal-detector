# Company Growth Signal Detector

Reads LinkedIn job postings as alternative financial intelligence. Give it a watchlist of companies, and it returns a structured brief per company — hiring velocity, department expansion, seniority shifts, tech stack pivots — before any of it shows up in a press release.

Built with [Bright Data's Web Scraper API](https://brightdata.com/products/web-scraper) and [Gemini 2.5 Flash](https://ai.google.dev/gemini-api/docs).

![Company Growth Signal Detector UI](https://imagedelivery.net/K11gkZF3xaVyYzFESMdWIQ/hiring-signal-ui-results-top/public)

---

## How it works

1. Bright Data's LinkedIn Jobs dataset (`discover_new` mode) scrapes live job postings for each company in your watchlist
2. Gemini 2.5 Flash analyzes the job data and returns a structured JSON brief with typed signals and cited evidence
3. A FastAPI backend serves the data, a vanilla JS frontend renders the briefs

---

## Prerequisites

- Python 3.10+
- [Bright Data account](https://brightdata.com) — API key from **Settings**
- [Google AI Studio account](https://aistudio.google.com) — Gemini API key

---

## Setup

```bash
git clone https://github.com/Stephen-Kimoi/bright-data-hiring-signal-detector.git
cd bright-data-hiring-signal-detector
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and fill in your keys:

```bash
cp .env.example .env
```

```text
BRIGHT_DATA_API_KEY=your_bright_data_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here
```

---

## Run

```bash
uvicorn backend.main:app --reload --port 8000
```

Open `http://localhost:8000`.

---

## Customize your watchlist

Edit `watchlist.json` to track any companies you want:

```json
[
  { "company": "Stripe", "location": "United States" },
  { "company": "Notion", "location": "United States" }
]
```

You can also add companies directly from the UI without restarting the server.

---

## Project structure

```
├── backend/
│   ├── main.py        — FastAPI app (watchlist + analyze endpoints)
│   ├── scraper.py     — Bright Data trigger/poll flow
│   └── analyzer.py    — Gemini structured analysis
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── app.js
├── watchlist.json     — companies to track
├── .env.example
└── requirements.txt
```

---

## Tutorial

Full step-by-step tutorial on [Lablab.ai](https://lablab.ai/t/bright-data-hiring-signal-detector).
