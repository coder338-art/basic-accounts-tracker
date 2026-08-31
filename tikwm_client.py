import time
import requests
from datetime import datetime

BASE = "https://api.tikwmapi.com"

def _get_json(url, params, headers):
    resp = requests.get(url, params=params, headers=headers, timeout=15)
    try:
        return resp.json()
    except ValueError:
        raise RuntimeError(
            f"Non-JSON response (status {resp.status_code}) from {url}: {resp.text[:300]!r}"
        )

def get_profile_and_videos(username: str, api_key: str, video_count: int = 1):
    headers = {"x-tikwmapi-key": api_key}
    user_resp = _get_json(
        f"{BASE}/user/info",
        params={"unique_id": username},
        headers=headers,
    )

    if user_resp.get("code") != 0:
        raise RuntimeError(f"user/info failed: {user_resp}")

    u = user_resp["data"]
    profile = {
        "username": u["user"]["uniqueId"],
        "nickname": u["user"].get("nickname", ""),
        "followers": u["stats"].get("followerCount", 0),
        "following": u["stats"].get("followingCount", 0),
        "hearts": u["stats"].get("heartCount", 0),
        "video_count": u["stats"].get("videoCount", 0),
    }

    posts_resp = _get_json(
        f"{BASE}/user/posts",
        params={"unique_id": username, "count": video_count},
        headers=headers,
    )

    if posts_resp.get("code") != 0:
        raise RuntimeError(f"user/posts failed: {posts_resp}")

    videos = []
    for v in posts_resp["data"].get("videos", []):
        vid = v.get("video_id", "")
        videos.append({
            "id": vid,
            "desc": v.get("title", ""),
            "views": v.get("play_count", 0),
            "likes": v.get("digg_count", 0),
            "comments": v.get("comment_count", 0),
            "shares": v.get("share_count", 0),
            "upload_timestamp": v.get("create_time", "") or v.get("createTime", ""),
            "url": f"https://www.tiktok.com/@{username}/video/{vid}" if vid else "",
        })

    return {"profile": profile, "latest_videos": videos}

def fetch_with_retries(username: str, api_key: str, max_retries: int = 3):
    last_error = None
    for attempt in range(1, max_retries + 1):
        try:
            return get_profile_and_videos(username, api_key, video_count=1)
        except requests.RequestException as exc:
            last_error = exc
        except Exception as exc:
            last_error = exc
        if attempt < max_retries:
            time.sleep(2)
    raise RuntimeError(f"API failed for {username}: {last_error}")
