from modicoin import db, login_manager, app
from flask_login import UserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

default_balance = 50


@login_manager.user_loader
def load_user(user_id):
	return User.query.get(int(user_id))


class User(db.Model, UserMixin):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(20), unique=True, nullable=False)
	email = db.Column(db.String(120), unique=True, nullable=False)
	image_file = db.Column(db.String(20), nullable=False, default="defualt.jpg")
	password = db.Column(db.String(60), nullable=False)
	balance = db.Column(db.Integer, nullable=False, default=default_balance)
	pending_transaction = db.Column(db.Integer, nullable=False, default=0)
	public_key = db.Column(db.String(100000), nullable=False)

	def get_reset_token(self, expires_in_sec=1800):
		s = Serializer(app.config['SECRET_KEY'], expires_in_sec)
		return s.dumps({'user_id': self.id}).decode('utf-8')

	def validate_token(token):
		s = Serializer(app.config['SECRET_KEY'])
		try:
			user_id = s.loads(token)['user_id']
		except:
			return None
		return User.query.get(user_id)	

	def __repr__(self):
		return f"User('{self.username}', '{self.email}', '{self.image_file}')"
