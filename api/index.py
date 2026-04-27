from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import requests
import os
import json

CLIENT_ID = os.environ["SPOTIFY_CLIENT_ID"]
CLIENT_SECRET = os.environ["SPOTIFY_CLIENT_SECRET"]
REDIRECT_URI = os.environ["SPOTIFY_REDIRECT_URI"]
SCOPE = "user-read-playback-state user-modify-playback-state"

AUTH_URL = "https://accounts.spotify.com/authorize"
TOKEN_URL = "https://accounts.spotify.com/api/token"


class handler(BaseHTTPRequestHandler):

    def do_GET(self):
        parsed = urlparse(self.path)

        # /api/login — redirect user to Spotify auth
        if parsed.path == "/api/login":
            params = (
                f"?client_id={CLIENT_ID}"
                f"&response_type=code"
                f"&redirect_uri={REDIRECT_URI}"
                f"&scope={SCOPE}"
            )
            self.send_response(302)
            self.send_header("Location", AUTH_URL + params)
            self.end_headers()
            return

        # /api/callback — exchange code for tokens
        if parsed.path == "/api/callback":
            code = parse_qs(parsed.query).get("code", [None])[0]
            if not code:
                self._respond(400, {"error": "missing code"})
                return

            resp = requests.post(TOKEN_URL, data={
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": REDIRECT_URI,
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
            })

            self._respond(resp.status_code, resp.json())
            return

        self._respond(404, {"error": "not found"})

    def _respond(self, status: int, body: dict):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(body).encode())
