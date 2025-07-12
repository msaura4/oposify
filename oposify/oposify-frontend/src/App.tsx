import React, { useState, useEffect } from 'react';
import { getPKCE } from '/Users/msaur/Desktop/Code/oposify/oposify/oposify-frontend/src/pkce.ts';

/// <reference types="react-scripts" />

const SPOTIFY_CLIENT_ID = process.env.REACT_APP_SPOTIFY_CLIENT_ID as string;
const REDIRECT_URI = process.env.REACT_APP_REDIRECT_URI as string;
const BACKEND_URL = process.env.REACT_APP_BACKEND_URL as string;

function App() {
  const [accessToken, setAccessToken] = useState<string | null>(null);
  const [recommendations, setRecommendations] = useState<any[]>([]);
  const [playlistUrl, setPlaylistUrl] = useState<string | null>(null);

  // Handle Spotify PKCE login
  const handleLogin = async () => {
    const code_challenge = await getPKCE();
    const scopes = 'playlist-modify-private playlist-modify-public';
    const url = `https://accounts.spotify.com/authorize?client_id=${SPOTIFY_CLIENT_ID}&response_type=code&redirect_uri=${encodeURIComponent(REDIRECT_URI)}&scope=${encodeURIComponent(scopes)}&code_challenge_method=S256&code_challenge=${code_challenge}`;
    window.location.href = url;
  };

  // Handle redirect from Spotify and exchange code for access token
  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const code = params.get('code');
    if (code) {
      const code_verifier = localStorage.getItem('pkce_code_verifier');
      fetch(`${BACKEND_URL}/exchange_code`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ code, code_verifier, redirect_uri: REDIRECT_URI }),
      })
        .then(res => res.json())
        .then(data => {
          setAccessToken(data.access_token);
          localStorage.setItem('spotify_access_token', data.access_token);
          window.history.replaceState({}, document.title, '/');
        });
    } else {
      const token = localStorage.getItem('spotify_access_token');
      if (token) setAccessToken(token);
    }
  }, []);

  // Fetch recommendations from backend
  useEffect(() => {
    fetch(`${BACKEND_URL}/recommendations`)
      .then(res => res.json())
      .then(data => setRecommendations(data));
  }, []);

  // Create playlist in user's Spotify account
  const createPlaylist = async () => {
    if (!accessToken) return;
    const trackIds = recommendations.map(r => r.track_id);
    const res = await fetch(`${BACKEND_URL}/create_playlist`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        access_token: accessToken,
        track_ids: trackIds,
        playlist_name: 'Oposify Recommendations'
      }),
    });
    const data = await res.json();
    setPlaylistUrl(data.playlist_url);
  };

  return (
    <div style={{ maxWidth: 600, margin: '2rem auto', fontFamily: 'sans-serif' }}>
      <h1>Oposify</h1>
      {!accessToken ? (
        <button onClick={handleLogin} type="button">
          Login with Spotify
        </button>
      ) : (
        <>
          <h2>Recommendations</h2>
          <ul>
            {recommendations.map(song => (
              <li key={song.track_id}>
                {song.track_name} - {song.artist_name || song.artist}
              </li>
            ))}
          </ul>
          <button onClick={createPlaylist}>Create Spotify Playlist</button>
          {playlistUrl && (
            <div>
              <a href={playlistUrl} target="_blank" rel="noopener noreferrer">
                Open Playlist
              </a>
            </div>
          )}
        </>
      )}
    </div>
  );
}

export default App;