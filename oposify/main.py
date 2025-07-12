from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import os
import numpy as np
from sklearn.metrics.pairwise import cosine_distances
import spotipy
import requests
from dotenv import load_dotenv
load_dotenv()

app = FastAPI()

# Allow CORS for local frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Paths to CSV files
HISTORY_CSV = os.path.join(os.path.dirname(__file__), 'spotify_history_with_features.csv')
KAGGLE_CSV = os.path.join(os.path.dirname(__file__), 'dataset.csv')

# Load datasets at startup
def load_datasets():
    history_df = pd.read_csv(HISTORY_CSV)
    kaggle_df = pd.read_csv(KAGGLE_CSV)

    numeric_features = [
        'popularity', 'acousticness', 'danceability', 'duration_ms', 'energy',
        'instrumentalness', 'liveness', 'loudness', 'speechiness', 'tempo', 'valence'
    ]
    for col in numeric_features:
        kaggle_df[col] = pd.to_numeric(kaggle_df[col], errors='coerce')

    # Remove duplicate columns in history_df except for the first occurrence
    history_df = history_df.loc[:, ~history_df.columns.duplicated()]

    # Merge features from Kaggle into history
    kaggle_features = kaggle_df[['track_id'] + numeric_features]
    history_df = pd.merge(
        history_df,
        kaggle_features,
        on='track_id',
        how='left',
        suffixes=('', '_kaggle')
    )

    # Overwrite original columns with Kaggle data if present
    for col in numeric_features:
        kaggle_col = col + '_kaggle'
        if kaggle_col in history_df.columns:
            col_series = history_df[col]
            kaggle_series = history_df[kaggle_col]
            if isinstance(col_series, pd.DataFrame):
                col_series = col_series.iloc[:, 0]
            if isinstance(kaggle_series, pd.DataFrame):
                kaggle_series = kaggle_series.iloc[:, 0]
            history_df[col] = col_series.combine_first(kaggle_series)
    # Drop all _kaggle columns
    history_df = history_df.loc[:, ~history_df.columns.duplicated()]
    history_df = history_df.drop(columns=[col for col in history_df.columns if col.endswith('_kaggle')])

    history_df.to_csv(HISTORY_CSV, index=False)

    return history_df, kaggle_df, numeric_features

history_df, kaggle_df, numeric_features = load_datasets()

@app.get("/songs")
def get_songs(limit: int = 100):
    """Return a list of songs from the Kaggle dataset."""
    df = kaggle_df.head(limit).replace([np.nan, np.inf, -np.inf], None)
    print(df.head())  # Debug: check if features are present
    return df.to_dict(orient="records")


@app.get("/history")
def get_history():
    """Return the user's listening history."""
    df = history_df.replace([np.nan, np.inf, -np.inf], None)
    return df.to_dict(orient="records")

@app.get("/recommendations")
def get_recommendations(limit: int = 20, percentile: float = 0.5):
    """Return songs most dissimilar to user's listening history based on audio features."""
    # Allow tracks with at least 5 features present (rows with >=5 non-NA values)
    hist_feat = history_df[numeric_features][history_df[numeric_features].notna().sum(axis=1) >= 5]
    if hist_feat.shape[0] == 0:
        return {"error": "No feature data in user history."}
    user_profile = np.array(hist_feat.mean()).reshape(1, -1)
    candidates = kaggle_df.dropna(subset=numeric_features).copy()
    if candidates.empty:
        return {"error": "No candidate songs with complete features."}
    X = candidates[numeric_features].values
    distances = cosine_distances(X, user_profile).flatten()
    candidates['dissimilarity'] = distances
    # Sort by dissimilarity descending
    sorted_candidates = candidates.sort_values(by='dissimilarity', ascending=False)
    # Take the top X% (by count)
    cutoff = int(len(sorted_candidates) * percentile)
    if cutoff < 1:
        cutoff = 1
    filtered = sorted_candidates.head(cutoff)
    # Randomly sample from the pool
    if len(filtered) > limit:
        top = filtered.sample(n=limit, random_state=None)
    else:
        top = filtered
    top = top.replace([np.nan, np.inf, -np.inf], None)
    return top.to_dict(orient="records")

@app.post("/create_playlist")
async def create_playlist(request: Request):
    """
    Create a Spotify playlist with the given track IDs for the authenticated user.
    Expects JSON: { "access_token": "...", "track_ids": [...], "playlist_name": "..." }
    """
    data = await request.json()
    access_token = data.get("access_token")
    track_ids = data.get("track_ids")
    playlist_name = data.get("playlist_name", "Oposify Recommendations")

    print(f"Create playlist request - token: {access_token[:20] if access_token else 'None'}..., track_count: {len(track_ids) if track_ids else 0}")

    if not access_token or not track_ids:
        raise HTTPException(status_code=400, detail="Missing access_token or track_ids")

    sp = spotipy.Spotify(auth=access_token)
    try:
        user = sp.current_user()
        print(f"Current user: {user.get('id') if user else 'None'}")
        if not user or "id" not in user:
            raise HTTPException(status_code=401, detail="Invalid or expired Spotify access token")
        user_id = user["id"]

        playlist = sp.user_playlist_create(user=user_id, name=playlist_name, public=False)
        if not playlist or "id" not in playlist:
            raise HTTPException(status_code=500, detail="Failed to create playlist")

        sp.playlist_add_items(playlist_id=playlist["id"], items=track_ids)
        playlist_url = playlist.get("external_urls", {}).get("spotify")
        if not playlist_url:
            raise HTTPException(status_code=500, detail="Failed to get playlist URL")

        print(f"Playlist created successfully: {playlist_url}")
        return {"playlist_url": playlist_url}
    except Exception as e:
        print(f"Error in create_playlist: {str(e)}")
        raise

@app.post("/exchange_code")
async def exchange_code(request: Request):
    data = await request.json()
    code = data["code"]
    code_verifier = data["code_verifier"]
    redirect_uri = data["redirect_uri"]

    print(f"Exchange code request - code: {code[:20]}..., verifier: {code_verifier[:20]}..., redirect_uri: {redirect_uri}")

    client_id = os.environ["SPOTIPY_CLIENT_ID"]
    token_url = "https://accounts.spotify.com/api/token"
    payload = {
        "client_id": client_id,
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": redirect_uri,
        "code_verifier": code_verifier,
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    response = requests.post(token_url, data=payload, headers=headers)
    
    print(f"Spotify token response status: {response.status_code}")
    print(f"Spotify token response: {response.text}")
    
    return response.json()