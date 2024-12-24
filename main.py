from flask import Flask, jsonify, redirect, render_template, url_for
from flask_dance.contrib.github import github
from flask_dance.contrib.discord import discord
from flask_login import logout_user, login_required, current_user

from models import db, login_manager, Like
from oauth import github_blueprint, discord_blueprint


app = Flask(__name__)
app.secret_key = "supersecretkey"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///./users.db"
app.register_blueprint(github_blueprint, url_prefix="/login_github")
app.register_blueprint(discord_blueprint, url_prefix="/login_discord")

db.init_app(app)
login_manager.init_app(app)

with app.app_context():
    db.create_all()


@app.route("/ping")
def ping():
    return jsonify(ping="pong")


@app.route("/")
def homepage():
    user_liked = False
    if current_user.is_authenticated:
        user_liked = Like.query.filter_by(user_id=current_user.id).first() is not None
    return render_template("index.html", user_liked=user_liked)


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
    res = discord.get("/api/users/@me")
    username = res.json()["username"]
    return f"You are @{username} on Discord"

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("homepage"))

@app.route("/like", methods=["POST"])
@login_required
def like():
    existing_like = Like.query.filter_by(user_id=current_user.id).first()
    if existing_like:
        # If the user already liked, remove the like (unlike)
        db.session.delete(existing_like)
        db.session.commit()
        return jsonify({"success": True, "action": "unliked"})
    else:
        # If the user has not liked yet, add a like
        new_like = Like(user_id=current_user.id)
        db.session.add(new_like)
        db.session.commit()
        return jsonify({"success": True, "action": "liked"})
    
@app.route("/likes", methods=["GET"])
def get_likes():
    total_likes = Like.query.count()
    return jsonify({"total_likes": total_likes})

if __name__ == "__main__":
    app.run(debug=True, port=80, host="0.0.0.0")
