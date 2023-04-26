import flask
from database import *
from flask import jsonify, request
from sqlalchemy import delete

blueprint = flask.Blueprint(
    'api',
    __name__,
)


@blueprint.route('/api/users/get')
def get_users():
    with Session() as session:
        return jsonify([item.to_dict(rules=("-hashed_password",)) for item in session.query(User).all()])


@blueprint.route('/api/users/get/<user_id>')
def get_user(user_id):
    with Session() as session:
        user = session.query(User).filter(User.id == user_id).first()
    return jsonify(user.to_dict(rules=("-hashed_password",)))


@blueprint.route('/api/users/add', methods=['POST'])
def create_user():
    with Session() as session:
        user = User(**request.json)
        session.add(user)
        session.commit()
    return jsonify({'success': 'OK'})


@blueprint.route("/api/users/delete/<user_id>")
def delete_user(user_id):
    with Session() as session:
        session.execute(delete(User).where(User.id == user_id))
        session.commit()
    return jsonify({'success': 'OK'})


@blueprint.route('/api/categories/get')
def get_categories():
    with Session() as session:
        return jsonify([item.to_dict() for item in session.query(Category).all()])


@blueprint.route('/api/categories/get/<category_id>')
def get_category(category_id):
    with Session() as session:
        category = session.query(Category).filter(Category.id == category_id).first()
    return jsonify(category.to_dict())


@blueprint.route('/api/categories/add', methods=['POST'])
def create_category():
    with Session() as session:
        category = Category(**request.json)
        session.add(category)
        session.commit()
    return jsonify({'success': 'OK'})


@blueprint.route("/api/categories/delete/<category_id>")
def delete_category(category_id):
    with Session() as session:
        session.execute(delete(Category).where(Category.id == category_id))
        session.commit()
    return jsonify({'success': 'OK'})


@blueprint.route('/api/forums/get')
def get_forums():
    with Session() as session:
        return jsonify([item.to_dict(rules=("-author.hashed_password",)) for item in session.query(Forum).all()])


@blueprint.route('/api/forums/get/<forum_id>')
def get_forum(forum_id):
    with Session() as session:
        forum = session.query(Forum).filter(Forum.id == forum_id).first()
    return jsonify(forum.to_dict(rules=("-author.hashed_password",)))


@blueprint.route('/api/forums/add', methods=['POST'])
def create_forum():
    with Session() as session:
        forum = Forum(**request.json)
        session.add(forum)
        session.commit()
    return jsonify({'success': 'OK'})


@blueprint.route("/api/forums/delete/<forum_id>")
def delete_forum(forum_id):
    with Session() as session:
        session.execute(delete(Forum).where(Forum.id == forum_id))
        session.commit()
    return jsonify({'success': 'OK'})


@blueprint.route('/api/messages/get')
def get_messages():
    with Session() as session:
        return jsonify([item.to_dict(rules=("-author.hashed_password", "-forum.author")) for item in session.query(Message).all()])


@blueprint.route('/api/messages/get/<message_id>')
def get_message(message_id):
    with Session() as session:
        message = session.query(Message).filter(Message.id == message_id).first()
    return jsonify(message.to_dict(rules=("-author.hashed_password", "-forum.author")))


@blueprint.route('/api/messages/add', methods=['POST'])
def create_message():
    with Session() as session:
        message = Message(**request.json)
        session.add(message)
        session.commit()
    return jsonify({'success': 'OK'})


@blueprint.route("/api/messages/delete/<message_id>")
def delete_message(message_id):
    with Session() as session:
        session.execute(delete(Message).where(Message.id == message_id))
        session.commit()
    return jsonify({'success': 'OK'})
