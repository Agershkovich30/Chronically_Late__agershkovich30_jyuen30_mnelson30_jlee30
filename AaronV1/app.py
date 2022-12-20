from flask import Flask, request, url_for, session, redirect, render_template
import requests
import base64
import json
import spotipy
import webbrowser
from credentials import CLIENT_ID, CLIENT_SECRET, SECRET_KEY
import os

REDIRECT_URL="http://localhost:5000/redirect"
ACCESS_TOKEN_URL='https://accounts.spotify.com/api/token'

app = Flask(__name__)
app.secret_key = SECRET_KEY
app.config['SESSION_COOKIE_NAME'] = 'Julia Cookie'

@app.route('/')
def index():
    return render_template('home.html')

#Redirects you to the Spotify authorize request page.
@app.route('/login', methods=["GET","POST"])
def login():
    scope = '''
    user-read-private user-read-email user-top-read user-library-read ugc-image-upload user-read-playback-state user-modify-playback-state
    user-read-currently-playing app-remote-control streaming playlist-read-private playlist-read-collaborative playlist-modify-private
    playlist-modify-public user-follow-modify user-follow-read user-read-playback-position user-top-read user-read-recently-played
    user-library-modify user-library-read user-read-email user-read-private
    ''' #Determines the scope of information you are requesting access to.
    # Gets the URL for the Spotify authorize request page.
    AUTH_TYPE = 'code'
    req = requests.get(f'https://accounts.spotify.com/authorize?client_id={CLIENT_ID}&response_type={AUTH_TYPE}&redirect_uri={REDIRECT_URL}&scope={scope}&show_dialog=true')
    temp = req.url
    return redirect(temp)

@app.route('/back', methods=["GET","POST"])
def back():
    access_token = request.args.get('token')
    return render_template('stats.html', access_token=access_token)

@app.route('/redirect', methods=["GET","POST"])
def process():
    #Stores the code that you got from the login page when you accepted the connection to spotify
    code = request.args.get('code')
    state = request.args.get('state')
    #This is the body of the post request you will make later.
    form = {
        'grant_type': 'authorization_code',
        'code': f'{code}',
        'redirect_uri': f'{REDIRECT_URL}'
    }
    #Spotify requires base64 encoding for client_id and client_secret when providing it in the header.
    client_creds = f'{CLIENT_ID}:{CLIENT_SECRET}'
    client_creds_b64 = base64.b64encode(client_creds.encode())
    headers = {
        'Authorization': f"Basic {client_creds_b64.decode()}"
    }
    #POST request using the code obtained from logging in. Most importantly, returns the token.
    req = requests.post(ACCESS_TOKEN_URL,data=form,headers=headers)
    access_token = req.json().get('access_token')
    return render_template('stats.html', access_token=access_token)

@app.route('/choose', methods=["GET", "POST"])
def choose():
    if request.method == "POST":
        access_token = request.args.get('token')
        if request.form["submit_button"] == "Get Top Tracks":
            return render_template("toptracks.html", oldtoken=access_token, newlimit=0, newoffset=0)
        elif request.form["submit_button"] == "Get Top Artists":
            return render_template("topartists.html", oldtoken=access_token, newlimit=0, newoffset=0)
    return render_template('stats.html', token=access_token)

@app.route('/toptracks', methods=['GET','POST'])
def getTracks():
    ACCESS_TOKEN = request.args.get('token')
    if request.method == "POST":
        # Provides the access token as a header
        headers = {
            "Authorization": f"Bearer {ACCESS_TOKEN}"
        }
        if request.form["see more"] == "add":
            limit = int(request.args.get('limit'))
            offset = int(request.args.get('offset'))
            if offset >= 40 and limit <= 40:
                limit += limit
        # Determines parameters of information to be obtained
        else:
            limit = request.form['limit']
            offset = request.form['offset']
        type = "tracks"
        # Long-term means over the span of multiple years according to spotify documentation
        time_range = "long_term"
        # URL that will be used to GET data with appropriate headers
        lookup_url = f"https://api.spotify.com/v1/me/top/{type}?limit={limit}&offset={offset}&time_range={time_range}"
        req = requests.get(lookup_url, headers=headers)
        allData = req.json()
        # Creates a list for top tracks to be listed
        toptracks = []
        # First, gets all of the data from the json data we requested earlier
        data = req.json().get('items')
        print(req)
        # For every item in that list of tracks
        for item in data:
            # Add the track's name to our list
            temp = [item.get('name'),item.get('id')]
            toptracks.append(temp)
        # Give us the list of our top 50 tracks
        return render_template("toptracks.html", data=toptracks, newoffset=int(offset), newlimit=int(limit), oldtoken=ACCESS_TOKEN)
    else:
        return render_template("toptracks.html", oldtoken=ACCESS_TOKEN, newlimit=0, newoffset=0)

