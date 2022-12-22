from flask import Flask, request, url_for, session, redirect, render_template
import requests
import base64
from keys.credentials import CLIENT_ID, CLIENT_SECRET, SECRET_KEY, LYRICS_KEY, CELEB_KEY
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
        if request.form["see more"] == "add" or request.form["see more"] == "back":
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
        # testing number of rows to be created
        # s = sqlite3.connect("Spotify.db")
        # c = s.cursor()
        # c.execute("SELECT COUNT(*) FROM toptracks")
        # maxrows = int(c.fetchone())
        # if maxrows > limit+offset:
        #     maxrows = limit+offset
        # Creates a dictionary with each of the artists and their information using the database. Each dict value is a tuple.
        while i < maxrows:
            data[str(i)] = topTracks_table.get(cursor=connection.cursor(), rank=i, session_key=ACCESS_TOKEN, term_length=time_range) 
            i += 1
        song = topTracks_table.get(cursor=connection.cursor(), rank=offset, term_length=time_range, session_key=ACCESS_TOKEN)
        song_name = song[0]
        song_artist = song[4]
        search_lyrics_url = f"http://api.musixmatch.com/ws/1.1/track.search?apikey={LYRICS_KEY}&q_artist={song_artist}&q_track={song_name}"
        lyrics_req = requests.get(search_lyrics_url)
        musixmatch_data = lyrics_req.json()
        song_id = musixmatch_data.get("message").get("body").get("track_list")[0].get("track").get("track_id")
        get_lyrics_url = f"http://api.musixmatch.com/ws/1.1/track.lyrics.get?apikey={LYRICS_KEY}&track_id={song_id}"
        req = requests.get(get_lyrics_url, headers=headers)
        lyrics_data = req.json()
        lyrics_string = str(lyrics_data.get("message").get("body").get("lyrics").get("lyrics_body"))
        return render_template("toptracks.html", data=data, newoffset=int(offset), newlimit=int(limit), oldtoken=ACCESS_TOKEN, time_range=time_range, LYRICS_BODY=lyrics_string)
    else:
        return render_template("toptracks.html", oldtoken=ACCESS_TOKEN, newlimit=0, newoffset=0)

@app.route('/toptracks/<trackid>', methods=['GET','POST'])
def displayTrack(trackid):
    ACCESS_TOKEN = request.args.get('token')
    limit = int(request.args.get('limit')) 
    offset = int(request.args.get('offset')) # Moves offset over by however much the limit is.
    time_range = request.args.get('range')
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}"
    }
    song = topTracks_table.get(cursor=connection.cursor(), trackID=trackid, term_length=time_range, session_key=ACCESS_TOKEN)
    song_name = song[0]
    song_artist = song[4]
    search_lyrics_url = f"http://api.musixmatch.com/ws/1.1/track.search?apikey={LYRICS_KEY}&q_artist={song_artist}&q_track={song_name}"
    lyrics_req = requests.get(search_lyrics_url)
    musixmatch_data = lyrics_req.json()
    has_lyrics = musixmatch_data.get("message").get("body").get("track_list")[0].get("track").get("has_lyrics")
    song_id = musixmatch_data.get("message").get("body").get("track_list")[0].get("track").get("track_id")
    get_lyrics_url = f"http://api.musixmatch.com/ws/1.1/track.lyrics.get?apikey={LYRICS_KEY}&track_id={song_id}"
    req = requests.get(get_lyrics_url, headers=headers)
    lyrics_data = req.json()
    # checking whether or not it actually has lyrics
    if (has_lyrics==0):
        lyrics_string = "This song has no lyrics :( Check back next time!"
    else:
        lyrics_string = str(lyrics_data.get("message").get("body").get("lyrics").get("lyrics_body"))
    return render_template("track.html", data = song, lyrics = lyrics_string, oldtoken=ACCESS_TOKEN, newlimit=limit, newoffset=offset, time_range=time_range)

@app.route('/<key>', methods=['GET','POST'])
def displayLyrics(key):
    ACCESS_TOKEN = request.args.get('token')
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}"
    }
    global DATA_GLOBAL_LYRICS
    trackid = DATA_GLOBAL_LYRICS.get(key)
    get_lyrics_url = f"http://api.musixmatch.com/ws/1.1/track.lyrics.get?apikey={LYRICS_KEY}&track_id={trackid}"
    req = requests.get(get_lyrics_url, headers=headers)
    lyrics_data = req.json()
    LYRICS = lyrics_data.get("message").get("body").get("lyrics").get("lyrics_body")
    return render_template("track.html", oldtoken=ACCESS_TOKEN, SONG_TITLE = trackid, SONG_LYRICS=LYRICS)
    

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

            headers = {
            "X-Api-Key": f"{CELEB_KEY}"
            }
            celebrity = topArtists_table.get(cursor=connection.cursor(), session_key=ACCESS_TOKEN, rank=0, term_length=time_range)
            celebrity_url = f"https://api.api-ninjas.com/v1/celebrity?name={celebrity[0]}"
            celeb_req = requests.get(celebrity_url, headers=headers)
            celeb_data = celeb_req.json()
            if len(celeb_data) > 0:
                net_worth = celeb_data[0].get('net_worth')
                nationality = celeb_data[0].get('nationality')
                birthday = celeb_data[0].get('birthday')
                topArtists_table.update(cursor=connection.cursor(), id=celebrity[2], net_worth=net_worth, nationality=nationality, birthday=birthday)

        data = {}
        i = offset
        # Creates a dictionary with each of the artists and their information using the database. Each dict value is a tuple.
        while i < limit+offset:
            data[str(i)] = topArtists_table.get(cursor=connection.cursor(), rank=i, session_key=ACCESS_TOKEN, term_length=time_range)
            i += 1
        return render_template("topartists.html", oldtoken=ACCESS_TOKEN, newlimit=limit, newoffset=offset, time_range=time_range, data=data)
    else:
        return render_template("topartists.html", oldtoken=ACCESS_TOKEN, newlimit=0, newoffset=0)

if __name__ == '__main__':
    app.run(
    debug = True
    )