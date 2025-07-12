"""
spotify_fetch.py

This script fetches your recent Spotify listening history and audio features, saving them as a CSV file.

Instructions:
1. Install dependencies:
   pip install spotipy pandas
2. Set your Spotify API credentials as environment variables:
   export SPOTIPY_CLIENT_ID='your_client_id'
   export SPOTIPY_CLIENT_SECRET='your_client_secret'
   export SPOTIPY_REDIRECT_URI='http://127.0.0.1:8888/callback'
3. Run the script:
   python spotify_fetch.py

The script will open a browser window for you to log in to Spotify and authorize access.
"""

import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import pandas as pd

from dotenv import load_dotenv
load_dotenv()

# Set the scope to read recently played tracks and audio features
SCOPE = 'user-read-recently-played'

# Number of tracks to fetch (max 50 per request, can loop for more)
NUM_TRACKS = 500

# Authenticate with Spotify
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=SCOPE))

KAGGLE_CSV = os.path.join(os.path.dirname(__file__), 'dataset.csv')

def fetch_recent_tracks(sp, num_tracks=100):
    tracks = []
    after = None
    fetched = 0
    while fetched < num_tracks:
        limit = min(50, num_tracks - fetched)
        results = sp.current_user_recently_played(limit=limit, after=after)
        items = results.get('items', [])
        if not items:
            break
        for item in items:
            track = item['track']
            tracks.append({
                'track_id': track['id'],
                'track_name': track['name'],
                'artist': track['artists'][0]['name'],
                'played_at': item['played_at']
            })
        fetched += len(items)
        if len(items) < limit:
            break
        after = pd.to_datetime(items[-1]['played_at']).value // 10**6  # ms timestamp
    return tracks

def fetch_audio_features(sp, track_ids):
    # Deduplicate and filter out None/invalid IDs
    unique_ids = list({tid for tid in track_ids if tid})
    features = {}
    for i in range(0, len(unique_ids), 50):
        batch = unique_ids[i:i+50]
        try:
            audio_features = sp.audio_features(batch)
            for f in audio_features:
                if f:
                    features[f['id']] = f
        except Exception as e:
            print(f"Error fetching audio features for batch: {batch}\nError: {e}")
    return features

def main():
    print("Fetching recent tracks...")
    tracks = fetch_recent_tracks(sp, NUM_TRACKS)
    print(f"Fetched {len(tracks)} tracks.")
    # Deduplicate and filter track IDs
    track_ids = [t['track_id'] for t in tracks if t['track_id']]
    print(f"Fetching audio features for {len(set(track_ids))} unique tracks...")
    features = fetch_audio_features(sp, track_ids)
    # Merge features into tracks
    for t in tracks:
        f = features.get(t['track_id'], {})
        t.update({
            'danceability': f.get('danceability'),
            'energy': f.get('energy'),
            'key': f.get('key'),
            'loudness': f.get('loudness'),
            'mode': f.get('mode'),
            'speechiness': f.get('speechiness'),
            'acousticness': f.get('acousticness'),
            'instrumentalness': f.get('instrumentalness'),
            'liveness': f.get('liveness'),
            'valence': f.get('valence'),
            'tempo': f.get('tempo'),
            'duration_ms': f.get('duration_ms'),
        })
    df = pd.DataFrame(tracks)
    df.to_csv('oposify/spotify_history_with_features.csv', index=False)
    print("Saved to spotify_history_with_features.csv")

if __name__ == "__main__":
    main() 