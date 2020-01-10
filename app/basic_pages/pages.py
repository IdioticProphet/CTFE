from flask import Flask, Blueprint, session, render_template, flash, redirect, current_app
from ..forms import LoginForm, RegisterForm, FlagForm, ProblemForm
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
from ..db import *

pages = Blueprint("pages", __name__, url_prefix="/")

def check_func(unique_id, solved_list):
        if len(solved_list) == 0:
                return False
        for record in solved_list:
                if record.unique_id == unique_id: return True
        return False


@pages.route("/")
@pages.route("/index")
def index():
        return render_template("index.html")

@pages.route("/login", methods=["GET", "POST"])
def login():
        form = LoginForm()
        if form.validate_on_submit():
                sql_connection = SQL_Connect()
                if sql_connection.is_up():
                        #Find the users
                        sql_command = "SELECT password FROM users WHERE name=:username"
                        user_data = sql_connection.connection.query(sql_command, username=form.username.data)
                        if not user_data.first():
                                flash("Invalid Username!")
                                return redirect("/login")
                        #If passwords do not match
                        if not check_password_hash(user_data[0].password, form.password.data):
                                flash("Invalid Password.")
                                return redirect("/login")
                        #We have the username now
                        session["username"] = form.username.data

                        #Getting the user ID
                        sql_command = "SELECT id FROM users WHERE name=:username"
                        user_id = sql_connection.connection.query(sql_command, username=session["username"]).first().id
                        session["user_id"] = user_id
                        
                        #Determine if user is admin
                        sql_command = "SELECT * FROM admins"
                        data = sql_connection.connection.query(sql_command, id=user_id)
                        all_admin_id = [1]
                        current_app.logger.info(session["user_id"] in all_admin_id)
                        if session["user_id"] in all_admin_id:
                                session["admin"] = True
                        else:
                                session["admin"] = False

                        #Determine the users team_id
                        sql_command = "SELECT team_id, email FROM users WHERE name=:username"
                        data = sql_connection.connection.query(sql_command, username=form.username.data)
                        if data.first().team_id != 0:
                                session["team_id"] = data.first().team_id
                        else:
                                session["team_id"] = 0
                        if data.first().email:
                                session["email"] = data.first().email
        
                        #who just logged in
                        current_app.logger.info(f"{form.username.data} logged in successfully, with team id {data.first().team_id}")
                        flash("Login Succeeded!")
                        return redirect("/")
                else:
                        flash("SQL Error 1")
                        return redirect("/404")
        return render_template("login.html", title="Sign in", form=form)

@pages.route('/logout')
def logout():
    session.pop("username", None)
    return "bye!"

@pages.route('/register', methods=["POST", "GET"])
def register():
        form = RegisterForm()
        if form.validate_on_submit():
                if not form.username.data.isalnum():
                        flash("Your username should only contain letters and numbers!")
                        return redirect("/register")
                if form.password.data != form.check_password.data:
                        flash("Passwords did not match!")
                        return redirect("/register")
                sql_connection = SQL_Connect()
                sql_command = ("SELECT name FROM users WHERE name=:username")
                output_data = sql_connection.connection.query(sql_command, username=form.username.data)
                if output_data:
                        flash("Username is already taken!")
                        sql_connection.disconnect()
                        return redirect("/register")
                sql_command = "SELECT email FROM users WHERE email=:email"
                output_data = sql_connection.connection.query(sql_command,email=form.email.data.lower())
                if output_data:
                        flash("Account already exists with that Email")
                        sql_connection.disconnect()
                        return redirect("/register")
                        
                sql_command = "SELECT * FROM users WHERE name=:username"
                output_data = sql_connection.connection.query(sql_command, username=f"{form.username.data}")   
                if not output_data.first():
                        sql_command = "INSERT INTO users(name, display_name, email, password) VALUES(:name, :display_name,:email, :password)"
                        password = generate_password_hash(form.password.data)
                        command_output = sql_connection.connection.query(sql_command, name=form.username.data, display_name=form.real_name.data, email=form.email.data.lower(), password=password)
                        flash(f"you have registered {form.username.data}, display name of {form.real_name.data} you will get a confirmation email sent to {form.email.data}. You can now log in")
                        sql_connection.disconnect()
                        return redirect('index')
                else:
                        flash("Username is already taken!")
                        sql_connection.disconnect()
                        return redirect("/register")
        else:       
                return render_template("register.html", title="Sign up", form=form)

@pages.route("/dashboard", methods=["POST", "GET"])
def dashboard():
        if "username" not in session.keys():
                flash("You have to login before accessing the dashboard!")
                return redirect("/index")  
        if not current_app.config["ALLOW_DASHBOARD"]:
                flash("The CTF has not started yet!")
                return redirect("/")           
        else:
                if session["team_id"] == 0:
                        flash("You have to create or join a team before you can access the dashboard! Do so from your profile.")
                        return redirect("/index")
                sql_connection = SQL_Connect()
                sql_command = "SELECT * FROM problems"
                output_data = sql_connection.connection.query(sql_command)
                if output_data is not None:
                    dashboard_data = output_data.all()
                    category_names = sql_connection.connection.query("SELECT DISTINCT category FROM problems").all()
                    sql_command = f"SELECT unique_id FROM team_solves WHERE team_id=:team_id"
                    solved_questions = sql_connection.connection.query(sql_command, team_id=session['team_id']).all()
                    current_app.jinja_env.globals.update(check_func=check_func)
                    return render_template("dashboard.html", problems=dashboard_data, category_names=category_names, solved_questions=solved_questions)
                else:
                    flash("Awkward... where are the ctf problems...")
                    return redirect("/404")
                flash("????????????? idk what went wrong")
                return redirect("/404")

@pages.route("/scoreboard")
def scoreboard():
        if "username" not in session.keys():
                flash("You need to login to view scoreboard, because I said so!")
                return redirect("index")
        if not current_app.config["ALLOW_DASHBOARD"]:
                flash("The CTF has not started yet!")
                return redirect("/")
        return render_template("scoreboard.html")
