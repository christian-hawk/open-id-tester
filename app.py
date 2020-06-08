import traceback

from flask import Flask, request, redirect, url_for
import requests
import base64
import os
import clientconfig as cfg


app = Flask(__name__)

# here you can setup acr_values for scripts
ACR_VALUES = "passport_saml"

sub = ''

'''
STILL NOT WORKING - TO DO

@app.route('/endsession/<token>')
def end_session(token):
    """
    Ends user session - uses logout redirect uri if string is not empty
    :param token: Previously issued ID Token (id_token) passed to the logout endpoint as a hint
    about the End-User's current authenticated session with the Client.
    :return: redirect to login
    """
    global sub
    params = {
        "id_token_hint": sub
        #"state": base64.b64encode(os.urandom(18)).decode()
        f
    }
    if cfg.LOGOUT_REDIRECT_URI is not "":
        params.update({"post_logout_redirect_uri" : cfg.LOGOUT_REDIRECT_URI})

    r = requests.get(url=cfg.ENDSESSION_URI, verify=cfg.SSL_VERIFY)
    #r = requests.get(url=cfg.ENDSESSION_URI, params=params, verify=cfg.SSL_VERIFY)

    print(r.json())

'''

@app.route('/login')
def login():
    '''
    Loads request object and shows page with Login button to authn
    :return: html page with login button
    '''
    html = ""
    html_line = '\t\t\t\t<input type="hidden" name="%s" value="%s" />\n'
    request_object = {"scope": cfg.SCOPE,
                      "response_type": "code",
                      "client_id": cfg.CLIENT_ID,
                      "client_secret": cfg.CLIENT_SECRET,
                      "redirect_uri": cfg.REDIRECT_URI,
                      "acr_values": ACR_VALUES,
                      "state": base64.b64encode(os.urandom(18)).decode(),
                      "nonce": base64.b64encode(os.urandom(18)).decode()
                      }

    for param in request_object.keys():
        html = html + html_line % (param, request_object[param])

    print("request_object = " + str(request_object))
    print("html = " + html)
    return '''
        <h1>Welcome to OpenID Tester</H1>
        <form action="%s" method="post">
            %s
            <input value="Login" type="submit" />
        </form>
    ''' % (cfg.AUTH_URI, html)



@app.route('/callback')
def callback():
    '''
    - Receives callback from OP, including 'code'
    - Get access token using the code
    - redirects to /userinfo/<token> OR links to userinfo
    :return: redirects to get_user_info url w/ access token OR links to userinfo
    '''
    if request.args.get('error_description'):
        print("OP error: " + request.args.get('error_description'))
    code = request.args.get('code')
    session_id = request.args.get('session_id')
    session_state = request.args.get('session_state')
    print("CODE: " + code)
    r = request.query_string
    print("Query string: " + str(r))
    tokens = get_tokens(code)
    print("Access Token: " + str(tokens['access_token']))

    return '''
    <H1> Logged in </H1>
    <a href="%s"> Get userinfo </a>
    ''' % (url_for('get_user_info', token=tokens['access_token']))





@app.route('/userinfo/<token>')
def get_user_info(token):
    '''''''''''''''''''''''''''''
    Shows user information scoped
    :param token: client token
    :return: all userinfo attribute                                                 s scoped
    '''
    print("Entered get_user_info")
    print(token)
    headers = {"Authorization": "Bearer %s" % token}

    r = requests.post(url=cfg.USERINFO, headers=headers, verify=cfg.SSL_VERIFY)

    print(r.json())
    json_resp = r.json()
    #global sub
    #sub = json_resp['sub']

    # lets create an HTML code while we don't use templates
    html = ''
    html_line = '\t\t\t\t<p><b>%s: </b>%s</p>\n'
    for item in json_resp:
        html = html + html_line % (item, json_resp[item])
        print(item)
        print(json_resp[item])

    return'''
    <H1>This is your userinfo</H1>
    %s
    ''' % html

    '''
    <H1>This is your userinfo</H1>
    <a href=%s>Logout</a>
    %s
    ''' % (url_for('end_session', token=token), html)
    '''
    '''

    #return r.json()


def get_tokens(code):
    '''
    Get tokens using the auth code
    :param code: auth code
    :return: {} tokens (dict)
    '''
    tokens = None

    # this is for client_secret_basic auth method
    credentials = requests.auth.HTTPBasicAuth(cfg.CLIENT_ID, cfg.CLIENT_SECRET)

    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    params = {
        "code": code,
        "grant_type": "authorization_code",
        "client_id": cfg.CLIENT_ID,
        "redirect_uri": cfg.REDIRECT_URI
    }

    print("params = " + str(params))

    try:
        r = requests.post(url=cfg.TOKEN_ENDPOINT,
                          data=params,
                          headers=headers,
                          auth=credentials,
                          verify=cfg.SSL_VERIFY)
        print(r)
        if r.status_code != 200:
            print("Token Error! Return Code %i" % r.status_code)
            print(r)
            print(r.json())
            return None
        tokens = r.json()
        print("Tokens: %s\n" % str(tokens))

    except:
        print(traceback.format_exc())

    print("Tokens = %s" % str(tokens))
    return tokens


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', ssl_context=('cert.pem', 'key.pem'))
