from flask import Flask
from flask_env import MetaFlaskEnv
from flask import render_template, request, session, redirect, abort
from google.auth import jwt

# from flask.ext.oidc import OpenIDConnect
import dns.resolver
import requests
import hashlib
import base64
import os

class Configuration(metaclass=MetaFlaskEnv):
    DEBUG = True # Turns on debugging features in Flask
    SECRET_KEY = "a super secret key"

app = Flask(__name__)
app.config.from_object(Configuration)

# This can all be moved to subapplication if things get complex
@app.route('/')
def hello_world():
    # if oidc.user_loggedin:
    #     return render_template('index.html', email=oidc.user_getfield('email'), logged_in=True)
    # else:
        return render_template('index.html', logged_in=False)


@app.route('/test')
def test():
    return render_template('index.html', email=oidc.user_getfield('email'), logged_in=True)


@app.route('/login', methods=["POST"])
def login():
    error = None
    email = request.form['email']
    if email.find("@") != -1:
        domain = email[email.find("@")+1:]
        answers = list(dns.resolver.query(domain, 'MX'))
        answers.sort(key=lambda x:x.preference)
        server = answers[0].exchange
        error = server
        state = hashlib.sha256(os.urandom(1024)).hexdigest()
        session['state'] = state
        req = requests.Request('GET', "https://accounts.google.com/o/oauth2/auth", params={
         "client_id":app.config["CLIENT_ID"],
         "response_type":"code",
         "scope":"email",
         "redirect_uri":"http://localhost:5000/oidc_callback",
         "state":state,
         "nonce":"1",
         "hd":str(domain)
        })
        url = requests.Session().prepare_request(req).url

        return redirect(url)
    else:
        error = "Not a valid email address"

    return render_template('login.html', error=error)

@app.route('/oidc_callback')
def callback():
    state = request.args.get('state', '')
    code = request.args.get('code', '')
    if state != session['state']:
        abort(401)
    resp = requests.post('https://accounts.google.com/o/oauth2/token', data={
    'code':code,
    'client_id':app.config["CLIENT_ID"],
    'client_secret':app.config["CLIENT_SECRET"],
    'redirect_uri':'http://localhost:5000/oidc_callback',
    'grant_type':'authorization_code'
    }).json()
    access_token = resp['access_token']
    claims = jwt.decode(resp['id_token'], verify=False)
    return render_template('login.html', error=resp, email=claims['email'])
