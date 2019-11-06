from flask import Flask, Blueprint, session, render_template, flash, redirect
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
                        data.as_dict()[0]["is_admin"]
                        if data.as_dict()[0]["is_admin"] == 1:
                                session["admin"] = True
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



