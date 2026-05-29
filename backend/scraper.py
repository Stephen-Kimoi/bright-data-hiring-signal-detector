import os
import time
import httpx
from typing import Any

BRIGHT_DATA_API_KEY = os.getenv("BRIGHT_DATA_API_KEY")
LINKEDIN_JOBS_DATASET_ID = "gd_lpfll7v5hcqtkxl6l"
BASE_URL = "https://api.brightdata.com/datasets/v3"


def _headers() -> dict:
    return {
        "Authorization": f"Bearer {BRIGHT_DATA_API_KEY}",
        "Content-Type": "application/json",
    }


def trigger_jobs_scrape(linkedin_url: str) -> str:
    """Trigger an async scrape for job listings at a LinkedIn company URL. Returns snapshot_id."""
    payload = [{"url": linkedin_url}]
    url = f"{BASE_URL}/trigger?dataset_id={LINKEDIN_JOBS_DATASET_ID}&format=json&uncompressed_webhook=true"
    with httpx.Client(timeout=30) as client:
        resp = client.post(url, json=payload, headers=_headers())
        resp.raise_for_status()
        data = resp.json()
        return data["snapshot_id"]


def poll_snapshot(snapshot_id: str, max_wait: int = 120) -> list[dict[str, Any]]:
    """Poll until snapshot is ready, then return the job records."""
    status_url = f"{BASE_URL}/snapshot/{snapshot_id}?format=json"
    deadline = time.time() + max_wait
    with httpx.Client(timeout=30) as client:
        while time.time() < deadline:
            resp = client.get(status_url, headers=_headers())
            if resp.status_code == 200:
                return resp.json()
            if resp.status_code == 202:
                time.sleep(5)
                continue
            resp.raise_for_status()
    raise TimeoutError(f"Snapshot {snapshot_id} not ready after {max_wait}s")


def fetch_jobs_for_company(jobs_url: str) -> list[dict[str, Any]]:
    """Full flow: trigger scrape, poll, return job records."""
    snapshot_id = trigger_jobs_scrape(jobs_url)
    return poll_snapshot(snapshot_id)
