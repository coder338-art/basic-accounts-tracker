import json
import os
from datetime import datetime

CACHE_FILE = "cache.json"

def load_cache():
    if not os.path.exists(CACHE_FILE):
        return {}
    try:
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def save_cache(cache):
    try:
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(cache, f, indent=2)
    except Exception:
        pass

def normalize_previous_snapshot(username: str, cached: dict) -> dict:
    if not cached:
        return {}
    if "video_id" in cached:
        return cached
    return {
        "username": username,
        "followers": int(cached.get("followers", 0)),
        "views": int(cached.get("views", 0)),
        "likes": int(cached.get("likes", 0)),
        "comments": int(cached.get("comments", 0)),
        "shares": int(cached.get("shares", 0)),
        "video_id": cached.get("latest_video", ""),
        "video_url": cached.get("latest_video_url", ""),
        "video_desc": cached.get("latest_video_description", ""),
        "upload_timestamp": cached.get("upload_timestamp", ""),
        "timestamp": cached.get("last_checked", datetime.now().isoformat()),
    }
