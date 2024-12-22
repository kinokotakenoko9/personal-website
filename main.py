from flask import Flask, jsonify, redirect, render_template, url_for
from flask_dance.contrib.github import github
from flask_dance.contrib.discord import discord
from flask_login import logout_user, login_required

from models import db, login_manager
from oauth import github_blueprint, discord_blueprint


app = Flask(__name__)
app.secret_key = "supersecretkey"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///./users.db"
app.register_blueprint(github_blueprint, url_prefix="/login")
app.register_blueprint(discord_blueprint, url_prefix="/login")

db.init_app(app)
login_manager.init_app(app)

with app.app_context():
    db.create_all()


@app.route("/ping")
def ping():
    return jsonify(ping="pong")


@app.route("/")
def homepage():
    return render_template("index.html")


@app.route("/github")
def login_github():
    if not github.authorized:
        return redirect(url_for("github.login"))
    res = github.get("/user")
    username = res.json()["login"]
    return f"You are @{username} on GitHub"

@app.route("/discord")
def login_discord():
    if not discord.authorized:
        return redirect(url_for("discord.login"))
    res = discord.get("/user")
    username = res.json()["login"]
    return f"You are @{username} on Discord"

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("homepage"))


if __name__ == "__main__":
    app.run(debug=True)