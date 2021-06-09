from datetime import MAXYEAR
from flask import Flask
from sqlalchemy.orm import defaultload
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from modicoin.blockchain import Blockchain
from flask_mail import Mail
import os

app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config["SECRET_KEY"] = "CHACHAAA"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///site.db"
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

# Mail server config
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('EMAIL_USER')
app.config['MAIL_PASSWORD'] = os.environ.get('EMAIL_PASS')
mail = Mail(app)

from modicoin import routes