@app.route('/toptracks/<trackid>', methods=['GET','POST'])
def displayTrack(trackid):
    ACCESS_TOKEN = request.args.get('token')
    if request.method == "POST":
        headers = {
            "Authorization": f"Bearer {ACCESS_TOKEN}"
        }
        type = "tracks"
        lookup_url = f"https://api.spotify.com/v1/{type}/{trackid}"
        req = requests.get(lookup_url, header=headers)
        allData = req.json()
        trackdata = []
        urls = allData.get('external_urls')
        trackdata.append(urls.get('href'))
        return f'This is the {trackid} and this is the link: {trackdata[0]}'
        oauth_object = spotipy.SpotifyOAuth(clientID,clientSecret,redirectURI)
        spotifyObject = spotipy.Spotify(auth=access_token)
        user = spotifyObject.current_user()
        print(json.dumps(user,sort_keys=True, indent=4))
        # Search for the Song.
        searchResults = spotifyObject.search(searchQuery,1,0, allData[0].get('track'))
        # Get required data from JSON response.
        tracks_dict = searchResults['tracks']
        tracks_items = tracks_dict['items']
        song = tracks_items[0]['external_urls']['spotify']
        # Open the Song in Web Browser
        webbrowser.open(song)
        print('Song has opened in your browser.')
    else:
        return "this doesn't work :("

@app.route('/topartists', methods=['GET','POST'])
def getArtists():
    ACCESS_TOKEN = request.args.get('token')
    if request.method == "POST":
        # Provides the access token as a header
        headers = {
            "Authorization": f"Bearer {ACCESS_TOKEN}"
        }
        if request.form["see more"] == "add":
            limit = int(request.args.get('limit'))
            offset = int(request.args.get('offset'))
            if offset >= 40 and limit <= 40:
                limit += (offset-limit)
        # Determines parameters of information to be obtained
        else:
            limit = request.form['limit']
            offset = request.form['offset']
        type = "artists"
        # Long-term means over the span of multiple years according to spotify documentation
        time_range = "long_term"
        # URL that will be used to GET data with appropriate headers
        lookup_url = f"https://api.spotify.com/v1/me/top/{type}?limit={limit}&offset={offset}&time_range={time_range}"
        req = requests.get(lookup_url, headers=headers)
        allData = req.json()
        # Creates a list for top tracks to be listed
        toptracks = []
        # First, gets all of the data from the json data we requested earlier
        data = req.json().get('items')
        # For every item in that list of tracks
        for item in data:
            # Add the track's name to our list
            temp = [item.get('name'),str(item.get('id'))]
            toptracks.append(temp)
        name = data[0].get('name')
        api_url = 'https://api.api-ninjas.com/v1/celebrity?name={}'.format(name)
        response = requests.get(api_url, headers={'X-Api-Key': '+M6tFBonGGlY40Dep3Fz5A==F0lCCUzJh88dYOtQ'})
        AllData = response.json()
        NetWorthData = AllData[0].get('net_worth')
        Nationality = AllData[0].get('nationality')
        Birthday = AllData[0].get('birthday')
        return render_template("topartists.html", data=toptracks, newoffset=int(offset), newlimit=int(limit), oldtoken=ACCESS_TOKEN, netWorth= NetWorthData, topArtist= name, nationality = Nationality, birthday = Birthday)
    else:
        return render_template("topartists.html", oldtoken=ACCESS_TOKEN, newlimit=0, newoffset=0)
if __name__ == '__main__':
    app.run(
    debug = True
    )