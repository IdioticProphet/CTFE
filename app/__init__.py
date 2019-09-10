from flask import Flask
from config import Config

app = Flask(__name__)
#app.config.from_object("config") 
app.config.from_object(Config)

from . import routes

#if __name__ == '__main__' or True:
#    app.run(debug=True)