import pytest
from unittest.mock import patch, MagicMock, call
from datetime import datetime, timedelta
import pickle
import os

# Import the classes from your module
from spotisyaspy import SIAP_Factory

# Mock data for various Spotify objects
# Simplified Artist
MOCK_SIMPLE_ARTIST_DATA = {
    "external_urls": {"spotify": "https://open.spotify.com/artist/0OdUWJ0sBjDrqHygGUXeCF"},
    "href": "https://api.spotify.com/v1/artists/0OdUWJ0sBjDrqHygGUXeCF",
    "id": "0OdUWJ0sBjDrqHygGUXeCF",
    "name": "Band of Horses",
    "type": "artist",
    "uri": "spotify:artist:0OdUWJ0sBjDrqHygGUXeCF",
}

# Full Artist
MOCK_FULL_ARTIST_DATA = {
    **MOCK_SIMPLE_ARTIST_DATA,
    "followers": {"href": None, "total": 493923},
    "genres": ["indie rock", "rock"],
    "images": [{"height": 640, "url": "https://i.scdn.co/image/ab6761610000e5eb1f5a09b8b6e9b0d8e3c1b3b1", "width": 640}],
    "popularity": 63,
}

# Simplified Album
MOCK_SIMPLE_ALBUM_DATA = {
    "album_type": "album",
    "artists": [MOCK_SIMPLE_ARTIST_DATA],
    "external_urls": {"spotify": "https://open.spotify.com/album/4m3m2PAI3YIEfNJ22a8M5D"},
    "href": "https://api.spotify.com/v1/albums/4m3m2PAI3YIEfNJ22a8M5D",
    "id": "4m3m2PAI3YIEfNJ22a8M5D",
    "images": [{"height": 640, "url": "https://i.scdn.co/image/ab67616d0000b273b1b1b1b1b1b1b1b1b1b1b1b1", "width": 640}],
    "name": "Cease to Begin",
    "release_date": "2007-10-09",
    "release_date_precision": "day",
    "total_tracks": 10,
    "type": "album",
    "uri": "spotify:album:4m3m2PAI3YIEfNJ22a8M5D",
}

# Full Album
MOCK_FULL_ALBUM_DATA = {
    **MOCK_SIMPLE_ALBUM_DATA,
    "label": "Sub Pop Records",
    "popularity": 54,
    "tracks": {
        "items": [
            {
                "artists": [MOCK_SIMPLE_ARTIST_DATA],
                "disc_number": 1,
                "duration_ms": 228293,
                "explicit": False,
                "external_urls": {"spotify": "https://open.spotify.com/track/4r_vSP2g5fQd92x222a8M5D"},
                "href": "https://api.spotify.com/v1/tracks/4r_vSP2g5fQd92x222a8M5D",
                "id": "4r_vSP2g5fQd92x222a8M5D",
                "is_local": False,
                "name": "Is There a Ghost",
                "preview_url": "https://p.scdn.co/mp3-preview/b1b1b1b1b1b1b1b1b1b1b1b1b1b1b1b1b1b1b1b1",
                "track_number": 1,
                "type": "track",
                "uri": "spotify:track:4r_vSP2g5fQd92x222a8M5D",
            }
        ],
        "total": 1,
    },
}

# Simplified Track
MOCK_SIMPLE_TRACK_DATA = {
    "artists": [MOCK_SIMPLE_ARTIST_DATA],
    "disc_number": 1,
    "duration_ms": 228293,
    "explicit": False,
    "external_urls": {"spotify": "https://open.spotify.com/track/4r_vSP2g5fQd92x222a8M5D"},
    "href": "https://api.spotify.com/v1/tracks/4r_vSP2g5fQd92x222a8M5D",
    "id": "4r_vSP2g5fQd92x222a8M5D",
    "is_local": False,
    "name": "Is There a Ghost",
    "preview_url": "https://p.scdn.co/mp3-preview/b1b1b1b1b1b1b1b1b1b1b1b1b1b1b1b1b1b1b1b1",
    "track_number": 1,
    "type": "track",
    "uri": "spotify:track:4r_vSP2g5fQd92x222a8M5D",
}

# Full Track
MOCK_FULL_TRACK_DATA = {
    **MOCK_SIMPLE_TRACK_DATA,
    "album": MOCK_SIMPLE_ALBUM_DATA,
    "popularity": 59,
    "external_ids": {"isrc": "USSUB0773901"},
}

