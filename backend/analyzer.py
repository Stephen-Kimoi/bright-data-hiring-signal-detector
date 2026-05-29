import os
import json
from google import genai
from google.genai import types

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
MODEL = "gemini-2.5-flash"

SYSTEM_PROMPT = """You are an expert analyst who reads company job posting data as alternative financial intelligence.
Given a list of recent job postings for a company, produce a structured growth signal brief.

Respond ONLY with valid JSON in this exact schema:
{
  "company": "string",
  "signal_summary": "2-3 sentence plain-English verdict on trajectory (growing, pivoting, contracting, stable)",
  "signals": [
    {
      "type": "string (one of: hiring_velocity, department_expansion, seniority_shift, tech_stack_pivot, geographic_expansion, contraction)",
      "description": "string",
      "evidence": "string (cite specific job titles or patterns from the data)"
    }
  ],
  "department_breakdown": {
    "Engineering": 0,
    "Sales": 0,
    "Marketing": 0,
    "Operations": 0,
    "Product": 0,
    "Other": 0
  },
  "top_roles": ["string", "string", "string"],
  "confidence": "high | medium | low",
  "confidence_reason": "string"
}"""


def analyze_jobs(company: str, jobs: list[dict]) -> dict:
    """Pass job listing data to Gemini 2.5 Pro and return a structured intelligence brief."""
    client = genai.Client(api_key=GEMINI_API_KEY)

    jobs_text = json.dumps(
        [
            {
                "title": j.get("job_title", ""),
                "function": j.get("job_function", ""),
                "seniority": j.get("job_seniority_level", ""),
                "location": j.get("job_location", ""),
                "posted": j.get("job_posted_date", ""),
                "employment_type": j.get("job_employment_type", ""),
            }
            for j in jobs
        ],
        indent=2,
    )

    prompt = f"Company: {company}\nTotal job postings: {len(jobs)}\n\nJob data:\n{jobs_text}"

    response = client.models.generate_content(
        model=MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            temperature=0.2,
            response_mime_type="application/json",
        ),
    )

    return json.loads(response.text)
