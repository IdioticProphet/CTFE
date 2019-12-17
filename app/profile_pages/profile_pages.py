from flask import Flask, Blueprint, session, render_template, flash, redirect, current_app
from ..forms import TeamForm, ChangeTeamForm
from ..db import *
from werkzeug.security import generate_password_hash, check_password_hash

profile_blueprint = Blueprint("profile_blueprint", __name__, url_prefix="/profile")

@profile_blueprint.before_request
def is_logged():
    if "username" not in session.keys():
        flash("You Need to Login before accessing your profile!")
        return redirect("/")

@profile_blueprint.route("/")
def profile():
    return render_template('profile.html')

@profile_blueprint.route("/join_team", methods=["POST", "GET"])
def join_team():
    form = ChangeTeamForm()
    if form.validate_on_submit():
        sql_connection = SQL_Connect()
        if sql_connection.is_up():
            sql_command = "SELECT team_password FROM teams WHERE id=:identification"
            data = sql_connection.connection.query(sql_command, identification=form.team_id.data)
            if data.first() is None:
                flash("Team Doesnt Exist")
                return redirect("/profile/join_team")
            if check_password_hash(data.first().team_password, form.team_password.data):
                sql_command = "SELECT members FROM teams where id=:identification"
                data = sql_connection.connection.query(sql_command, identification=form.team_id.data)
                member_list = data.first().members
                if session["username"] not in member_list.split():
                    member_list += f" {session['username']}"
                sql_command = "UPDATE teams SET members=:new_list"
                sql_connection.connection.query(sql_command, new_list=member_list)
                sql_command = "UPDATE users SET team_id=:new_id"
                sql_connection.connection.query(sql_command, new_id=form.team_id.data)
                current_app.logger.info(f"{session['username']} joined team with ID {form.team_id.data}")
                flash("Joined Team Successfully")
                return redirect("/profile/join_team")
            else:
                flash("Password is incorrect")
                return redirect("/profile/join_team")
        else:
            flash("SQL Error 1")
            return redirect("/404")
    else:
        return render_template("join_team_form.html", form=form)
        

@profile_blueprint.route("/create_team", methods=["GET", "POST"])
def create_team():
        form = TeamForm()
        if form.validate_on_submit():
            if form.new_team_password != form.confirm_team_password:
                flash("The Passwords did not match!")
                return redirect("/profile/create_team")
            sql_connection = SQL_Connect()
            if sql_connection.is_up():
                #Removing user from a team
                sql_command = f"SELECT members FROM teams WHERE id={session['team_id']}"
                data = sql_connection.connection.query(sql_command)
                if data.first():
                    current_members = data.first().members.split()
                    if session['username'] in current_members:
                        current_members.remove(session['username'])
                    member_list = " ".join(current_members)
                    sql_command = f"UPDATE teams SET members=:members WHERE id=:id"
                    sql_connection.connection.query(sql_command, members=member_list, id=session['team_id'])

                # Creating the New team
                sql_command = "INSERT INTO teams(team_name, members, team_password) VALUES (:team_name, :members, :team_password)"
                team_name = form.new_team_name.data
                members = session["username"]
                team_password = generate_password_hash(form.new_team_password.data)
                sql_connection.connection.query(sql_command, team_name=team_name, members=members, team_password=team_password)

                # Getting the new Teams ID
                sql_command = "SELECT id FROM teams where members=:members"
                data = sql_connection.connection.query(sql_command, members=session["username"])
                team_id = data.first().id

                # Ensuring the User is associated with their team
                sql_command = f"UPDATE users SET team_id = {team_id} WHERE name=:username"
                sql_connection.connection.query(sql_command, username=session["username"])

                # Adding new team to scoring table
                sql_command = f"INSERT INTO team_solves(team_id) VALUES ({team_id})"
                sql_connection.connection.query(sql_command)

                
                session['team_id'] = team_id
                current_app.logger.info(f"{session['username']} created team with ID {team_id}, name {form.new_team_name.data}")
                flash("Team created Successfully, and joined")
                return redirect("/index")
            else:
                flash("SQL Error 1")
                return redirect("/404")
        else:
            return render_template("create_team.html", form=form)
        
@profile_blueprint.route("/team_id")
def team_id():
    return str(session["team_id"])
