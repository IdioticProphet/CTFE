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
                        try:
                                random_string = user_data[0]
                        except:
                                flash("Invalid Username!")
                                return redirect("/login")
                        if not check_password_hash(user_data[0].password, form.password.data):
                                flash("Invalid Password.")
                                return redirect("/login")
                        session['username'] = form.username.data
                        flash("Login Succeeded!")
                        return redirect("/index")
                else:
                        flash("SQL Error 1")
                        return redirect("/404")
        return render_template("login.html", title="Sign in", form=form)

@app.route("/amILoggedIn")
def amI():
        flash(session)
        return render_template("logged_in.html")

@app.route('/logout')
def logout():
    session.pop("username", None)
    return "bye!"
        
@app.route('/register', methods=["POST", "GET"])
def register():
        form = RegisterForm()
        if form.validate_on_submit():
                sql_connection = SQL_Connect()
                sql_command = ("SELECT name FROM users")
                try:
                        output_data = sql_connection.connection.query(sql_command)
                except:
                        flash("SQL_NOT_UP")
                        sql_connection.disconnect()
                        return redirect("/404")
                
                all_names = [x.name.lower() for x in output_data]
                
                if form.username.data.lower() in all_names:
                        flash("Username is already taken!")
                        sql_connection.disconnect()
                        return redirect("/register")

                sql_command = ("SELECT email FROM users")
                try:
                        output_data = sql_connection.connection.query(sql_command)
                except:
                        flash("SQL_NOT_UP")
                        sql_connection.disconnect()
                        return redirect("/404")
                all_emails = [x.email.lower() for x in output_data]
                
                if form.email.data.lower() in all_emails:
                        flash("Account already exists with that Email")
                        sql_connection.disconnect()
                        return redirect("/register")
                        
                sql_command = ("SELECT * FROM users WHERE name=:username")
                try:
                        output_data = sql_connection.connection.query(sql_command, username=f"{form.username.data}")
                except:
                        flash("SQL_NOT_UP")
                        sql_connection.disconnect()
                        return redirect("/404")
                        
                if output_data is not None:
                        sql_command = ("INSERT INTO users(name, email, password) VALUES(:name, :email, :password)")
                        password = generate_password_hash(form.password.data)
                        try:
                                command_output = sql_connection.connection.query(sql_command, name=form.username.data, email=form.email.data, password=password)
                        except:
                                flash(all_names)
                                sql_connection.disconnect()
                                return redirect("/404")
                        flash(f"you have registered {form.username.data} you will get a confirmation email sent to {form.email.data}")
                        sql_connection.disconnect()
                        return redirect('index')
                else:
                        flash("Username is already taken")
                        sql_connection.disconnect()
                        return redirect("/register")
        else:       
                return render_template("register.html", title="Sign up", form=form)
       
@app.route("/dashboard")
def dashboard():
        try:
                if session['username']:
                        boolean=True
        except:
                flash("uh-oh you have to login first! Naughty boy.")
                return redirect("/index")
	#get ctf problems
        
        sql_connection = SQL_Connect()
        sql_command = ("SELECT * FROM ctf_problems")
        output_data = sql_connection.connection.query(sql_command)
        #except:
        #        flash("SQL_NOT_UP" )
        #        return redirect("/404")

        if output_data is not None:
            flash(output_data.all())
            return render_template("dashboard.html")
        else:
            flash("Awkward... where are the ctf problems...")
            return redirect("/404")
        flash("????????????? idk what went wrong")
        return redirect("/404")

@app.route("/404")
def error():
    return render_template("404.html", title="Error, your Error is here!")
