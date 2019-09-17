class Config:
    DEBUG = True 
    import os
    SECRET_KEY = "SUPER SECRET TOKEN"#os.urandom(32)
    #SESSION_COOKIE_SECURE = True
    basedir = os.path.abspath
