from flask import Flask
from config import Config
from flaskext.markdown import Markdown
from flask_mail import Mail


app = Flask(__name__, static_url_path="/static")
SESSION_COOKIE_SECURE = True
REMEMBER_COOKIE_SECURE = True
app.config.from_object(Config)
mail = Mail()
mail.init_app(app)
Markdown(app)

from . import routes
