#!/usr/bin/python
# -*- coding: UTF-8 -*-
from werkzeug.security import generate_password_hash,check_password_hash
from . import db
from . import login_manager
from datetime import datetime
import hashlib
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from markdown import markdown
import bleach
from flask import current_app, request, url_for
from flask_login import UserMixin, AnonymousUserMixin

class Permission:
    LIKE = 0x01
    COMMENT = 0x02
    WRITE_ARTICLES = 0x04
    MODERATE_COMMENTS = 0x08
    ADMINISTER = 0x80


class Like(db.Model):
    __tablename__='likes'
    liker_id=db.Column(db.Integer,db.ForeignKey('users.id'),primary_key=True)
    liked_id=db.Column(db.Integer,db.ForeignKey('url_resources.id'),primary_key=True)
    like_date=db.Column(db.DateTime,default=datetime.utcnow)

class User(UserMixin,db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    register_date=db.Column(db.DateTime(),default=datetime.utcnow)

    liker = db.relationship('Like',
                               foreign_keys=[Like.liker_id],
                               backref=db.backref('liker', lazy='joined'),
                               lazy='dynamic',
                               cascade='all, delete-orphan')

    def to_json(self):
        json_user = {
            'url': url_for('api.get_user', id=self.id, _external=True),
            'username': self.username,
            #'resources': url_for('api.get_user_resources', id=self.id, _external=True),
            'register_date': self.register_date
        }
        return json_user


    def like(self, resource):
        if not self.is_liking(resource):
            f = Like(liker=self, liked=resource)
            db.session.add(f)

    def unlike(self, resource):
        f = resource.liked.filter_by(liked_id=resource.id).first()
        if f:
            db.session.delete(f)

    def is_liking(self, resource):
        return self.liker.filter_by(
            liked_id=resource.id).first() is not None



    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @property
    def liked_Resources(self):
        return UrlResource.query.join(Like, Like.liked_id == UrlResource.id) \
            .filter(Like.liker_id == self.id)

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    @staticmethod
    def generate_fake(count=10):
        from sqlalchemy.exc import IntegrityError
        from random import seed
        import forgery_py

        seed()
        for i in range(count):
            u = User(
                username=forgery_py.internet.user_name(True),
                password=forgery_py.lorem_ipsum.word())
            db.session.add(u)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()

class UrlResource(db.Model):
    __tablename__='url_resources'
    id=db.Column(db.Integer,primary_key=True)
    title=db.Column(db.String(128))
    theme=db.Column(db.String(128))
    url = db.Column(db.String(128))
    like_num=db.Column(db.Integer,default=0)
    author_id=db.Column(db.Integer,index=True)
    post_date=db.Column(db.DateTime)

    liked = db.relationship('Like',
                           foreign_keys=[Like.liked_id],
                           backref=db.backref('liked', lazy='joined'),
                           lazy='dynamic',
                           cascade='all, delete-orphan')

    def to_json(self):
        json_resources = {
            'url': url_for('api.get_resource', id=self.id, _external=True),
            'title': self.title,
            'theme': self.theme,
            'resource_url': self.url,
            # 'author': url_for('api.get_user', id=self.author_id,
            #                   _external=True),
            'like_num' : self.like_num,
            'post_date': self.post_date,
        }
        return json_resources


    def is_liked_by(self, user):
        return self.liked.filter_by(
            liked_id=user.id).first() is not None

class Alembic(db.Model):
    __tablename__ = 'alembic_version'
    version_num = db.Column(db.String(32), primary_key=True, nullable=False)

    @staticmethod
    def clear_A():
        for a in Alembic.query.all():
            db.session.delete(a)
        db.session.commit()


class Files(db.Model):
    __tablename__='Files'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128))
    url = db.Column(db.String(128),unique=True)
    describe=db.Column(db.String(128),default='作者没什么要说的...')
    format = db.Column(db.String(128))
    author_id = db.Column(db.Integer, index=True)
    is_private=db.Column(db.Boolean)
    download_num = db.Column(db.Integer, default=0)
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

