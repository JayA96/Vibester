import base64
import os
import json
import requests
from flask import request
from urllib.parse import quote

# Client keys
client_id = os.environ.get('SPOTIFY_CLIENT_ID')
client_secret = os.environ.get('SPOTIFY_CLIENT_SECRET')

# Spotify URLs
spotify_auth_url = "https://accounts.spotify.com/authorize"
token_url = "https://accounts.spotify.com/api/token"
base_url = "https://api.spotify.com"
api_version = "v1"
api_url = f"{base_url}/{api_version}"

# Server Parameters
client_url = "https://vibester.herokuapp.com/"
port = 8080
redirect_uri = f"{client_url}/callback/q"
scope = "user-library-read playlist-read-private playlist-modify-public playlist-modify-private playlist-read-collaborative"


# Authorize app with Spotify
def app_auth():
    auth_parameters = {
        "response_type": "code",
        "redirect_uri": redirect_uri,
        "scope": scope,
        "client_id": client_id
    }

    url_args = "&".join([f"{key}={quote(str(val))}" for key, val in auth_parameters.items()])
    auth_url = f"{spotify_auth_url}/?{url_args}"
    return auth_url


def user_auth():
    auth_token = request.args['code']
    code_data = {
        "grant_type": "authorization_code",
        "code": str(auth_token),
        "redirect_uri": redirect_uri,
        "client_id": client_id,
        "client_secret": client_secret
    }

    client_creds = f"{client_id}:{client_secret}"
    client_creds_b64 = base64.b64encode(client_creds.encode())
    client_creds_b64 = client_creds_b64.decode()

    code_header = {
        "Authorization": f"Basic {client_creds_b64}"
    }

    post_request = requests.post(token_url, data=code_data, headers=code_header)

    response_data = json.loads(post_request.text)
    access_token = response_data["access_token"]
    refresh_token = response_data["refresh_token"]
    token_type = response_data["token_type"]
    expires_in = response_data["expires_in"]

    auth_header = {"Authorization": f"Bearer {access_token}"}

    return auth_header
