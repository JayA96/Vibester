import requests
import json


def get_saved_tracks(api_url, auth_header):
    # Get user tracks data

    # Use endpoint to determine total number of saved tracks
    user_tracks_api_endpoint = f"{api_url}/me/tracks?limit=1"
    user_tracks_response = requests.get(user_tracks_api_endpoint, headers=auth_header)
    user_tracks_data = json.loads(user_tracks_response.text)
    total_tracks = user_tracks_data["total"]

    # Exit function if user has no tracks
    if total_tracks == 0:
        return None

    # Initialise list of tracks
    tracks = [None] * total_tracks

    # API limits number of tracks per request at 50. Function has to be repeated for every 50 tracks
    for offset in range(0, total_tracks, 50):
        user_tracks_api_endpoint = f"{api_url}/me/tracks?limit=50&offset={offset}"
        user_tracks_response = requests.get(user_tracks_api_endpoint, headers=auth_header)
        user_tracks_data = json.loads(user_tracks_response.text)

        # Get the list of items from JSON
        tracks_items = user_tracks_data["items"]

        # Get data from each track and store relevant data in a list of dictionaries
        for i in range(len(tracks_items)):
            tracks[i + offset] = {
                "track_name": tracks_items[i]["track"]["name"],
                "artist_name": tracks_items[i]["track"]["artists"][0]["name"],
                "track_id": tracks_items[i]["track"]["id"],
                "artist_id": tracks_items[i]["track"]["artists"][0]["id"],
                "release_date": tracks_items[i]["track"]["album"]["release_date"],
                "release_date_precision": tracks_items[i]["track"]["album"]["release_date_precision"],
                "track_uri": tracks_items[i]["track"]["uri"]
            }
    return tracks


def get_playlists(api_url, auth_header):
    # Get user playlists data

    # Use endpoint to determine total number of playlists
    user_playlists_api_endpoint = f"{api_url}/me/playlists?limit=1"
    user_playlists_response = requests.get(user_playlists_api_endpoint, headers=auth_header)
    user_playlists_data = json.loads(user_playlists_response.text)
    total_playlists = user_playlists_data["total"]

    # Initialise list of playlists
    playlists = [None] * total_playlists

    # API limits number of playlists per request at 50. Function has to be repeated for every 50 playlists.
    for offset in range(0, total_playlists, 50):
        user_playlists_api_endpoint = f"{api_url}/me/playlists?limit=50&offset={offset}"
        user_playlists_response = requests.get(user_playlists_api_endpoint, headers=auth_header)
        user_playlists_data = json.loads(user_playlists_response.text)

        # Get the list of items from JSON
        playlists_items = user_playlists_data["items"]

        # Get data from each playlist and store relevant data in a list of dictionaries
        for i in range(len(playlists_items)):
            playlists[i + offset] = {
                "playlist_name": playlists_items[i]["name"],
                "playlist_id": playlists_items[i]["id"]
            }
    return playlists


def get_genre(genres, possible_genres):
    # Finds the genre of the song from a short list of possible genres

    # Starts from the last element in the genre list as for multi-genre songs, this tends to be the more dominant genre
    for i in range(-1, -len(genres), -1):
        for j in range(len(possible_genres)):
            if possible_genres[j] in genres[i]:
                genre = possible_genres[j]
                return genre
    return 'miscellaneous'


def get_main_genre(genres):
    # Finds a more broad genre for a song. This is to reduce the likelihood of many small playlists being formed

    # List of possible genres to be compared with
    possible_genres = ['rock', 'pop', 'country', 'metal', 'hip hop', 'rap', 'soul', 'funk', 'blues', 'folk', 'edm',
                       'house',
                       'electronic', 'techno', 'jazz', 'lounge', 'swing', 'r&b', 'classical', 'hollywood', 'show tunes',
                       'soundtrack', 'reggae']

    # Use get_genre function to determine which of the possible genres the song is most likely to match
    genre = get_genre(genres, possible_genres)

    # Using if and elif statements, find which playlist the song belongs in
    if genre in possible_genres[0]:
        main_genre = 'Rock'
    elif genre in possible_genres[1]:
        main_genre = 'Pop'
    elif genre in possible_genres[2]:
        main_genre = 'Country'
    elif genre in possible_genres[3]:
        main_genre = 'Metal'
    elif genre in possible_genres[4:6]:
        main_genre = 'Hip-hop'
    elif genre in possible_genres[6:8]:
        main_genre = 'Funk and Soul'
    elif genre in possible_genres[8]:
        main_genre = 'Blues'
    elif genre in possible_genres[9]:
        main_genre = 'Folk Music'
    elif genre in possible_genres[10:14]:
        main_genre = 'Electronic'
    elif genre in possible_genres[14]:
        main_genre = 'Jazz'
    elif genre in possible_genres[15:17]:
        main_genre = 'Lounge Music'
    elif genre in possible_genres[17]:
        main_genre = 'R&B'
    elif genre in possible_genres[18]:
        main_genre = 'Classical'
    elif genre in possible_genres[19:22]:
        main_genre = 'Musicals and Film Music'
    elif genre in possible_genres[22]:
        main_genre = 'Reggae'
    else:
        main_genre = None
    return main_genre


