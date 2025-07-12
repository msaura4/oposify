# Oposify

Oposify is a personalized Spotify playlist generator and music exploration tool. It analyzes your Spotify listening history, compares it with a large public dataset, and recommends tracks that are most different from your usual listening habits. You can then create a new Spotify playlist with these recommendations directly from the app.

## Features
- **Spotify OAuth Integration:** Securely connect your Spotify account.
- **Personalized Recommendations:** Find songs that are most dissimilar to your listening history using audio features and cosine distance.
- **Playlist Creation:** Instantly create a new Spotify playlist with recommended tracks.
- **Frontend & Backend:** Modern React frontend and FastAPI backend.

## How It Works
1. **Data Collection:**
   - Your Spotify listening history is fetched and enriched with audio features using the Spotify API.
   - A large public dataset from Kaggle provides additional track features for comparison.
2. **Feature Engineering:**
   - Numeric audio features (e.g., danceability, energy, valence) are extracted and merged.
3. **Recommendation Algorithm:**
   - The backend computes the average feature vector of your listening history.
   - It finds tracks in the Kaggle dataset that are most dissimilar (using cosine distance) to your profile.
   - A random sample of these "opposite" tracks is recommended.
4. **Playlist Creation:**
   - You can create a new Spotify playlist with the recommended tracks using your authenticated account.

## Project Structure
```
oposify/
├── main.py                # FastAPI backend
├── spotify_fetch.py       # Script to fetch your Spotify history
├── spotify_history_with_features.csv  # (User-provided, see DATA_SETUP.md)
├── dataset.csv            # (Kaggle dataset, see DATA_SETUP.md)
├── oposify-frontend/      # React frontend
│   ├── src/
│   └── ...
├── DATA_SETUP.md          # How to get the required data files
└── README.md              # This file
```

## Setup & Usage
1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/oposify.git
   cd oposify
   ```
2. **Install Python dependencies:**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
3. **Set up environment variables:**
   - Copy `.env.example` to `.env` and fill in your Spotify API credentials.
4. **Prepare data files:**
   - Follow `DATA_SETUP.md` to obtain `spotify_history_with_features.csv` and `dataset.csv`.
5. **Run the backend:**
   ```bash
   uvicorn oposify.main:app --reload
   ```
6. **Run the frontend:**
   ```bash
   cd oposify/oposify-frontend
   npm install
   npm start
   ```
7. **Open your browser:**
   - Go to `http://localhost:3000` to use the app.

## Implementation Details
- **Backend:**
  - Built with FastAPI (Python)
  - Handles data loading, merging, recommendation logic, and Spotify playlist creation
  - Endpoints: `/songs`, `/history`, `/recommendations`, `/create_playlist`, `/exchange_code`
- **Frontend:**
  - Built with React (TypeScript)
  - Handles authentication (PKCE flow), displays recommendations, and interacts with backend
- **Data:**
  - User's Spotify history (private, not in repo)
  - Kaggle Spotify dataset (public, not in repo)

## License
MIT License

## Acknowledgments
- [Spotify Web API](https://developer.spotify.com/documentation/web-api/)
- [Kaggle Spotify Dataset 1921-2020](https://www.kaggle.com/datasets/yamaerenay/spotify-dataset-19212020-600k-tracks) 