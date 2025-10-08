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

# constants
ACCESS_TOKEN = os.environ.get('ACCESS_TOKEN', '')
NAME_DEMO = __name__

def genius(search_term, per_page=15):
    """
    Collect data from the Genius API by searching for `search_term`.
    
    **Assumes ACCESS_TOKEN is loaded in environment.**

    Parameters
    ----------
    search_term : str
        The name of an artist, album, etc.
    per_page : int, optional
        Maximum number of results to return, by default 15

    Returns
    -------
    list
        All the hits which match the search criteria.
    """
    if not ACCESS_TOKEN:
        print("Warning: ACCESS_TOKEN environment variable not set. Returning empty result.")
        return []
    genius_search_url = f"http://api.genius.com/search?q={search_term}&" + \
                        f"access_token={ACCESS_TOKEN}&per_page={per_page}"
    response = requests.get(genius_search_url)
    
    if response.status_code != 200:
        print(f"Error: {response.status_code} for {search_term}")
        return []
    
    json_data = response.json()
    
    if not json_data or 'response' not in json_data or 'hits' not in json_data['response']:
        return []
    
    return json_data['response']['hits']


def genius_to_df(search_term, n_results_per_term=10, 
                 verbose=True, savepath=None):
    """
    Generate a pandas.DataFrame from a single call to the Genius API.

    Parameters
    ----------
    search_term : str
        Genius search term
    n_results_per_term : int, optional
        Number of results "per_page" for each search term provided, by default 10

    Returns
    -------
    pandas.DataFrame
        The final DataFrame containing the results. 
    """
    json_data = genius(search_term, per_page=n_results_per_term)
    if not json_data:
        if verbose:
            print(f'PID: {os.getpid()} ... search_term:', search_term)
            print(f"No data gathered for {search_term}.")
        return pd.DataFrame()
    hits = [hit['result'] for hit in json_data]
    if not hits:
        if verbose:
            print(f'PID: {os.getpid()} ... search_term:', search_term)
            print(f"No data gathered for {search_term}.")
        return pd.DataFrame()
    df = pd.DataFrame(hits)

    # expand dictionary elements
    if 'stats' in df.columns:
        df_stats = df['stats'].apply(pd.Series)
        df_stats.rename(columns={c:'stat_' + c for c in df_stats.columns}, inplace=True)
        df = pd.concat((df, df_stats), axis=1)
    if 'primary_artist' in df.columns:
        df_primary = df['primary_artist'].apply(pd.Series)
        df_primary.rename(columns={c:'primary_artist_' + c for c in df_primary.columns}, inplace=True)
        df = pd.concat((df, df_primary), axis=1)

    if verbose:
        print(f'PID: {os.getpid()} ... search_term:', search_term)
        print(f"Data gathered for {search_term}.")

    # this is a good practice for numerous automated data pulls ...
    if savepath:
        df.to_csv(savepath + '/genius-{searchname}.csv', index=False)

    return df

def genius_to_dfs(search_terms, **kwargs):
    """
    Generate a pandas.DataFrame from multiple calls to the Genius API.

    Parameters
    ----------
    search_terms : list of strings
        List of artists (say) to search in Genius.
    
    **kwargs : arguments passed to genius_api.genius_to_df

    Returns
    -------
    pandas.DataFrame
        The final DataFrame containing the results. 
    """

    dfs = []
    # loop through search_terms in question
    for search_term in tqdm(search_terms):
        df = genius_to_df(search_term, **kwargs)
        if not df.empty:
            dfs.append(df)
    if dfs:
        return pd.concat(dfs)
    else:
        return pd.DataFrame()
def get_artists(artist_names, n_results_per_term=10):
    """
    Return a DataFrame with artist information for one or more artists.
    """
    if not isinstance(artist_names, list):
        artist_names = [artist_names]
    
    df = genius_to_dfs(artist_names, n_results_per_term=n_results_per_term, verbose=False)
    
    # Return empty DataFrame if no data
    if df.empty:
        return pd.DataFrame(columns=["primary_artist_name", "primary_artist_id", "primary_artist_url"])
    
    # Select only relevant artist columns
    cols = [c for c in ["primary_artist_name", "primary_artist_id", "primary_artist_url"] if c in df.columns]
    return df[cols].drop_duplicates()    

def testing():
    print('Testing 1, 2, 3 ...')
    return None

def job_test(num, mult=2):
    print(f'PID: {os.getpid()} ... num:', num)
    sleep(uniform(0.5, 1.5))
    return num * mult


# print("__name__ is", __name__)
if __name__ == "__main__":

    # ------------------------------------
    #   SIMPLE EXAMPLE
    # ------------------------------------
    testing()

    # ------------------------------------
    #   DATA COLLECTION EXAMPLE
    # ------------------------------------

    # search_terms = ['The Beatles', 
    #                 'Missy Elliot', 
    #                 'Andy Shauf', 
    #                 'Slowdive', 
    #                 'Men I Trust']
    
    # n_results_per_term = 10

    # df_genius = genius_to_dfs(search_terms, 
    #                           n_results_per_term=n_results_per_term,
    #                           verbose=False)

    # df_genius.to_csv('./data/genius_data.csv')

    # ------------------------------------
    #   SIMPLE MULTIPROCESSING EXAMPLE
    # ------------------------------------

    # with Pool(4) as p:
    #     results = p.map(job_test, [1, 2, 3, 4])
    #     print("\nFinal results:\n", results)

    # ------------------------------------
    #   API MULTIPROCESSING EXAMPLE
    # ------------------------------------

    # search_terms = ['The Beatles', 
    #                 'Missy Elliot', 
    #                 'Andy Shauf', 
    #                 'Slowdive', 
    #                 'Men I Trust']
    
    # # (optional) if you need to pass multiple arguments
    # n = 20

    #  # then "unpack" `args` within the function (e.g., args[0])
    # args = [(t, n) for t in search_terms]

    # with Pool(8) as p:
    #     results = p.map(genius_to_df, search_terms)
    #     print("\n Total number of results: ", len(results))

    # df_genius = pd.concat(results)

    # df_genius.to_csv('./data/genius_data_mp.csv', index=False)

    



