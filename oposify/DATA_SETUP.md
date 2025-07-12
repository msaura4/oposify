# Data Setup Guide

This project requires two CSV files that are not included in the repository due to their large size:

## Required Files

1. **`spotify_history_with_features.csv`** (16GB) - Your Spotify listening history with audio features
2. **`dataset.csv`** (19MB) - Kaggle Spotify dataset with track features

## How to Obtain the Files

### 1. Spotify History with Features
This file contains your personal Spotify listening history with audio features. You can generate it using the `spotify_fetch.py` script:

```bash
cd oposify
python spotify_fetch.py
```

**Prerequisites:**
- Spotify Developer account
- Client ID and Client Secret from Spotify Developer Dashboard
- Environment variables set up (see `.env.example`)

### 2. Kaggle Dataset
Download the Spotify dataset from Kaggle:

1. Go to [Spotify Dataset 1921-2020](https://www.kaggle.com/datasets/yamaerenay/spotify-dataset-19212020-600k-tracks)
2. Download the dataset
3. Extract and rename the main CSV file to `dataset.csv`
4. Place it in the `oposify/` directory

## File Structure
After setup, your directory should look like:
```
oposify/
├── main.py
├── spotify_fetch.py
├── spotify_history_with_features.csv  # Your personal data
├── dataset.csv                        # Kaggle dataset
└── oposify-frontend/
    └── ...
```

## Environment Variables
Create a `.env` file in the root directory with:
```
SPOTIPY_CLIENT_ID=your_spotify_client_id
SPOTIPY_CLIENT_SECRET=your_spotify_client_secret
```

## Notes
- These files are excluded from version control due to their large size
- The `spotify_history_with_features.csv` contains personal data and should not be shared
- The `dataset.csv` is publicly available from Kaggle 