import requests
import json
import os
from helpers import get_main_genre, get_saved_tracks, sort_by_genre, get_decade, sort_by_decade, \
    get_audio_features, sort_by_audio_features
from flask import Flask, redirect, render_template, request, session
from auth import app_auth, user_auth, api_url, port

app = Flask(__name__)

app.secret_key = os.environ.get('SPOTIFY_SECRET_KEY')


@app.route("/")
def index():
    # Reset session data for new user
    session.pop("header", None)
    session.pop("custom_data", None)
    session.pop("name", None)
    return render_template("index.html")


@app.route("/authorize")
def authorize():
    auth_url = app_auth()
    return redirect(auth_url)


@app.route("/callback/q")
def callback():
    session["header"] = user_auth()
    return redirect("/home")


@app.route("/home")
def home():
    return render_template("home.html")


@app.route("/genre")
def genre():
    # Sort songs into genre playlists
    auth_header = session["header"]
    # Get user tracks data
    tracks = get_saved_tracks(api_url, auth_header)

    # Check user has more than 0 and less than 4000 tracks
    if tracks is None:
        return render_template("error.html", type="no_tracks")
    elif len(tracks) > 4000:
        return render_template("error.html", type="too_many_tracks")

    # Get genre and release decade for each track
    tracks_remainder = len(tracks) % 50
    for offset in range(0, len(tracks), 50):
        if len(tracks) < offset + 50:
            artist_ids = [tracks[i + offset]["artist_id"] for i in range(tracks_remainder)]
        else:
            artist_ids = [tracks[i + offset]["artist_id"] for i in range(50)]
        artist_ids = ",".join(artist_ids)
        artist_api_endpoint = f"{api_url}/artists?ids={artist_ids}"
        artist_response = requests.get(artist_api_endpoint, headers=auth_header)
        artist_data = json.loads(artist_response.text)
        artists = artist_data["artists"]
        for i in range(len(artists)):
            tracks[i + offset]["genre"] = get_main_genre(artists[i]["genres"])
            tracks[i + offset]["decade"] = get_decade(tracks[i + offset])

        # Get audio features for all tracks
        get_audio_features(tracks, api_url, auth_header)
    playlist_ids = sort_by_genre(tracks, api_url, auth_header)
    return render_template("playlists.html", playlist_type="genre", ids=playlist_ids)


@app.route("/decade")
def decade():
    # Sort songs into decade playlists
    auth_header = session["header"]
    # Get user tracks data
    tracks = get_saved_tracks(api_url, auth_header)

    # Check user has more than 0 and less than 4000 tracks
    if tracks is None:
        return render_template("error.html", type="no_tracks")
    elif len(tracks) > 4000:
        return render_template("error.html", type="too_many_tracks")

    # Get genre and release decade for each track
    tracks_remainder = len(tracks) % 50
    for offset in range(0, len(tracks), 50):
        if len(tracks) < offset + 50:
            artist_ids = [tracks[i + offset]["artist_id"] for i in range(tracks_remainder)]
        else:
            artist_ids = [tracks[i + offset]["artist_id"] for i in range(50)]
        artist_ids = ",".join(artist_ids)
        artist_api_endpoint = f"{api_url}/artists?ids={artist_ids}"
        artist_response = requests.get(artist_api_endpoint, headers=auth_header)
        artist_data = json.loads(artist_response.text)
        artists = artist_data["artists"]
        for i in range(len(artists)):
            tracks[i + offset]["genre"] = get_main_genre(artists[i]["genres"])
            tracks[i + offset]["decade"] = get_decade(tracks[i + offset])

        # Get audio features for all tracks
        get_audio_features(tracks, api_url, auth_header)
    playlist_ids = sort_by_decade(tracks, api_url, auth_header)
    return render_template("playlists.html", playlist_type="decade", ids=playlist_ids)


@app.route("/custom", methods=["POST", "GET"])
def custom():
    # Creates a custom playlist based on user parameters

    # Post request takes custom values from the json and stores it in a global variable to be used by get request
    if request.method == "POST":
        custom_data = request.get_json()
        session["custom_data"] = custom_data
    else:
        custom_data = session["custom_data"]
        auth_header = session["header"]
        # Get user tracks data
        tracks = get_saved_tracks(api_url, auth_header)

        # Check user has more than 0 and less than 4000 tracks
        if tracks is None:
            return render_template("error.html", type="no_tracks")
        elif len(tracks) > 4000:
            return render_template("error.html", type="too_many_tracks")

        # Get genre and release decade for each track
        tracks_remainder = len(tracks) % 50
        for offset in range(0, len(tracks), 50):
            if len(tracks) < offset + 50:
                artist_ids = [tracks[i + offset]["artist_id"] for i in range(tracks_remainder)]
            else:
                artist_ids = [tracks[i + offset]["artist_id"] for i in range(50)]
            artist_ids = ",".join(artist_ids)
            artist_api_endpoint = f"{api_url}/artists?ids={artist_ids}"
            artist_response = requests.get(artist_api_endpoint, headers=auth_header)
            artist_data = json.loads(artist_response.text)
            artists = artist_data["artists"]
            for i in range(len(artists)):
                tracks[i + offset]["genre"] = get_main_genre(artists[i]["genres"])
                tracks[i + offset]["decade"] = get_decade(tracks[i + offset])

            # Get audio features for all tracks
            get_audio_features(tracks, api_url, auth_header)
        playlist_id = sort_by_audio_features(tracks, custom_data, api_url, auth_header)
    return render_template("playlists.html", playlist_type="custom", id=playlist_id)


if __name__ == "__main__":
    app.run(port=port)
