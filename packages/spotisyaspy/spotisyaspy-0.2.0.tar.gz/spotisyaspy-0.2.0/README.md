# SpotIsyAsPy - Spotify, as Easy as Pie 🎧🥧

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**SpotIsyAsPy** (pronounced *spot-easy-as-pie*), _SIAP_ for short, is a powerful, intuitive and lightweight Python library that provides an object-relational mapping (ORM)-style interface for the Spotify Web API. It's designed to make interacting with Spotify's data — such as Artists, Albums, Tracks, and Playlists — feel like you're working with native Python objects, abstracting away the complexities of direct HTTP requests, authentication, pagination, and rate-limiting.

## What is SpotIsyAsPy?

Instead of making you handle raw API endpoint responses (usually complex JSON/dictionaries), SpotIsyAsPy maps Spotify entities like Artists, Albums, and Tracks to Python classes. You can search for an artist, and you'll get back an `Artist` object. You can then call `.albums` on that object, and the library will automatically fetch and return a list of `Album` objects for you.

The core of the library is the `SIAP_Factory`, a singleton object factory and store that manages all API interactions and ensures that you're always working with a consistent and efficient representation of Spotify's data.

### Main Features

*   **Object-Oriented Interface**: Interact with `Artist`, `Album`, `Track`, and `Playlist` objects, not dictionaries.
*   **Automatic Authentication**: Handles both the simple Client Credentials flow (for public data) and the user-involved Authorization Code flow (for managing user playlists).
*   **Seamless Pagination**: When a search returns hundreds of results, SpotIsyAsPy automatically handles the pagination for you, fetching all the required pages in the background, optionally displaying progress bars for long requests.
*   **Lazy Loading**: Objects are loaded with minimal data first (e.g., a simplified `Album` object). When you access a property that requires more data (like `.tracks`), the library automatically fetches the full details from the API. This is efficient and fast.
*   **Built-in Caching**: The factory caches every object it creates. If you request the same artist twice, you'll get the exact same object from memory, avoiding redundant API calls. The cache can also be saved to and loaded from a file.
*   **Intuitive User Playlist Management**: Create new user playlists and add tracks to them with simple method calls. The library manages the one-time user authorization process by automatically opening a browser window and running a temporary local server.

---

## Prerequisites and Setup

Before you can use SpotIsyAsPy, you need to set up a few things.

### 1. Installation

You can install SpotIsyAsPy using pip:

```bash
pip install spotisyaspy
```

Alternatively you can simply import the module `spotisyaspy.py` after downloading it from GitHub. In this case, you need to install its dependencies before import. The module relies on `requests`, `flask`, and `tqdm`. You can install them using pip:

```bash
pip install requests flask tqdm
```

### 2. Get Spotify API Credentials

You need a **Client ID** and a **Client Secret** from Spotify to use the API.

