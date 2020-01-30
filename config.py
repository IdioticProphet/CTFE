class Config:
        import os
        BASEDIR = os.path.abspath(os.path.dirname(__file__))
        TOP_LEVEL_DIR = os.path.abspath(os.curdir)
        UPLOAD_FOLDER = TOP_LEVEL_DIR + '/app/static/uploads/'
        MAX_CONTENT_LENGTH = 16 * 1024 * 1024
        DEBUG = True
        SECRET_KEY = os.urandom(32)
        SQL_PASSWORD = ""
        ALLOW_DASHBOARD= True
        MAIL_SERVER = 'smtp.googlemail.com'
        MAIL_PORT = 465
        MAIL_USE_TLS = False
        MAIL_USE_SSL = True
        MAIL_USERNAME = "ctf.hhscyber@gmail.com"
        MAIL_PASSWORD = "Uthought"
        basedir = os.path.abspath
