import requests
import os

# Set this to your Vercel deployment URL
API_BASE = os.environ.get("LOOSEPICK_API_URL", "http://localhost:3000")


class SpotifyController:
    def __init__(self):
        self.access_token = os.environ.get("SPOTIFY_ACCESS_TOKEN", "")
        if not self.access_token:
            raise ValueError(
                "SPOTIFY_ACCESS_TOKEN not set. "
                f"Visit {API_BASE}/api/login to authenticate."
            )

    def _headers(self):
        return {"Authorization": f"Bearer {self.access_token}"}

    def get_current_track(self) -> str:
        try:
            resp = requests.get(f"{API_BASE}/api/playback/current", headers=self._headers())
            return resp.json().get("track", "Nothing playing")
        except Exception as e:
            print(f"Error fetching track: {e}")
            return "Nothing playing"

    def play_pause(self):
        try:
            requests.post(f"{API_BASE}/api/playback/play-pause", headers=self._headers())
        except Exception as e:
            print(f"Error toggling playback: {e}")

    def next_track(self):
        try:
            requests.post(f"{API_BASE}/api/playback/next", headers=self._headers())
        except Exception as e:
            print(f"Error skipping track: {e}")
