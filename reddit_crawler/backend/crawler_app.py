import json
import random
import threading
import time
import praw

from flask import Flask, render_template, jsonify, request
from models import db, User, create_admin_user, bcrypt, Subreddit, Post, Response
from flask import Flask
from sqlalchemy.exc import IntegrityError
from flask_cors import CORS
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required

post_limit = 5000
current_subreddit = None
currently_collecting = False
status = "Online"

with open("reddit_config.json") as config_file:
    config = json.load(config_file)

reddit = praw.Reddit(
    client_id=config["client_id"],
    client_secret=config["client_secret"],
    user_agent=config["user_agent"]
)

app = Flask(__name__)
CORS(app, supports_credentials=True)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

app.config.from_object('config.Config')
db.init_app(app)

with app.app_context():
    db.create_all()
    if not User.query.filter_by(username='admin').first():
        create_admin_user()


@app.route('/protected')
def protected():
    if current_user.is_authenticated:
        return jsonify({"loggedIn": True}), 200
    else:
        return jsonify({"loggedIn": False}), 401


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/login', methods=['POST'])
def login():
    data = request.json
    user = User.query.filter_by(username=data['username']).first()

    if user and bcrypt.check_password_hash(user.password, data['password']):
        login_user(user)
        print("Logged in successfully!")
        return jsonify({"success": True, "message": "Logged in successfully!"}), 200
    else:
        return jsonify({"success": False, "message": "Invalid credentials"}), 401


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return jsonify({"message": "Logged out successfully!"}), 200


def collection_wrapper():
    global current_subreddit, currently_collecting, status
    currently_collecting = True
    with app.app_context():
        current_subreddit = Subreddit.query.filter_by(collection_done=False).first()

        while current_subreddit:
            collect_posts(current_subreddit.name)
            current_subreddit.collection_done = True
            current_subreddit.collected_posts = post_limit
            db.session.commit()
            current_subreddit = Subreddit.query.filter_by(collection_done=False).first()

    status = "Collection done"
    currently_collecting = False


def collect_posts(subreddit_name):
    global status
    subreddit = reddit.subreddit(subreddit_name)
    post_counter = 0

    for post in subreddit.hot(limit=post_limit):
        new_post = Post(
            post_id=post.id,
            title=post.title,
            content=post.selftext,
            subreddit_id=Subreddit.query.filter_by(name=subreddit_name).first().id
        )

        try:
            current_subreddit.collected_posts += 1
            db.session.add(new_post)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()

        post.comments.replace_more(limit=0)
        top_comments = sorted(post.comments, key=lambda x: x.score, reverse=True)[:5]

        for comment in top_comments:
            new_response = Response(
                response_id=comment.id,
                post_id=new_post.id,
                content=comment.body,
                score=comment.score
            )

            try:
                db.session.add(new_response)
                db.session.commit()
            except IntegrityError:
                db.session.rollback()

        post_counter += 1

        pause_time = random.uniform(0.5, 2.5)
        status = f"Saved Post {post_counter}/{post_limit} - Pause for {pause_time} seconds."
        time.sleep(pause_time)


@app.route('/')
@login_required
def home():
    return jsonify(message="Flask App with Admin User")


@app.route('/post_limit')
@login_required
def post_limit():
    return f"Post limit: {post_limit}"


@app.route('/change_post_limit/<int:new_limit>')
@login_required
def change_post_limit(new_limit):
    global post_limit
    post_limit = new_limit
    return f"Post limit changed to {new_limit}"


@app.route('/subreddit_list')
@login_required
def subreddit_list():
    subreddits = Subreddit.query.all()
    subreddit_data = [
        {
            'name': subreddit.name,
            'collected_posts': subreddit.collected_posts,
            'post_limit': post_limit
        }
        for subreddit in subreddits
    ]
    return jsonify(subreddit_data)


@app.route('/add_subreddit/<subreddit_name>')
@login_required
def add_subreddit(subreddit_name):
    check = Subreddit.query.filter_by(name=subreddit_name).first()
    if check:
        return f"Subreddit {subreddit_name} already exists"
    new_subreddit = Subreddit(name=subreddit_name)
    db.session.add(new_subreddit)
    db.session.commit()
    return f"Subreddit {subreddit_name} added"


@app.route('/start_collection')
@login_required
def start_collection():
    collection_thread = threading.Thread(target=collection_wrapper)
    collection_thread.start()
    return "Collection started"


@app.route('/status')
@login_required
def get_status():
    return jsonify({
        'status': status,
        'current_subreddit': current_subreddit.name if current_subreddit else None,
        'currently_collecting': currently_collecting,
        'post_limit': post_limit
    })


if __name__ == '__main__':
    app.run(debug=True)
