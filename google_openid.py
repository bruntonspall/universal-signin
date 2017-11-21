from flask import render_template, request, session, redirect, abort
from google.auth import jwt
import dns.resolver

import requests
import hashlib
import os
import logging

class OpenIdConnectClient(object):
    def __init__(self, app):
        self.client_id = app.config["CLIENT_ID"]
        self.client_secret = app.config["CLIENT_SECRET"]
        self.redirect_base = app.config["REDIRECT_BASE"]

    def detectGoogleSuite(self, domain):
        answers = list(dns.resolver.query(domain, 'MX'))
        answers.sort(key=lambda x:x.preference)
        server = answers[0].exchange
        logging.warning("Looked up %s and MX record is: '%s'" % (domain,server))
        if str(server) == "aspmx.l.google.com.":
            return True
        headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.62 Safari/537.36'}
        r = requests.get('https://www.google.com/a/%s/ServiceLogin?service=mail' % (domain), allow_redirects=False, headers=headers)
        logging.warning("Requesting Google Login page %s = %s" % (r.url, r.status_code,))
        if r.status_code == 302:
            return True
        return False


    def redirect(self, domain):
        state = hashlib.sha256(os.urandom(1024)).hexdigest()
        session['state'] = state
        req = requests.Request('GET', "https://accounts.google.com/o/oauth2/auth", params={
         "client_id":self.client_id,
         "response_type":"code",
         "scope":"email",
         "redirect_uri":"%s/oidc_callback" % (self.redirect_base,),
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
        'redirect_uri':'%s/oidc_callback' % (self.redirect_base,),
        'grant_type':'authorization_code'
        }).json()
        access_token = resp['access_token']
        claims = jwt.decode(resp['id_token'], verify=False)
        return claims
