import os
import json
import requests
import sys
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

    # Return a list of dictionaries
    def get_user_favorite_songs(self, username):
        method = "user.getlovedtracks&user={}&limit={}&api_key={}&format=json".format(
            username,
            100,
            self.lastfm_key
        )

        query = self.root.format(method)
        response = requests.get(query)

        # Collect each artist and song name from the query
        content = json.loads(response.content)
        favorite_songs = []
        for track in content['lovedtracks']['track']:
            favorite_songs.append({
                'artist': track['artist']['name'],
                'song': track['name']
            })
        
        return favorite_songs
    


if __name__ == '__main__':
    cp = CreatePlaylist()
    print(cp.get_user_friends("DiNNo0"))

