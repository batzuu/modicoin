from flask import render_template, url_for, flash, redirect, request, session as sess
from flask_login.utils import login_fresh
from sqlalchemy.orm import session
from wtforms.validators import Email
from modicoin import app, db, bcrypt, blockchain, login_manager
from modicoin.forms import RegistrationForm, LoginForm
from modicoin.models import User
from flask_login import login_user, current_user, logout_user, login_required


@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_pass = bcrypt.generate_password_hash(form.password.data)
        key = blockchain.generate_keys()
        public_key = key.get('public')
        user = User(
            email=form.email.data,
            password=hashed_pass,
            username=form.username.data,
            public_key=public_key,
        )
        db.session.add(user)
        db.session.commit()
        login_user(user)
        flash(f"Account created for {form.username.data}! Please copy your private key and keep it secure", "info")
        sess["key"] = key.get('private')
        return redirect(url_for("key_download"))
    return render_template("register.html", title="Register", form=form)


@app.route("/home")
def home():
    return render_template("home.html", title="Homepage")


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            if form.email.data == "batzu@one.com":
                flash("Admin Login Success", "danger")
            else:
                flash("Welcome!", "success")
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            return redirect(url_for("home"))
        flash("Login failed! Invalid email and/or password", "danger")
    return render_template("login.html", title="Login", form=form)

@app.route("/account")
@login_required
def account():
    return render_template("account.html", user=current_user)

@app.route("/about")
def about():
    return "<h1> About page <h1>"


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("login"))

@app.route("/key_download")
def key_download():
    key = request.args.get('key')
    return render_template("key_download.html", key=sess["key"], user=current_user)



@app.route("/")
def index():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    else:
        return redirect(url_for("login"))