def sort_by_genre(tracks, api_url, auth_header):
    # Sorts all the users saved tracks into different playlists for each genre

    # Get all unique genres in users saved tracks
    unique_genres = list(set([tracks[i]["genre"] for i in range(len(tracks)) if tracks[i]["genre"]]))

    # Get names of current playlists
    playlists = get_playlists(api_url, auth_header)
    playlist_names = [playlists[playlist]["playlist_name"] for playlist in range(len(playlists))]

    playlist_ids = []

    # Make a playlist for each genre
    for i in range(len(unique_genres)):

        # Using a list comprehension, put the uris for all the tracks of the selected genre into a list
        uris = [tracks[j]["track_uri"] for j in range(len(tracks)) if tracks[j]["genre"] == unique_genres[i]]

        playlist_exists = False

        # Check if playlist for genre currently exists. If it does exist, replace the contents
        for j in range(len(playlist_names)):
            if unique_genres[i] == playlist_names[j]:
                playlist_id = playlists[j]["playlist_id"]
                playlist_ids.append(playlist_id)
                add_to_playlist_api_endpoint = f"{api_url}/playlists/{playlist_id}/tracks"
                total_uris = len(uris)

                # Get the remaining number of uri after dividing by 100. This will become useful as we're limited to 100 track uris per request
                uris_remainder = total_uris % 100

                # The below if else statement is required to prevent the index for uris from going out of range on the final iteration
                for k in range(0, total_uris, 100):
                    if total_uris < k + 100:
                        add_to_playlist_body = json.dumps({
                            "uris": uris[k:k + uris_remainder]
                        })
                    else:
                        add_to_playlist_body = json.dumps({
                            "uris": uris[k:k + 100]
                        })

                    # After first iteration add tracks onto playlist
                    if k != 0:
                        requests.post(add_to_playlist_api_endpoint, data=add_to_playlist_body, headers=auth_header)

                    # On first iteration replace all songs in the playlist
                    else:
                        requests.put(add_to_playlist_api_endpoint, data=add_to_playlist_body, headers=auth_header)

                playlist_exists = True
                break

        # If the playlist doesn't already exist, create the new playlist and fill it:
        if not playlist_exists:
            # Make body for request
            create_playlist_body = json.dumps({
                "name": f"{unique_genres[i]}",
                "public": True
            })

            # Create new playlist
            create_playlist_api_endpoint = f"{api_url}/me/playlists"

            create_playlist_response = requests.post(create_playlist_api_endpoint, data=create_playlist_body,
                                                     headers=auth_header)
            new_playlist_data = json.loads(create_playlist_response.text)

            # Get the id of the new playlist
            playlist_id = new_playlist_data["id"]

            # Add id to list of ids
            playlist_ids.append(playlist_id)

            add_to_playlist_api_endpoint = f"{api_url}/playlists/{playlist_id}/tracks"

            total_uris = len(uris)

            # Get the remaining number of uri after dividing by 100. This will become useful as we're limited to 100 track uris per request
            uris_remainder = total_uris % 100

            # Cycle through every 100 songs and add them to the playlist
            for j in range(0, total_uris, 100):
                # The below if else statement is required to prevent the index for uris from going out of range on the final iteration
                if total_uris < j + 100:
                    add_to_playlist_body = json.dumps({
                        "uris": uris[j:j + uris_remainder]
                    })
                else:
                    add_to_playlist_body = json.dumps({
                        "uris": uris[j:j + 100]
                    })

                # Using a POST request, add all the tracks from the uri list to the playlist
                requests.post(add_to_playlist_api_endpoint, data=add_to_playlist_body, headers=auth_header)

        # Reset the uris list for the next genre
        uris.clear()
    return playlist_ids


