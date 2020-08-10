import os
import json
import requests
import sys
import random as rd
import pprint

from bs4 import BeautifulSoup

from exceptions import ResponseException
sys.path.insert(1, '../Secrets')
from secrets import lastfm_key, spotify_token, spotify_user_id

class CreatePlaylist:
    def __init__(self):
        self.root = "http://ws.audioscrobbler.com/2.0/?method={}"
        self.best_friends = []
    
    """ USER ORIENTED FUNCTIONS """

    # Returns a list of usernames
    def get_user_friends(self, username):
        method = "user.getfriends&user={}&limit={}&api_key={}&format=json".format(
            username,
            60,
            lastfm_key
        )
        query = self.root.format(method)
        response = requests.get(query)

        # Collect each username from the query
        content = json.loads(response.content)
        friends = []
        for user in content['friends']['user']:
            friends.append(user['name'])

        return friends

    # Return a list of dictionaries with keys 'artist','song', 'playcount'
    def get_most_listened(self, username, limit=200):
        method = "user.gettoptracks&user={}&api_key={}&limit={}&format=json".format(
            username,
            lastfm_key,
            limit
        )

        query = self.root.format(method)
        response = requests.get(query)
        content = json.loads(response.content)

        most_listened_tracks = []
        if content['toptracks']['track']:
            for track in content['toptracks']['track']:
                most_listened_tracks.append({
                        'artist': track['artist']['name'],
                        'song': track['name'],
                        'playcount': track['playcount']
                    })
        else:
            print("\n It seems that {} hasn't scrobbled yet.\n".format(username))
        return most_listened_tracks

    # Return a list of dictionaries with keys 'artist','song', 'playcount'
    def get_user_favorite_songs(self, username, limit=100):
        method = "user.getlovedtracks&user={}&limit={}&api_key={}&format=json".format(
            username,
            limit,
            lastfm_key
        )
        # Question: Do I always need to get all the loved songs?

        query = self.root.format(method)
        response = requests.get(query)

        # Collect each artist and song name from the query
        content = json.loads(response.content)
        favorite_songs = []
        if content.get('lovedtracks', None):
            if content['lovedtracks'].get('track', None):
                for track in content['lovedtracks']['track']:
                    favorite_songs.append({
                        'artist': track['artist']['name'],
                        'song': track['name']
                    })
            else:
                print("\n The {} seems not have any favorite songs, therefore, we're going to take his most heard songs.\n".format(username))
                # Use a function to get the most played songs
                favorite_songs = self.get_most_listened(username, limit=limit)
        
        return favorite_songs

    # Return a playlist of X-amount songs from each friend
    def generate_playlist_from_friends(self, username, friends=None, amount=5, random=True):
        # Get friends
        if not friends:
            friends = self.get_user_friends(username)

        songs = []

        # Get favorite songs from each friend
        for friend in friends:
            song = self.get_user_favorite_songs(friend)
            if len(song) > amount:
                if random:
                    song = rd.sample(song, k = amount)
                else:
                    song = song[0:amount]
            songs += song

        return songs

    """ ARTISTS ORIENTED FUNCTIONS """

    # Verify if an artist exists
    def search_artist(self, artist):
        method = "artist.search&artist={}&api_key={}&format=json".format(
            artist,
            lastfm_key
        )

        query = self.root.format(method)
        response = requests.get(query)
        content = json.loads(response.content)
        if content['results']['opensearch:totalResults'] == '0':
            print("Artist not found!")
            return False
        else:
            #return content['results']['artistmatches']['artist'][0]['name']
            return True

    # Return a list with a tuple (Album's title, 'Play count')
    def get_top_albums(self, artist, amount=10):
        method = "artist.gettopalbums&artist={}&api_key={}&format=json".format(
            artist,
            lastfm_key
        )

        query = self.root.format(method)
        response = requests.get(query)
        content = json.loads(response.content)

        albums = []

        if content['topalbums']['album']:
            for album in content['topalbums']['album']:
                albums.append((album.get('name'),album.get('playcount'),album.get('url')))

        albums = sorted(albums, key = lambda tup: tup[1], reverse = True)
        return albums[0:amount]

    # Return the album's URL
    def get_album_url(self, artist, album):
        method = "album.getinfo&api_key={}&artist={}&album={}&format=json".format(
            lastfm_key,
            artist,
            album
        )

        query = self.root.format(method)
        response = requests.get(query)
        content = json.loads(response.content)
        if content.get('album'):
            print(content['album']['url'])
            return content['album']['url']
        else:
            print('Album "{}" not found!'.format(album))
            return None

    # Return a list with X amount of album's track
    def get_album_toptracks(self, artist, album, amount=5, remove_mainstream=0):
        # Get the album's URL
        URL = self.get_album_url(artist, album)
        page = requests.get(URL)
        soup = BeautifulSoup(page.content, 'html.parser')
        
        data = []
        table = soup.find('table', attrs={'class':'chartlist'})
        table_body = table.find('tbody')

        rows = table_body.find_all('tr')
        for row in rows:
            name = row.find('td', class_='chartlist-name')
            count = row.find('span', class_='chartlist-count-bar-value')
            if None in (name, count):
                continue
            name = name.text.strip()
            count = count.text.strip().replace(' listeners','').replace(',','')
            data.append((name, int(count)))

        data = sorted(data, key = lambda tup: tup[1], reverse = True)
        
        # We can could the artist's top tracks list 
        if remove_mainstream:
            while (remove_mainstream > len(data)):
                remove_mainstream -= 1
                return data[remove_mainstream:amount]
        else:
            return data[0:amount]


    """ SPOTIFY FUNCTIONS """
    
    # Search for the song
    def get_spotify_url(self, song_name, artist):
        query = "https://api.spotify.com/v1/search?query=track%3A{}+artist%3A{}&type=track&offset=0&limit=3".format(
            song_name,
            artist
        )
        response = requests.get(
            query,
            headers = {
                "Content-Type": "application/json",
                "Authorization": "Bearer {}".format(spotify_token)

            }
        )
        content = json.loads(response.content)
        
        if content.get('tracks', None):
            if content['tracks'].get('items', None):
                songs = content["tracks"]["items"]
            else:
                return None
        else:
            return None

        if len(songs) > 0:
            uri = songs[0]["uri"]
        else:
            uri = None
        return uri

    # Create a new playlist
    def create_playlist(self, name, description):
        requests_body = json.dumps({
            "name": name,
            "description": description,
            "public": False
        })

        query = "https://api.spotify.com/v1/users/{}/playlists".format(
            spotify_user_id
        )
        response = requests.post(
            query,
            data=requests_body,
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer {}".format(spotify_token)
            }
        )

        content = json.loads(response.content)
        print(content)
        #Playlist ID
        return content["id"]

    # Add all liked songs into a new Spotify playlist
    def add_song_to_playlist(self):
        songs = self.get_most_listened("edupeixoto", limit=30)
        uris = []
        for song in songs:
            url = self.get_spotify_url(song.get('song'), song.get('artist'))
            if url:
                print(song.get('song'), url)
                uris.append(url)
        
        playlist_id = self.create_playlist("Peixo Most Listened", "")

        request_data = json.dumps(uris)

        query = "https://api.spotify.com/v1/playlists/{}/tracks".format(
            playlist_id
        )        

        response = requests.post(
            query,
            data=request_data,
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer {}".format(spotify_token)
            }
        )

        if response.status_code != 200:
            raise ResponseException(response.status_code)

        response_json = response.json()
        return response_json





if __name__ == '__main__':
    cp = CreatePlaylist()
    #print(cp.get_most_listened("mathcola"))
    #print(cp.get_spotify_url("Terrible Lie", "Nine Inch Nails"))
    #print(cp.create_playlist("Teste", "Teste"))
    print(cp.add_song_to_playlist())