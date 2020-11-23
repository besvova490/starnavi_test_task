from app import db, models_base_class
from datetime import datetime
from passlib.hash import sha256_crypt
from sqlalchemy.orm import load_only


class User(db.Model, models_base_class.BaseModelsClass):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(), unique=True)
    password = db.Column(db.String())
    last_online = db.Column(db.DateTime)
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    likes = db.relationship('Like', backref='user', lazy='dynamic')

    @classmethod
    def signup(cls, data):
        return User(**data).to_dict()

    @classmethod
    def login(cls, login_data):
        user = User.query.filter_by(username=login_data['username']).first()
        if user.check_password_hash(login_data['password']):
            return user
        return False

    def __init__(self, username, password):
        self.username = username
        self.password = sha256_crypt.hash(password)
        db.session.add(self)
        db.session.commit()

    def check_password_hash(self, password):
        return sha256_crypt.verify(password, self.password)

    def to_dict(self):
        return dict(id=self.id, username=self.username, last_oline=self.last_online, total_posts=self.posts.count(),
                    total_likes=self.likes.count(), liked_posts=self.likes.with_entities(Post.title))

    def create_post(self, title, context):
        post = Post(title, context, self)
        db.session.add(post)
        db.session.commit()

    def like_post(self, post):
        like = Like(self, post)
        db.session.add(like)
        db.session.commit()

    def unlike_post(self, post):
        like = Like.query.filter_by(user=self, post=post)
        db.session.delete(like)
        db.session.commit()

    def __repr__(self):
        return f'<User: {self.username}>'


class Post(db.Model, models_base_class.BaseModelsClass):
    __tablename__ = 'posts'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String())
    context = db.Column(db.String())
    posted_date = db.Column(db.DateTime())
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    likes = db.relationship('Like', backref='post', lazy='dynamic')

    def __init__(self, title, context, author):
        self.title = title
        self.context = context
        self.author = author

    def to_dict(self):
        return dict(id=self.id, title=self.title, context=self.context, author=self.author.username, likes=self.likes.count())

    def __repr__(self):
        return f'<Post: {self.title}>'


class Like(db.Model):
    __tablename__ = 'likes'

    id = db.Column(db.Integer, primary_key=True)
    like_date = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))

    def __init__(self, user, post):
        self.user = user
        self.post = post
        db.session.add(self)
        db.session.commit()

    def to_dict(self):
        return dict(like_date=self.like_date, user=self.user.username, post=self.post.title)

    @classmethod
    def get_global_analitics(cls, date_from, date_to):
        date_from = datetime.strptime(date_from, '%Y-%m-%d')
        date_to = datetime.strptime(date_to, '%Y-%m-%d')
        likes = cls.query.filter(Like.like_date > date_from, Like.like_date < date_to)
        users = set(like.user for like in likes)
        posts = set(like.post for like in likes)
        users_total_like = [{'username': user.username, 'total_likes': likes.filter_by(user=user).count()} for user in users]
        posts_total_like = [{'title': post.title, 'total_likes': likes.filter_by(post=post).count()} for post in posts]
        return {'users_analitics': users_total_like, 'posts_analitics': posts_total_like, 'date_from': date_from, 'date_to': date_to}
