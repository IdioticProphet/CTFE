from flask_wtf import Form
from wtforms import StringField, BooleanField, PasswordField, SubmitField
from wtforms.validators import DataRequired

class LoginForm(Form):
	username = StringField("Username", validators=[DataRequired()])
	password = PasswordField("Password", validators=[DataRequired()])
	submit =  SubmitField("Sign In")
    
class RegisterForm(Form):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired()])
    agreement = BooleanField("I accept the terms and conditions.", validators=[DataRequired()])
    submit = SubmitField("Register")