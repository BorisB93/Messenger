from application import db, create_app, db_utils
from application.models import User, Message

app = create_app("dev")


with app.app_context():
    users = User.query.all()
    for user in users:
        print(user)
        print(user.sent_messages)
        print(user.received_messages)

    # messages = Message.query.all()
    # for msg in messages:
    #     print(msg)
        # print(msg.receiver_id)

    # db.session.commit()


    # unread_msgs = db_utils.get_all_unread_messages("jane")
    # msgs = db_utils.get_all_messages("jake")
    # print(msgs)



