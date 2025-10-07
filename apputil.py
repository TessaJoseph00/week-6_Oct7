# your code here ...

# apputil.py
from genius_api import genius
import pandas as pd
import requests
import os

ACCESS_TOKEN = os.environ['ACCESS_TOKEN']

class Genius:
    def __init__(self, access_token=ACCESS_TOKEN):
        self.access_token = access_token

    def get_artist(self, search_term):
        """
        Retrieve full artist information from Genius for a given search term.

        This method searches for the artist name using the Genius API, extracts 
        the primary artist ID from the first search hit, and returns the detailed
        artist information as a JSON dictionary.

        Args:
            search_term (str): The name of the artist to search for.

        Returns:
            dict: A dictionary containing the artist's information as returned 
                by the Genius API. Returns None if no artist is found.
        """

        hits = genius(search_term)
        if not hits:
            return None

        # 2. Extract the primary artist ID from the first hit
        artist_id = hits[0]['result']['primary_artist']['id']

        # 3. Get artist info using /artists/{id}
        artist_url = f"http://api.genius.com/artists/{artist_id}?access_token={self.access_token}"
        response = requests.get(artist_url)
        response.raise_for_status()
        return response.json()

    def get_artists(self, search_terms):
        """
        Retrieve artist information for a list of search terms as a DataFrame.

        This method iterates over each search term, calls `get_artist` to fetch
        detailed information for the most likely (primary) artist, and constructs
        a pandas DataFrame containing the following columns:
            - search_term: the original search term
            - artist_name: the artist's name from Genius
            - artist_id: the Genius Artist ID
            - followers_count: the number of followers (if available)

        Args:
            search_terms (list of str): List of artist names to search for.

        Returns:
            pandas.DataFrame: A DataFrame where each row corresponds to a search
            term and contains the artist information. If no artist is found for
            a search term, the row will contain None values.

        """
        rows = []
        for term in search_terms:
            artist_data = self.get_artist(term)
            if artist_data is None:
                rows.append({
                    "search_term": term,
                    "artist_name": None,
                    "artist_id": None,
                    "followers_count": None
                })
            else:
                artist_info = artist_data["response"]["artist"]
                rows.append({
                    "search_term": term,
                    "artist_name": artist_info.get("name"),
                    "artist_id": artist_info.get("id"),
                    "followers_count": artist_info.get("followers_count")
                })
        return pd.DataFrame(rows)


if __name__ == "__main__":
    genius_obj = Genius()
    print(genius_obj.access_token)
    print(genius_obj.get_artist("Radiohead")["response"]["artist"]["name"])
    print(genius_obj.get_artists(['Rihanna', 'Tycho', 'Seal', 'U2']))

