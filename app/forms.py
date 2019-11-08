from flask_wtf import Form
from wtforms import TextAreaField, FileField, StringField, BooleanField, PasswordField, SubmitField, IntegerField
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
    
class FlagForm(Form):
    flag = StringField("Flag", validators=[DataRequired()])
    submit = SubmitField("Submit")

class ProblemForm(Form):
        problem_name = StringField("Problem Name", validators=[DataRequired()])
        summary = TextAreaField("Problem Summary")
        unique_id = IntegerField("Unique ID", validators=[DataRequired()])
        solution_flag = StringField("Flag", validators=[DataRequired()])
        file_field = FileField("File Upload")
        submit = SubmitField("Submit")

class TeamForm(Form):
        new_team_name = StringField("Team Name", validators=[DataRequired()])
        new_team_password = StringField("Password", validators=[DataRequired()])
        submit = SubmitField("Submit")

class ChangeTeamForm(Form):
        team_id = IntegerField("Team ID")
        team_password = StringField("Password to Join")
        submit = SubmitField("Submit")
        
