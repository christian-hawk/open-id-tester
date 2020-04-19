# OpenID Connect Tester

This is a small and simple flask OpenID client for testing Gluu Server (gluu.org) locally.

## Installation

Clone the repository

Install packages: `pip install -r requirements.txt`

create `clientconfig.py`

`
CLIENT_ID = "YOURCLIENTID"
CLIENT_SECRET = "YOURCLIENTSECRET"
AUTH_URI = "https://YOURHOST/oxauth/restv1/authorize"
SCOPE = "openid profile"
RESPONSE_TYPE = "code"
REDIRECT_URI = "https://localhost:5000/callback"
TOKEN_ENDPOINT = "https://YOURHOST/oxauth/restv1/token"
USERINFO = 'https://YOURHOST/oxauth/restv1/userinfo'
SSL_VERIFY = False`

run `openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365`