1.  **Go to the Spotify Developer Dashboard**: [https://developer.spotify.com/dashboard/](https://developer.spotify.com/dashboard/)
2.  **Log in** with your normal Spotify account.
3.  Click **"Create app"**.
4.  Give your app a name and description. In the section **Which API/SDKs are you planning to use?**, select _"Web API"_.
5.  In the **"Redirect URIs"** field, add the following value:
    ```
    http://127.0.0.1:8050/callback
    ```
    Then click **"Add"**, then **"Save"** at the bottom of the page.

    The application will use the specified port for user authentication, which only comes into play if you want to create new playlists or add tracks to your playlists using SpotIsyAsPy. You still have to add a valid value if you will not be using this functionality since this is a required field of the Dashboard form, but it will not be used in that case.
    
    If you do want to work with playlists and are already using 8050 on the machine you want to run SpotIsyAsPy on or want to use a different IP address, you can do this. The correct port number and IP address can be set to the preferred values on initialisation of the SpotIsyAsPy factory using the attributes `SIAP_Factory(auth_server_ip="0.0.0.0", auth_server_port=8888)`, or by assigning the preferred value to the `factory.auth_server_ip` or `factory.auth_server_port` attributes before calling a method that triggers authorization. 

6.  Once the app is created, you will see your **Client ID**. Click **"Show client secret"** to see your **Client Secret**. **Copy both of these values.**
7.  **For user-related actions (like creating playlists):** If you own several Spotify user accounts and want to manage their playlists with SpotIsyAsPy, you don't need separate client IDs and secrets for each user. It is sufficient to add further users (up to 25) under User Management in the developer Dashboard and use the same ID and secrets for all of the user logins. You don't have to add the owner of the app (the account with which you have got your client credentials) as user. For all other Spotify accounts, open the "User Management" tab, enter the user's name and email address (the one with which the Spotify account is linked) and click "Add user". It is neither documented in the Web API docs nor entirely clear whether these users need to have a Spotify Developer account activated before they can access their playlists and account data through the API.

---

## User's Guide

### 1. Getting Started: The Factory

All interactions are managed through the `SIAP_Factory` singleton. You only need to initialize it once with your credentials.

```python
from spotisyaspy import SIAP_Factory

CLIENT_ID = "YOUR_CLIENT_ID"
CLIENT_SECRET = "YOUR_CLIENT_SECRET"

# Initialize the factory
factory = SIAP_Factory(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
```

Alternatively you can put your client ID and secret in a simple text file containing the ID on the first line and the secret on the second and call the constructor like this:

```python
factory = SIAP_Factory(credentials_file="my_credentials.txt")
```

### 2. Searching for Content

The `search()` method is your primary tool for finding content on Spotify.

#### Basic Search

To search for tracks, albums, artists, or playlists, specify the `obj_type`.

```python
# Search for tracks by the artist "Tame Impala"
tracks = factory.search("Tame Impala", obj_type="track", max_results=10)

for track in tracks:
    # track is a Track object!
    print(f"- {track.name} ({track.duration}) from the album '{track.album.name}'")

# Search for albums
albums = factory.search("Currents", obj_type="album", max_results=5)
for album in albums:
    # album is an Album object!
    print(f"- {album.name} by {' & '.join(str(a) for a in album.artists)}")
```

#### Advanced Search with Filters

You can use field filters to narrow down your search, just like in the Spotify app.

```python
# Find albums by "Daft Punk" released between 2000 and 2005
albums = factory.search(
    query="Daft Punk",
    obj_type="album",
    filters={"year": "2000-2005"}
)

for album in albums:
    artists = ' & '.join(str(a) for a in album.artists)
    print(f"- {album.name}, {album.album_type} by {artists} (Released: {album.release_date})")
```
Valid filters depend on the `obj_type` and are documented in the `search()` method's docstring.

### 3. Working with Objects (Lazy Loading)

SpotIsyAsPy uses a lazy-loading system. When you search, you get back "simplified" objects. When you access a property that requires more data, the library fetches it automatically.

```python
# This search returns a list of SimplifiedAlbum objects
albums = factory.search("Pink Floyd The Wall", obj_type="album", max_results=1)
the_wall = albums[0]

# The simplified object has basic info
print(f"Album Name: {the_wall.name}")
print(f"Release Date: {the_wall.release_date}")

# Accessing '.tracks' requires a full album object.
# The library will transparently make a new API call to get the full data.
print("\nFetching tracklist...")
for track in the_wall.tracks:
    # Each track is a Track object
    print(f"  - {track.disc_number}-{track.track_number:02d}: {track.name}")

# Now, the_wall is a FullAlbum object in the cache, with all data loaded.
print(f"\nAlbum Popularity: {the_wall.popularity}")
```

Although SpotIsyAsPy's classes mirror the Spotify API's distinction between simplified and full objects, the interface presented to the user abstracts away from this implementational detail. Both types of object have the same attributes and methods, and simplified objects are silently and automatically upgraded to (i.e. replaced by) full objects in the factory's cache. The correspondence between simplified and full objects is represented by the object's (Spotify) id attribute.

### 4. Direct Access by Spotify ID

If you already have a Spotify ID for an item, you can fetch it directly. This always returns a "full" object.

```python
# Spotify ID for the artist "Queen"
queen_id = "1dfeR4HaWDbWqFHLkxsg1d"

# Get the FullArtist object directly
queen = factory.get_artist(queen_id)

print(f"Artist: {queen.name}")
print(f"Followers: {queen.followers}")
print(f"Genres: {', '.join(queen.genres)}")

# Get the artist's studio albums
studio_albums = queen.get_albums("album")
for album in studio_albums:
    print(f"- {album.name}")
```

### 5. Managing User Playlists

This requires user authorization. The first time you call a method like `create_user_playlist`, SpotIsyAsPy will:
1.  Open your default web browser to the Spotify authorization page.
2.  Ask you to log in and grant permissions to your app.
3.  Once you click "Allow", Spotify redirects you back to a temporary local web server, which captures the authorization token and shuts down.

This only happens once. The factory stores the token in memory and will use it for all future user-related requests, refreshing it automatically if it has expired.

```python
# 1. Create a new playlist
# This will trigger the one-time browser authentication flow.
print("Creating a new playlist...")
my_playlist = factory.create_user_playlist(
    playlist_name="My Awesome Mix",
    description="A playlist created with SpotIsyAsPy!",
    public=False
)
print(f"Successfully created playlist: {my_playlist.name}")

# 2. Find some tracks to add
tracks_to_add = factory.search("artist:Gorillaz", obj_type="track", max_results=5)
print("\nFound tracks to add:")
for t in tracks_to_add:
    print(f"- {t.name}")

# 3. Add tracks to the new playlist
my_playlist.add_tracks(tracks_to_add)
print(f"\nAdded {len(tracks_to_add)} tracks to '{my_playlist.name}'.")
print(f"Playlist now has {len(my_playlist)} tracks.")

# 4. Modify the playlist's details
# These setters automatically call the API to update the playlist on Spotify
my_playlist.name = "My Super Awesome Mix"
my_playlist.description = "Updated description."
print(f"\nPlaylist updated to '{my_playlist.name}'")
```

### 6. Caching

To speed up subsequent runs of your script, you can save the factory's cache to a file and load it back later.

```python
# At the end of your script
factory.save_cache("spotify_cache.pkl")
print("Cache saved.")

# At the beginning of a new script
factory = SIAP_Factory(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
factory.load_cache("spotify_cache.pkl")
print("Cache loaded.")
```

---

## SpotIsyAsPy vs. Spotipy

**Spotipy** is the most popular and comprehensive Python library for the Spotify API. The key difference is philosophical:

*   **Spotipy** is a direct, procedural wrapper around the API endpoints. You call a function that maps to an endpoint, and it returns the raw JSON data as a Python dictionary.
*   **SpotIsyAsPy** is an object-oriented abstraction layer. It hides the direct API calls behind an intuitive object model, promoting a more "Pythonic" and readable coding style.

Let's compare a common task: **Find an artist and list the titles of their albums.**

#### Using SpotIsyAsPy

The code is linear, readable, and object-centric.

```python
# spotisyaspy_example.py
from spotisyaspy import SIAP_Factory

factory = SIAP_Factory(client_id="...", client_secret="...")

# Search returns a list of Artist objects
artists = factory.search("Led Zeppelin", obj_type="artist", max_results=1)

if artists:
    led_zeppelin = artists[0]
    print(f"Found artist: {led_zeppelin.name}")

    # Accessing the .albums property fetches the albums automatically
    print("\nAlbums:")
    for album in led_zeppelin.albums:
        # album is an Album object
        print(f"- {album.name} ({album.release_date})")
```

#### Using Spotipy

The code requires you to know the structure of the JSON response and manually chain API calls.

```python
# spotipy_example.py
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

auth_manager = SpotifyClientCredentials(client_id="...", client_secret="...")
sp = spotipy.Spotify(auth_manager=auth_manager)

# The result is a dictionary
results = sp.search(q="Led Zeppelin", type="artist", limit=1)
artist_items = results['artists']['items']

if artist_items:
    # You need to extract the ID from the dictionary
    artist_id = artist_items[0]['id']
    artist_name = artist_items[0]['name']
    print(f"Found artist: {artist_name}")

    # You must make a separate, explicit call to get the albums
    album_results = sp.artist_albums(artist_id, album_type='album')
    album_items = album_results['items']

    print("\nAlbums:")
    for album_item in album_items:
        # album_item is a dictionary
        print(f"- {album_item['name']} ({album_item['release_date']})")
```

As you can see, SpotIsyAsPy provides a higher-level, more expressive way to work with the API, especially for developers who prefer object-oriented design patterns.

#### Comparison with Tekore

**[Tekore](https://tekore.readthedocs.io/en/stable/)** is a full-featured object-oriented library for Spotify that offers a similar approach to SpotIsyAsPy, but mirrors the Web API much more closely with its objects and methods. SpotIsyAsPy was developed mainly as a tool to support offline analysis of data retrieved from Spotify. This is the main motivation for 

---

## API Coverage and Limitations

SpotIsyAsPy is a new library and currently focuses on the most common use cases for music data retrieval and playlist management. The current version **does not** cover:

*   **Player Control**: Starting/stopping playback, controlling volume, managing the queue.
*   **User Library**: Accessing or modifying a user's saved tracks, albums, or shows ("Your Library").
*   **Following**: Following or unfollowing artists or playlists.

*   **Audiobooks, Shows and Episodes**: Audiobooks and their chapters are only available within the US, UK, Canada, Ireland, New Zealand and Australia markets and thus are not relevant to an international public. As I personally only use Spotify for music and non-English audiobooks that are treated as albums, I have only added rudimentary support for shows and episodes. While these types can be searched for, they are not mapped to dedicated Python objects. A search for these objects returns the parsed JSON data from the Spotify API response instead.
*   **Browsing new releases and categories**

**Deprecated API endpoints are not implemented.** These endpoints are only accessible to applications that were created before these endpoints were phased out. The main reason for not including these is that I don't have access to these endpoints myself and would not have been able to test whether everything is working if I had implemented them. The deprecated features with restricted availability include:
* Browsing featured playlists & category playlists
* Audio features & analysis: Endpoints like `GET /audio-features/{id}`.
* Recommendations & genre seeds: Endpoints like `GET /recommendations`.
* Artists' related artists
* Track previews

Contributions to expand the API coverage are welcome.