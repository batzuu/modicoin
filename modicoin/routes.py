from flask import render_template, url_for, flash, redirect, request, session as sess
from flask_login.utils import login_fresh
from sqlalchemy.orm import session
from wtforms.validators import Email
from modicoin import app, db, bcrypt, login_manager
from modicoin.blockpickle import blockchain
from modicoin.forms import KeyDownForm, RegistrationForm, LoginForm, TransactionForm
from modicoin.models import User
from flask_login import login_user, current_user, logout_user, login_required
from modicoin.blockchain import Block, Transaction, Blockchain

miner_reward = blockchain.miner_reward

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

@app.route("/explore")
@login_required
def explore():
	return render_template("chainexplore.html", blockchain=blockchain)

@app.route("/home")
@login_required
def home():
	return render_template("home.html", title="Homepage")

@app.route("/transaction", methods=["GET", "POST"])
@login_required
def transaction():
	form = TransactionForm()
	if form.validate_on_submit():
		print(f"Reciver - {form.receiver.data} Amt - {form.amount.data} Key - ")
		sender = User.query.filter_by(username=current_user.username).first()
		receiver = User.query.filter_by(username=form.receiver.data).first()
		print(f'{form.amount.data} from {sender.username} to {receiver.username}')
		transaction = Transaction(sender.username, receiver.username, int(form.amount.data))
		pub_key = sender.public_key
		if transaction.is_valid(form.private_key.data, pub_key):
			blockchain.add_new_transaction(transaction)
			flash(f'Transaction was valid and added to unconfirmed pool', 'success')
		else:
			flash(f'Transaction failed invalid KEY!', 'danger')
		return redirect(url_for('transaction'))
	
	form.receiver.data = ""
	form.amount.data = ""
	form.private_key.data= ""
	return render_template("transaction.html", form=form, user=current_user)

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

@app.route("/mine")
@login_required
def mine():
	return render_template("mine.html", transactions=blockchain.unconfirmed_trainsactions, reward=miner_reward)

@app.route("/mineblock")
@login_required
def mineblock():
	for transaction in blockchain.unconfirmed_trainsactions:
		print(transaction)

	for transaction in blockchain.unconfirmed_trainsactions:
		amt = transaction.amt
		if not transaction.sender == "MinerReward":
			sender = User.query.filter_by(username=transaction.sender).first()
			sender.balance -= amt
		receiver = User.query.filter_by(username=transaction.receiver).first()
		receiver.balance += amt
		db.session.commit()
	blockchain.mine(current_user.username)
	print("Block was successfully mined")
	transaction = Transaction(sender="MinerReward", receiver=current_user.username, amt=blockchain.miner_reward)
	blockchain.unconfirmed_trainsactions.append(transaction)
	flash(f'Block was mined successfuly')
	return redirect(url_for('mine'))



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

@app.route("/key_download", methods=["GET", "POST"])
def key_download():
	form = KeyDownForm()
	if form.validate_on_submit():
		flash(f'Welcom {current_user.username}!', 'success')
		return redirect(url_for('home'))
	key = request.args.get('key')
	return render_template("key_download.html", key=sess["key"], user=current_user, form=form)



@app.route("/")
def index():
	if current_user.is_authenticated:
		return redirect(url_for("home"))
	else:
		return redirect(url_for("login"))
