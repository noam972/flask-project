from flask import Flask, request, jsonify,make_response
from flask_sqlalchemy import SQLAlchemy
#from flask_marshmallow import Marshmallow
import pymysql
from sqlalchemy import or_
from datetime import datetime
from functools import wraps

DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'


app = Flask(__name__)
pymysql.install_as_MySQLdb()  #to convert from pymysql to MYSQL DB.
app.config['SECRET_KEY'] = 'secretkey'  #limits the clint accesses to the back
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://b135a625f099ae:62853ebb@eu-cdbr-west-01.cleardb.com'\
                                        '/heroku_b4f91ef857282d3?'


db = SQLAlchemy(app)


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender = db.Column(db.String(80), nullable=False)
    receiver = db.Column(db.String(80), nullable=False)
    message = db.Column(db.String(300), nullable=False)
    subject = db.Column(db.String(80), nullable=False)
    creation_date = db.Column(db.DateTime, nullable=False)
    unread = db.Column(db.Boolean, unique=False, default=True)

    def to_dict(self):
        return {
            "sender": self.sender,
            "receiver": self.receiver,
            "subject": self.subject,
            "messages": self.message,
            "creation_date": self.creation_date.strftime(DATETIME_FORMAT)
        }


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(8), nullable=False)

#db.create_all()
#db.session.commit()


def auth_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not (auth and auth.username and auth.password):
            return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm="Login required."'})

        user = User.query.filter_by(username=auth.username).first()
        if not user:
            return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm="Login required."'})

        if not user.password == auth.password:
            return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm="Login required."'})

        return f(*args, **kwargs)
    return decorated


def get_all_msgs(read):
    username = request.authorization.username
    if read:
        all_msg = Message.query.filter_by(receiver=username)
    else:
        all_msg = Message.query.filter_by(receiver=username, unread=read)

    messages = []
    for msg in all_msg:
        messages.append(msg.to_dict())
        msg.unread = False
        db.session.commit()
    return messages


@app.route('/user/sign_up', methods=['POST'])
def sign_up():
    with app.app_context():
        data = request.get_json()
        username = data['username']
        password = str(data['password'])

        if len(username) > 80:
            return jsonify({'message': 'username {} is too long, please select username up to 20 characters.'.format(username)})
        if len(password) > 8:
            return jsonify({'message': 'password is too long, please select password up to 8 characters.'})

        name = User.query.filter_by(username=username).first()
        if name:
            return 'username already taken!'
        user = User(username=username, password=password)
        db.session.add(user)
        db.session.commit()
        return jsonify({'message': 'Welcome {}'.format(username)})


@app.route('/user/login', methods=['GET'])
@auth_required
def login():
    return 'welcome back!'


@app.route('/msg/write_msg', methods=['POST'])
@auth_required
def write_msg():
    with app.app_context():
        data = request.get_json()
        sender = request.authorization.username
        receiver = data['receiver']
        message = data['message']
        subject = data['subject']
        creation_date = datetime.strptime(data['creation_date'], DATETIME_FORMAT)
        msg = Message(sender=sender, receiver=receiver, message=message, subject=subject, creation_date=creation_date)
        db.session.add(msg)
        db.session.commit()
        return 'message received successfully'


@app.route('/msg/get_all_messages', methods=['GET'])
@auth_required
def get_all_msg():
    messages = get_all_msgs(True)
    return jsonify({"messages": messages})


@app.route('/msg/get_all_unread_messages', methods=['GET'])
@auth_required
def get_all_unread_messages():
    messages = get_all_msgs(False)
    if not  messages.first():
        return 'all messages were read!'
    return jsonify({"messages": messages})


@app.route('/msg/read_msg', methods=['GET'])
@auth_required
def read_msg():
    username = request.authorization.username
    msg = Message.query.filter_by(receiver=username,unread=True).first()
    if not msg:
        return 'all messages were read!'
    msg.unread = False
    db.session.commit()
    return jsonify(msg.to_dict)


@app.route('/msg/delete_msg', methods=['GET'])
@auth_required
def delete_msg():
    username = request.authorization.username
    msg = Message.query.filter(or_(Message.sender == username, Message.receiver == username)).first()
    db.session.delete(msg)
    db.session.commit()
    return 'message deleted!'


@app.route('/')
def hello_world():
    return 'Hello World!'


if __name__ == '__main__':  #check is its the main file
    app.run()
