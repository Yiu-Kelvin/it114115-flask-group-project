from threading import Thread
from flask import render_template
from flask_mail import Message
from app import app, mail


def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)


def send_email(subject, sender, recipients, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.html = html_body
    Thread(target=send_async_email, args=(app, msg)).start()

def send_to_followed(followed_users, post_id):
    with mail.connect() as conn:
        for user in followed_users:
            subject = "[StackOverflow] Someone answered a question which you followed"
            msg = Message(recipients=[user.email],
                        html=render_template('email/answered_notification.html.j2',
                                         user=user, post_id=post_id),
                        subject=subject,
                        sender=app.config['ADMINS'][0])
            print(f"sending to {user.email}")
            conn.send(msg)

def send_answered_notification(followed_users,user, post_id):
    send_to_followed(followed_users, post_id)
    send_email('[StackOverflow] Someone answered your question',
               sender=app.config['ADMINS'][0],
               recipients=[user.email],
               html_body=render_template('email/answered_notification.html.j2',
                                         user=user, post_id=post_id, author=True))

def send_password_reset_email(user):
    token = user.get_reset_password_token()
    send_email('[StackOverflow] Reset Your Password',
               sender=app.config['ADMINS'][0],
               recipients=[user.email],
               html_body=render_template('email/reset_password.html.j2',
                                         user=user, token=token))
