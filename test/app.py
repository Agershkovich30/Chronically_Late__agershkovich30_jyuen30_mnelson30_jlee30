from flask import Flask, request, url_for, session, redirect, render_template
import requests
import base64

CLIENT_ID="6a0dedd845844c95a73948003cc241b7"
CLIENT_SECRET="62c8b70c2c684632b447ae65b1f4dd0e"
SECRET_KEY="seret-key"
REDIRECT_URL="http://localhost:5000/redirect"
ACCESS_TOKEN_URL='https://accounts.spotify.com/api/token'

app = Flask(__name__)
app.secret_key = SECRET_KEY
app.config['SESSION_COOKIE_NAME'] = 'Julia Cookie'

@app.route('/')
def index():
    return redirect('/login')

#Redirects you to the Spotify authorize request page.
@app.route('/login', methods=["GET","POST"])
def login():
    scope = 'user-read-private user-read-email' #Determines the scope of information you are requesting access to.
    # Gets the URL for the Spotify authorize request page.
    req = requests.get(f'https://accounts.spotify.com/authorize?client_id={CLIENT_ID}&response_type=code&redirect_uri={REDIRECT_URL}&scope={scope}')
    temp = req.url
    return redirect(temp)

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
    return req.json()

if __name__ == '__main__':
    app.run(
    debug = True
    )