# Playlist
MOCK_PLAYLIST_DATA = {
    "collaborative": False,
    "description": "A test playlist.",
    "external_urls": {"spotify": "https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M"},
    "followers": {"href": None, "total": 100},
    "href": "https://api.spotify.com/v1/playlists/37i9dQZF1DXcBWIGoYBM5M",
    "id": "37i9dQZF1DXcBWIGoYBM5M",
    "images": [],
    "name": "Test Playlist",
    "owner": {"display_name": "Spotify", "id": "spotify"},
    "public": True,
    "snapshot_id": "snapshot_id_123",
    "tracks": {
        "href": "https://api.spotify.com/v1/playlists/37i9dQZF1DXcBWIGoYBM5M/tracks",
        "items": [
            {"track": MOCK_FULL_TRACK_DATA}
        ],
        "limit": 100,
        "next": None,
        "offset": 0,
        "previous": None,
        "total": 1
    },
    "type": "playlist",
    "uri": "spotify:playlist:37i9dQZF1DXcBWIGoYBM5M",
}

def read_credentials():
    """Read client ID and secret from a file."""
    try:
        with open('client_credentials.txt') as f:
            credentials = f.readlines()
            return credentials[0].strip(), credentials[1].strip()
    except FileNotFoundError:
        raise ValueError("Credentials file not found. "
        "Please create 'credentials.txt' with your Spotify API credentials. "
        "The file should contain two lines: your client ID on the first line "
        "and your client secret on the second.")

@pytest.fixture
def factory():
    """Provides a fresh SIAP_Factory instance for each test."""
    # Reset the singleton for isolation between tests
    if hasattr(SIAP_Factory, '_instance'):
        SIAP_Factory._instance = None
    client_id, client_secret = read_credentials()
    return SIAP_Factory(client_id=client_id,
                        client_secret=client_secret, silent=True)

@pytest.fixture
def mock_requests():
    """Mocks the requests library."""
    with patch('spotisyaspy.spotisyaspy.requests') as mock_req:
        yield mock_req

class TestSIAPFactory:
    """Tests for the main SIAP_Factory class."""

    def test_singleton_pattern(self):
        """Verify that the factory is a singleton."""
        client_id, client_secret = read_credentials()
        factory1 = SIAP_Factory(client_id=client_id,
                                client_secret=client_secret)
        factory2 = SIAP_Factory(client_id=client_id,
                                client_secret=client_secret)
        assert factory1 is factory2
        factory1._cache['test'] = 'value'
        assert factory2._cache['test'] == "value"

    def test_initialization_requires_credentials(self):
        """
        Test that the factory raises an error if neither credential variables
        nor a credentials file are provided on first init.
        """
        if hasattr(SIAP_Factory, '_instance'):
            SIAP_Factory._instance = None
        with pytest.raises(RuntimeError):
            SIAP_Factory(credentials_file=None)

    @patch('spotisyaspy.spotisyaspy.requests.post')
    def test_get_access_token(self, mock_post, factory):
        """Test that the factory correctly requests and stores an access token."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'access_token': 'new_access_token',
            'expires_in': 3600
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        factory._get_access_token()

        assert factory._access_token == 'new_access_token'
        assert factory._token_expiration_time > datetime.now()
        mock_post.assert_called_once()

    def test_cache_save_and_load(self, factory):
        """Test that the object cache can be saved to and loaded from a file."""
        artist = factory._create_object_from_data('artist',
                                                  MOCK_SIMPLE_ARTIST_DATA['id'],
                                                  MOCK_SIMPLE_ARTIST_DATA)
        cache_file = "test_cache.pkl"
        
        factory.save_cache(cache_file)
        assert os.path.exists(cache_file)

        # Create a new factory to load the cache into
        if hasattr(SIAP_Factory, '_instance'):
            SIAP_Factory._instance = None
        new_factory = SIAP_Factory(client_id=factory.client_id,
                                   client_secret=factory.client_secret,
                                   silent=True)
        new_factory.load_cache(cache_file)

        assert 'artist' in new_factory._cache
        assert MOCK_SIMPLE_ARTIST_DATA['id'] in new_factory._cache['artist']
        
        # Clean up the created file
        os.remove(cache_file)

    def test_search(self, factory, mock_requests):
        """Test the search functionality, including object creation and caching."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'artists': {
                'items': [MOCK_FULL_ARTIST_DATA],
                'total': 1,
                'next': None
            }
        }
        mock_requests.request.return_value = mock_response

        results = factory.search(query="Band of Horses", obj_type="artist")

        assert len(results) == 1
        artist = results[0]
        assert isinstance(artist, factory.FullArtist)
        assert artist.id == MOCK_FULL_ARTIST_DATA['id']
        assert artist.name == MOCK_FULL_ARTIST_DATA['name']

        # Verify that the object was cached
        assert factory._cache['artist'][artist.id] is artist

    def test_get_full_object(self, factory, mock_requests):
        """Test retrieving a full object by its ID."""
        mock_response = MagicMock()
        mock_response.json.return_value = MOCK_FULL_ALBUM_DATA
        mock_requests.request.return_value = mock_response

        album = factory.get_album(MOCK_FULL_ALBUM_DATA['id'])

        assert isinstance(album, factory.FullAlbum)
        assert album.id == MOCK_FULL_ALBUM_DATA['id']
        assert album.label == MOCK_FULL_ALBUM_DATA['label']

        # Verify it's cached
        assert factory._cache['album'][album.id] is album

        # Verify that calling get again returns the cached object without an API call
        mock_requests.request.reset_mock()
        cached_album = factory.get_album(MOCK_FULL_ALBUM_DATA['id'])
        assert cached_album is album
        mock_requests.request.assert_not_called()

