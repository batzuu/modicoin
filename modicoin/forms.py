from flask_wtf import FlaskForm
from flask_wtf.recaptcha import validators
from wtforms import SelectField
from wtforms.fields import StringField, PasswordField, SubmitField, BooleanField
from wtforms.fields.simple import SubmitField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from modicoin.models import User


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
