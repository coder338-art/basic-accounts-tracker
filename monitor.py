import time
from datetime import datetime

from tikwm_client import fetch_with_retries
from notifier import send_discord_embed
from db import init_db, upsert_account, upsert_video, insert_snapshot
from cache import load_cache, save_cache, normalize_previous_snapshot

def format_number(value: int) -> str:
    return f"{value:,}"

def run_monitor(config: dict):
    api_key = config.get("TIKWM_API_KEY", "")
    webhook = config.get("DISCORD_WEBHOOK", "")
    mention = config.get("DISCORD_MENTION_ID", "<@id>")
    interval = int(config.get("CHECK_INTERVAL", 60))
    accounts = config.get("ACCOUNTS", [])
    stage1 = int(config.get("VIRAL_STAGE_1_VIEWS", 5000))
    stage2 = int(config.get("VIRAL_STAGE_2_VIEWS", 10000))

    conn = init_db()
    cache = load_cache()
    for u in accounts:
        cache.setdefault(u, {})
    save_cache(cache)

    while True:
        for username in accounts:
            now = datetime.now().strftime("%H:%M:%S")
            print(f"[{now}] Checking {username}")
            try:
                data = fetch_with_retries(username, api_key)
                profile = data["profile"]
                videos = data.get("latest_videos", [])
                video = videos[0] if videos else {}
                current = {
                    "username": username,
                    "followers": int(profile.get("followers", 0)),
                    "views": int(video.get("views", 0)),
                    "likes": int(video.get("likes", 0)),
                    "comments": int(video.get("comments", 0)),
                    "shares": int(video.get("shares", 0)),
                    "video_id": video.get("id", ""),
                    "video_url": video.get("url", ""),
                    "video_desc": video.get("desc", ""),
                    "upload_timestamp": video.get("upload_timestamp", ""),
                    "timestamp": datetime.now().isoformat(),
                }

                prev = normalize_previous_snapshot(username, cache.get(username, {}))

                upsert_account(conn, username, profile)
                if video:
                    upsert_video(conn, username, video)
                insert_snapshot(conn, username, current)

                # New post detection
                if current["video_id"] and prev.get("video_id") != current["video_id"]:
                    send_discord_embed(
                        webhook, mention,
                        "🚨 New Video",
                        f"@{username}",
                        0xFF0000,
                        [
                            {"name": "Description", "value": current.get("video_desc", ""), "inline": False},
                            {"name": "Watch", "value": current.get("video_url", ""), "inline": False},
                        ],
                    )

                # Stage-based viral alerts (only when thresholds crossed)
                prev_views = int(prev.get("views", 0))
                cur_views = current["views"]
                if prev_views < stage1 <= cur_views:
                    send_discord_embed(
                        webhook, mention,
                        "🔥 Stage 1: Rising",
                        f"@{username} video reached {format_number(cur_views)} views",
                        0xFFA500,
                        [{"name": "Views", "value": format_number(cur_views), "inline": True}],
                    )
                if prev_views < stage2 <= cur_views:
                    send_discord_embed(
                        webhook, mention,
                        "🔥 Stage 2: Potential VIRAL",
                        f"@{username} video reached {format_number(cur_views)} views",
                        0xFFD700,
                        [
                            {"name": "Views", "value": format_number(cur_views), "inline": True},
                            {"name": "URL", "value": current.get("video_url", ""), "inline": False},
                        ],
                    )

                # Update cache
                cache[username] = {
                    "username": username,
                    "followers": current["followers"],
                    "views": current["views"],
                    "likes": current["likes"],
                    "comments": current["comments"],
                    "shares": current["shares"],
                    "video_id": current["video_id"],
                    "video_url": current["video_url"],
                    "video_desc": current["video_desc"],
                    "upload_timestamp": current["upload_timestamp"],
                    "last_checked": current["timestamp"],
                }
                save_cache(cache)

                view_gain = current["views"] - int(prev.get("views", 0))
                like_gain = current["likes"] - int(prev.get("likes", 0))
                print(f"Views: {'+'+str(view_gain) if view_gain>=0 else view_gain} | Likes: {'+'+str(like_gain) if like_gain>=0 else like_gain}")
            except Exception as e:
                print(f"Error checking {username}: {e}")
        time.sleep(interval)
