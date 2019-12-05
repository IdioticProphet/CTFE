from flask import Flask
from config import Config
from flaskext.markdown import Markdown

app = Flask(__name__, static_url_path="/static")
app.config.from_object(Config)
Markdown(app)

from . import routes
