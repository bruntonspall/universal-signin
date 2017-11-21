from flask import render_template, request, session, redirect, abort
from google.auth import jwt

import requests
import hashlib
import os
import logging


class OpenIdConnectClient(object):
    def __init__(self, app):
        self.client_id = app.config["MS_CLIENT_ID"]
        self.redirect_base = app.config["REDIRECT_BASE"]

    def redirect(self, email):
        state = hashlib.sha256(os.urandom(1024)).hexdigest()
        session['state'] = state
        req = requests.Request('GET', "https://login.microsoftonline.com/common/oauth2/v2.0/authorize", params={
         "client_id":self.client_id,
         "response_type":"id_token",
         "response_mode":"form_post",
         "scope":"openid email",
         "redirect_uri":"%s/ms_oidc_callback" % (self.redirect_base,),
         "state":state,
         "nonce":"1",
         "login_hint": email
        })
        url = requests.Session().prepare_request(req).url

        return redirect(url)

    def get_claims(self, id_token):
        claims = jwt.decode(id_token, verify=False)
        logging.warning("MS Claim: '%s'" % (claims,))
        return claims
