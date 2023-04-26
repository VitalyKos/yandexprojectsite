__all__ = ["Category", "Forum", "Message", "User", "Session"]

import datetime
import random
import time
from ast import literal_eval
from functools import cached_property

import markdown
import sqlalchemy
from flask_login import current_user, UserMixin
from sqlalchemy import orm
from sqlalchemy.orm import relationship
from sqlalchemy_serializer import SerializerMixin
from werkzeug.security import check_password_hash, generate_password_hash

BASE = orm.declarative_base()

user_colors = {
    False: "user-link",
    True: "admin-link",
}


class User(BASE, UserMixin, SerializerMixin):
    __tablename__ = "users"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    administrator = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
    nickname = sqlalchemy.Column(sqlalchemy.String, unique=True)
    email = sqlalchemy.Column(sqlalchemy.String, unique=True)
    born_at = sqlalchemy.Column(sqlalchemy.Date)
    hashed_password = sqlalchemy.Column(sqlalchemy.String)
    city = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    registered_at = sqlalchemy.Column(sqlalchemy.DateTime(timezone=True), default=datetime.datetime.now)
    status = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    icon = sqlalchemy.Column(sqlalchemy.String, default="unknown.png")

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)

    @cached_property
    def messages_count(self):
        with Session() as session:
            return session.query(Message).filter(Message.author_id == self.id).count()

    def __str__(self):
        return f'<a href="/account/{self.id}" class="{user_colors[self.administrator]}">{self.nickname}</a>'


class Category(BASE, SerializerMixin):
    __tablename__ = "categories"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    title = sqlalchemy.Column(sqlalchemy.String, unique=True)

    @cached_property
    def forums(self):
        with Session() as session:
            return session.query(Forum).filter(Forum.category_id == self.id).all()


class Forum(BASE, SerializerMixin):
    __tablename__ = "forums"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    category_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("categories.id"))
    author_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))
    title = sqlalchemy.Column(sqlalchemy.String)
    icon = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    created_at = sqlalchemy.Column(sqlalchemy.DateTime(timezone=True), default=datetime.datetime.now)
    closed_at = sqlalchemy.Column(sqlalchemy.DateTime(timezone=True), nullable=True)
    likes = sqlalchemy.Column(sqlalchemy.String, default="set()")
    dislikes = sqlalchemy.Column(sqlalchemy.String, default="set()")

    category = relationship("Category", foreign_keys=[category_id], lazy='subquery')
    author = relationship("User", foreign_keys=[author_id], lazy='subquery')

    @property
    def liked(self):
        return current_user.id in literal_eval(self.likes)

    @property
    def disliked(self):
        return current_user.id in literal_eval(self.dislikes)

    @cached_property
    def reputation(self):
        return len(literal_eval(self.likes)) - len(literal_eval(self.dislikes))

    @cached_property
    def messages(self):
        with Session() as session:
            return session.query(Message).filter(Message.forum_id == self.id).all()


class Message(BASE, SerializerMixin):
    __tablename__ = "messages"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    author_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))
    forum_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("forums.id"))
    text = sqlalchemy.Column(sqlalchemy.String)
    sent_at = sqlalchemy.Column(sqlalchemy.DateTime(timezone=True), default=datetime.datetime.now)
    edited_at = sqlalchemy.Column(sqlalchemy.DateTime(timezone=True), onupdate=datetime.datetime.now)

    author = relationship("User", foreign_keys=[author_id], lazy='subquery')
    forum = relationship("Forum", foreign_keys=[forum_id], lazy='subquery')

    @cached_property
    def markdown_text(self):
        return markdown.markdown(self.text, extensions=["nl2br", "fenced_code", "codehilite"])

    def decl(self, number, titles):
        if 4 < number % 100 < 20:
            return f"{number} {titles[2]} назад"
        if number % 10 == 1:
            return f"{number} {titles[0]} назад"
        if number % 10 < 5:
            return f"{number} {titles[1]} назад"
        return f"{number} {titles[2]} назад"

    def relative_format_time(self):
        diff = datetime.datetime.now() - self.sent_at
        if diff.days == 0:
            hours, minutes = divmod(diff.seconds, 3600)
            minutes, seconds = divmod(minutes, 60)
            if hours:
                return "сегодня, " + self.decl(hours, ["час", "часа", "часов"])
            if minutes:
                return self.decl(minutes, ["минута", "минуты", "минут"])
            return self.decl(seconds, ["секунда", "секунды", "секунд"])
        elif diff.days < 7:
            if diff.days == 1:
                return "вчера"
            return self.decl(diff.days, ["день", "дня", "дней"])
        elif diff.days < 30:
            return self.decl(diff.days // 7, ["неделя", "недели", "недель"])
        elif diff.days < 365:
            return self.decl(diff.days // 30, ["месяц", "месяца", "месяцев"])
        return self.decl(diff.days // 365, ["год", "года", "лет"])


engine = sqlalchemy.create_engine(f"sqlite:///database.sqlite?check_same_thread=False")
BASE.metadata.create_all(engine, checkfirst=True)
Session = orm.sessionmaker(bind=engine, expire_on_commit=False)
