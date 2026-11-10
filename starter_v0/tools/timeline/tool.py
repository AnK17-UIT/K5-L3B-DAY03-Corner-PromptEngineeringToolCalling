from __future__ import annotations

import os
import re
from typing import Any

import requests

from tools._shared import TIMEOUT


def _twitter_get(path: str, params: dict[str, Any]) -> dict[str, Any]:
    key = os.getenv("RAPIDAPI_KEY")
    host = os.getenv("RAPIDAPI_TWITTER_HOST", "twitter-api45.p.rapidapi.com")
    if not key:
        raise RuntimeError("Missing RAPIDAPI_KEY env var")
    response = requests.get(
        f"https://{host}{path}",
        params=params,
        headers={"x-rapidapi-key": key, "x-rapidapi-host": host},
        timeout=TIMEOUT,
    )
    response.raise_for_status()
    return response.json()


def _tweet_item(raw: dict[str, Any]) -> dict[str, Any]:
    handle = raw.get("screen_name") or (raw.get("author") or {}).get("screen_name") or ""
    tweet_id = raw.get("tweet_id") or raw.get("id") or ""
    text = (raw.get("text") or "").strip()
    return {
        "title": text.split("\n")[0][:120],
        "summary": text,
        "url": f"https://x.com/{handle}/status/{tweet_id}" if handle and tweet_id else "",
        "source": f"@{handle}" if handle else "x.com",
        "date": raw.get("created_at"),
        "metrics": {"favorites": raw.get("favorites"), "retweets": raw.get("retweets"), "views": raw.get("views")},
    }


def _tweets_from(data: dict[str, Any], limit: int) -> list[dict[str, Any]]:
    raw_items = data.get("timeline") or data.get("tweets") or []
    items = [_tweet_item(item) for item in raw_items if item.get("tweet_id") or item.get("id")]
    return items[: int(limit or 5)]


def get_user_tweets(screenname: str = "", limit: int = 5, verify_only: bool = False) -> dict[str, Any]:
    if not isinstance(screenname, str) or not re.fullmatch(r"[A-Za-z0-9_]{1,15}", screenname):
        return {"error": "invalid_handle", "items": []}

    params = {"screenname": screenname}
    result = {"tool": "get_user_tweets", "screenname": screenname, "items": []}
    try:
        profile = _twitter_get("/screenname.php", params)
    except Exception:
        return {**result, "account_status": "unverified"}

    if profile.get("status") == "notfound":
        return {**result, "account_status": "not_found"}

    actual_handle = profile.get("profile")
    if not isinstance(actual_handle, str) or actual_handle.casefold() != screenname.casefold():
        return {**result, "account_status": "unverified"}

    result.update(
        account_status="found",
        screenname=actual_handle,
        display_name=profile.get("name"),
        profile_url=f"https://x.com/{actual_handle}",
    )
    if verify_only:
        return result

    try:
        data = _twitter_get("/timeline.php", {"screenname": actual_handle})
        result["items"] = _tweets_from(data, limit)
    except Exception:
        result["error"] = "timeline_unavailable"
    return result
