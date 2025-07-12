# Oposify

## Backend
- FastAPI backend for music recommendations and playlist creation.
- Endpoints:
  - `/recommendations` — Get dissimilar song recommendations
  - `/create_playlist` — Create a Spotify playlist from recommendations

## Frontend (to be created)
- React app for:
  - Logging in with Spotify
  - Viewing recommendations
  - Creating a playlist from recommendations

### Setup (after files are created)
1. `cd oposify-frontend`
2. `npm install`
3. Create a `.env` file with your Spotify client ID and redirect URI:
   ```
   REACT_APP_SPOTIFY_CLIENT_ID=your_spotify_client_id
   REACT_APP_REDIRECT_URI=http://localhost:3000/callback
   REACT_APP_BACKEND_URL=http://localhost:8000
   ```
4. `npm start`

---

The frontend will handle Spotify OAuth, display recommendations, and allow playlist creation. 