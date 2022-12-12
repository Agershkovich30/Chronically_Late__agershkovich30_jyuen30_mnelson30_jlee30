from flask import Flask, request, url_for, session, redirect, render_template
import requests
import base64

CLIENT_ID="6a0dedd845844c95a73948003cc241b7"
CLIENT_SECRET="62c8b70c2c684632b447ae65b1f4dd0e"
SECRET_KEY="seret-key"
REDIRECT_URL="http://localhost:5000/redirect"
LOCAL_URL="http://localhost:5000"
ACCESS_TOKEN_URL='https://accounts.spotify.com/api/token'
TOKEN_CODE = "BQDs01Ihut6uZ9Z9alod7ft9uBn_85hTd57TsNOMEypwPjZILXZgzlxlmrk4-T85wSjzItPX0wsai31g3C9f88mwZQvTYA629PadhDMZGxkL_LvpM9bIeCpww7jss2I_ruJ_Z89eeP9TBee_hfMlnyDGxuakl6_3bWch0SrxAt0S2xXdKFUW-IpvElRR5PcSjsyhaOrgvvg1qODKw4Y"

app = Flask(__name__)
app.secret_key = SECRET_KEY
app.config['SESSION_COOKIE_NAME'] = 'Julia Cookie'

@app.route('/')
def index():
    return redirect('/login')

@app.route('/login', methods=["GET","POST"])
def login():
    scope = 'user-read-private user-read-email'
    req = requests.get(f'https://accounts.spotify.com/authorize?client_id={CLIENT_ID}&response_type=code&redirect_uri={REDIRECT_URL}&scope={scope}')
    temp = req.url
    return redirect(temp)

@app.route('/redirect', methods=["GET","POST"])
def process():
    code = request.args.get('code')
    state = request.args.get('state')
    form = {
        'grant_type': 'authorization_code',
        'code': f'{code}',
        'redirect_uri': f'{REDIRECT_URL}'
    }
    client_creds = f'{CLIENT_ID}:{CLIENT_SECRET}'
    client_creds_b64 = base64.b64encode(client_creds.encode())
    headers = {
        'Authorization': f"Basic {client_creds_b64.decode()}"
    }
    req = requests.post(ACCESS_TOKEN_URL,data=form,headers=headers)
    return req.json()

if __name__ == '__main__':
    app.run(
    debug = True
    )
