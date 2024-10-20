import uuid
from sqlalchemy.dialects.postgresql import UUID
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import UserMixin

db = SQLAlchemy()
bcrypt = Bcrypt()


class User(db.Model, UserMixin):
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f"User('{self.username}', 'Admin: {self.is_admin}')"


class Subreddit(db.Model):
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = db.Column(db.String(20), unique=True, nullable=False)
    collected_posts = db.Column(db.Integer, default=0)
    collection_done = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f"Subreddit('{self.name}')"


class Post(db.Model):
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    post_id = db.Column(db.String(10), unique=True, nullable=False)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    subreddit_id = db.Column(UUID(as_uuid=True), db.ForeignKey('subreddit.id'), nullable=False)

    def __repr__(self):
        return f"Post('{self.title}', '{self.subreddit}')"


class Response(db.Model):
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    response_id = db.Column(db.String(10), unique=True, nullable=False)
    post_id = db.Column(UUID(as_uuid=True), db.ForeignKey('post.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    score = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f"Response('{self.content}', '{self.score}')"


def create_admin_user():
    hashed_password = bcrypt.generate_password_hash('deep_learning_is_cool').decode('utf-8')
    admin = User(username='admin', password=hashed_password, is_admin=True)
    db.session.add(admin)
    db.session.commit()