def get_decade(track):
    # Gets the decade a track was released

    # Determines the year a track was released
    if track["release_date_precision"] == "year":
        release_year = track["release_date"]
    elif track["release_date_precision"] == "month" or "day":
        release_year = track["release_date"][:4]
    else:
        release_year = None

    # From the year, finds the decade the track was released
    if 2020 <= int(release_year) < 2030:
        decade = "2020s"
    elif 2010 <= int(release_year) < 2020:
        decade = "2010s"
    elif 2000 <= int(release_year) < 2010:
        decade = "2000s"
    elif 1990 <= int(release_year) < 2000:
        decade = "90s"
    elif 1980 <= int(release_year) < 1990:
        decade = "80s"
    elif 1970 <= int(release_year) < 1980:
        decade = "70s"
    elif 1960 <= int(release_year) < 1970:
        decade = "60s"
    elif 1950 <= int(release_year) < 1960:
        decade = "50s"
    elif 1940 <= int(release_year) < 1950:
        decade = "40s"
    elif 1930 <= int(release_year) < 1940:
        decade = "30s"
    elif int(release_year) < 1930:
        decade = "Pre 1930"
    else:
        decade = None

    return decade


def sort_by_decade(tracks, api_url, auth_header):
    # Sorts all the users saved tracks into different playlists for each decade

    # Get all unique decades in users saved tracks
    unique_decades = list(set([tracks[i]["decade"] for i in range(len(tracks)) if tracks[i]["decade"]]))

    # Get names of current playlists
    playlists = get_playlists(api_url, auth_header)
    playlist_names = [playlists[playlist]["playlist_name"] for playlist in range(len(playlists))]

    playlist_ids = []

    # Make a playlist for each decade
    for i in range(len(unique_decades)):

        # Using a list comprehension, put the uris for all the tracks of the selected decade into a list
        uris = [tracks[j]["track_uri"] for j in range(len(tracks)) if tracks[j]["decade"] == unique_decades[i]]
        add_to_playlist_body = json.dumps({
            "uris": uris
        })

        playlist_exists = False

        # Check if playlist for decade currently exists. If it does exist, replace the contents
        for j in range(len(playlist_names)):
            if unique_decades[i] == playlist_names[j]:
                playlist_id = playlists[j]["playlist_id"]
                playlist_ids.append(playlist_id)
                add_to_playlist_api_endpoint = f"{api_url}/playlists/{playlist_id}/tracks"

                total_uris = len(uris)

                # Get the remaining number of uri after dividing by 100. This will become useful as we're limited to 100 track uris per request
                uris_remainder = total_uris % 100

                # Cycle through every 100 songs and add them to the playlist
                for k in range(0, total_uris, 100):
                    # The below if else statement is required to prevent the index for uris from going out of range on the final iteration
                    if total_uris < k + 100:
                        add_to_playlist_body = json.dumps({
                            "uris": uris[k:k + uris_remainder]
                        })
                    else:
                        add_to_playlist_body = json.dumps({
                            "uris": uris[k:k + 100]
                        })

                    # Using a POST request, add all the tracks from the uri list to the playlist
                    requests.post(add_to_playlist_api_endpoint, data=add_to_playlist_body, headers=auth_header)
                playlist_exists = True
                break

        # If the playlist doesn't already exist, create the new playlist and fill it:
        if not playlist_exists:
            # Make body for request
            create_playlist_body = json.dumps({
                "name": f"{unique_decades[i]}",
                "public": True
            })

            # Create new playlist
            create_playlist_api_endpoint = f"{api_url}/me/playlists"

            create_playlist_response = requests.post(create_playlist_api_endpoint, data=create_playlist_body,
                                                     headers=auth_header)
            new_playlist_data = json.loads(create_playlist_response.text)

            # Get the id of the new playlist
            playlist_id = new_playlist_data["id"]

            # Add id to list of ids
            playlist_ids.append(playlist_id)

            add_to_playlist_api_endpoint = f"{api_url}/playlists/{playlist_id}/tracks"

            total_uris = len(uris)

            # Get the remaining number of uri after dividing by 100. This will become useful as we're limited to 100 track uris per request
            uris_remainder = total_uris % 100

            # Cycle through every 100 songs and add them to the playlist
            for j in range(0, total_uris, 100):
                # The below if else statement is required to prevent the index for uris from going out of range on the final iteration
                if total_uris < j + 100:
                    add_to_playlist_body = json.dumps({
                        "uris": uris[j:j + uris_remainder]
                    })
                else:
                    add_to_playlist_body = json.dumps({
                        "uris": uris[j:j + 100]
                    })

                # Using a POST request, add all the tracks from the uri list to the playlist
                requests.post(add_to_playlist_api_endpoint, data=add_to_playlist_body, headers=auth_header)

        # Reset the uris list for the next decade
        uris.clear()
    return playlist_ids


