from flask import Flask
from flask_env import MetaFlaskEnv
from flask import render_template, request, session, redirect, abort

# from flask.ext.oidc import OpenIDConnect
import google_openid
import microsoft_openid
import dns.resolver


class Configuration(metaclass=MetaFlaskEnv):
    DEBUG = True # Turns on debugging features in Flask
    SECRET_KEY = "a super secret key"

app = Flask(__name__)
app.config.from_object(Configuration)

google = google_openid.OpenIdConnectClient(app)
microsoft = microsoft_openid.OpenIdConnectClient(app)

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
        if google.detectGoogleSuite(domain):
            return google.redirect(domain)
        else:                
            return microsoft.redirect(email)
    else:
        error = "Not a valid email address"

    return render_template('login.html', error=error)

@app.route('/ms_oidc_callback', methods=["POST"])
def microsoft_callback():
    state = request.form['state']
    id_token = request.form['id_token']
    if state != session['state']:
        abort(401)
    claims = microsoft.get_claims(id_token)
    return render_template('login.html', error=claims, email=claims['email'])

@app.route('/oidc_callback')
def google_callback():
    state = request.args.get('state', '')
    code = request.args.get('code', '')
    if state != session['state']:
        abort(401)
    claims = google.get_claims(code)
    return render_template('login.html', error=claims, email=claims['email'])