class TestSimplifiedToFullObjectUpgrade:
    """Tests the automatic upgrade from a simplified to a full object."""

    def test_simplified_artist_to_full(self, factory, mock_requests):
        """Test that accessing a full property on a simplified artist triggers an upgrade."""
        # 1. Create a simplified artist and cache it
        simple_artist = factory._create_object_from_data('artist',
                                                         MOCK_SIMPLE_ARTIST_DATA['id'],
                                                         MOCK_SIMPLE_ARTIST_DATA)
        assert isinstance(simple_artist, factory.Artist)
        assert not isinstance(simple_artist, factory.FullArtist)

        # 2. Mock the API response for the full artist details
        mock_response = MagicMock()
        mock_response.json.return_value = MOCK_FULL_ARTIST_DATA
        mock_requests.request.return_value = mock_response

        # 3. Access a property that only exists on the full object
        popularity = simple_artist.popularity

        # 4. Assert that the correct value was returned
        assert popularity == MOCK_FULL_ARTIST_DATA['popularity']

        # 5. Assert that an API call was made to fetch the full data
        mock_requests.request.assert_called_once_with('GET', f"{factory.base_api_url}/artists/{simple_artist.id}", 
                                                      headers=factory._get_headers())

        # 6. Assert that the object in the cache has been upgraded to a FullArtist
        cached_artist = factory._cache['artist'][simple_artist.id]
        assert isinstance(cached_artist, factory.FullArtist)
        assert cached_artist.popularity == MOCK_FULL_ARTIST_DATA['popularity']

    def test_simplified_album_to_full(self, factory, mock_requests):
        """Test that accessing a full property on a simplified album triggers an upgrade."""
        simple_album = factory._create_object_from_data('album',
                                                        MOCK_SIMPLE_ALBUM_DATA['id'],
                                                        MOCK_SIMPLE_ALBUM_DATA)
        assert isinstance(simple_album, factory.Album)
        assert not isinstance(simple_album, factory.FullAlbum)

        mock_response = MagicMock()
        mock_response.json.return_value = MOCK_FULL_ALBUM_DATA
        mock_requests.request.return_value = mock_response

        # Access the 'tracks' property, which requires the full object
        tracks = simple_album.tracks

        assert len(tracks) == 1
        assert tracks[0].name == "Is There a Ghost"
        mock_requests.request.assert_called_once_with('GET', f"{factory.base_api_url}/albums/{simple_album.id}",
                                                      headers=factory._get_headers())
        
        cached_album = factory._cache['album'][simple_album.id]
        assert isinstance(cached_album, factory.FullAlbum)

    def test_simplified_track_to_full(self, factory, mock_requests):
        """Test that accessing a full property on a simplified track triggers an upgrade."""
        # A simplified track is created as part of the creation of a full album
        full_album = factory._create_object_from_data('album',
                MOCK_FULL_ALBUM_DATA["id"],
                MOCK_FULL_ALBUM_DATA,
                is_full_object=True)
        simple_track = full_album.tracks[0]
        assert isinstance(simple_track, factory.Track)
        assert not isinstance(simple_track, factory.FullTrack)

        mock_response = MagicMock()
        mock_response.json.return_value = MOCK_FULL_TRACK_DATA
        mock_requests.request.return_value = mock_response
        
        popularity = simple_track.popularity

        assert popularity == MOCK_FULL_TRACK_DATA['popularity']
        mock_requests.request.assert_called_once_with('GET', f"{factory.base_api_url}/tracks/{simple_track.id}",
                                                      headers=factory._get_headers())

        cached_track = factory._cache['track'][simple_track.id]
        assert isinstance(cached_track, factory.FullTrack)

