import os
import time
import httpx
from typing import Any

BRIGHT_DATA_API_KEY = os.getenv("BRIGHT_DATA_API_KEY")
LINKEDIN_JOBS_DATASET_ID = "gd_lpfll7v5hcqtkxl6l"
BASE_URL = "https://api.brightdata.com/datasets/v3"
JOBS_PER_COMPANY = 25


def _headers() -> dict:
    return {
        "Authorization": f"Bearer {BRIGHT_DATA_API_KEY}",
        "Content-Type": "application/json",
    }


def trigger_jobs_discover(company: str, location: str = "United States") -> str:
    """Trigger a discover_new scrape for a company's job listings. Returns snapshot_id."""
    url = (
        f"{BASE_URL}/trigger"
        f"?dataset_id={LINKEDIN_JOBS_DATASET_ID}"
        f"&type=discover_new"
        f"&discover_by=keyword"
        f"&limit_per_input={JOBS_PER_COMPANY}"
        f"&include_errors=true"
        f"&format=json"
    )
    payload = [{"company": company, "location": location}]
    with httpx.Client(timeout=30) as client:
        resp = client.post(url, json=payload, headers=_headers())
        resp.raise_for_status()
        return resp.json()["snapshot_id"]


def poll_snapshot(snapshot_id: str, max_wait: int = 180) -> list[dict[str, Any]]:
    """Poll until snapshot is ready, then return the job records."""
    status_url = f"{BASE_URL}/snapshot/{snapshot_id}?format=json"
    deadline = time.time() + max_wait
    with httpx.Client(timeout=30) as client:
        while time.time() < deadline:
            resp = client.get(status_url, headers=_headers())
            if resp.status_code == 200:
                return resp.json()
            if resp.status_code == 202:
                time.sleep(8)
                continue
            resp.raise_for_status()
    raise TimeoutError(f"Snapshot {snapshot_id} not ready after {max_wait}s")


def fetch_jobs_for_company(company: str, location: str = "United States") -> list[dict[str, Any]]:
    """Full flow: trigger discover scrape, poll, return job records."""
    snapshot_id = trigger_jobs_discover(company, location)
    jobs = poll_snapshot(snapshot_id)
    # Filter out error/metadata records — keep only records with a job_title
    return [j for j in jobs if j.get("job_title")]
