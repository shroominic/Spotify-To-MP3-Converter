from spotipy.oauth2 import SpotifyClientCredentials
from eyed3.id3.frames import ImageFrame
from ytmusicapi import YTMusic
import urllib.request
import subprocess
import secrets
import difflib
import spotipy
import pytube
import eyed3
import html
import os
import re

path = os.path.dirname(os.path.realpath(__file__)) + os.sep

youtube_api = YTMusic()

client_credentials_manager = SpotifyClientCredentials(client_id=secrets.client_id, client_secret=secrets.client_secret)
spotify_api = spotipy.Spotify(client_credentials_manager=client_credentials_manager)


def clear():
    os.system('cls' if os.name == 'nt' else 'clear')


def build_results(tracks, album=None):
    results = []
    for track in tracks:
        if 'track' in track:
            track = track['track']
        if not track:
            continue
        album_name = album if album else track['album']['name']
        results.append({
            'artist': ' '.join([artist['name'] for artist in track['artists']]),
            'name': track['name'],
            'album': album_name,
            'duration': track['duration_ms'] / 1000,
            'cover_url': track['album']['images'][0]['url'],
        })

    return results


def get_id_from_url(url):
    url_parts = url.split('/')
    return url_parts[4].split('?')[0]


def get_spotify_playlist(url):
    playlist_id = get_id_from_url(url)
    if len(playlist_id) != 22:
        raise Exception('Bad playlist id: ' + playlist_id)

    results = spotify_api.playlist(playlist_id)
    name = results['name']
    total = int(results['tracks']['total'])
    tracks = build_results(results['tracks']['items'])
    count = len(tracks)
    print(f"Spotify tracks: {count}/{total}")

    while count < total:
        more_tracks = spotify_apiapi.playlist_items(playlist_id, offset=count, limit=100)
        tracks += build_results(more_tracks['items'])
        count = count + 100
        print(f"Spotify tracks: {count}/{total}")

    return {'tracks': tracks, 'name': name, 'description': html.unescape(results['description'])}


def get_best_fit_song_id(results, song):
    match_score = {}
    title_score = {}
    for res in results:
        if res['resultType'] not in ['song', 'video']:
            continue

        duration_match = None
        if 'duration' in res and res['duration']:
            duration_items = res['duration'].split(':')
            duration = int(duration_items[0]) * 60 + int(duration_items[1])
            duration_match = 1 - abs(duration - song['duration'])  # * 2 / song['duration']

        title = res['title']
        # for videos,
        if res['resultType'] == 'video':
            title_split = title.split('-')
            if len(title_split) == 2:
                title = title_split[1]

        artists = ' '.join([a['name'] for a in res['artists']])

        title_score[res['videoId']] = difflib.SequenceMatcher(a=title.lower(), b=song['name'].lower()).ratio()
        song['artist'] = song['artist'].replace("\'", "")
        scores = [title_score[res['videoId']],
                  difflib.SequenceMatcher(a=artists.lower(), b=song['artist'].lower()).ratio()]
        if duration_match:
            scores.append(duration_match)

        # add album for songs only
        if res['resultType'] == 'song' and res['album'] is not None:
            scores.append(difflib.SequenceMatcher(a=res['album']['name'].lower(), b=song['album'].lower()).ratio())
        match_score[res['videoId']] = sum(scores) / len(scores)

    if len(match_score) == 0:
        return None

    max_score = max(match_score, key=match_score.get)

    if title_score[max_score] < 0.5:
        print(f'\nSpotify: \n - Song: {song["name"]}\n - Artist: {song["artist"]}\n - Album: {song["album"]}'
              f'\n - Duration: {song["duration"]}')
        print('YouTube results:')
        for i, res in enumerate(results):
            if res['resultType'] not in ['song', 'video']:
                continue
            print(f'[{i}] {res["title"]}')
        choice = input('\nChoos song manually: ')
        try:
            return results[int(choice)]['videoId']
        except ValueError:
            pass

    return max_score


def search_song(song):
    found_song = []
    not_found = False
    name = re.sub(r' \(feat.*\..+\)', '', song['name'])
    query = song['artist'] + ' ' + name
    query = query.replace(" &", "")
    results = youtube_api.search(query, ignore_spelling=True)

    if len(results) == 0:
        not_found = True
    else:
        target_song = get_best_fit_song_id(results, song)
        if not target_song:
            not_found = True
        else:
            song['video_id'] = target_song
            found_song = song
    if not_found:
        with open(path + 'not_found.txt', 'w', encoding="utf-8") as file:
            file.write("\n".join(song))
            file.write("\n")
            file.close()
    return found_song


def download_yt_mp3(song, output_path):
    print(f'\nDownloading: \n - Song: {song["name"]}\n - Artist: {song["artist"]}\n - Album: {song["album"]}'
          f'\n - Duration: {song["duration"]}')
    url = 'https://www.youtube.com/watch?v=' + song['video_id']
    video = pytube.YouTube(url).streams.get_by_itag(251)
    webm_filename = video.default_filename
    mp3_filename = webm_filename[:-4] + 'mp3'
    # download from YT
    video.download(output_path)

    # convert .webm to .mp3
    subprocess.run([
        'ffmpeg',
        '-i', os.path.join(output_path, webm_filename),
        os.path.join(output_path, mp3_filename)
    ], stderr=subprocess.DEVNULL)

    # delete .webm file
    os.remove(os.path.join(output_path, webm_filename))

    urllib.request.urlretrieve(song['cover_url'], 'cover.jpg')

    audiofile = eyed3.load(os.path.join(output_path, mp3_filename))
    audiofile.tag.artist = song['artist']
    audiofile.tag.album = song['album']
    audiofile.tag.title = song['name']
    audiofile.tag.images.set(ImageFrame.FRONT_COVER, open('cover.jpg', 'rb').read(), 'image/jpeg')
    audiofile.tag.save()

    os.remove('cover.jpg')

    print(mp3_filename + ' downloaded successfully!\n')


def main():
    playlist_link = "https://open.spotify.com/playlist/5gQqufCoYgEKopKlWMTxux"
    playlist = get_spotify_playlist(playlist_link)

    output = "downloads"

    for song in playlist['tracks']:
        clear()
        found_song = search_song(song)

        download_yt_mp3(found_song, output)


if __name__ == "__main__":
    main()
