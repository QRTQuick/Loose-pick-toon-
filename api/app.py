from flask import Flask, redirect, request, jsonify
from flask_cors import CORS
import requests
import os
import base64

app = Flask(__name__)
CORS(app)

CLIENT_ID     = os.environ["SPOTIFY_CLIENT_ID"]
CLIENT_SECRET = os.environ["SPOTIFY_CLIENT_SECRET"]
REDIRECT_URI  = os.environ["SPOTIFY_REDIRECT_URI"]  # https://loose-pick-toon.vercel.app/api/callback
SCOPE         = "user-read-playback-state user-modify-playback-state"

SPOTIFY_AUTH_URL  = "https://accounts.spotify.com/authorize"
SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"
SPOTIFY_API       = "https://api.spotify.com/v1/me/player"


# ── Auth ──────────────────────────────────────────────────────────────────────

@app.route("/api/login")
def login():
    """Redirect the desktop app browser to Spotify login."""
    url = (
        f"{SPOTIFY_AUTH_URL}"
        f"?client_id={CLIENT_ID}"
        f"&response_type=code"
        f"&redirect_uri={REDIRECT_URI}"
        f"&scope={SCOPE}"
    )
    return redirect(url)


@app.route("/api/callback")
def callback():
    """Spotify redirects here after user approves. Returns tokens as JSON."""
    code = request.args.get("code")
    error = request.args.get("error")

    if error or not code:
        return jsonify({"error": error or "missing code"}), 400

    creds = base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()
    resp = requests.post(SPOTIFY_TOKEN_URL, data={
        "grant_type":   "authorization_code",
        "code":         code,
        "redirect_uri": REDIRECT_URI,
    }, headers={"Authorization": f"Basic {creds}"})

    data = resp.json()

    # Return a simple HTML page so the desktop user sees their token
    access_token  = data.get("access_token", "")
    refresh_token = data.get("refresh_token", "")

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
      <title>Loose Pick — Authenticated</title>
      <style>
        body {{ background:#111; color:#fff; font-family:sans-serif; display:flex;
                flex-direction:column; align-items:center; justify-content:center; height:100vh; margin:0; }}
        h1   {{ color:#1DB954; }}
        code {{ background:#222; padding:8px 16px; border-radius:8px; word-break:break-all; }}
        p    {{ color:#aaa; font-size:13px; }}
      </style>
    </head>
    <body>
      <h1>✅ Authenticated!</h1>
      <p>Copy your access token into your <code>.env</code> as <strong>SPOTIFY_ACCESS_TOKEN</strong></p>
      <code>{access_token}</code>
      <br/><br/>
      <p>Refresh token (save this too):</p>
      <code>{refresh_token}</code>
    </body>
    </html>
    """
    return html, 200


@app.route("/api/refresh", methods=["POST"])
def refresh():
    """Exchange a refresh token for a new access token."""
    body = request.get_json(force=True)
    refresh_token = body.get("refresh_token")
    if not refresh_token:
        return jsonify({"error": "missing refresh_token"}), 400

    creds = base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()
    resp = requests.post(SPOTIFY_TOKEN_URL, data={
        "grant_type":    "refresh_token",
        "refresh_token": refresh_token,
    }, headers={"Authorization": f"Basic {creds}"})

    return jsonify(resp.json()), resp.status_code


# ── Playback ──────────────────────────────────────────────────────────────────

def _auth_header():
    token = request.headers.get("Authorization", "")
    if not token:
        return None, (jsonify({"error": "missing Authorization header"}), 401)
    return {"Authorization": token}, None


@app.route("/api/playback/current")
def current_track():
    headers, err = _auth_header()
    if err:
        return err

    resp = requests.get(SPOTIFY_API, headers=headers)
    if resp.status_code == 204:
        return jsonify({"track": "Nothing playing", "is_playing": False})

    data = resp.json()
    item = data.get("item")
    if not item:
        return jsonify({"track": "Nothing playing", "is_playing": False})

    return jsonify({
        "track":      f"{item['artists'][0]['name']} - {item['name']}",
        "is_playing": data.get("is_playing", False),
        "album_art":  item["album"]["images"][0]["url"] if item["album"]["images"] else None,
    })


@app.route("/api/playback/play-pause", methods=["POST"])
def play_pause():
    headers, err = _auth_header()
    if err:
        return err

    state = requests.get(SPOTIFY_API, headers=headers)
    if state.status_code == 200 and state.json().get("is_playing"):
        requests.put(f"{SPOTIFY_API}/pause", headers=headers)
    else:
        requests.put(f"{SPOTIFY_API}/play", headers=headers)

    return jsonify({"ok": True})


@app.route("/api/playback/next", methods=["POST"])
def next_track():
    headers, err = _auth_header()
    if err:
        return err
    requests.post(f"{SPOTIFY_API}/next", headers=headers)
    return jsonify({"ok": True})


@app.route("/api/playback/previous", methods=["POST"])
def previous_track():
    headers, err = _auth_header()
    if err:
        return err
    requests.post(f"{SPOTIFY_API}/previous", headers=headers)
    return jsonify({"ok": True})


if __name__ == "__main__":
    app.run(debug=True, port=5000)
