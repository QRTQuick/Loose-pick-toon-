from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import requests
import json

SPOTIFY_API = "https://api.spotify.com/v1/me/player"


class handler(BaseHTTPRequestHandler):

    def do_GET(self):
        parsed = urlparse(self.path)
        token = self._get_token()
        if not token:
            self._respond(401, {"error": "missing Authorization header"})
            return

        headers = {"Authorization": f"Bearer {token}"}

        # /api/playback/current
        if parsed.path == "/api/playback/current":
            resp = requests.get(SPOTIFY_API, headers=headers)
            if resp.status_code == 204:
                self._respond(200, {"track": "Nothing playing"})
                return
            data = resp.json()
            item = data.get("item")
            if item:
                artist = item["artists"][0]["name"]
                name = item["name"]
                is_playing = data.get("is_playing", False)
                self._respond(200, {
                    "track": f"{artist} - {name}",
                    "is_playing": is_playing
                })
            else:
                self._respond(200, {"track": "Nothing playing", "is_playing": False})
            return

        self._respond(404, {"error": "not found"})

    def do_POST(self):
        parsed = urlparse(self.path)
        token = self._get_token()
        if not token:
            self._respond(401, {"error": "missing Authorization header"})
            return

        headers = {"Authorization": f"Bearer {token}"}

        # /api/playback/play-pause
        if parsed.path == "/api/playback/play-pause":
            state = requests.get(SPOTIFY_API, headers=headers)
            if state.status_code == 200 and state.json().get("is_playing"):
                requests.put(f"{SPOTIFY_API}/pause", headers=headers)
            else:
                requests.put(f"{SPOTIFY_API}/play", headers=headers)
            self._respond(200, {"ok": True})
            return

        # /api/playback/next
        if parsed.path == "/api/playback/next":
            requests.post(f"{SPOTIFY_API}/next", headers=headers)
            self._respond(200, {"ok": True})
            return

        self._respond(404, {"error": "not found"})

    def _get_token(self):
        auth = self.headers.get("Authorization", "")
        if auth.startswith("Bearer "):
            return auth[7:]
        return None

    def _respond(self, status: int, body: dict):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(body).encode())
