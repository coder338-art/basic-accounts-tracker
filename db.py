import sqlite3
from datetime import datetime

DB_FILE = "tiktok_stats.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS accounts (
            username TEXT PRIMARY KEY,
            nickname TEXT,
            followers INTEGER,
            following INTEGER,
            hearts INTEGER,
            video_count INTEGER,
            last_seen TEXT
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS videos (
            id TEXT PRIMARY KEY,
            username TEXT NOT NULL,
            description TEXT,
            url TEXT,
            upload_timestamp TEXT,
            views INTEGER,
            likes INTEGER,
            comments INTEGER,
            shares INTEGER
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS snapshots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            followers INTEGER,
            views INTEGER,
            likes INTEGER,
            comments INTEGER,
            shares INTEGER,
            video_id TEXT,
            video_url TEXT
        )
        """
    )
    conn.commit()
    return conn

def upsert_account(conn, username, profile):
    conn.execute(
        """
        INSERT INTO accounts(username, nickname, followers, following, hearts, video_count, last_seen)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(username) DO UPDATE SET
            nickname=excluded.nickname,
            followers=excluded.followers,
            following=excluded.following,
            hearts=excluded.hearts,
            video_count=excluded.video_count,
            last_seen=excluded.last_seen
        """,
        (
            username,
            profile.get("nickname", ""),
            profile.get("followers", 0),
            profile.get("following", 0),
            profile.get("hearts", 0),
            profile.get("video_count", 0),
            datetime.now().isoformat(),
        ),
    )
    conn.commit()

def upsert_video(conn, username, video):
    conn.execute(
        """
        INSERT INTO videos(id, username, description, url, upload_timestamp, views, likes, comments, shares)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(id) DO UPDATE SET
            username=excluded.username,
            description=excluded.description,
            url=excluded.url,
            upload_timestamp=excluded.upload_timestamp,
            views=excluded.views,
            likes=excluded.likes,
            comments=excluded.comments,
            shares=excluded.shares
        """,
        (
            video.get("id", ""),
            username,
            video.get("desc", ""),
            video.get("url", ""),
            video.get("upload_timestamp", ""),
            video.get("views", 0),
            video.get("likes", 0),
            video.get("comments", 0),
            video.get("shares", 0),
        ),
    )
    conn.commit()

def insert_snapshot(conn, username, snapshot):
    conn.execute(
        """
        INSERT INTO snapshots(username, timestamp, followers, views, likes, comments, shares, video_id, video_url)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            username,
            snapshot.get("timestamp"),
            snapshot.get("followers", 0),
            snapshot.get("views", 0),
            snapshot.get("likes", 0),
            snapshot.get("comments", 0),
            snapshot.get("shares", 0),
            snapshot.get("video_id", ""),
            snapshot.get("video_url", ""),
        ),
    )
    conn.commit()
