import requests
import os

API_BASE = os.environ.get("LOOSEPICK_API_URL", "https://loose-pick-toon.vercel.app")


class SpotifyController:
    def __init__(self):
        self.access_token  = os.environ.get("SPOTIFY_ACCESS_TOKEN", "")
        self.refresh_token = os.environ.get("SPOTIFY_REFRESH_TOKEN", "")

        if not self.access_token:
            raise ValueError(
                f"No access token. Visit {API_BASE}/api/login in your browser to authenticate."
            )

    def _headers(self):
        return {"Authorization": f"Bearer {self.access_token}"}

    def _refresh(self):
        """Silently refresh the access token using the refresh token."""
        if not self.refresh_token:
            return
        try:
            resp = requests.post(f"{API_BASE}/api/refresh", json={"refresh_token": self.refresh_token})
            data = resp.json()
            if "access_token" in data:
                self.access_token = data["access_token"]
        except Exception as e:
            print(f"Token refresh failed: {e}")

    def _get(self, path):
        resp = requests.get(f"{API_BASE}{path}", headers=self._headers())
        if resp.status_code == 401:
            self._refresh()
            resp = requests.get(f"{API_BASE}{path}", headers=self._headers())
        return resp

    def _post(self, path):
        resp = requests.post(f"{API_BASE}{path}", headers=self._headers())
        if resp.status_code == 401:
            self._refresh()
            resp = requests.post(f"{API_BASE}{path}", headers=self._headers())
        return resp

    def get_current_track(self) -> str:
        try:
            data = self._get("/api/playback/current").json()
            return data.get("track", "Nothing playing")
        except Exception as e:
            print(f"Error fetching track: {e}")
            return "Nothing playing"

    def play_pause(self):
        try:
            self._post("/api/playback/play-pause")
        except Exception as e:
            print(f"Error toggling playback: {e}")

    def next_track(self):
        try:
            self._post("/api/playback/next")
        except Exception as e:
            print(f"Error skipping: {e}")

    def previous_track(self):
        try:
            self._post("/api/playback/previous")
        except Exception as e:
            print(f"Error going back: {e}")
