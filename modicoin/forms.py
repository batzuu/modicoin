from flask_wtf import FlaskForm
from flask_wtf.recaptcha import validators, widgets
from wtforms import SelectField
from wtforms.fields import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, html5 as h5field
from wtforms.fields.core import IntegerField
from wtforms.fields.simple import SubmitField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from wtforms.widgets.core import CheckboxInput
from wtforms.widgets import html5 as h5widget
from modicoin.models import User
from flask_login import current_user


class RegistrationForm(FlaskForm):
	username = StringField(
		"Username", validators=[DataRequired(), Length(min=2, max=20)]
	)

	email = StringField("Email", validators=[DataRequired(), Email()])

	password = PasswordField("Password", validators=[DataRequired()])

	confirm_password = PasswordField(
		"Confirm Password", validators=[DataRequired(), EqualTo("password")]
	)

	submit = SubmitField("Sign Up")

	def validate_username(self, username):
		user = User.query.filter_by(username=username.data).first()
		print(type(User.query.filter_by(username=username.data).first()))
		if user:
			raise ValidationError("Username is already taken")

	def validate_email(self, email):
		user = User.query.filter_by(email=email.data).first()
		if user:
			raise ValidationError("Email already in use")


class LoginForm(FlaskForm):
	email = StringField("Email", validators=[DataRequired(), Email()])

	password = PasswordField("Password", validators=[DataRequired()])

	remember = BooleanField("Remember me")

	submit = SubmitField("Login")


class KeyDownForm(FlaskForm):
	accept_check = BooleanField("I Have Copied the key", validators=[DataRequired()])

	submit = SubmitField("Next")

class TransactionForm(FlaskForm):
	receiver = StringField(
		"Receiver", validators=[DataRequired(), Length(min=2, max=20)]
	)
	amount = h5field.IntegerField("Amount", validators=[DataRequired()], widget=h5widget.NumberInput(min=1, step=1))

	private_key= TextAreaField("Private Key", validators=[DataRequired()], render_kw={"row":70})

	submit = SubmitField("Make Transaction")

	def validate_receiver(self, receiver):
		reci = User.query.filter_by(username=receiver.data).first()
		print(reci)
		if not reci:
			raise ValidationError("No receiver with this user name exist")
	
	def validate_amount(self, amount):
		user = User.query.filter_by(username=current_user.username).first()
		balance = user.balance
		pending = user.pending_transaction
		if int(amount.data) > int(balance - pending):
			if int(pending):
				raise ValidationError(f"Not enough balance! Current Balance: {balance} - {pending}(pending) modicoins")
			else:
				raise ValidationError(f"Not enough balance! Current Balance: {balance} modicoins")

class RequestForgotPassForm(FlaskForm):
	email = StringField("Email", validators=[DataRequired(), Email()])

	submit = SubmitField("Request Reset")

	def validate_email(self, email):
		user = User.query.filter_by(email=email.data).first()
		if not user:
			raise ValidationError("Email not found! You must register first!")

class ForgotPassForm(FlaskForm):
	password = PasswordField("New Password", validators=[DataRequired()])

	confirm_password = PasswordField(
		"Confirm Password", validators=[DataRequired(), EqualTo("password")]
	)

	submit = SubmitField("Reset Password")