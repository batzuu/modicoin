from flask import render_template, url_for, flash, redirect, request, session as sess
from flask_login.utils import login_fresh
from sqlalchemy.orm import session
from wtforms.validators import Email
from modicoin import app, db, bcrypt, login_manager, mail
from modicoin.blockpickle import blockchain
from modicoin.forms import KeyDownForm, RegistrationForm, LoginForm, TransactionForm, RequestForgotPassForm, ForgotPassForm
from modicoin.models import User
from flask_login import login_user, current_user, logout_user, login_required
from modicoin.blockchain import Block, Transaction, Blockchain
from flask_mail import Message

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
	return render_template("chainexplore.html", blockchain=blockchain, title="Explore")

@app.route("/showtransactions/<index>")
@login_required
def showtransactions(index):
	return render_template("transactionview.html", transactions = blockchain.chain[int(index)].transactions, index=index)
	

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
			sender.pending_transaction = form.amount.data
			db.session.commit()
			flash(f'Transaction was valid and added to unconfirmed pool', 'success')
		else:
			flash(f'Transaction failed invalid KEY!', 'danger')
		return redirect(url_for('transaction'))
	
	form.receiver.data = ""
	form.amount.data = ""
	form.private_key.data= ""
	return render_template("transaction.html", form=form, user=current_user, title="Send Modicoin")

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
	return render_template("mine.html", transactions=blockchain.unconfirmed_trainsactions, reward=miner_reward, title="Mine")

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
			sender.pending_transaction = 0
		receiver = User.query.filter_by(username=transaction.receiver).first()
		receiver.balance += amt
		db.session.commit()
	blockchain.mine(current_user.username)
	print("Block was successfully mined")
	transaction = Transaction(sender="MinerReward", receiver=current_user.username, amt=blockchain.miner_reward)
	blockchain.unconfirmed_trainsactions.append(transaction)
	flash(f'Block was mined successfuly', 'success')
	return redirect(url_for('mine'))



@app.route("/account")
@login_required
def account():
	return render_template("account.html", user=current_user, title="Your Account")

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
		return redirect(url_for('explore'))
	key = request.args.get('key')
	return render_template("key_download.html", key=sess["key"], user=current_user, form=form, title="Key")



@app.route("/")
def index():
	if current_user.is_authenticated:
		return redirect(url_for("explore"))
	else:
		return redirect(url_for("login"))

def send_reset_email(user):
	token = user.get_reset_token()
	msg = Message("Password Reset for ModiCoin", sender="modicoin", recipients=[user.email])
	msg.body = f'''To reset the password click on the link below:
{url_for('reset_token', token=token, _external=True)}
Contact admin if you did not create the password reset request
	'''
	mail.send(msg)

@app.route("/reset_password", methods=["GET", "POST"])
def reset_req():
	if current_user.is_authenticated:
		return redirect(url_for("home"))
	form = RequestForgotPassForm()
	if form.validate_on_submit():
		email = form.email.data
		user = User.query.filter_by(email=email).first()
		send_reset_email(user)
		flash('A mail has been sent to you containing instructions to reset your password', 'success')
		return redirect(url_for('login'))
	return render_template('reset_req.html', title='Reset Password', form=form)
	
@app.route("/reset_password/<token>", methods=["GET", "POST"])
def reset_token(token):
	if current_user.is_authenticated:
		return redirect(url_for("home"))
	user = User.validate_token(token)
	if not user:
		flash("Invalid/Expired token", 'warning')
		return redirect(url_for('reset_req'))
	
	form = ForgotPassForm()
	if form.validate_on_submit():
		hashed_pass = bcrypt.generate_password_hash(form.password.data)
		user.password = hashed_pass	
		db.session.commit()
		flash(f"Your password has been reset! You can now login.", 'success')
		return redirect(url_for("login"))

	return render_template("reset_token.html", title='Reset Password', form=form)	
