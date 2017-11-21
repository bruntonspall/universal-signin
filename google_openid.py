from flask import render_template, request, session, redirect, abort
from google.auth import jwt

import requests
import hashlib
import os

class OpenIdConnectClient(object):
    def __init__(self, app):
        self.client_id = app.config["CLIENT_ID"]
        self.client_secret = app.config["CLIENT_SECRET"]

    def redirect(self, domain):
        state = hashlib.sha256(os.urandom(1024)).hexdigest()
        session['state'] = state
        req = requests.Request('GET', "https://accounts.google.com/o/oauth2/auth", params={
         "client_id":self.client_id,
         "response_type":"code",
         "scope":"email",
         "redirect_uri":"http://localhost:5000/oidc_callback",
         "state":state,
         "nonce":"1",
         "hd":str(domain)
        })
        url = requests.Session().prepare_request(req).url

        return redirect(url)

    def get_claims(self, code):
        resp = requests.post('https://accounts.google.com/o/oauth2/token', data={
        'code':code,
        'client_id':self.client_id,
        'client_secret':self.client_secret,
        'redirect_uri':'http://localhost:5000/oidc_callback',
        'grant_type':'authorization_code'
        }).json()
        access_token = resp['access_token']
        claims = jwt.decode(resp['id_token'], verify=False)
        return claims
