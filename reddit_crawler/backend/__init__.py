from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from reddit_crawler.backend.config import Config
from reddit_crawler.backend.models import User, create_admin_user

db = SQLAlchemy()
bcrypt = Bcrypt()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    bcrypt.init_app(app)

    with app.app_context():
        db.create_all()
        if not User.query.filter_by(username='admin').first():
            create_admin_user()

    return app
