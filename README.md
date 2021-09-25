# Spotify-To-MP3-Converter
 Searches songs from Spotify on YouTube and downloads them using pytube

## Planned Features
  - Arguments to use only inside terminal
  - Better automatic serching on YouTube

## Requirements
  - Spotify API Key
  - Python 3
  - ffmpeg

### Python Libraries
  - spotipy
  - ytmusicapi
  - pytube
  - eyed3
  
## Usage
  1. Clone the Repository.
  2. Change into the cloned directory: `cd Spotify-To-MP3-Converter`
  3. Install the required python packages using pip: `pip install -r requirements` or `pip3 install -r requirements`
  4. Install `ffmpeg`:
    - On Linux you can install ffmpeg using your preferred package manager (see https://www.ffmpeg.org/download.html#build-linux)
    - On Windows, you can download builds from https://www.ffmpeg.org/download.html#build-windows
    - On Mac, you can download builds from https://www.ffmpeg.org/download.html#build-mac
  5. Create a new file `secrets.py` to store your Spotify API Keys
     ```
     # secrets.py
     
     client_id = 'YOUR_CLIENT_ID'
     client_secret = 'YOUR_CLIENT_SECRET'
     
  6. Change the Spotify Playlist Link 
     ```
     # spotip3.py
     
     [...]
     def main():
        playlist_link = 'YOUR_PLAYLIST_LINK'
     [...]
  7. Execute the script using python 3: `python3 spotip3.py `

       
## Bugs and Contributions
  If you find any bugs or issues with the script, please report them here on the "Issues" tab.