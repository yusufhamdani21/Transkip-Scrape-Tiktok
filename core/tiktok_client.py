import json
import requests
from config import RAPIDAPI_KEY, RAPIDAPI_HOST


class TikTokClient:
    def __init__(self, api_key=None):
        self.api_key = api_key or RAPIDAPI_KEY
        self.base_url = f"https://{RAPIDAPI_HOST}"
        self.headers = {
            "x-rapidapi-key": self.api_key,
            "x-rapidapi-host": RAPIDAPI_HOST,
        }

    @property
    def is_configured(self):
        return bool(self.api_key)

    def _get(self, endpoint, params=None):
        if not self.api_key:
            raise ValueError(
                "RAPIDAPI_KEY belum diatur. Setel di config.py atau env RAPIDAPI_KEY"
            )
        url = f"{self.base_url}{endpoint}"
        resp = requests.get(url, headers=self.headers, params=params, timeout=30)
        resp.raise_for_status()
        return resp.json()

    def get_trending_feed(self, region="ID"):
        data = self._get("/trending/feed", {"region": region})
        raw = data.get("data", [])
        return self._parse_videos(raw)

    def search_videos(self, keyword, count=20):
        data = self._get("/video/search", {"keyword": keyword, "count": count})
        raw = data.get("data", {}).get("videos", [])
        return self._parse_videos(raw)

    def search_hashtags(self, keyword, count=10):
        data = self._get("/challenge/search", {"keyword": keyword, "count": count})
        raw = data.get("data", {}).get("challenges", [])
        results = []
        for h in raw:
            results.append(
                {
                    "title": h.get("title", ""),
                    "video_count": h.get("videoCount", 0),
                    "view_count": h.get("viewCount", 0),
                }
            )
        return results

    def search_music(self, keyword, count=10):
        data = self._get("/music/search", {"keyword": keyword, "count": count})
        raw = data.get("data", {}).get("musics", [])
        results = []
        for m in raw:
            results.append(
                {
                    "title": m.get("title", ""),
                    "author": m.get("authorName", ""),
                    "duration": m.get("duration", 0),
                    "plays": m.get("playCount", 0),
                }
            )
        return results

    def _parse_videos(self, raw):
        videos = []
        for v in raw:
            videos.append(
                {
                    "id": v.get("video_id", ""),
                    "title": v.get("title", ""),
                    "description": v.get("description", ""),
                    "author": v.get("author", {}).get("nickname", ""),
                    "author_followers": v.get("author", {}).get(
                        "followerCount", 0
                    ),
                    "likes": v.get("stats", {}).get("diggCount", 0),
                    "comments": v.get("stats", {}).get("commentCount", 0),
                    "shares": v.get("stats", {}).get("shareCount", 0),
                    "plays": v.get("stats", {}).get("playCount", 0),
                    "duration": v.get("duration", 0),
                    "hashtags": ", ".join(
                        h.get("name", "") for h in v.get("challenge", [])
                    ),
                    "music": v.get("music", {}).get("title", ""),
                    "url": f"https://www.tiktok.com/@{v.get('author', {}).get('uniqueId', '')}/video/{v.get('video_id', '')}",
                    "cover": v.get("cover", ""),
                }
            )
        return videos
