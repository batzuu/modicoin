from flask import render_template, url_for, flash, redirect, request
from wtforms.validators import Email
from modicoin import app, db, bcrypt, blockchain
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
        public_key = blockchain.generate_keys()
        user = User(
            email=form.email.data,
            password=hashed_pass,
            username=form.username.data,
            public_key=public_key,
        )
        db.session.add(user)
        db.session.commit()
        flash(f"Account created for {form.username.data}! You can now login", "success")
        return redirect(url_for("login"))
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


@app.route("/")
def index():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    else:
        return redirect(url_for("login"))
