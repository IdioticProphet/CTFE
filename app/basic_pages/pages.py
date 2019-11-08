from flask import Flask, Blueprint, session, render_template, flash, redirect, current_app
from ..forms import LoginForm, RegisterForm, FlagForm, ProblemForm
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
from ..db import *

pages = Blueprint("pages", __name__, url_prefix="/")

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
                sql_connection = SQL_Connect()
                sql_command = ("SELECT name FROM users")
                output_data = sql_connection.connection.query(sql_command)
                all_names = [x.name.lower() for x in output_data]
                if form.username.data.lower() in all_names:
                        flash("Username is already taken!")
                        sql_connection.disconnect()
                        return redirect("/register")
                sql_command = ("SELECT email FROM users")
                output_data = sql_connection.connection.query(sql_command)
                all_emails = [x.email.lower() for x in output_data]
                
                if form.email.data.lower() in all_emails:
                        flash("Account already exists with that Email")
                        sql_connection.disconnect()
                        return redirect("/register")
                        
                sql_command = ("SELECT * FROM users WHERE name=:username")
                output_data = sql_connection.connection.query(sql_command, username=f"{form.username.data}")   
                if output_data is not None:
                        sql_command = ("INSERT INTO users(name, email, password) VALUES(:name, :email, :password)")
                        password = generate_password_hash(form.password.data)
                        command_output = sql_connection.connection.query(sql_command, name=form.username.data, email=form.email.data, password=password)
                        flash(f"you have registered {form.username.data} you will get a confirmation email sent to {form.email.data}")
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
        form = FlagForm()

        if "username" not in session.keys():
                flash("uh-oh you have to login first! Naughty boy.")
                return redirect("/index")
	#get ctf problems
        
        if form.validate_on_submit():
                flash(f"everything went OK {form.flag.data} {dir(form)}")
                return redirect("/404")
        else:
                if session["team_id"] == 0:
                        flash("You have to create or join a team before you solve any problems!")
                        return redirect("/index")
                sql_connection = SQL_Connect()
                sql_command = ("SELECT * FROM ctf_problems")
                output_data = sql_connection.connection.query(sql_command)
                if output_data is not None:
                    flash(output_data.all())
                    return render_template("dashboard.html", form=form)
                else:
                    flash("Awkward... where are the ctf problems...")
                    return redirect("/404")
                flash("????????????? idk what went wrong")
                return redirect("/404")





