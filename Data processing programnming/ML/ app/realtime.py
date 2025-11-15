import os
import asyncio
import logging
from datetime import datetime
from typing import Dict, Any, Optional

import httpx

from app import storage
from app.engine.recommender import recommend_pipeline

logger = logging.getLogger("realtime")
logger.setLevel(logging.INFO)

REALTIME_API_URL = os.getenv("REALTIME_API_URL", "").strip()
POLL_INTERVAL = int(os.getenv("POLL_INTERVAL", "30"))
LOCATION_ID = os.getenv("REALTIME_LOCATION_ID", "RT-001")

async def fetch_realtime_data(client: httpx.AsyncClient, url: str, timeout: int = 10) -> Optional[Dict[str, Any]]:
    """
    Fetch data from your realtime API. Assumes GET and JSON response by default.
    If your API uses POST or requires auth, modify this function to include headers, payload, or auth.
    """
    try:
        r = await client.get(url, timeout=timeout)
        r.raise_for_status()
        data = r.json()
        if isinstance(data, dict):
            return data
        logger.warning("Realtime API returned non-dict JSON: %s", type(data))
    except Exception as e:
        logger.exception("Error fetching realtime data: %s", e)
    return None

def map_to_features(payload: Dict[str, Any]) -> Dict[str, float]:
    """
    Map remote JSON fields to features expected by our engine.
    Modify this mapping if your realtime API uses different field names.
    """
    # default mapping - keep consistent with data/example_request.json
    features = {
        "temp_c": float(payload.get("temp_c", payload.get("temperature", 0.0) or 0.0)),
        "humidity": float(payload.get("humidity", 0.0)),
        "power_usage_kw": float(payload.get("power_usage_kw", payload.get("power_kw", 0.0) or 0.0)),
        "traffic_index": float(payload.get("traffic_index", payload.get("traffic", 0.0) or 0.0)),
        "production_rate": float(payload.get("production_rate", 1.0)),
        "co2_measured": float(payload.get("co2_measured", payload.get("co2", 0.0) or 0.0)),
        "is_working_day": int(payload.get("is_working_day", payload.get("working_day", 1) or 1))
    }
    return features

async def realtime_poller_loop():
    if not REALTIME_API_URL:
        logger.info("REALTIME_API_URL not set - realtime poller disabled.")
        return

    logger.info("Starting realtime poller for %s (interval %s s)", REALTIME_API_URL, POLL_INTERVAL)
    async with httpx.AsyncClient() as client:
        while True:
            try:
                remote = await fetch_realtime_data(client, REALTIME_API_URL)
                if remote:
                    features = map_to_features(remote)
                    timestamp = datetime.utcnow().isoformat() + "Z"
                    ctx = {
                        "timestamp": timestamp,
                        "location_id": LOCATION_ID,
                        "features": features,
                        "constraints": remote.get("constraints"),  # optionally pass through
                        "weights": remote.get("weights")  # optionally pass through
                    }
                    # Save context
                    storage.save_context(ctx)
                    logger.info("Saved realtime context: %s %s", LOCATION_ID, timestamp)

                    # Run recommend pipeline (synchronous function) - note: recommender may be CPU bound; keep it short for demo
                    try:
                        rec = recommend_pipeline(timestamp, LOCATION_ID, features, ctx.get("constraints"), ctx.get("weights"))
                        storage.save_recommendation({
                            "timestamp": timestamp,
                            "location_id": LOCATION_ID,
                            "features": features,
                            "recommendation": rec
                        })
                        logger.info("Realtime recommendation computed: top1=%s", rec["recommended"][0]["action_ids"] if rec["recommended"] else None)
                    except Exception as e:
                        logger.exception("Error running recommendation pipeline: %s", e)
                else:
                    logger.debug("No data from realtime API this cycle.")
            except Exception:
                logger.exception("Unexpected error in realtime poller loop.")
            await asyncio.sleep(POLL_INTERVAL)

async def start_realtime_poller_on_startup():
    """
    Start a background task for the poller. Call this in FastAPI startup event.
    """
    if not REALTIME_API_URL:
        logger.info("Realtime poller is disabled (REALTIME_API_URL not set).")
        return
    # create background task without awaiting
    loop = asyncio.get_event_loop()
    loop.create_task(realtime_poller_loop())