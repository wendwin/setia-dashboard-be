from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

# class Type(db.Model):
#     __tablename__ = 'types'

#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(10), nullable=False, unique=True)

#     topics = db.relationship('Topic', backref='type', cascade='all, delete-orphan', lazy=True)

# class Topic(db.Model):
#     __tablename__ = 'topics'

#     id = db.Column(db.Integer, primary_key=True)
#     topic_type= db.Column(db.String(1), nullable=False)
#     sentiment = db.Column(db.Enum('positif', 'negatif', name='sentiment_enum'), nullable=False)
#     # type_id = db.Column(db.Integer, db.ForeignKey('types.id'), nullable=False)
#     title = db.Column(db.String(100), nullable=False)

#     suggestions = db.relationship('Suggestion', backref='topic', cascade='all, delete-orphan', lazy=True)

# class Suggestion(db.Model):
#     __tablename__ = 'suggestions'

#     id = db.Column(db.Integer, primary_key=True)
#     topic_id = db.Column(db.Integer, db.ForeignKey('topics.id'), nullable=False)
#     content = db.Column(db.Text, nullable=False)
#     created_at = db.Column(db.DateTime, default=datetime.now)
#     updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)


class TypeTopic(db.Model):
    __tablename__ = 'types'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(10), nullable=False, unique=True)

    summaries = db.relationship('Summary', backref='type', cascade='all, delete-orphan', lazy=True)


class Topic(db.Model):
    __tablename__ = 'topics'

    id = db.Column(db.Integer, primary_key=True)
    topic_type = db.Column(
        db.String(10),
        db.ForeignKey('types.name'),
        nullable=False
    )
    sentiment = db.Column(
        db.Enum('positif', 'negatif', name='sentiment_enum'),
        nullable=False
    )
    title = db.Column(db.String(100), nullable=False)

    # Relationships
    suggestions = db.relationship('Suggestion', backref='topic', cascade='all, delete-orphan', lazy=True)
    type = db.relationship('TypeTopic', backref=db.backref('topics', lazy=True), foreign_keys=[topic_type])


class Suggestion(db.Model):
    __tablename__ = 'suggestions'

    id = db.Column(db.Integer, primary_key=True)
    topic_id = db.Column(db.Integer, db.ForeignKey('topics.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Summary(db.Model):
    __tablename__ = 'summaries'

    id = db.Column(db.Integer, primary_key=True)
    type_name = db.Column(db.String(10), db.ForeignKey('types.name'), nullable=False)
    sentiment = db.Column(
        db.Enum('positif', 'negatif', name='summary_sentiment_enum'),
        nullable=False
    )
    content = db.Column(db.Text, nullable=False)

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)

    def getEmail(self):
        return self.email

    def getPassword(self):
        return self.password

    # Method untuk set password (hash)
    def set_password(self, password):
        self.password = generate_password_hash(password)

    # Method untuk verifikasi password
    def check_password(self, password):
        return check_password_hash(self.password, password)

    def __repr__(self):
        return f'<User {self.username}>'