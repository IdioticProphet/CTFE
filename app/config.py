class Config:
    DEBUG = True 
    import os
    SECRET_KEY = os.urandom(32)

    basedir = os.path.abspath(os.path.dirname(__file__))

