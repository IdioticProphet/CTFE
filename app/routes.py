from flask import render_template
from flask import flash
from flask import redirect
from .forms import LoginForm
from .forms import RegisterForm
from app import app
from .db import SQL_Connect
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
from flask import session

@app.route('/index')
def index():
	return render_template('index.html')

@app.route('/')
def ind():
	return render_template('index.html')

@app.route('/boomer')
def boomer():
	return render_template("boomer.html")

@app.route('/login', methods=["GET", "POST"])
def login():
	form = LoginForm()
	if form.validate_on_submit():
		sql_connection = SQL_Connect()
		if sql_connection.is_up():
			sql_command = "SELECT password FROM users WHERE name=:username"
			user_data = sql_connection.connection.query(sql_command, username=form.username.data)

			if not user_data[0]:
				flash("Invalid Username")
				return redirect("/login")
			if not check_password_hash(user_data[0].password, form.password.data):
				flash("Invalid Password.")
				return redirect("/login")
			session['logged_in'] = True
			flash("Login Succeeded!")
			return redirect("/index")
		else:
                        flash("Something went wrong")
                        return redirect("/404")
	return render_template("login.html", title="Sign in", form=form)

#@app.route("/amILoggedIn")
#def amI():
#        flash(session)
#        return render_template("logged_in.html")

@app.route('/logout')
def logout():
    session['logged_in'] = False
	
@app.route('/register', methods=["POST", "GET"])
def register():
	form = RegisterForm()
	if form.validate_on_submit():
		sql_connection = SQL_Connect()
		sql_command = ("SELECT name FROM users")
		output_data = sql_connection.connection.query(sql_command)
		all_names = [x.name.lower() for x in output_data]
		if form.username.data in all_names:
			flash("Username is already taken!")
			return redirect("/register")
		sql_command = ("SELECT * FROM users WHERE name=:username")
		output_data = sql_connection.connection.query(sql_command, username=f"{form.username.data}")
		if output_data is not None:
			sql_command = ("INSERT INTO users(name, email, password) VALUES(:name, :email, :password)")
			password = generate_password_hash(form.password.data)
			try:
				command_output = sql_connection.connection.query(sql_command, name=form.username.data, email=form.email.data, password=password)
			except:
				return redirect("/404")
		else:
			flash("Username is already taken")
			sql_connection.disconnect()
		if output_data is not None:
			flash(f"you have registered {form.username.data} you will get a confirmation email sent to {form.email.data}")
			return redirect('index')
	return render_template("register.html", title="Sign up", form=form)
	
@app.route("/404")
def error():
	return render_template("404.html", title="Error, your Error is here!")
