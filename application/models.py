from application import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash


class User(db.Model):
    """A user model with a relationship to the Messages table for sent and received messages per user."""
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), index=True, unique=True)
    email = db.Column(db.String(100), index=True, unique=True)
    pw_hash = db.Column(db.String())

    sent_messages = db.relationship("Message", primaryjoin="User.id==Message.sender_id", backref="sender")
    received_messages = db.relationship("Message", primaryjoin="User.id==Message.receiver_id", backref="receiver")

    def __repr__(self):
        return f'User: {self.username}, ID: {self.id}'

    def set_password(self, password):
        self.pw_hash = generate_password_hash(str(password))

    def check_password(self, password):
        return check_password_hash(self.pw_hash, str(password))


class Message(db.Model):
    """
    A message model with a relationship with the Users tables for sender and receiver.
    Both sides can access the message and read it. When one side deletes a message, the respective id becomes null.
    If both sides delete the message, it is deleted from the database.
    """
    __tablename__ = "messages"

    id = db.Column(db.Integer, primary_key=True)
    subject = db.Column(db.String(50))
    content = db.Column(db.String(250))
    sent_date = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    sender_id = db.Column(db.Integer, db.ForeignKey(User.id), nullable=True)
    receiver_id = db.Column(db.Integer, db.ForeignKey(User.id), nullable=True)
    sender_name = db.Column(db.String(30))
    receiver_name = db.Column(db.String(30))
    read = db.Column(db.Boolean, default=False)

    __table_args__ = (
        db.CheckConstraint(sender_id != receiver_id),
    )

    def __init__(self, sender_id, receiver_id, sender, receiver, subject, content):
        self.sender_id = sender_id
        self.receiver_id = receiver_id
        self.sender_name = sender
        self.receiver_name = receiver
        self.subject = subject
        self.content = content

    def __repr__(self):
        return f'Sender: {self.sender_name}, Receiver: {self.receiver_name}, ' \
               f'Date Sent: {self.sent_date}, Subject: {self.subject}'


class RevokedToken(db.Model):
    """A model for revoked/invalid tokens."""
    __tablename__ = 'revoked_tokens'

    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String(120))

    def __init__(self, jti):
        self.jti = jti

    @classmethod
    def is_jti_blacklisted(cls, jti):
        query = cls.query.filter_by(jti=jti).first()

        return bool(query)
