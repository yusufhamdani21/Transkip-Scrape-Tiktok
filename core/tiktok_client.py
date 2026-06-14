import requests
from config import RAPIDAPI_KEY, RAPIDAPI_HOST


class TikTokClient:
    def __init__(self, api_key=None):
        self.api_key = api_key or RAPIDAPI_KEY
        self.base_url = f"https://{RAPIDAPI_HOST}"

    @property
    def headers(self):
        return {
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
        videos = self._parse_videos(raw)
        if region:
            videos = [v for v in videos if v.get("region", "").upper() == region.upper()]
        return videos

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
            author = v.get("author") or {}
            videos.append(
                {
                    "id": v.get("video_id") or "",
                    "title": v.get("title") or "",
                    "description": v.get("title") or "",
                    "author": author.get("nickname") or "",
                    "author_username": author.get("unique_id") or "",
                    "author_avatar": author.get("avatar") or "",
                    "likes": v.get("digg_count") or 0,
                    "comments": v.get("comment_count") or 0,
                    "shares": v.get("share_count") or 0,
                    "plays": v.get("play_count") or 0,
                    "duration": v.get("duration") or 0,
                    "hashtags": "",
                    "music": (v.get("music_info") or {}).get("title") or "",
                    "url": f"https://www.tiktok.com/@{(author.get('unique_id') or '')}/video/{(v.get('video_id') or '')}",
                    "cover": v.get("cover") or "",
                    "region": v.get("region") or "",
                    "create_time": v.get("create_time") or 0,
                }
            )
        return videos
