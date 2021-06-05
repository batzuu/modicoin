from flask_wtf import FlaskForm
from flask_wtf.recaptcha import validators
from wtforms import SelectField
from wtforms.fields import StringField, PasswordField, SubmitField, BooleanField
from wtforms.fields.core import IntegerField
from wtforms.fields.simple import SubmitField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, NumberRange
from wtforms.widgets.core import CheckboxInput
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
    amount = IntegerField("Amount", validators=[DataRequired(), NumberRange(min=1, message="Minimum Transaction amount is 1 modicoin")])

    private_key= StringField("Private Key", validators=[DataRequired()])

    submit = SubmitField("Make Transaction")

    def validate_receiver(self, receiver):
        reci = User.query.filter_by(username=receiver.data).first()
        print(reci)
        if not reci:
            raise ValidationError("No receiver with this user name exist")
    
    def validate_amount(self, amount):
        balance = User.query.filter_by(username=current_user.username).first().balance
        if int(amount.data) > int(balance):
            raise ValidationError(f"Not enough balance! Current Balance: {balance}")
    