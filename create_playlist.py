import os
import json
import requests
import sys
import random as rd
import pprint

from bs4 import BeautifulSoup

from exceptions import ResponseException
sys.path.insert(1, '../Secrets')
from secrets import lastfm_key

class CreatePlaylist:
    def __init__(self):
        self.lastfm_key = lastfm_key
        self.root = "http://ws.audioscrobbler.com/2.0/?method={}"
        self.best_friends = []
    
    # Returns a list of usernames
    def get_user_friends(self, username):
        method = "user.getfriends&user={}&limit={}&api_key={}&format=json".format(
            username,
            60,
            self.lastfm_key
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
            self.lastfm_key,
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
                        'song': track['name']
                        'playcount': track['playcount']
                    })
        else:
            print("\n It seems that {} hasn't scrobbled yet.\n".format(username))
        return

    # Return a list of dictionaries with keys 'artist','song', 'playcount'
    def get_user_favorite_songs(self, username, limit=100):
        method = "user.getlovedtracks&user={}&limit={}&api_key={}&format=json".format(
            username,
            limit,
            self.lastfm_key
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
                        'playcount': track['playcount']
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

    # Verify if an artist exists
    def search_artist(self, artist):
        method = "artist.search&artist={}&api_key={}&format=json".format(
            artist,
            self.lastfm_key
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
            self.lastfm_key
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
            self.lastfm_key,
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


if __name__ == '__main__':
    cp = CreatePlaylist()
    cp.get_most_listened("mathcola")
