
from .transporte import app, db, mail

from flask import flash, Markup, url_for

from flask_login import UserMixin
from flask_mail import Message

from itsdangerous import URLSafeTimedSerializer as Serializer
from itsdangerous import BadSignature, SignatureExpired


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(256), index=True, unique=True)
    role = db.Column(db.String(64), default='user')
    transports = db.relationship('Transport', backref='user', lazy='dynamic')

    def create_token(self):
        s = Serializer(app.config['SECRET_KEY'])
        token = s.dumps({'id': self.id})

        if app.config['DEBUG']:
            flash(
                Markup('<b>DEBUG:</b> <a href={url}>{url}</a>'.format(
                    url=url_for('login_with_token', token=token, _external=True))),
                'warning')
            return

        # send login email
        msg = Message('Ohai!', recipients=[self.login])
        msg.body = 'Here is your login link: {}'.format(url_for('login_with_token', token=token, _external=True))

        mail.send(msg)

    @staticmethod
    def verify_login_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            data = s.loads(token, max_age=10*60)
        except SignatureExpired:
            # valid token, but expired
            return None
        except BadSignature:
            # invalid token
            return None
        return User.query.get(data['id'])

    def __repr__(self):
        return '<User {}>'.format(self.login)


class Transport(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ticket_id = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    organizer = db.Column(db.String(256), nullable=False)
    needs_organization = db.Column(db.Boolean, default=False, nullable=False)
    location_from = db.Column(db.Text, nullable=False)
    location_to = db.Column(db.Text, nullable=False)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.Time)
    vehicle = db.Column(db.String(32), nullable=False)
    goods = db.Column(db.Text, nullable=False)
    vehicle_owner = db.Column(db.String(256))
    driver_contact = db.Column(db.Text)
    orga_contact = db.Column(db.Text, nullable=False)
    comment = db.Column(db.Text)
    done = db.Column(db.Boolean, default=False, nullable=False)
    cancelled = db.Column(db.Boolean, default=False, nullable=False)
    files = db.relationship('File', backref='transport', lazy='dynamic')

    def __repr__(self):
        return '<Transport {}>'.format(self.id)


class File(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    transport_id = db.Column(db.Integer, db.ForeignKey('transport.id'), nullable=False)
    name = db.Column(db.String(256), nullable=False)
    path = db.Column(db.String(256), nullable=False)

    def __repr__(self):
        return '<File {}>'.format(self.path)