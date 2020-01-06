class Config:
        import os
        BASEDIR = os.path.abspath(os.path.dirname(__file__))
        TOP_LEVEL_DIR = os.path.abspath(os.curdir)
        UPLOAD_FOLDER = TOP_LEVEL_DIR + '/app/static/uploads/'
        MAX_CONTENT_LENGTH = 16 * 1024 * 1024
        DEBUG = True
        SECRET_KEY = os.urandom(32)
        SQL_PASSWORD = "Epic_SQL_Password!23"
        ALLOW_DASHBOARD= True
        basedir = os.path.abspath
