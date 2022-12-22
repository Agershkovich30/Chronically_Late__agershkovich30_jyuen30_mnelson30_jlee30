# Spotify Bootstrapped by Chronically Late

## Roles:
- Aaron: PM
- Julia, Maya, Jasmine: Developers

## Description:
Our most certainly professional Spotify Bootstrapped will present you with a variety of Spotify stats relating to your Spotify year. There will be lots of data that your typical Spotify Wrapped may have failed to provide you with. As of right now, we are looking to include information about who your top artists were in multiple time frames, as well as time listened, most popular album from them, and percentage of total listeners for that artist. We are open to changing our idea depending on our ability to process the information that we are able to glean from the Spotify APIs. We will also provide a Artist informations section where you can learn more about your favorite artists! 

## APIs and Cards:
- https://github.com/stuy-softdev/notes-and-code/blob/main/api_kb/411_on_Spotify.md
- https://github.com/stuy-softdev/notes-and-code/blob/main/api_kb/411_on_genius.md
- https://github.com/stuy-softdev/notes-and-code/blob/main/api_kb/411_on_musiXmatch.md

## Launch Code:
### Before Running Anything:
- Option 1 (May take more time than Option 2):
  - Contact Devos and ask to have your Spotify email added to our app.
- Option 2:
  - Go to https://developer.spotify.com/dashboard/login and create your own Spotify app.
  - Go to edit settings in your app.
  - Add the following links to your Redirect URIs:
    - http://localhost:5000/redirect
    - http://localhost:5000
  - Update credentials.py's CLIENT_SECRET and CLIENT_KEY to match your app's credentials.
### After Setting Up the Spotify App:
- in terminal: ~```pip install requests```
- run seed.py to create database file
  ```python3 seed.py```
- Just run ```python3 app.py``` and it should work.
- When logging in, use shared Spotify account or ask devos to add your account to the app.
  - Spotify API requires you to add access users, so anyone whos email isn't added cannot get their data from the Spotify API through our app. We can have a maximum of 25 users for a single app.

## Resources:
- https://spotipy.readthedocs.io/en/2.16.1/
- https://github.com/eriktoor/receiptify-flask.git
- https://levelup.gitconnected.com/how-to-build-a-spotify-player-with-react-in-15-minutes-7e01991bc4b6
