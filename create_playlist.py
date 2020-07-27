import os
import json
import requests
import sys
import random as rd

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

    # Return a list of dictionaries with keys 'artist','song'
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
                    })
            else:
                print("\n The {} seems not have any favorite songs, therefore, we're going to take his most heard songs.\n".format(username))
                # Use a function to get the most played songs
                pass
        
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
                

    


if __name__ == '__main__':
    cp = CreatePlaylist()
    print(cp.generate_playlist_from_friends("BrasilianGuy", random=False))
    #print(cp.generate_playlist_from_friends("DiNNo0"))
    #print(cp.get_user_favorite_songs("BrasilianGuy"))
    
