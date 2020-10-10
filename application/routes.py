from sqlalchemy import exc
from flask import Blueprint, request, jsonify, current_app
from . import jwt
from flask_jwt_extended import (
    jwt_required, jwt_optional, get_jwt_identity, create_access_token, create_refresh_token,
    jwt_refresh_token_required, get_raw_jwt
)
import application.db_utils as db_utils

routes_bp = Blueprint('routes_bp', __name__)


@routes_bp.route('/')
def index():
    current_user = get_jwt_identity()

    if current_user:
        return f"Welcome back to the Messenger API, {current_user}!"
    else:
        return "Welcome to the Messenger API!"


@routes_bp.route('/create_user', methods=['POST'])
def create_user():
    username = request.json.get('username')
    email = request.json.get('email')
    password = request.json.get('password')

    # Check for invalid arguments
    if username is None or password is None or email is None:
        return "Missing arguments. Please provide username, password and email.", 400

    # Check if username already exists in the database
    if db_utils.get_user(username) is not None:
        return "Username taken.", 400

    db_utils.create_user(username, email, password)
    current_app.logger.info(f"A new user has been created. Username: {username}")

    return f"User created successfully! Username: {username}", 201


@routes_bp.route('/messages', methods=['GET'])
@jwt_required
def show_messages():
    username = get_jwt_identity()
    messages = db_utils.get_all_messages(username)

    return messages, 200


@routes_bp.route('/messages/unread', methods=['GET'])
@jwt_required
def show_unread_messages():
    username = get_jwt_identity()
    messages = db_utils.get_all_unread_messages(username)

    return messages, 200


@routes_bp.route('/messages/send_message', methods=['POST'])
@jwt_required
def send_message():
    current_user = get_jwt_identity()
    sender = db_utils.get_user(current_user)
    receiver_name = request.json.get('receiver')
    content = request.json.get('content')
    subject = request.json.get('subject')

    if receiver_name is None or content is None or subject is None:
        return "Missing arguments. Please provide a receiver, subject and content.", 400

    receiver = db_utils.get_user(receiver_name)

    if not receiver:
        return "Receiver does not exist.", 400

    try:
        db_utils.send_message(sender, receiver, subject, content)
    except exc.IntegrityError as e:
        return jsonify(e.orig.args), 400

    current_app.logger.info("A new message has been sent successfully.")

    return "Message sent successfully!", 201


@routes_bp.route('/messages/read_message', methods=['GET'])
@jwt_required
def read_message():
    msg_id = request.json.get('id')

    if not msg_id:
        return "Missing message id.", 400

    current_user = get_jwt_identity()
    msg = db_utils.get_message(msg_id, current_user)

    if msg is None:
        return "Message has been deleted or id is invalid.", 200

    return msg, 201


@routes_bp.route('/messages/delete_message', methods=['DELETE'])
@jwt_required
def delete_message():
    msg_id = request.json.get('id')

    if not msg_id:
        return "Missing message id.", 400

    current_user = get_jwt_identity()
    result = db_utils.delete_message(msg_id, current_user)

    if result:
        current_app.logger.info(f"Message #{msg_id} has been deleted.")

        return "Message deleted successfully.", 200

    else:
        return "Message has already been deleted or ID is invalid.", 200


@routes_bp.route('/login', methods=['POST'])
@jwt_optional
def login():
    current_user = get_jwt_identity()
    jti = get_raw_jwt()

    # Check for an existing token in the request
    if jti and check_if_token_in_blacklist(jti):
        return f"Expired token in request. Please provide a fresh token.", 200

    # If token exists and is fresh, user is already logged in
    if current_user:
        return f"You are already logged in as {current_user}.", 200

    try:
        username = request.json.get('username')
        password = request.json.get('password')
    except AttributeError:
        return "Username or password are missing in the request.", 400

    user = db_utils.get_user(username)

    if user is None or password is None:
        return "Please provide a username and password to log in.", 400

    if not user.check_password(password):
        return "Incorrect password.", 400

    access_token = create_access_token(identity=username)
    refresh_token = create_refresh_token(identity=username)
    current_app.logger.info(f"User {username} has logged into the system.")

    return jsonify(access_token=access_token, refresh_token=refresh_token), 200


@routes_bp.route('/refresh', methods=['POST'])
@jwt_refresh_token_required
def refresh():
    current_user = get_jwt_identity()
    access_token = create_access_token(identity=current_user)

    return jsonify(access_token=access_token), 200


@routes_bp.route('/logout', methods=['DELETE'])
@jwt_required
def logout():
    current_user = get_jwt_identity()
    jti = get_raw_jwt()['jti']
    db_utils.add_token_to_db(jti)
    current_app.logger.info(f"User {current_user} has logged out.")

    return "Logged out successfully - access token has been revoked.", 200


@jwt.token_in_blacklist_loader
def check_if_token_in_blacklist(check_token):
    jti = check_token['jti']
    token = db_utils.get_token(jti)

    return token.is_jti_blacklisted(jti)