class TestObjectPropertiesAndCaching:
    """Test properties and ensure data is cached correctly."""

    def test_full_artist_properties(self, factory):
        """Test properties of a FullArtist object."""
        artist = factory._create_object_from_data('artist',
                                                  MOCK_FULL_ARTIST_DATA['id'],
                                                  MOCK_FULL_ARTIST_DATA,
                                                  is_full_object=True)
        
        assert artist.name == MOCK_FULL_ARTIST_DATA['name']
        assert artist.popularity == MOCK_FULL_ARTIST_DATA['popularity']
        assert artist.followers == MOCK_FULL_ARTIST_DATA['followers']['total']
        assert artist.genres == MOCK_FULL_ARTIST_DATA['genres']
        # Derived properties
        assert artist.uri == f"spotify:artist:{artist.id}"
        assert artist.external_urls['spotify'] == f"https://open.spotify.com/artist/{artist.id}"

    def test_full_album_properties(self, factory):
        """Test properties of a FullAlbum object."""
        album = factory._create_object_from_data('album',
                                                 MOCK_FULL_ALBUM_DATA['id'],
                                                 MOCK_FULL_ALBUM_DATA,
                                                 is_full_object=True)

        assert album.name == MOCK_FULL_ALBUM_DATA['name']
        assert album.label == MOCK_FULL_ALBUM_DATA['label']
        assert album.popularity == MOCK_FULL_ALBUM_DATA['popularity']
        assert len(album.tracks) == 1
        assert album.tracks[0].id == MOCK_FULL_ALBUM_DATA['tracks']['items'][0]['id']

    def test_full_track_properties(self, factory):
        """Test properties of a FullTrack object."""
        factory._create_object_from_data('album',
                                         MOCK_SIMPLE_ALBUM_DATA['id'],
                                         MOCK_SIMPLE_ALBUM_DATA)
        track = factory._create_object_from_data('track',
                                                 MOCK_FULL_TRACK_DATA['id'],
                                                 MOCK_FULL_TRACK_DATA,
                                                 is_full_object=True)

        assert track.name == MOCK_FULL_TRACK_DATA['name']
        assert track.popularity == MOCK_FULL_TRACK_DATA['popularity']
        assert track.isrc == MOCK_FULL_TRACK_DATA['external_ids']['isrc']
        assert track.duration == "03:48" # 228293 ms
        assert track.album.id == MOCK_SIMPLE_ALBUM_DATA['id']

    def test_playlist_properties(self, factory):
        """Test properties of a Playlist object."""
        factory._create_object_from_data('album',
                                         MOCK_SIMPLE_ALBUM_DATA['id'],
                                         MOCK_SIMPLE_ALBUM_DATA)
        playlist = factory._create_object_from_data('playlist',
                                                    MOCK_PLAYLIST_DATA['id'],
                                                    MOCK_PLAYLIST_DATA,
                                                    is_full_object=True)

        assert playlist.name == MOCK_PLAYLIST_DATA['name']
        assert playlist.description == MOCK_PLAYLIST_DATA['description']
        assert playlist.owner_name == MOCK_PLAYLIST_DATA['owner']['display_name']
        assert len(playlist) == 1
        assert len(playlist.tracks) == 1
        assert playlist.tracks[0].id == MOCK_FULL_TRACK_DATA['id']

    def test_data_is_cached(self, factory):
        """Verify that object attributes are stored and not re-fetched."""
        # Create a full artist, which should have its data stored internally
        artist = factory.FullArtist(MOCK_FULL_ARTIST_DATA, factory)

        # Accessing properties should not trigger new API calls
        with patch.object(factory, '_request') as mock_req:
            _ = artist.popularity
            _ = artist.followers
            _ = artist.genres
            mock_req.assert_not_called()

    def test_derived_and_excluded_properties_not_in_cache(self, factory):
        """
        Verify that properties like URI, URLs, or separately fetched data (images)
        are not part of the core cached data dict of the object.
        """
        artist = factory.FullArtist(MOCK_FULL_ARTIST_DATA, factory)
        
        # These are dynamically generated or handled by specific methods
        assert '_uri' not in artist.__dict__
        assert '_external_urls' not in artist.__dict__
        assert '_href' not in artist.__dict__
        assert '_images' not in artist.__dict__ # images are fetched on demand

        # These are part of the core data
        assert '_popularity' in artist.__dict__
        assert '_followers' in artist.__dict__
        assert '_genres' in artist.__dict__

