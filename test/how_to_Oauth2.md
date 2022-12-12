# What is OAUTH 2.0?

It is an authorization tool that many applications use in order to gain access to information from different sources on a user without actually gathering their account credentials.
After having the user log into their account on a different platform, the application then receives an access token that they can then use to gather the information that they need.

## Prerequisites:
Knowledge of how to set up your API’s redirect urls and what query values each request needs.
Know your app’s client id and secret if necessary.

## Steps:
1. Use GET to get the url for your API’s authorization using their authorize url and provide all necessary query values.

Ex for Spotify:
```py
CLIENT_ID = <client id>
CLIENT_SECRET= <client secret>
REDIRECT_URL="http://localhost:5000/redirect"
# Redirects you to the Spotify authorize request page.
@app.route('/login', methods=["GET","POST"])
def login():
    scope = 'user-read-private user-read-email' #Determines the scope of information you are requesting access to.
    # Gets the URL for the Spotify authorize request page and redirects the user to that page.
    req = requests.get(f'https://accounts.spotify.com/authorize?client_id={CLIENT_ID}&response_type=code&redirect_uri={REDIRECT_URL}&scope={scope}')
    temp = req.url
    return redirect(temp)

```

2. Store the necessary information (code) returned in the GET request.
3. The redirect_uri provided in the previous request will bring you to that link once the authorization request is accepted.
4. In the route that will be used when you are redirected from your previous request, make a POST request using the given access token url for your API and provide all necessary data and headers.
5. Read the POST requests’ data, and save the token data given.

```py
#You will be redirected here because the provided redirect_uri was http://localhost:5000/redirect
@app.route('/redirect', methods=["GET","POST"])
def process():
    #Stores the code that you got from the login page when you accepted the connection to spotify
    code = request.args.get('code')
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
```