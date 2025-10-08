# built-in
import requests
import os
from multiprocessing import Pool
from time import sleep

# user-installed
import pandas as pd
from tqdm import tqdm
from numpy.random import uniform
from dotenv import load_dotenv

load_dotenv()

# -------------------------
# constants
# -------------------------
ACCESS_TOKEN = os.environ.get('ACCESS_TOKEN', '') 
NAME_DEMO = __name__

# -------------------------
# genius function
# -------------------------
def genius(search_term, per_page=15):
    if not ACCESS_TOKEN:
        print("Warning: ACCESS_TOKEN not set. Returning empty result.")
        return []

    genius_search_url = f"http://api.genius.com/search?q={search_term}&access_token={ACCESS_TOKEN}&per_page={per_page}"
    try:  
        response = requests.get(genius_search_url)
        response.raise_for_status()
        json_data = response.json()
    except Exception as e:
        print(f"Error fetching data for {search_term}: {e}")
        return []

    if not json_data or 'response' not in json_data or 'hits' not in json_data['response']:
        return []

    return json_data['response']['hits']

def genius_to_df(search_term, n_results_per_term=10, verbose=True, savepath=None):
    json_data = genius(search_term, per_page=n_results_per_term)
    if not json_data:
        if verbose:
            print(f"No data gathered for {search_term}.")
        return pd.DataFrame()

    hits = [hit['result'] for hit in json_data]
    if not hits:
        if verbose:
            print(f"No hits for {search_term}.")
        return pd.DataFrame()

    df = pd.DataFrame(hits)

    # Expand nested dicts
    if 'stats' in df.columns:
        df_stats = df['stats'].apply(pd.Series)
        df_stats.rename(columns={c: 'stat_' + c for c in df_stats.columns}, inplace=True)
        df = pd.concat([df, df_stats], axis=1)

    if 'primary_artist' in df.columns:
        df_primary = df['primary_artist'].apply(pd.Series)
        df_primary.rename(columns={c: 'primary_artist_' + c for c in df_primary.columns}, inplace=True)
        df = pd.concat([df, df_primary], axis=1)

    if savepath:
        df.to_csv(savepath + f'/genius-{search_term}.csv', index=False)

    return df

def genius_to_dfs(search_terms, **kwargs):
    dfs = []
    for term in tqdm(search_terms):
        df = genius_to_df(term, **kwargs)
        if not df.empty:
            dfs.append(df)
    if dfs:
        return pd.concat(dfs)
    else:
        return pd.DataFrame()


def get_artists(artist_names, n_results_per_term=10):
    if not isinstance(artist_names, list):
        artist_names = [artist_names]

    df = genius_to_dfs(artist_names, n_results_per_term=n_results_per_term, verbose=False)

    if df.empty:
        return pd.DataFrame(columns=["primary_artist_name", "primary_artist_id", "primary_artist_url"])

    cols = [c for c in ["primary_artist_name", "primary_artist_id", "primary_artist_url"] if c in df.columns]
    return df[cols].drop_duplicates()

def testing():
    print("Testing 1, 2, 3 ...")

def job_test(num, mult=2):
    sleep(uniform(0.5, 1.5))
    return num * mult
