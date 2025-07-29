import warnings
from datetime import datetime, timedelta
from time import sleep
import pickle
import threading
import webbrowser
import requests
import base64
import urllib.parse
from typing import List, Dict, Union
from collections import namedtuple

import requests
from tqdm import tqdm
from flask import Flask, request, redirect

class AttrDict(dict):
    """
    A dictionary subclass that allows
    attribute-style access to its keys.
    """
    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError as e:
            raise AttributeError(
                f"'AttrDict' object has no attribute '{key}'") from e

    def __setattr__(self, key, value):
        self[key] = value

    def __delattr__(self, key):
        try:
            del self[key]
        except KeyError as e:
            raise AttributeError(
                f"'AttrDict' object has no attribute '{key}'") from e

class SIAP_Factory:
    """
    A singleton factory class to interact with
    the Spotify REST API in an ORM-like manner.
    It handles authentication, request retries,
    pagination, and object caching.
    """
    _instance = None
    SPOTIFY_ID_LEN = 22

    # Named tuple to hold a reference to a cache object's key.
    # This is used in case the same entity has multiple IDs
    # in Spotify's database, e.g. getting an artist by its Spotify ID
    # returns an artist object with a DIFFERENT ID, but it's
    # still the same artist. The CachePointer object is stored
    # in the cache under the requested (secondary) ID, and it points to the
    # actual artist etc. object in the cache, which is shelved under the
    # actual ID contained in the object's data as returned by Spotify.
    # Thus the value of the ref attribute is the (main) ID of the object.
    CachePointer = namedtuple('CachePointer', ['ref'])

    class ObjectCache(dict):
        """
        A dictionary subclass that stores objects
        of a specific type and automatically resolves
        cache pointer values to the actual objects.

        Items and values methods ignore CachePointer values
        and key-value pairs where the value is a CachePointer.
        """
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

        def __getitem__(self, key):
            value = super().__getitem__(key)
            if isinstance(value, SIAP_Factory.CachePointer):
                # Resolve the pointer to the actual object
                return self[value.ref]
            return value

        def __setitem__(self, key, value, resolve_pointer=False):
            if (key in self
                    and isinstance(super().__getitem__(key),
                                   SIAP_Factory.CachePointer)
                    and resolve_pointer):
                ref_key = super().__getitem__(key).ref
                super().__setitem__(ref_key, value)
            else:
                super().__setitem__(key, value)

        def get(self, key, default=None):
            value = super().get(key, default)
            if isinstance(value, SIAP_Factory.CachePointer):
                # Resolve the pointer to the actual object
                return self[value.ref]
            return value

        # Items and values should ignore CachePointer values
        # and key-value pairs the value of which is a CachePointer.
        # Thus if the items are iterated over, they will not include
        # artificial duplicate values.
        def items(self):
            return_list = []
            for key, value in super().items():
                if not isinstance(value, SIAP_Factory.CachePointer):
                    return_list.append((key, value))
            return return_list
        
        def values(self):
            return [value for _, value in self.items()]

        def pointers(self):
            """
            Returns a dictionary of keys that hold CachePointer values
            and the referenced keys that the pointers point to.

            This is useful for debugging or inspecting
            the cache to see which keys are CachePointers.

            len(pointers) + len(items) should be equal to len(self)
            """
            return {key: value.ref
                    for key, value in super().items()
                    if isinstance(value, SIAP_Factory.CachePointer)}
                        
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(SIAP_Factory, cls).__new__(cls)
        return cls._instance

    def __init__(self, client_id=None, client_secret=None,
                 credentials_file="client_credentials.txt",
                 auth_server_ip="127.0.0.1",
                 auth_server_port=8050,
                 silent=False, max_retries=3):
        """
        Initializes the factory with the given
        client ID and secret.
        If client_id and client_secret are not provided,
        the initialization will attempt to read them
        from a credentials file on the given path,
        which should contain the client ID on the first line
        and the client secret on the second line.
        If the file is not found or does not contain the
        required information, and client_id and client_secret
        are not provided as arguments either,
        a RuntimeError is raised.
        Args:
            client_id (str): Spotify API client ID.
            client_secret (str): Spotify API client secret.
            auth_server_ip (str): IP address for a Flask auth server
                that handles user authorization. Defaults to 127.0.0.1.
            auth_server_port (int): Port for the Flask auth server.
                Defaults to 8050.
            silent (bool): If True, suppresses output messages
                and progress bars. Defaults to False (verbose mode).
        """
        # The singleton pattern requires initialization logic to run only once.
        if hasattr(self, '_initialized'):
            return
        
        if client_id is None or client_secret is None:
            try:
                with open(credentials_file, "r") as f:
                    lines = f.readlines()
                    client_id = lines[0].strip()
                    client_secret = lines[1].strip()
            except:
                pass

        if not client_id or not client_secret:
            raise RuntimeError("Client ID and Client Secret are "
                               "required for initialization.")
        
        self.client_id = client_id
        self.client_secret = client_secret
        self.silent = silent
        self.max_retries = max_retries
        
        self.base_api_url = "https://api.spotify.com/v1"
        self.auth_url = "https://accounts.spotify.com/api/token"
        
        # Cache for storing created objects by type and ID
        # This is the most important part of the factory.
        self._cache = {
            'artist': SIAP_Factory.ObjectCache({}),
            'album': SIAP_Factory.ObjectCache({}),
            'track': SIAP_Factory.ObjectCache({}),
            'playlist': SIAP_Factory.ObjectCache({}),
            'show': SIAP_Factory.ObjectCache({}),
            'episode': SIAP_Factory.ObjectCache({}),
            'audiobook': SIAP_Factory.ObjectCache({}),
        }

        # These are the "client credentials" used for
        # everything except user-specific actions.
        # These include searching, getting artists, albums,
        # tracks, public, playlists, etc.
        self._access_token = None
        self._token_expiration_time = None

        # These are the IP address and port
        # on which the Flask server runs to handle
        # user authorization. The server is started
        # when the user calls a method that requires
        # user authorization, such as creating a playlist.
        self.auth_server_ip = auth_server_ip
        self.auth_server_port = auth_server_port

        # These are the user authorization tokens by which
        # the user authorizes the app to access their
        # private playlists, modify them, etc.
        self._auth_access_token = None
        self._auth_refresh_token = None
        self._auth_token_expiration_time = None

        self._get_access_token()
        self._initialized = True

    def save_cache(self, filename: str):
        """
        Saves the current cache to a pickle file.
        """
        with open(filename, 'wb') as f:
            pickle.dump(self._cache, f)

    def load_cache(self, filename: str):
        """
        Loads a cache from a pickle file.
        """
        try:
            with open(filename, 'rb') as f:
                self._cache = pickle.load(f)
        except FileNotFoundError:
            if not self.silent:
                print(f"Cache file '{filename}' not found. "
                      "Starting with an empty cache.")

    @property
    def albums(self) -> ObjectCache:
        """
        Returns a dict containing all albums in the cache.
        The keys are album IDs, and the values are simplified
        or full album objects.
        """
        return self._cache['album']

    @property
    def artists(self) -> ObjectCache:
        """
        Returns a dict containing all artists in the cache.
        The keys are artist IDs, and the values are simplified
        or full artist objects.
        """
        return self._cache['artist']

    @property
    def tracks(self) -> ObjectCache:
        """
        Returns a dict containing all tracks in the cache.
        The keys are track IDs, and the values are simplified
        or full track objects.
        """
        return self._cache['track']

    @property
    def playlists(self) -> ObjectCache:
        """
        Returns a dict containing all playlists in the cache.
        The keys are playlist IDs, and the values are playlist objects.
        """
        return self._cache['playlist']

    def _get_access_token(self) -> None:
        """
        Retrieves and stores a new access token from the Spotify API.
        Raises ValueError if the request fails.
        """
        try:
            response = requests.post(self.auth_url, data={
                'grant_type': 'client_credentials',
                'client_id': self.client_id,
                'client_secret': self.client_secret,
            })
            response.raise_for_status()
            data = response.json()
            self._access_token = data['access_token']
            expires_in = data.get('expires_in', 3600)
            self._token_expiration_time =\
                datetime.now() + timedelta(seconds=expires_in)
        except requests.exceptions.RequestException as e:
            print("FATAL: Could not authenticate "
                  f"with Spotify API. Error: {e}")
            raise ValueError(
                "Failed to retrieve access token. "
                "Please check your client ID and secret.") from e

    def _get_headers(self, auth_type='client') -> Dict[str, str]:
        """
        Constructs request headers and retrieves an access token
        from the API or refreshes it if it's expired.
        Args:
            auth_type (str): The type of authentication to use.
                'client' for client credentials,
                'user' for user authorization.
        Returns:
            A dictionary containing the 'Authorization' header.
        Raises ValueError if the user authorization fails.
        """
        if auth_type == 'client':
            # An access token is retrieved on creation of the factory,
            # so it is assumed to be available.
            # Check if the access token is expired and
            # refresh it if necessary.
            if (not self._token_expiration_time
                or self._token_expiration_time < datetime.now()):
                if not self.silent:
                    print("Access token expired, refreshing...")
                self._get_access_token()
            return {'Authorization': f'Bearer {self._access_token}'}

        elif auth_type == 'user':
            if not self._auth_access_token:
                # User authorization has not yet been completed
                # for user-specific actions
                print("User authorization is required for this action.")
                print("Starting the authorization flow...")
                self._run_auth_server()

                if not self._auth_access_token:
                    raise ValueError("User authorization failed. "
                        "Please check your credentials and try again.")
                return {'Authorization': f'Bearer {self._auth_access_token}'}

            # Check if the user access token is expired
            # and refresh it if necessary            
            if (not self._auth_token_expiration_time
                or self._auth_token_expiration_time < datetime.now()):
                if not self.silent:
                    print("User access token expired, refreshing...")
                self._refresh_auth_token()
            return {'Authorization': f'Bearer {self._auth_access_token}'}

    def _request(self, method: str, url: str,
                 **kwargs) -> Dict[str, Union[str, List]]:
        """
        A centralized method for making API requests
        with built-in error handling and retries.
        Args:
            method (str): HTTP method (GET, POST, etc.)
            url (str): The API endpoint URL
            **kwargs: Additional parameters for the request
        Returns:
            The parsed JSON response from the API as a
            dictionary-like json object.
        """
        for attempt in range(self.max_retries):
            try:
                headers = self._get_headers()
                response = requests.request(method, url,
                                            headers=headers, **kwargs)
                
                # Handle specific error codes before raising for status
                if response.status_code == 401:
                    self._get_access_token()
                    continue 

                if response.status_code == 429:
                    wait_time = int(response.headers.get('Retry-After', 1))
                    if not self.silent:
                        print("Warning: Received 429 (Rate Limit Exceeded). "
                              f"Waiting {wait_time} s.")
                    sleep(wait_time)
                    continue

                response.raise_for_status() # Raise HTTPError for other 4xx/5xx responses
                return response.json()

            except requests.exceptions.HTTPError as e:
                # Handle server-side errors (5xx)
                if 500 <= e.response.status_code < 600:
                    wait_time = 3
                    if not self.silent:
                        print("Warning: Received server error "
                              f"{e.response.status_code}. "
                              f"Retrying in {wait_time}s.")
                    sleep(wait_time)
                else:
                    # For other client errors, break and re-raise
                    raise e
            except requests.exceptions.RequestException as e:
                # For connection errors, etc.
                if attempt < self.max_retries - 1:
                    if not self.silent:
                        print(f"Warning: Request failed ({e}). Retrying...")
                    sleep(1)
                else:
                    raise e

        raise requests.exceptions.RequestException(
            f"API request failed after {self.max_retries} retries.")

    def _paginate(self, initial_response: dict,
                  max_results: Union[int, None], silent: bool,
                  search_type=None) -> List[Dict[str, Union[str, List]]]:
        """
        Handles pagination for any API endpoint
        that returns a paginated list.
        """
        items = initial_response.get('items', [])
        total = initial_response.get('total')
        limit = initial_response.get('limit')
        next_url = initial_response.get('next')

        if max_results and len(items) > max_results:
            return items[:max_results]

        # Show progress bar only if there's more than one page and not silent
        show_progress = total and limit and total > limit and not silent
        
        progress_bar = None

        if max_results:
            total = min(total, max_results)
        else:
            # If no max_results is specified, use total from the API.
            # This is useful because the API changes the total
            # on each paginated search GET request, and this behavior
            # would not be consistent with the progress bar.
            # The search could go on longer than the number of items
            # shown in the progress bar.
            # We want search pages to stop once the end of the
            # progress bar is reached.
            max_results = total

        if show_progress:
            progress_bar = tqdm(total=total,
                                initial=len(items), 
                                desc="Fetching pages", unit="items")
        
        while next_url:
            data = self._request('GET', next_url)
            if search_type:
                data = data[search_type]
            new_items = data.get('items', [])
            items.extend(new_items)
            if len(items) > max_results:
                diff = len(items) - max_results
                if progress_bar:
                    progress_bar.update(len(new_items)-diff)
                    progress_bar.close()
                return items[:max_results]

            next_url = data.get('next')
            if progress_bar:
                progress_bar.update(len(new_items))
        
        if progress_bar:
            progress_bar.close()

        return items

    def _create_object_from_data(
            self, obj_type: str, requested_obj_id: str, data: dict,
            is_full_object=False) -> Union['SIAP_Factory.BaseObject', None]:
        """
        Creates or updates a cached object from API data.
        If a simplified object exists and full data
        is provided, it upgrades the object.
        """
        assert obj_type in self._cache, \
            f"Object type '{obj_type}' is not supported."

        obj_id = data.get('id')
        if not obj_id:
            raise ValueError(
                f"Data for {obj_type} must contain an 'id' field.")

        # If the requested ID is not the same as the ID in the data,
        # this means that the user requested the entity by a secondary ID
        # in a case where Spotify has multiple IDs for the same entity.
        # The GET request then returns the entity with its main ID.
        # In this case, we need to create a CachePointer that is stored
        # in the cache under the requested ID, and it points to the
        # actual object in the cache, which is shelved under the main ID.

        if requested_obj_id != obj_id:
            # Create a CachePointer to the actual object
            # and store it in the cache under the requested ID.
            self._cache[obj_type][requested_obj_id] =\
                SIAP_Factory.CachePointer(ref=obj_id)
        
        # The referenced object itself may still need to be created
        # or updated in the cache.

        existing_obj = self._cache[obj_type].get(obj_id)

        if is_full_object:
            full_type = self._get_class_for_type(obj_type, is_full=True)

            # If a full object already exists, return it. If not, create one.
            if isinstance(existing_obj, full_type):
                return existing_obj
            else:
                # Create a new full object using the class constructor
                # and replace the simplified one in cache if there is one.
                # Since obj_id is coming from the Spotify data, it is
                # (hopefully) the main ID of the object and does not need
                # to be resolved.
                obj = full_type(data, self)
                self._cache[obj_type][obj_id] = obj
                return obj
        else: # A simplified object is requested
            # If any object (full or simplified) exists, return it
            if existing_obj:
                return existing_obj
            # Otherwise, create a new simplified one
            else:
                obj = self._get_class_for_type(
                    obj_type, is_full=False)(data, self)
                self._cache[obj_type][obj_id] = obj
                return obj

    def _get_class_for_type(self, obj_type: str,
                            is_full: bool) -> 'SIAP_Factory.BaseObject':
        """
        Returns the appropriate class (e.g., FullArtist)
        for a given type and status.
        Raises ValueError for unsupported types.
        """
        class_map = {
            'artist': (self.Artist, self.FullArtist),
            'album': (self.Album, self.FullAlbum),
            'track': (self.Track, self.FullTrack),
            'playlist': (self.Playlist, self.Playlist),
        }

        if obj_type not in class_map:
            raise ValueError(
                f"Object creation is not supported for type: '{obj_type}'")

        simplified_class, full_class = class_map[obj_type]
        
        if is_full:
            return full_class
        else:
            return simplified_class

    def _run_auth_server(self, server_ip=None, port=None) -> None:
        """
        Starts a Flask server to handle Spotify OAuth authentication.
        This method is used to redirect the user to Spotify's
        authorization page and handle the callback.

        The method assumes that the callback URL is
        http://<server_ip>:<port>/callback.
        This URL needs to be set in the Spotify Developer Dashboard.
        The user's name and email who is logged in to Spotify
        and completed the authorization also need to be set
        in the Dashboard under User Management for the app.
        Otherwise the Spotify API will return an authorization error.

        Args:
            server_ip (str): The IP address to run the Flask server on.
                Defaults to the factory's auth_server_ip attribute,
                which is 127.0.0.1 by default.
            port (int): The port to run the Flask server on.
                Defaults to the factory's auth_server_port attribute,
                which is 8050 by default.
        """
        if server_ip is None:
            server_ip = self.auth_server_ip
        if port is None:
            port = self.auth_server_port
        shutdown_event = threading.Event()
        app = Flask(__name__)
        server_thread = None
        redirect_uri = f'http://{server_ip}:{port}/callback'
        # Define the scope for the authorization.
        # Scopes comprise only those that are needed for the app
        # to be able to create, read and modify the user's playlists.
        scope = ('playlist-read-private '
                 'playlist-modify-private '
                 'playlist-modify-public')

        # To let the main app stop the Flask server
        def shutdown():
            func = request.environ.get('werkzeug.server.shutdown')
            if func:
                func()

        @app.route('/')
        def login():
            params = {
                'client_id': self.client_id,
                'response_type': 'code',
                'redirect_uri': redirect_uri,
                'scope': scope,
                'show_dialog': 'true',
                'state': 'secure_random_state', # Optionally use a secure random string for CSRF protection
            }
            auth_params = urllib.parse.urlencode(params)
            url = f"https://accounts.spotify.com/authorize?{auth_params}"
            return redirect(url)

        @app.route('/shutdown-dummy')
        def shutdown_dummy():
            return ''

        @app.route('/callback')
        def callback():
            code = request.args.get('code')
            if not code:
                return "Authorization failed."

            # Exchange code for token
            token_url = 'https://accounts.spotify.com/api/token'
            auth_str = f"{self.client_id}:{self.client_secret}"
            b64_auth = base64.b64encode(auth_str.encode()).decode()

            headers = {
                'Authorization': f'Basic {b64_auth}',
                'Content-Type': 'application/x-www-form-urlencoded'
            }

            data = {
                'grant_type': 'authorization_code',
                'code': code,
                'redirect_uri': redirect_uri
            }

            res = requests.post(token_url, headers=headers, data=data)
            if res.status_code != 200:
                return f"Failed to get token: {res.text}"

            tokens = res.json()
            self._auth_access_token = tokens['access_token']
            self._auth_refresh_token = tokens['refresh_token']
            self._auth_token_expiration_time =\
                datetime.now() + timedelta(seconds=tokens['expires_in'])

            # shutdown_func = request.environ.get('werkzeug.server.shutdown')
            # if shutdown_func is None:
            #     raise RuntimeError('Not running with the Werkzeug Server')
            # shutdown_func()

            # Signal to shut down
            shutdown_event.set()

            return "Authorization successful! You can close this window."

        def flask_thread():
            app.run(host="127.0.0.1", port=8050, use_reloader=False)

        # Start Flask in a thread
        server_thread = threading.Thread(target=flask_thread)
        server_thread.daemon = True
        server_thread.start()

        # Wait for Flask to be ready
        sleep(1)

        # Open browser to login page, which runs on the / root URL
        webbrowser.open(f"http://{server_ip}:{port}/")

        # Wait for shutdown signal
        shutdown_event.wait()

        # Kill Flask after auth (forcefully)
        requests.get("http://127.0.0.1:8050/shutdown-dummy")  # dummy request to unblock server
        
        print("Flask auth server has stopped.")

    def _refresh_auth_token(self) -> None:
        auth_str = f"{self.client_id}:{self.client_secret}"
        b64_auth = base64.b64encode(auth_str.encode()).decode()

        headers = {
            'Authorization': f'Basic {b64_auth}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        data = {
            'grant_type': 'refresh_token',
            'refresh_token': self._auth_refresh_token
        }

        response = requests.post('https://accounts.spotify.com/api/token',
                                 headers=headers, data=data)

        if response.status_code != 200:
            raise Exception(f"Failed to refresh token: {response.text}")

        new_tokens = response.json()

        # Update access_token, 
        # possibly refresh_token too (Spotify may return a new one)
        self._auth_access_token = new_tokens['access_token']
        if 'refresh_token' in new_tokens:
            self._auth_refresh_token = new_tokens['refresh_token']
        self._auth_token_expiration_time =\
            datetime.now() + timedelta(seconds=new_tokens['expires_in'])

    def search(self, query: str,
               obj_type="track",
               filters=None, max_results=None,
               silent=None) -> List[Union['SIAP_Factory.BaseObject', str]]:
        """
        Performs a search on the Spotify API.

        Args:
            query (str): The search query.
            obj_type (str, optional): The type of item to search for.
                Defaults to "track".
                Allowed values: "album", "artist", "playlist",
                                "track", "show", "episode", "audiobook".
            filters (dict, optional): Field filters to apply to the search.
                Defaults to None, meaning no filters are applied.
                Allowed filters depend on the type:
                - "album": album, artist*, year, upc,
                  {'tag': 'new'}, {'tag': 'hipster'}
                - "artist": artist*, year, genre
                - "track": track, artist, album, year, isrc, genre
                - "playlist", "show", "episode", "audiobook": no filters
                Notes:
                - items marked by * are allowed in the API but don't return
                  any results in practice,
                - tag:new means new releases,
                - tag:hipster means "only albums with the
                  lowest 10% popularity".
                - the value for year can be a full year or a range
                  (e.g., "2020", "2019-2021").
                - upc is the Universal Product Code, a 12-digit barcode
                  that uniquely identifies an album.
                - isrc means International Standard Recording Code, see
                  https://en.wikipedia.org/wiki/International_Standard_Recording_Code
            max_results (int, optional): The maximum number of results
                to return. Defaults to None, meaning unlimited.
            silent (bool, optional): If True, suppresses output messages
                and progress bars. Defaults to None, which means that the
                factory's silent mode setting is used.

        Returns:
            - A list of objects of specified type if obj_type is one of
                "album", "artist", "playlist" or "track".
            - A list of strings if obj_type is "show", "episode" or "audiobook". 
        """
        if obj_type not in ["album", "artist", "playlist",
                               "track", "show", "episode", "audiobook"]:
            raise ValueError("Invalid search type specified.")

        is_silent = self.silent if silent is None else silent

        if filters:
            self._validate_filters(obj_type, filters)
            query += " " + " ".join([f"{k}:{v}"
                                     for k, v in filters.items()])

        params = {'q': query, 'type': obj_type}

        endpoint = f"{self.base_api_url}/search"
        response = self._request('GET', endpoint, params=params)
        
        paginated_data_key = f"{obj_type}s"
        if response and paginated_data_key in response:
            if not is_silent:
                print(f"Found {response[f'{obj_type}s']['total']} "
                        f"{obj_type}s", end="")
                if (max_results and 
                    max_results < response[f"{obj_type}s"]['total']):
                    print(f", retrieving the first {max_results}.", end="")
                print()
        else:
            if not is_silent:
                print(f"No results found.")
            return []

        paginated_response = response[paginated_data_key]
        all_items_data = self._paginate(paginated_response,
                                        max_results, is_silent,
                                        search_type=paginated_data_key)        

        if obj_type in ["show", "episode", "audiobook"]:
            return [item_data for item_data in all_items_data]
        
        return_items = []

        if obj_type in ["artist", "track"]:
            full = True  # according to the API
        else:
            full = False

        for item_data in all_items_data:
            try:
                item = self._create_object_from_data(
                    obj_type, item_data['id'], item_data, is_full_object=full)
                return_items.append(item)
            except ValueError as e:
                if not is_silent:
                    print(f"Error creating object for {obj_type}: {e}")
                    print("Invalid data:", item_data)
                continue            

        # Remove duplicates from the return list
        seen_ids = set()
        unique_items = []
        for item in return_items:
            if item.id not in seen_ids:
                seen_ids.add(item.id)
                unique_items.append(item)

        if not is_silent:
            print(f"Retrieved {len(unique_items)} unique {obj_type}s.")

        return unique_items
    
    def _validate_filters(self, obj_type: str,
                          filters: Dict[str, str]) -> None:
        """
        Checks whether the provided filters are
        valid for the given search type.
        Raises ValueError if any filter is invalid.
        """
        valid_filters = {
            "album": ["album", "artist", "year",
                      "upc", "tag"],
            "artist": ["artist", "year", "genre"],
            "track": ["track", "artist", "album",
                      "year", "isrc", "genre"],
            "playlist": [],
            "show": [],
            "episode": [],
            "audiobook": []
        }
        for f in filters:
            if f not in valid_filters[obj_type]:
                raise ValueError("Invalid filter "
                                 f"'{f}' for search type '{obj_type}'")
        if ("tag" in filters
            and filters["tag"] not in ["new", "hipster"]):
            raise ValueError("Invalid tag filter. "
                             "Allowed values are 'new' and 'hipster'.")
    
    def _full_exists(self, obj_type: str, obj_id: str) -> bool:
        """
        Checks if an object of the given full type
        and ID exists in the cache.
        Returns True if it exists, False otherwise.
        """
        existing_obj = self._cache[obj_type].get(obj_id, None)
        full_type = self._get_class_for_type(obj_type, is_full=True)
        return isinstance(existing_obj, full_type)

    def get_artist(self, artist_id: str) -> 'SIAP_Factory.FullArtist':
        """
        Retrieves a full artist object by its ID.
        """
        if self._full_exists('artist', artist_id):
            return self.artists[artist_id]
        
        data = self._request(
            'GET', f"{self.base_api_url}/artists/{artist_id}")
        return self._create_object_from_data(
            'artist', artist_id, data, is_full_object=True)

    def get_album(self, album_id: str) -> 'SIAP_Factory.FullAlbum':
        """
        Retrieves a full album object by its ID.
        """
        if self._full_exists('album', album_id):
            return self.albums[album_id]

        data = self._request(
            'GET', f"{self.base_api_url}/albums/{album_id}")
        return self._create_object_from_data(
            'album', album_id, data, is_full_object=True)

    def get_track(self, track_id: str) -> 'SIAP_Factory.FullTrack':
        """
        Retrieves a full track object by its ID.
        """
        if self._full_exists('track', track_id):
            return self.tracks[track_id]

        data = self._request(
            'GET', f"{self.base_api_url}/tracks/{track_id}")
        return self._create_object_from_data(
            'track', track_id, data, is_full_object=True)

    def get_playlist(self, playlist_id: str) -> 'SIAP_Factory.FullPlaylist':
        """
        Retrieves a full playlist object by its ID.
        """
        if playlist_id in self.playlists:
            return self.playlists[playlist_id]
        data = self._request(
            'GET', f"{self.base_api_url}/playlists/{playlist_id}")
        return self._create_object_from_data(
            'playlist', playlist_id, data, is_full_object=True)

    def create_user_playlist(self, playlist_name: str, description: str,
                             public=True) -> 'SIAP_Factory.FullPlaylist':
        """
        Creates a new, empty user playlist with
        the given name and description. It can be public or private
        (default is public) and is non-collaborative when created.
        It can be modified later to be collaborative
        using the playlist object's collaborative property.

        This method requires the user to be authenticated.
        For this, the user must be logged in to Spotify. When this
        method is called, an authorization flow is started. The user
        must complete the authorization flow in their browser.
        This simply means clicking "Allow" on the Spotify
        authorization page that opens in the browser.
        
        For authentication, the factory starts a Flask server
        on the specified IP address and port. By default,
        it runs on 127.0.0.1:8050. The ip and port can be
        changed by passing the auth_server_ip and
        auth_server_port parameters to the factory's constructor
        or by setting its attributes of the same name.
        For authorization to work, the callback URL
        must be set in the Spotify Developer Dashboard to
        the same address and port, adding '/callback', e.g.,
        for the default values,
        http://127.0.0.1:8050/callback.

        Once the authentication has been completed,
        the new playlist is created and returned as a FullPlaylist
        object, and tracks can be added to it using method calls.

        Authorisation is only completed once. The factory
        stores the access token and refresh token, so the user
        does not have to log in again for every playlist creation.

        Args:
            playlist_name (str): The name of the playlist. Required.
            description (str): The description of the playlist. Optional.
            public (bool): Whether the playlist should be public or private.
        Returns:
            A FullPlaylist object representing the created playlist.

        Note: SpotIsyAsPy only supports creating playlists
        for the authenticated user as well as adding tracks to it.
        It does not support creating or modifying playlist
        for other users, removing items from playlists,
        reordering items or deleting playlists.
        """
        headers = self._get_headers(auth_type='user')
        headers['Content-Type'] = 'application/json'

        data = {
            'name': playlist_name,
            'description': description,
            'public': public
        }

        response = requests.post(
            f"{self.base_api_url}/me/playlists",
            headers=headers, json=data)

        if response.status_code != 201:
            raise requests.exceptions.HTTPError(
                f"Failed to create playlist: {response.text}")
        
        new_playlist_id = response.json().get('id')

        return self.get_playlist(new_playlist_id)

    class BaseObject:
        """Base class for all Spotify objects to handle common logic."""
        def __init__(self, data: dict, factory: 'SIAP_Factory'):
            self._factory = factory
            self.type = data.get('type')
            self.id = data.get('id')

        def _fetch_full_data(self) -> dict:
            """Fetches full object data from API."""
            full_data = self._factory._request(
                'GET', f"{self._factory.base_api_url}/{self.type}s/{self.id}")
            return full_data

        @property
        def external_urls(self) -> AttrDict:
            """
            Returns a dictionary with external URLs for the object.
            The dictionary contains a single key 'spotify'
            with the URL to the object on Spotify.
            """
            return AttrDict(
                 {"spotify":
                  f"https://open.spotify.com/{self.type}/{self.id}"})

        @property
        def uri(self) -> str:
            return f"spotify:{self.type}:{self.id}"

        @property
        def href(self) -> str:
            return f"{self._factory.base_api_url}/{self.type}s/{self.id}"
            
        @property
        def images(self) -> Union[List[Dict[str, str]], None]:
            # Tracks don't have images, so we return None
            if self.type == 'track':
                return None
            return self._fetch_full_data().get('images', None)

        @property
        def full(self) -> 'SIAP_Factory.BaseObject':
            """
            Returns the full object corresponding to a simplified object.
            If the object is already full, it returns itself.
            """
            if self._factory._full_exists(self.type, self.id):
                return self._factory._cache[self.type][self.id]
            
            data = self._factory._request(
                'GET', f"{self._factory.base_api_url}/{self.type}s/{self.id}")
            return self._factory._create_object_from_data(
                self.type, self.id, data, is_full_object=True)

        @property
        def update(self) -> 'SIAP_Factory.BaseObject':
            """
            Returns the cached version of the current object.
            """
            return self._factory._cache[self.type][self.id]

        def to_dict(self) -> Dict[str, Union[str, List]]:
            """
            Retrieves the object's full data from the API
            and returns it as a dictionary.
            """
            # External-facing alias for _fetch_full_data
            return self._fetch_full_data()

    class Artist(BaseObject):
        """Represents a simplified Spotify Artist object."""
        def __init__(self, data: dict, factory: 'SIAP_Factory'):
            super().__init__(data, factory)
            self.name = data.get('name')

        @property
        def genres(self) -> List[str]:
            """
            Returns the artist's genres.
            Creates full artist object to access genres if necessary.
            """
            return self.full.genres

        @property
        def popularity(self) -> int:
            """
            Returns the artist's popularity.
            Creates full artist object to access popularity if necessary.
            """
            return self.full.popularity
        
        @property
        def followers(self) -> int:
            """
            Returns the artist's number of followers.
            Creates full artist object to access followers if necessary.
            """
            return self.full.followers
        
        @property
        def albums(self) -> List['SIAP_Factory.Album']:
            """
            Returns a list of the artist's albums.
            Creates full artist object to access albums if necessary.
            """
            return self.full.albums
        
        @property
        def appears_on(self) -> List['SIAP_Factory.Album']:
            """
            Returns a list of albums the artist appears on.
            Creates full artist object to access appears_on if necessary.
            """
            return self.full.appears_on
        
        def get_albums(self, *album_type) -> List['SIAP_Factory.Album']:
            """
            Returns a list of albums by type, similar to the API's
            include_groups parameter.
            Create full artist object to access albums if necessary.
            If no album type is specified, returns the artist's
            albums (including singles, compilations, etc.) and
            the albums they appear on.
            Args:
                album_type (zero, one or more strings):
                    The type(s) of albums to filter by.
                    Allowed values are "album", "single", "compilation"
                    or "appears_on".                    
            """
            return self.full.get_albums(*album_type)

        def __repr__(self):
            return f"<Simplified Artist: {self.name} (ID: {self.id})>"
        
        def __str__(self):
            return self.name

    class FullArtist(Artist):
        """Represents a full Spotify Artist object."""
        def __init__(self, data: dict, factory: 'SIAP_Factory'):
            super().__init__(data, factory)
            self._genres = data.get('genres', [])
            self._popularity = data.get('popularity')
            self._followers = data.get('followers', {}).get('total')
            self._albums = None  # list of album IDs
            self._appears_on = None  # list of album IDs
            self._tracks = []  # list of track IDs

        @property
        def genres(self) -> List[str]:
            return self._genres

        @property
        def popularity(self) -> int:
            return self._popularity
        
        @property
        def followers(self) -> int:
            return self._followers

        @property
        def albums(self) -> List['SIAP_Factory.Album']:
            """
            Lazily loads the artist's albums
            and ones they appear on.
            Returns a list of the artist's albums only.
            
            To return albums that the artist appears on,
            use the appears_on property.
            To return both the artist's albums
            and the ones they appear on, use get_albums().

            May return an empty list if the artist has no albums
            according to the API.
            """
            if self._albums is None:
                self._albums = []
                self._appears_on = []
                for album_type in ["album", "single", "compilation", 
                                   "appears_on"]:
                    if not self._factory.silent:
                        print(f"Fetching {album_type} albums")
                    endpoint =\
                        f"{self._factory.base_api_url}/artists/{self.id}/albums"
                    paginated_response = self._factory._request(
                        'GET', endpoint, params={'include_groups': album_type})
                    album_items = self._factory._paginate(
                        paginated_response, None, self._factory.silent)
                    for album_data in album_items:
                        try:
                            album_obj = self._factory._create_object_from_data(
                                'album', album_data['id'], album_data,
                                is_full_object=False)
                            if album_type == "appears_on":
                                self._appears_on.append(album_obj.id)
                            else:
                                self._albums.append(album_obj.id)
                        except ValueError as e:
                            if not self._factory.silent:
                                print(f"Error creating album object: {e}")
                                print("Invalid data:", album_data)
                            continue
            return [self._factory.albums[album_id]
                    for album_id in self._albums]

        @property
        def appears_on(self) -> List['SIAP_Factory.Album']:
            """
            Lazily loads the albums the artist appears on.
            Returns a list of albums where the artist is featured.
            This is different from the albums property,
            which returns the artist's own albums.

            May return an empty list if the artist does not appear
            on any albums according to the API.
            """
            if self._appears_on is None:
                self.albums
            return [self._factory.albums[album_id]
                    for album_id in self._appears_on]

        def get_albums(self, *album_type) -> List['SIAP_Factory.Album']:
            """
            Returns a list of albums by type, similar to the API's
            include_groups parameter.
            If no album type is specified, returns the artist's
            albums (including singles, compilations, etc.) and
            the albums they appear on.
            Args:
                album_type (zero, one or more strings):
                    The type(s) of albums to filter by.
                    Allowed values are "album", "single", "compilation"
                    or "appears_on".                    
            """
            if not album_type:
                return self.albums + self.appears_on
            if not all(t in ["album", "single", "compilation", "appears_on"]
                       for t in album_type):
                raise ValueError(
                    "Invalid album type. Allowed values are "
                    "'album', 'single', 'compilation', 'appears_on'.")
            filtered_albums = []
            for album in self.albums:
                if album.album_type in album_type:
                    filtered_albums.append(album)
            if 'appears_on' in album_type:
                filtered_albums.extend(self.appears_on)
            return filtered_albums

        def __repr__(self):
            return f"<Full Artist: {self.name} (ID: {self.id}, " +\
                f"Popularity: {self.popularity}, Followers: {self.followers})>"

    class Album(BaseObject):
        """Represents a simplified Spotify Album object."""
        def __init__(self, data: dict, factory: 'SIAP_Factory'):
            super().__init__(data, factory)
            self.name = data.get('name')
            self.album_type = data.get('album_type')  #  "album", "single", "compilation"
            self.total_tracks = data.get('total_tracks')
            self.release_date = data.get('release_date')
            self.release_date_precision = data.get(
                'release_date_precision') #  "day", "month" or "year"
            self.restrictions = data.get('restrictions', {}).get('reason')
            self._artist_ids = []
            for artist in data.get('artists', []):
                artist_id = artist.get('id')
                if artist_id:
                    self._artist_ids.append(artist_id)
                    self._factory._create_object_from_data(
                        'artist', artist_id, artist, is_full_object=False)
                assert artist_id in self._factory.artists, \
                    f"Artist ID {artist_id} not found in artists cache."
                assert self._factory.artists[artist_id].id == artist_id, \
                    f"Artist ID {artist_id} in cache does not match data."

        @property
        def artists(self) -> List['SIAP_Factory.Artist']:
            """
            Returns a list of Artist objects
            associated with this album.
            """
            return [self._factory.artists[artist_id]
                    for artist_id in self._artist_ids]

        @property
        def popularity(self) -> int:
            """
            Returns the album's popularity.
            Creates full album object to access popularity if necessary.
            """
            return self.full.popularity
        
        @property
        def label(self) -> Union[str, None]:
            """
            Returns the label of the album.
            Creates full album object to access label if necessary.
            """
            return self.full.label
        
        @property
        def tracks(self) -> List['SIAP_Factory.Track']:
            """
            Returns a list of Track objects.
            Creates full album object to access tracks if necessary.
            """
            return self.full.tracks

        @property
        def external_ids(self) -> AttrDict:
            """
            Returns a dictionary of external IDs for the album.
            This can include ISRC, EAN and UPC.
            Creates full album object to access external_ids if necessary.
            """
            return self.full.external_ids
        
        @property
        def ean(self) -> Union[str, None]:
            """
            Returns the EAN (European Article Number) of the album.
            Creates full album object to access EAN if necessary.
            """
            return self.full.ean
        
        @property
        def upc(self) -> Union[str, None]:
            """
            Returns the UPC (Universal Product Code) of the album.
            Creates full album object to access UPC if necessary.
            """
            return self.full.upc
        
        @property
        def isrc(self) -> Union[str, None]:
            """
            Returns the ISRC (International Standard Recording Code)
            of the album.
            Creates full album object to access ISRC if necessary.
            """
            return self.full.isrc

        def tracks_string(self, duration=True, artists=True) -> str:
            """
            Returns a string representation of the album's tracklist.
            Creates full album object to access tracks if necessary.
            Args:
                duration (bool): If True, includes track durations.
                artists (bool): If True, includes artist names.
            """
            return self.full.tracks_string(duration, artists)

        def full_info(self) -> str:
            """
            Returns a string representation of the album,
            including artist names, album name
            and tracklist.
            Creates full album object to access full info if necessary.
            """
            return self.full.full_info()
        
        def __repr__(self):
            return f"<Simplified Album: {self.name} (ID: {self.id}, Type: {self.album_type}, Release Date: {self.release_date})>"

        def __str__(self):
            return f"{' & '.join(str(a) for a in self.artists)}: {self.name}"

    class FullAlbum(Album):
        """Represents a full Spotify Album object."""
        def __init__(self, data:dict, factory: 'SIAP_Factory'):
            super().__init__(data, factory)
            self._label = data.get('label')
            self._popularity = data.get('popularity')
            self._external_ids = data.get('external_ids', {})
            self._tracks_partial = data.get('tracks', {})
            self._tracks = None
            self.tracks

        @property
        def popularity(self) -> int:
            return self._popularity
        
        @property
        def label(self) -> Union[str, None]:
            return self._label

        @property
        def external_ids(self) -> AttrDict:
            return AttrDict(self._external_ids)
        
        @property
        def ean(self) -> Union[str, None]:
            """Returns the EAN (European Article Number) of the album."""
            return self._external_ids.get('ean', None)
        
        @property
        def upc(self) -> Union[str, None]:
            """Returns the UPC (Universal Product Code) of the album."""
            return self._external_ids.get('upc', None)
        
        @property
        def isrc(self) -> Union[str, None]:
            """
            Returns the ISRC (International Standard Recording Code)
            of the album.
            """
            return self._external_ids.get('isrc', None)
        
        @property
        def tracks(self) -> List['SIAP_Factory.Track']:
            """Lazily loads the album's tracks."""
            if self._tracks is None:
                # If tracks are not loaded yet, fetch them
                if not self._tracks_partial:
                    endpoint = (self._factory.base_api_url
                                + f"/albums/{self.id}/tracks")
                    self._tracks_partial = self._factory._request(
                        'GET', endpoint)
                # If tracks are multi-page, paginate from partial data
                if self._tracks_partial.get('next'):
                    track_items = self._factory._paginate(
                        self._tracks_partial, None, self._factory.silent)
                else:
                    track_items = self._tracks_partial.get('items', [])

                # Populate the tracks list
                self._tracks = []
                for item in track_items:
                    if item.get('type') != 'track':
                        if not self._factory.silent:
                            warnings.warn(f"Skipping non-track item: {item}")
                        continue
                    # Create Track objects and cache them
                    track_obj = self._factory._create_object_from_data(
                        'track', item['id'], item, is_full_object=False)
                    self._tracks.append(track_obj.id)

                    # Set album ID for the track
                    # This is necessary for simplified tracks
                    # because they don't include album ID in the item data.
                    track_obj._album_id = self.id

                self._tracks_partial = None  # Clear partial data

            return [self._factory.tracks[track_id]
                    for track_id in self._tracks]

        def tracks_string(self, duration=True, artists=True) -> str:
            """
            Returns a string representation of the album's tracklist.
            """
            s = "Tracks:\n"
            for i, track in enumerate(self.tracks, start=1):
                dur_str = track.duration + " " if duration else ""
                artist_str = f" ({', '.join(str(a) for a in track.artists)})" if artists else ""
                s += f"\t{i:02d}. {dur_str}{track.name}{artist_str}\n"
            return s

        def full_info(self) -> str:
            """
            Returns a string representation of the album,
            including artist names, album name
            and tracklist.
            """
            s = f"{' & '.join(str(a) for a in self.artists)}: {self.name}\n" +\
                self.tracks_string()
            return s

        def __repr__(self):
            return f"<Full Album: {self.name} by {' & '.join(f'{str(a)} ({a.id})' for a in self.artists)} "\
                   f"(ID: {self.id}, Type: {self.album_type}, "\
                   f"Release Date: {self.release_date}, Popularity: {self.popularity},"\
                   f" Label: {self.label}, Total Tracks: {self.total_tracks})>"

    class Track(BaseObject):
        """Represents a simplified Spotify Track object."""
        def __init__(self, data: dict, factory: 'SIAP_Factory'):
            super().__init__(data, factory)
            self.name = data.get('name')
            self.disc_number = data.get('disc_number')
            self.track_number = data.get('track_number')
            self.duration_ms = data.get('duration_ms')
            self.explicit = data.get('explicit')
            self.restrictions = data.get('restrictions', {}).get('reason')
            self._artist_ids = []
            # The album ID is not included in the simplified track data
            # because the simplified track object is part of the album object.
            # This means that whenever a simplified track object is created,
            # it always has an album object associated with it, but the album ID
            # must be set manually after the track is created.
            self._album_id = None
            for artist in data.get('artists', []):
                artist_id = artist.get('id')
                if artist_id:
                    # Create a simplified Artist object
                    self._factory._create_object_from_data(
                        'artist', artist_id, artist, is_full_object=False)
                    self._artist_ids.append(artist_id)
                elif not self._factory.silent:
                    warnings.warn(f"Artist ID missing in track data: {data}")
            
        @property
        def album(self) -> 'SIAP_Factory.Album':
            """
            Returns the album object associated with the track.
            
            If a full album object is already cached when this method
            is called, this object is returned.
            
            If the album was not cached earlier, a full album object
            is created for it and returned.

            If a simplified album object was already cached
            independently of the track, it is returned without
            being fetched from the API or being upgraded to a 
            full album object.
            """

            # Unless the simplified track was created incorrectly,
            # it should always have an album ID, which is set
            # when the track is created as part of an album object,
            # after initialization of the track object.
            assert self._album_id is not None, \
                "Album ID is not set for the track. " \
                "This is likely an error in the code that created the track."
            
            # If this method is called for a simplified track,
            # a full album object is already cached by the time the
            # track is created, so it can be returned directly.
            # However, if it is called for a full track object
            # (via inheritance), it means that the track was created
            # without an album object as part of a playlist, search
            # results or directly retrieved by its ID.
            # In this case, the album ID is known from the track data,
            # but the album object is not cached, so it must be fetched
            # and created. Full track objects always contain a partial
            # album object, so the object to be associated with the track
            # should ideally be a partial album, but since it would
            # be wasteful to retrieve a partial album object (via a track)
            # or retrieve a full album object (via an album ID) but then
            # ignore some of its data on object creation, a full album
            # object is created for the track.
            return self._factory.albums.get(self._album_id) or \
                self._factory.get_album(self._album_id)
        
        @property
        def artists(self) -> List['SIAP_Factory.Artist']:
            return [self._factory.artists[artist_id]
                    for artist_id in self._artist_ids]

        @property
        def duration(self) -> str:
            """
            Returns string representation
            of duration in mm:ss format.
            """
            minutes, seconds = divmod(self.duration_ms // 1000, 60)
            return f"{minutes:02}:{seconds:02}"
        
        @property
        def popularity(self) -> int:
            """
            Returns the track's popularity.
            Creates full track object to access popularity if necessary.
            """
            return self.full.popularity

        @property
        def external_ids(self) -> AttrDict:
            """
            Returns a dictionary of external IDs for the track.
            This can include ISRC, EAN and UPC.
            Create full track object to access popularity if necessary.
            """
            return self.full.external_ids
        
        @property
        def ean(self) -> Union[str, None]:
            """
            Returns the EAN (European Article Number) of the track.
            Creates full track object to access EAN if necessary.
            """
            return self.full.ean
        
        @property
        def upc(self)   -> Union[str, None]:
            """
            Returns the UPC (Universal Product Code) of the track.
            Creates full track object to access UPC if necessary.
            """
            return self.full.upc
        
        @property
        def isrc(self):
            """
            Returns the ISRC (International Standard Recording Code)
            of the track.
            """
            return self.full.isrc

        @property
        def available_markets(self):
            """
            Returns a list of markets where the track is available.
            """
            return self._fetch_full_data().get('available_markets')

        def __repr__(self):
            return f"<Simplified Track: {self.name}, " \
                   + f"duration: {self.duration} " \
                   + f"(ID: {self.id}) from {self.album} "\
                   + f"(ID: '{self.album.id})>"

        def __str__(self):
            return self.name

    class FullTrack(Track):
        """Represents a full Spotify Track object."""
        def __init__(self, data: dict, factory: 'SIAP_Factory'):
            super().__init__(data, factory)
            self._popularity = data.get('popularity')
            self._album_id = data.get('album', {}).get('id')
            self._external_ids = data.get('external_ids', {})
            self.album  # Ensure album object is initialized and cached
        
        @property
        def popularity(self):
            return self._popularity

        @property
        def external_ids(self) -> AttrDict:
            return AttrDict(self._external_ids)
        
        @property
        def ean(self):
            """Returns the EAN (European Article Number) of the track."""
            return self._external_ids.get('ean', None)
        
        @property
        def upc(self):
            """Returns the UPC (Universal Product Code) of the track."""
            return self._external_ids.get('upc', None)
        
        @property
        def isrc(self):
            """Returns the ISRC (International Standard Recording Code) of the track."""
            return self._external_ids.get('isrc', None)

        def __repr__(self):
            return super().__repr__().replace("<Simplified", "<Full")
            
        def __str__(self):
            artist_names = ' & '.join(str(a) for a in self.artists)
            return f"Track: {self.name} by {artist_names}"

    class Playlist(BaseObject):
        """Represents a Spotify Playlist object."""
        def __init__(self, data: dict, factory: 'SIAP_Factory'):
            super().__init__(data, factory)
            self._name = data.get('name')
            self._description = data.get('description')
            self._collaborative = data.get('collaborative')
            self._public = data.get('public', None)
            self.owner_name = data.get('owner', {}).get('display_name')
            self.owner_id = data.get('owner', {}).get('id')
            self._tracks = None
            self._tracks_partial = data.get('tracks', {})
            self._len_tracks = self._tracks_partial.get('total', 0)

        @property
        def name(self):
            """Returns the name of the playlist."""
            return self._name

        @name.setter
        def name(self, new_name: str):
            """
            Sets a new name for the playlist and updates it on Spotify.
            Raises ValueError if the new name is empty.
            If the update is successful, updates the name of the playlist
            object. Has no effect if the update fails.

            User authorization is required for this operation
            and needs to be completed in a browser window
            that should open automatically if it is not already done.
            See SIAP_Factory.create_user_playlist() for more details.
            """
            if self._playlist_setter('name', new_name):
                self._name = new_name

        @property
        def description(self):
            """Returns the description of the playlist."""
            return self._description

        @description.setter
        def description(self, new_description: str):
            """
            Sets a new description for the playlist
            and updates it on Spotify. New description can be empty.
            If the update is successful, updates the description
            of the playlist object. Has no effect if the update fails.

            User authorization is required for this operation
            and needs to be completed in a browser window
            that should open automatically if it is not already done.
            See SIAP_Factory.create_user_playlist() for more details.
            """
            if self._playlist_setter('description', new_description):
                self._description = new_description
        
        @property
        def collaborative(self):
            """Returns whether the playlist is collaborative."""
            return self._collaborative
        
        @collaborative.setter
        def collaborative(self, is_collaborative: bool):
            """
            Sets whether the playlist is collaborative
            and updates it on Spotify.
            If the playlist is public, it cannot be collaborative.
            Raises ValueError if the playlist is public
            and collaborative is set to True.
            If the update is successful, updates the collaborative
            status of the playlist object. Has no effect if the update fails.

            User authorization is required for this operation
            and needs to be completed in a browser window
            that should open automatically if it is not already done.
            See SIAP_Factory.create_user_playlist() for more details.
            """
            if is_collaborative and self._public:
                raise ValueError(
                    "Collaborative playlists cannot be public. "
                    "Set 'public' to False before "
                    "setting 'collaborative' to True.")
            if self._playlist_setter('collaborative', is_collaborative):
                self._collaborative = is_collaborative

        @property
        def public(self):
            """Returns whether the playlist is public."""
            return self._public        

        @public.setter
        def public(self, is_public: bool):
            """
            Sets whether the playlist is public
            and updates it on Spotify.
            If the playlist is collaborative, it cannot be public.
            Raises ValueError if the playlist is collaborative
            and public is set to True.
            If the update is successful, updates the public
            status of the playlist object. Has no effect if the update fails.
            
            User authorization is required for this operation
            and needs to be completed in a browser window
            that should open automatically if it is not already done.
            See SIAP_Factory.create_user_playlist() for more details.
            """
            if is_public and self._collaborative:
                raise ValueError(
                    "Collaborative playlists cannot be public. "
                    "Set 'collaborative' to False before "
                    "setting 'public' to True.")
            if self._playlist_setter('public', is_public):
                self._public = is_public

        def _playlist_setter(self, attr_name, value):
            """
            Generic setter for playlist attributes.
            Raises ValueError if the value is invalid
            or if the attribute name is not valid.
            Updates the playlist on Spotify if possible.
            Args:
                attr_name (str): The name of the attribute to set.
                value: The value to set for the attribute.
            Returns:
                True if the value was successfully set,
                False if the value was not set due to an error.
            Raises:
                ValueError: If the attribute name is invalid
                or if the value is invalid.
            """
            if attr_name not in ['name', 'description',
                                 'public', 'collaborative']:
                raise ValueError(
                    f"Invalid attribute '{attr_name}' for Playlist.")
            if attr_name == 'name' and not value:
                raise ValueError(f"Playlist name cannot be empty.")
            headers = self._factory._get_headers(auth_type='user')
            headers['Content-Type'] = 'application/json'
            data = {attr_name: value}
            endpoint = f"{self._factory.base_api_url}/playlists/{self.id}"
            response = requests.put(endpoint, headers=headers, json=data)
            if response.status_code != 200:
                print(f"Failed to set value of {attr_name}: {response.text}")
                return False
            else:
                print(f"Successfully set {attr_name} to '{value}'")
                return True

        @property
        def tracks(self):
            """Lazily loads the playlist's tracks."""
            if self._tracks is None:
                self._tracks = []
                playlist_items = self._factory._paginate(
                    self._tracks_partial, None, self._factory.silent)
                
                episode_count = 0
                for item in playlist_items:
                    track_data = item.get('track')
                    if track_data and track_data.get('type') == 'track':
                        self._tracks.append(
                            self._factory._create_object_from_data(
                                'track', track_data['id'], track_data,
                                is_full_object=True))
                    else:
                        episode_count += 1
                
                if episode_count > 0 and not self._factory.silent:
                    warnings.warn(
                        f"Playlist '{self.name}' contains {episode_count} "
                        "episode(s) which were ignored.")
            return self._tracks
            
        def add_tracks(self, tracks):
            """
            Adds tracks to the playlist.
            A maximum of 100 items can be added in one request
            according to the Spotify API.
            This method does NOT paginate the request
            if more than 100 tracks are provided.
            It is up to the caller to ensure correct pagination,
            or just call add_tracks one by one for each track.

            User authorization is required for this operation
            and needs to be completed in a browser window
            that should open automatically if it is not already done.
            See SIAP_Factory.create_user_playlist() for more details.

            Args:
                tracks: A list of track objects or their IDs to add,
                        or a single track object or ID.
            Returns:
                Updated Playlist object with the new tracks added.
            Raises:
                ValueError: If user authorization is required
                    but not provided, or if the tracks are invalid.
                requests.exceptions.HTTPError: If the API request fails.
            """
            if not isinstance(tracks, list):
                tracks = [tracks]

            if len(tracks) > 100:
                raise ValueError(
                    f"The list of tracks contains {len(tracks)} items. "
                    "Cannot add more than 100 tracks at once.")

            headers = self._factory._get_headers(auth_type='user')
            headers['Content-Type'] = 'application/json'
            track_ids = []
            for track in tracks:
                if isinstance(track, self._factory.Track):
                    track_ids.append(track.id)
                elif (isinstance(track, str)
                      and len(track) == self._factory.SPOTIFY_ID_LEN):
                    track_ids.append(track)
                else:
                    raise ValueError(
                        "Invalid track type or ID. "
                        "Must be a Track object or a string ID.")
            data = {'uris': [f"spotify:track:{track_id}"
                             for track_id in track_ids]}
            
            endpoint = f"{self._factory.base_api_url}/playlists/{self.id}/tracks"
            response = requests.post(endpoint, headers=headers, json=data)
            
            if response.status_code == 201:
                del self._factory.playlists[self.id]
                playlist = self._factory.get_playlist(self.id)
                return playlist
            else:
                print(f"Failed to add tracks: {response.text}")
        
        def __len__(self):
            """
            Returns the number of tracks in the playlist.
            If tracks are not loaded yet, returns the total count
            from the initial data.
            """
            if self._tracks is not None:
                return len(self._tracks)
            return self._len_tracks

        def __repr__(self):
            return f"<Playlist: {self.name} (ID: {self.id}, "\
                f"Owner: {self.owner_name}, Owner ID: {self.owner_id}, "\
                f"Tracks: {len(self.tracks)})>"
        
        def __str__(self):
            return f"Playlist: {self.name} by {self.owner_name}"
