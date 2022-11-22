# import requests
import streamlit as st
import streamlit.components.v1 as components
# import lyricsgenius
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from bs4 import BeautifulSoup
import time
import json
import os
import sys
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager

opt = Options()
opt.add_argument("--headless")
driver_service = Service(GeckoDriverManager().install())
driver = webdriver.Firefox(
    options=opt,
    service=driver_service,
)
scope = 'playlist-modify-public'
username = st.secrets['username']

spotify_user_id = st.secrets['spotify_user_id']
spotify_token = st.secrets['spotify_token']
# genius_token = st.secrets['genius_token']
#
# genius = lyricsgenius.Genius(genius_token)

st.title("Wax Lyrical Playlist Generator")
name = st.text_input("Enter a name or Nickname:")
searched_lyric = st.text_input("Please enter a word or sentence you'd like to search:")

if searched_lyric:
    with st.spinner("Cooking up your playlist 🧑‍🍳"):
        playlist_name = f'"{name}" Waxing Lyrical | Songs containing "{searched_lyric}"'
        playlist_description = f"Songs containing the lyrics '{searched_lyric}'"

        spotifyObject = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=spotify_user_id,
                                                                  client_secret=spotify_token,
                                                                  redirect_uri="http://127.0.0.1:8080",
                                                                  scope=scope))
        # create the playlist
        spotifyObject.user_playlist_create(user=username, name=playlist_name, public=True,
                                           description=playlist_description)

        # lyric_search_results = genius.search_lyrics(searched_lyric)

        list_of_songs = []
        url = f"https://genius.com/api/search/lyrics?q={searched_lyric}"

        driver.get(url)
        print("THIS IS DRIVER PAGE SOURCE: ", driver.page_source)
        soup = BeautifulSoup(driver.page_source, 'html')
        driver.quit()
        print("THIS IS SOUP GET TEXT: ", soup.get_text())
        json_response = json.loads(soup.get_text())
        # print(json_response)

        for lyric in json_response["response"]["sections"][0]['hits']:
            artist_name = lyric['result']['artist_names']
            song_title = lyric['result']['title']
            lyric_ranges = lyric['highlights'][0]['ranges']
            lyric_samples = lyric['highlights'][0]['value']

            result = spotifyObject.search(q=f"{song_title} {artist_name}")
            try:
                song_uri = result['tracks']['items'][0]['uri']
                list_of_songs.append(song_uri)
            except:
                pass


        # find the new playlist
        prePlaylist = spotifyObject.user_playlists(user=username)
        playlist = prePlaylist['items'][0]['id']

        # add songs
        spotifyObject.user_playlist_add_tracks(user=username, playlist_id=playlist, tracks=list_of_songs)
        placeholder = st.empty()
    placeholder.success("Bon Appétit!", icon="🎺")
    time.sleep(1)
    placeholder.empty()
    components.iframe(f"https://open.spotify.com/embed/playlist/{playlist}", width=700, height=600)
