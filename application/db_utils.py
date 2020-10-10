from .models import User, Message, RevokedToken
from . import db


def get_user(username):
    """Gets a user from the database according to username."""

    user = User.query.filter_by(username=username).first()

    return user


def create_user(username, email, password):
    """Adds a new user to the database."""

    user = User(username=username, email=email)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    return username


def send_message(sender, receiver, subject, content):
    """Adds a new message to the database."""

    message = Message(sender.id, receiver.id, sender.username, receiver.username, subject, content)
    db.session.add(message)
    db.session.commit()


def get_message(msg_id, username):
    """Gets a message from the database according to id. If the given username is the receiver, marks as read."""

    message = Message.query.get(msg_id)
    user = get_user(username)

    # If the message exists in the database and matches the ID of the user, it is still readable
    if message and (message.receiver_id == user.id or message.sender_id == user.id):
        # If the user is the receiver, mark as read
        if message.receiver_name == username:
            message.read = True
            db.session.commit()

        # Format the message from an SQLAlchemy result to a dict and add the content
        formatted_message = format_message(message)
        formatted_message['Content'] = message.content

        return formatted_message

    return None


def get_all_messages(username):
    """Gets all messages for the user, sent or received."""

    user = get_user(username)
    sent_messages = user.sent_messages
    received_messages = user.received_messages
    sent_dict = {}
    received_dict = {}

    for msg in sent_messages:
        sent_dict[msg.id] = format_message(msg)

    for msg in received_messages:
        received_dict[msg.id] = format_message(msg)

    messages = {'sent': sent_dict, 'received': received_dict}

    return messages


def get_all_unread_messages(username):
    """Gets all unread messages sent to the user."""

    user = get_user(username)
    received_messages = user.received_messages
    unread_messages = {}

    for msg in received_messages:
        if msg.read is False:
            unread_messages[msg.id] = format_message(msg)

    return unread_messages


def delete_message(msg_id, username):
    """Deletes a message from the sender/receiver side. If both deleted, removes the message from the database."""

    user = get_user(username)
    message = Message.query.get(msg_id)
    result = False

    if message is None:
        return False

    if message.sender_id == user.id:
        message.sender_id = None
        result = True

    if message.receiver_id == user.id:
        message.receiver_id = None
        result = True

    if message.receiver_id is None and message.sender_id is None:
        db.session.delete(message)

    db.session.commit()

    return result


def get_token(jti):
    """Queries the database for a token according to identity."""

    token = RevokedToken.query.filter_by(jti=jti).first()

    return token


def add_token_to_db(jti):
    """Adds a revoked token to the database in order to track all invalid tokens."""

    token = RevokedToken(jti)
    db.session.add(token)
    db.session.commit()


def format_message(msg):
    """Receives an SQLAlchemy Message object and formats it into a dictionary to solve JSON serialization issues."""

    formatted_msg = {'Sender': msg.sender_name,
                     'Receiver': msg.receiver_name,
                     'Date': str(msg.sent_date),
                     'Subject': msg.subject}

    return formatted_msg
