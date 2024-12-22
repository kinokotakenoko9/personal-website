from flask import Flask, redirect, url_for, session, render_template, request
from authlib.integrations.flask_client import OAuth
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)
oauth = OAuth(app)

# GitHub OAuth configuration
github = oauth.register(
    'github',
    client_id='YOUR_GITHUB_CLIENT_ID',
    client_secret='YOUR_GITHUB_CLIENT_SECRET',
    authorize_url='https://github.com/login/oauth/authorize',
    access_token_url='https://github.com/login/oauth/access_token',
    api_base_url='https://api.github.com/',
    client_kwargs={'scope': 'user:email'},
)

# Telegram OAuth configuration (handled via Telegram Login Widget)
TELEGRAM_BOT_USERNAME = 'YOUR_TELEGRAM_BOT_USERNAME'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login/github')
def login_github():
    return github.authorize_redirect(url_for('github_callback', _external=True))

@app.route('/login/github/callback')
def github_callback():
    token = github.authorize_access_token()
    if not token:
        return 'Login failed.'
    user_info = github.get('user').json()
    session['user'] = user_info
    return redirect(url_for('resume'))

@app.route('/login/telegram')
def login_telegram():
    return render_template('telegram_login.html', bot_username=TELEGRAM_BOT_USERNAME)

@app.route('/login/telegram/callback', methods=['POST'])
def telegram_callback():
    user_data = request.form.to_dict()
    # Implement Telegram login verification (e.g., hash validation)
    session['user'] = user_data
    return redirect(url_for('resume'))

@app.route('/resume')
def resume():
    if 'user' not in session:
        return redirect(url_for('index'))
    return render_template('resume.html', user=session['user'])

if __name__ == '__main__':
    app.run(debug=True)
