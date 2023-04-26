import os
from ast import literal_eval

from flask import Flask, redirect, render_template, request
from flask_login import current_user, login_required, login_user, LoginManager, logout_user
from werkzeug.security import generate_password_hash

from api import v1
from database import *
from forms import *

app = Flask(__name__)
app.config["SECRET_KEY"] = "123"
app.json.ensure_ascii = False
app.register_blueprint(v1.blueprint)
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    with Session() as session:
        return session.query(User).filter(User.id == user_id).first()


@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        with Session() as session:
            form.hashed_password.data = generate_password_hash(form.hashed_password.data)
            data = {k: v for k, v in form.data.items() if v and k not in ("submit", "csrf_token")}
            if "icon" in data:
                number = len(os.listdir("static/img"))
                with open(f"static/img/{number}.png", "wb") as file:
                    file.write(data["icon"].read())
                data["icon"] = f"{number}.png"
            session.add(User(**data))
            session.commit()
        return redirect("/login")
    return render_template("register.html", form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        with Session() as session:
            user = session.query(User).filter(User.nickname == form.nickname.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=True)
            return redirect("/")
        return redirect("/login")
    return render_template("login.html", form=form)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route("/like/<forum_id>")
@login_required
def like(forum_id):
    with Session() as session:
        forum = session.query(Forum).filter(Forum.id == forum_id).first()
        forum.likes = str(literal_eval(forum.likes) | {current_user.id})
        forum.dislikes = str(literal_eval(forum.dislikes) - {current_user.id})
        session.commit()
    return redirect("/")


@app.route("/dislike/<forum_id>")
@login_required
def dislike(forum_id):
    with Session() as session:
        forum = session.query(Forum).filter(Forum.id == forum_id).first()
        forum.dislikes = str(literal_eval(forum.dislikes) | {current_user.id})
        forum.likes = str(literal_eval(forum.likes) - {current_user.id})
        session.commit()
    return redirect("/")


@app.route("/")
def index_page():
    with Session() as session:
        categories_list = session.query(Category).all()
    return render_template("index.html", categories_list=categories_list)


@app.route("/forum/<forum_id>", methods=["GET", "POST"])
def forum_page(forum_id):
    with Session() as session:
        forum = session.query(Forum).filter(Forum.id == forum_id).first()
    form = MessageForm()
    if form.validate_on_submit():
        with Session() as session:
            session.add(Message(
                text=form.text.data,
                author_id=current_user.id,
                forum_id=forum_id
            ))
            session.commit()
        return redirect(request.referrer)
    page = int(request.args.get("page", 1))
    return render_template("forum.html", forum=forum, messages=[forum.messages[0], *forum.messages[(page - 1) * 20 + 1:page * 20 + 1]],
                           total_pages=len(forum.messages) // 20 + bool(len(forum.messages) % 20), form=form)


@app.route("/account/<user_id>")
def account_page(user_id):
    with Session() as session:
        user = session.query(User).filter(User.id == user_id).first()
    if not user:
        return "Пользователь не существует"
    return render_template("account.html", user=user)

@login_required
@app.route("/new_forum/<category_id>", methods=["GET", "POST"])
def new_forum(category_id):
    form = ForumForm()
    form.category_id.data = category_id
    form.author_id.data = current_user.id
    if form.validate_on_submit():
        with Session() as session:
            if form.icon.data:
                number = len(os.listdir("static/img"))
                with open(f"static/img/{number}.png", "wb") as file:
                    file.write(form.data.icon.read())
                form.icon.data = f"{number}.png"
            else:
                form.icon.data = "unknown.png"
            forum = Forum(
                category_id=form.category_id.data,
                author_id=form.author_id.data,
                title=form.title.data,
                icon=form.icon.data
            )
            session.add(forum)
            session.commit()
            session.refresh(forum)
            session.add(Message(
                author_id=form.author_id.data,
                forum_id=forum.id,
                text=form.first_message.data
            ))
            session.commit()
        return redirect("/")
    return render_template("new_forum.html", form=form)

@login_required
@app.route("/new_category", methods=["GET", "POST"])
def new_category():
    form = CategoryForm()
    if form.validate_on_submit():
        with Session() as session:
            data = {k: v for k, v in form.data.items() if v and k not in ("submit", "csrf_token")}
            session.add(Category(**data))
            session.commit()
        return redirect("/")
    return render_template("new_category.html", form=form)


if __name__ == "__main__":
    app.run(port=8080, host="127.0.0.1")
