from app import db

from flask_login import UserMixin

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False, unique=True)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password_hash = db.Column(db.String(256), nullable=False, unique=True)
    is_active = db.Column(db.Boolean, default=True)

    posts = db.relationship(
        'Post',
        backref = 'author',
        lazy = True
    )

    comments = db.relationship(
        'Comment',
        backref = 'author',
        lazy = True
    )

    def __str__(self):
        return self.username


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False, unique=True)
    content = db.Column(db.String(300), nullable=False, unique=True)
    created_at = db.Column(db.TIMESTAMP, nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    comments = db.relationship(
        'Comment',
        backref = 'author',
        lazy = True
    )

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(200))
    created_at = db.Column(db.TIMESTAMP, nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)


    
