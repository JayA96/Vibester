import requests
import json
from helpers import get_main_genre, get_saved_tracks, sort_by_genre, get_playlists, get_decade, sort_by_decade, \
    get_audio_features, sort_by_audio_features
from flask import Flask, redirect, render_template, request
from auth import app_auth, user_auth, api_url, port
from time import sleep

app = Flask(__name__)

auth_header = None
tracks = None
custom_data = None
name = None


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/authorize")
def authorize():
    auth_url = app_auth()
    return redirect(auth_url)


@app.route("/callback/q")
def callback():
    global auth_header
    auth_header = user_auth()
    # Get user tracks data
    global tracks
    tracks = get_saved_tracks(api_url, auth_header)

    # Get genre and release decade for each track
    for i in range(len(tracks)):
        artist_id = tracks[i]["artist_id"]
        artist_api_endpoint = f"{api_url}/artists/{artist_id}"
        artist_response = requests.get(artist_api_endpoint, headers=auth_header)
        artist_data = json.loads(artist_response.text)
        genres = artist_data["genres"]
        tracks[i]["decade"] = get_decade(tracks[i])
        tracks[i]["genre"] = get_main_genre(genres)

        # Get audio features for all tracks
        get_audio_features(tracks, api_url, auth_header)
    return redirect("/home")


@app.route("/home")
def home():
    return render_template("home.html")


@app.route("/genre")
def genre():
    # Sort songs into genre playlists
    playlist_ids = sort_by_genre(tracks, api_url, auth_header)
    print(playlist_ids)
    return render_template("playlists.html", playlist_type="genre", ids=playlist_ids)


@app.route("/decade")
def decade():
    # Sort songs into decade playlists
    playlist_ids = sort_by_decade(tracks, api_url, auth_header)
    return render_template("playlists.html", playlist_type="decade", ids=playlist_ids)


@app.route("/custom", methods=["POST", "GET"])
def custom():
    # Creates a custom playlist based on user parameters

    # Post request takes custom values from the json and stores it in a global variable to be used by get request
    if request.method == "POST":
        global custom_data
        custom_data = request.get_json()
    else:
        playlist_id = sort_by_audio_features(tracks, custom_data, api_url, auth_header)
    return render_template("playlists.html", playlist_type="custom", id=playlist_id)


if __name__ == "__main__":
    app.run(debug=True, port=port)