def get_audio_features(tracks, api_url, auth_header):
    # Get the audio analysis features for each track

    total_tracks = len(tracks)

    # Store the track ids for every track in a list
    track_ids = [tracks[i]["track_id"] for i in range(total_tracks)]

    # Get the remaining number of tracks after dividing by 100. This will become useful as we're limited to 100 tracks per request
    tracks_remainder = total_tracks % 100

    # Loop through every 100 tracks
    for i in range(0, total_tracks, 100):

        # The below if else statement is required to prevent the index for track_id_limited from going out of range on the final iteration
        if total_tracks < i + 100:
            track_ids_limited = track_ids[i:i + tracks_remainder]
        else:
            track_ids_limited = track_ids[i:i + 100]

        # Convert list into comma separated string for the endpoint query
        track_ids_limited_string = ",".join(track_ids_limited)

        # Get the audio features for the 100 tracks and take the relevant data and use it to update the tracks list
        audio_features_api_endpoint = f"{api_url}/audio-features?ids={track_ids_limited_string}"
        audio_features_response = requests.get(audio_features_api_endpoint, headers=auth_header)
        audio_features_data = json.loads(audio_features_response.text)
        audio_features = audio_features_data["audio_features"]
        for track in range(len(track_ids_limited)):
            tracks[track + i].update({
                "danceability": audio_features[track]["danceability"],
                "energy": audio_features[track]["energy"],
                "valence": audio_features[track]["valence"]
            })
    return


def sort_by_audio_features(tracks, custom_data, api_url, auth_header):
    # Generates a playlist of songs which match the users audio features

    # Each range is a list storing the min and max value
    energy_range = list(map(float, custom_data["energy"]))
    dance_range = list(map(float, custom_data["danceability"]))
    valence_range = list(map(float, custom_data["valence"]))
    energy_range[:] = [i / 100 for i in energy_range]
    dance_range[:] = [i / 100 for i in dance_range]
    valence_range[:] = [i / 100 for i in valence_range]
    name = custom_data["name"]
    if not name:
        name = "Vibester Custom Playlist"

    # Using a list comprehension, put the uris for all the tracks which match the parameters into a list
    uris = [tracks[i]["track_uri"] for i in range(len(tracks)) if
            energy_range[0] <= tracks[i]["energy"] <= energy_range[1] and (
                    dance_range[0] <= tracks[i]["danceability"] <= dance_range[1]) and (
                    valence_range[0] <= tracks[i]["valence"] <= valence_range[1])]

    # Make body for request
    create_playlist_body = json.dumps({
        "name": name,
        "public": True
    })

    # Create new playlist
    create_playlist_api_endpoint = f"{api_url}/me/playlists"

    create_playlist_response = requests.post(create_playlist_api_endpoint, data=create_playlist_body,
                                             headers=auth_header)
    new_playlist_data = json.loads(create_playlist_response.text)

    # Get the id of the new playlist
    playlist_id = new_playlist_data["id"]

    add_to_playlist_api_endpoint = f"{api_url}/playlists/{playlist_id}/tracks"

    total_uris = len(uris)

    # Get the remaining number of uri after dividing by 100. This will become useful as we're limited to 100 track uris per request
    uris_remainder = total_uris % 100

    # Cycle through every 100 songs and add them to the playlist
    for i in range(0, total_uris, 100):

        # The below if else statement is required to prevent the index for uris from going out of range on the final iteration
        if total_uris < i + 100:
            add_to_playlist_body = json.dumps({
                "uris": uris[i:i + uris_remainder]
            })
        else:
            add_to_playlist_body = json.dumps({
                "uris": uris[i:i + 100]
            })

        # Using a POST request, add all the tracks from the uri list to the playlist
        requests.post(add_to_playlist_api_endpoint, data=add_to_playlist_body, headers=auth_header)
    return playlist_id
