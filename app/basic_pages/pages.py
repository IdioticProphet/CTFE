from flask import Flask, Blueprint, session, render_template, flash, redirect, current_app
from ..forms import LoginForm, RegisterForm, FlagForm, ProblemForm
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
from ..db import *

pages = Blueprint("pages", __name__, url_prefix="/")

def check_func(unique_id, solved_list):
        string= f"problem_{unique_id}"
        if len(solved_list) == 0:
                return False
        if string in solved_list[0].keys():
                if solved_list[0][string] == 1:
                        return True
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
                        session["username"] = form.username.data
                        sql_command = "SELECT is_admin from users WHERE name=:username"
                        data = sql_connection.connection.query(sql_command, username=form.username.data)
                        if data.first().is_admin == 1:
                                session["admin"] = True
                        else:
                                session["admin"] = False
                        sql_command = "SELECT team_id FROM users WHERE name=:username"
                        data = sql_connection.connection.query(sql_command, username=form.username.data)
                        if data.first().team_id is not None:
                                session["team_id"] = data.first().team_id
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
                if " " in form.username.data.split():
                        flash("Your username should not contain spaces!")
                        return redirect("/register")
                if form.password.data != form.check_password.data:
                        flash("Passwords did not match!")
                        return redirect("/register")
                sql_connection = SQL_Connect()
                sql_command = ("SELECT name FROM users")
                output_data = sql_connection.connection.query(sql_command)
                all_names = [x.name.lower() for x in output_data]
                if form.username.data.lower() in all_names:
                        flash("Username is already taken!")
                        sql_connection.disconnect()
                        return redirect("/register")
                sql_command = "SELECT email FROM users"
                output_data = sql_connection.connection.query(sql_command)
                all_emails = [x.email.lower() for x in output_data]
                
                if form.email.data.lower() in all_emails:
                        flash("Account already exists with that Email")
                        sql_connection.disconnect()
                        return redirect("/register")
                        
                sql_command = "SELECT * FROM users WHERE name=:username"
                output_data = sql_connection.connection.query(sql_command, username=f"{form.username.data}")   
                if output_data is not None:
                        sql_command = "INSERT INTO users(name, display_name, email, password) VALUES(:name, :display_name,:email, :password)"
                        password = generate_password_hash(form.password.data)
                        command_output = sql_connection.connection.query(sql_command, name=form.username.data, display_name=form.real_name.data, email=form.email.data.lower(), password=password)
                        flash(f"you have registered {form.username.data}, display name of {form.real_name.data} you will get a confirmation email sent to {form.email.data}. You can now log in")
                        sql_connection.disconnect()
                        return redirect('index')
                else:
                        flash("Username is already taken")
                        sql_connection.disconnect()
                        return redirect("/register")
        else:       
                return render_template("register.html", title="Sign up", form=form)

@pages.route("/dashboard", methods=["POST", "GET"])
def dashboard():
        if "username" not in session.keys():
                flash("You have to login before accessing the dashboard!")
                return redirect("/index")             
        else:
                if session["team_id"] == 0:
                        flash("You have to create or join a team before you can access the dashboard! Do so from your profile.")
                        return redirect("/index")
                sql_connection = SQL_Connect()
                sql_command = "SELECT * FROM ctf_problems"
                output_data = sql_connection.connection.query(sql_command)
                if output_data is not None:
                    dashboard_data = output_data.all()
                    flash(dashboard_data)
                    category_names = sql_connection.connection.query("SELECT DISTINCT category FROM ctf_problems").all()
                    sql_command = f"SELECT * FROM team_solves WHERE team_id={session['team_id']}"
                    solved_questions = sql_connection.connection.query(sql_command).as_dict()
                    current_app.jinja_env.globals.update(check_func=check_func)
                    return render_template("dashboard.html", category_names=category_names, solved_questions=solved_questions)
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
        return render_template("scoreboard.html")
