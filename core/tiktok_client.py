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

    def get_trending_feed(self, region="ID", count=20):
        data = self._get("/feed/list", {"region": region, "count": count})
        raw = data.get("data", [])
        return self._parse_videos(raw)

    def get_user_info(self, unique_id):
        data = self._get("/user/info", {"unique_id": unique_id})
        return data.get("data", {})

    def get_user_posts(self, unique_id, count=20):
        data = self._get("/user/posts", {"unique_id": unique_id, "count": count})
        raw = data.get("data", [])
        return self._parse_videos(raw)

    def get_comments(self, url, count=20):
        data = self._get("/comment/list", {"url": url, "count": count})
        return data.get("data", [])

    def _parse_videos(self, raw):
        videos = []
        for v in raw:
            author = v.get("author", {}) or {}
            videos.append(
                {
                    "id": v.get("video_id", ""),
                    "title": v.get("title", ""),
                    "description": v.get("title", ""),
                    "author": author.get("nickname", ""),
                    "author_username": author.get("unique_id", ""),
                    "author_avatar": author.get("avatar", ""),
                    "likes": v.get("digg_count", 0),
                    "comments": v.get("comment_count", 0),
                    "shares": v.get("share_count", 0),
                    "plays": v.get("play_count", 0),
                    "duration": v.get("duration", 0),
                    "hashtags": "",
                    "music": v.get("music_info", {}).get("title", ""),
                    "url": f"https://www.tiktok.com/@{author.get('unique_id', '')}/video/{v.get('video_id', '')}",
                    "cover": v.get("cover", ""),
                    "region": v.get("region", ""),
                    "create_time": v.get("create_time", 0),
                }
            )
        return videos
