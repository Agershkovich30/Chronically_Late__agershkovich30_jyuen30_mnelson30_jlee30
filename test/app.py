from flask import Flask, request, url_for, session, redirect, render_template
import requests
import base64
from credentials import CLIENT_ID, CLIENT_SECRET, SECRET_KEY, LYRICS_KEY
import os
import Database.topTracks as topTracks_table
import Database.topArtists as topArtists_table
import sqlite3

REDIRECT_URL="http://localhost:5000/redirect"
ACCESS_TOKEN_URL='https://accounts.spotify.com/api/token'

app = Flask(__name__)
app.secret_key = SECRET_KEY
app.config['SESSION_COOKIE_NAME'] = 'Julia Cookie'
database_name = "Spotify.db"
connection = sqlite3.connect(database_name, check_same_thread = False)

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
    return render_template('stats.html', old_token=access_token)

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
    return render_template('stats.html', oldtoken=access_token)

@app.route('/choose', methods=["GET", "POST"])
def choose():
    access_token = request.args.get('token')
    if request.method == "POST":
        if request.form["submit_button"] == "Get Top Tracks":
            return render_template("toptracks.html", oldtoken=access_token, newlimit=0, newoffset=0)
        elif request.form["submit_button"] == "Get Top Artists":
            return render_template("topartists.html", oldtoken=access_token, newlimit=0, newoffset=0)
    return render_template('stats.html', oldtoken=access_token)

@app.route('/toptracks', methods=['GET','POST'])
def getTracks():
    ACCESS_TOKEN = request.args.get('token')
    if request.method == "POST":
        # Provides the access token as a header
        headers = {
            "Authorization": f"Bearer {ACCESS_TOKEN}"
        }
        # If we don't have the data for the request, it will redirect the user to the page to choose a new journey.
        if int(request.args.get('offset')) + int(request.args.get('limit')) > 100:
            return render_template("stats.html", oldtoken=ACCESS_TOKEN)
        # If the user requested to see more information, gives the next set of top tracks.
        if request.form["see more"] == "add":
            limit = int(request.args.get('limit')) 
            offset = int(request.args.get('offset')) # Moves offset over by however much the limit is.
            time_range = request.args.get('range')
        else:
            limit = int(request.form['limit'])
            offset = int(request.form['offset'])
            type = "tracks"
            # Long-term means over the span of multiple years according to spotify documentation
            time_range = request.form["see more"]
            # URL that will be used to GET data with appropriate headers
            lookup_url = f"https://api.spotify.com/v1/me/top/{type}?limit=50&offset=0&time_range={time_range}"
            req = requests.get(lookup_url, headers=headers)
            allData = req.json()
            items = allData.get("items")
            if len(items) > 0:
                topTracks_table.create(cursor=connection.cursor(), list=items, start=0, key=ACCESS_TOKEN, term_length=time_range)
            # URL that will be used to GET data with appropriate headers
            lookup_url = f"https://api.spotify.com/v1/me/top/{type}?limit=50&offset=49&time_range={time_range}"
            req = requests.get(lookup_url, headers=headers)
            allData = req.json()
            items = allData.get("items") # List with each of the artists
            if len(items) > 0:
                topTracks_table.create(cursor=connection.cursor(), list=items, start=49, key=ACCESS_TOKEN, term_length=time_range)
        data = {}
        i = offset
        # Creates a dictionary with each of the artists and their information using the database. Each dict value is a tuple.
        while i < limit+offset:
            data[str(i)] = topTracks_table.get(cursor=connection.cursor(), rank=i, session_key=ACCESS_TOKEN, term_length=time_range)
            i += 1

        # MUSIXMATCH STUFF
        lyrics_string = ""
        top_song_name = data.get("0")[0].replace(" ", "%20")
        top_song_artist = data.get("0")[4].replace(" ", "%20")
        search_lyrics_url = f"http://api.musixmatch.com/ws/1.1/track.search?apikey={LYRICS_KEY}&q_artist={top_song_artist}&q_track={top_song_name}"
        req = requests.get(search_lyrics_url, headers=headers)
        musixmatch_data = req.json()
        song_id = musixmatch_data.get("message").get("body").get("track_list")[0].get("track").get("track_id")
        get_lyrics_url = f"http://api.musixmatch.com/ws/1.1/track.lyrics.get?apikey={LYRICS_KEY}&track_id={song_id}"
        req = requests.get(get_lyrics_url, headers=headers)
        lyrics_data = req.json()
        lyrics_string = lyrics_data.get("message").get("body").get("lyrics").get("lyrics_body")

        # MUSIXMATCH DONE

        return render_template("toptracks.html", data=data, newoffset=int(offset), newlimit=int(limit), oldtoken=ACCESS_TOKEN, time_range=time_range, LYRICS_BODY=lyrics_string)
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
        if int(request.args.get('offset')) + int(request.args.get('limit')) > 100:
            return render_template("stats.html", oldtoken=ACCESS_TOKEN)
        if request.form["see more"] == "add":
            limit = int(request.args.get('limit'))
            offset = int(request.args.get('offset'))
            time_range = request.args.get('range')
        # Determines parameters of information to be obtained
        else:
            limit = int(request.form['limit'])
            offset = int(request.form['offset'])
            type = "artists"
            # Long-term means over the span of multiple years according to spotify documentation
            time_range = request.form["see more"]
            # URL that will be used to GET data with appropriate headers
            lookup_url = f"https://api.spotify.com/v1/me/top/{type}?limit=50&offset=0&time_range={time_range}"
            req = requests.get(lookup_url, headers=headers)
            allData = req.json()
            items = allData.get("items")
            if len(items) > 0:
                topArtists_table.create(cursor=connection.cursor(), list=items, start=0, key=ACCESS_TOKEN, term_length=time_range)
            # URL that will be used to GET data with appropriate headers
            lookup_url = f"https://api.spotify.com/v1/me/top/{type}?limit=50&offset=49&time_range={time_range}"
            req = requests.get(lookup_url, headers=headers)
            allData = req.json()
            items = allData.get("items") # List with each of the artists
            if len(items) > 0:
                topArtists_table.create(cursor=connection.cursor(), list=items, start=49, key=ACCESS_TOKEN, term_length=time_range)
        data = {}
        i = offset
        # Creates a dictionary with each of the artists and their information using the database. Each dict value is a tuple.
        while i < limit+offset:
            data[str(i)] = topArtists_table.get(cursor=connection.cursor(), rank=i, session_key=ACCESS_TOKEN, term_length=time_range)
            i += 1
        return render_template("topartists.html", data=data, newoffset=int(offset), newlimit=int(limit), oldtoken=ACCESS_TOKEN, time_range=time_range)
        # name = topartists[0].get('name')
        # api_url = 'https://api.api-ninjas.com/v1/celebrity?name={}'.format(name)
        # response = requests.get(api_url, headers={'X-Api-Key': '+M6tFBonGGlY40Dep3Fz5A==F0lCCUzJh88dYOtQ'})
        # AllData = response.json()
        # NetWorthData = AllData[0].get('net_worth')
        # Nationality = AllData[0].get('nationality')
        # Birthday = AllData[0].get('birthday')
    else:
        return render_template("topartists.html", oldtoken=ACCESS_TOKEN, newlimit=0, newoffset=0)

if __name__ == '__main__':
    app.run(
    debug = True
    )
