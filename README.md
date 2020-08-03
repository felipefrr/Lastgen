# Lastlist

Lastlist is a simple script that generates a Spotify playlist based on your Last.fm profile. 

## Table of Contents
* [Features](#Features)
* [Tasks](#Tasks)
* [Troubleshooting](#Troubleshooting)

## Features
* Create a playlist based on your favorite songs;
* Create a playlist based other user favorite songs;
* Create a playlist based on your friends' favorite songs;
* Create a playlist based on the artist's ranking.

## Tasks
1. Understand the Last.fm API; ✔
2. **Create each feature method (Working)**:
	1. Create a list with user favorite songs; ✔
	2. Create a list with friends' favorite songs; ✔
	3. Create a list based on the artist's ranking. ✔
3. **Deal with errors and implement exceptions (Working)**;
4. Understand the Spotify API;
5. Create the Spotify playlist:
	1. Create the Spotify playlist;
	2. Get the spotify URL's song;
	3. Add the song to the Spotify playlist.
6. Fill the about section on the repository page;
7. Create the Run the File section;
8. Create the Local Setup section;
9. Create the Troubleshooting section; ✔
10. Create the Technologies section. ✔

## Technologies
* [Last.fm API]
* [Spotify Web API]
* [Requests Library v 2.22.0]
* [Account Overview]
* [Get Oauth]
* [Beautiful Soup Library v 4.9.1]

## Troubleshooting
* Spotify Oauth token expires very quickly, If you come across a `KeyError` this could
be caused by an expired token. So just refer back to step 3 in local setup, and generate a new
token! 

   [Last.fm API]:  <https://www.last.fm/api/intro>
   [Spotify Web API]: <https://developer.spotify.com/documentation/web-api/>
   [Requests Library v 2.22.0]: <https://requests.readthedocs.io/en/master/>
   [Account Overview]: <https://www.spotify.com/us/account/overview/>
   [Get Oauth]: <https://developer.spotify.com/console/post-playlists/>
