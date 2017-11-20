from flask import Flask
from flask import render_template

app = Flask(__name__)
app.config.from_object('config')

# This can all be moved to subapplication if things get complex
@app.route('/')
def hello_world():
    return render_template('index.html')
