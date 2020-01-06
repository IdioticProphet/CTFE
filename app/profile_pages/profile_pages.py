from flask import Flask, Blueprint, session, render_template, flash, redirect, current_app
from ..forms import TeamForm, ChangeTeamForm
from ..db import *
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import Signer
from collections import namedtuple

profile_blueprint = Blueprint("profile_blueprint", __name__, url_prefix="/profile")

@profile_blueprint.before_request
def is_logged():
    if "username" not in session.keys():
        flash("You Need to Login before accessing your profile!")
        return redirect("/")

@profile_blueprint.route("/")
def profile():
    sql_connection = SQL_Connect()
    if sql_connection.is_up():
        tnp = namedtuple("team", "team_id, team_name, members, score")
        if session["team_id"] == 0:
            form = ChangeTeamForm()
            team = tnp(0, "Default Team", session["username"], 0)
        else:
            sql_command = "SELECT * FROM teams WHERE team_id=:TID"
            team_data = sql_connection.connection.query(sql_command, TID=session["team_id"]).all()[0]
            form = None
            sql_command = "SELECT * FROM teams WHERE team_id=:team_id"
            data = sql_connection.connection.query(sql_command, team_id=session["team_id"])
            team_name = data.first().team_name
            team_members = data.first().members
            team_points = data.first().score
            team = tnp(session["team_id"], team_name, team_members)
        return render_template('profile.html', team=team, form=form)

@profile_blueprint.route("/join_team", methods=["POST", "GET"])
def join_team():
    form = ChangeTeamForm()
    if form.validate_on_submit():
        if not form.team_id.data.isnumeric():
            flash("Team ID is not a number!")
            return redirect("/profile/join_team")
        sql_connection = SQL_Connect()
        if sql_connection.is_up():
            sql_command = "SELECT team_password FROM teams WHERE team_id=:id"
            data = sql_connection.connection.query(sql_command, id=form.team_id.data)
            if data.first() is None:
                flash("Team Does not Exist")
                return redirect("/profile/join_team")
            if check_password_hash(data.first().team_password, form.team_password.data):
                sql_command = "SELECT members FROM teams where team_id=:id"
                data = sql_connection.connection.query(sql_command, id=form.team_id.data)
                member_list = data.first().members
                #making the new list of users
                if session["username"] not in member_list.split():
                    member_list += f" {session['username']}"
                #Updating teams to use the new list
                sql_command = "UPDATE teams SET members=:new_list WHERE team_id=:id"
                sql_connection.connection.query(sql_command, new_list=member_list, id=form.team_id.data)

                # Make user use new team ID
                sql_command = "UPDATE users SET team_id=:new_id WHERE id=:user_id"
                sql_connection.connection.query(sql_command, new_id=form.team_id.data, user_id=session["user_id"])
                current_app.logger.info(f"{session['username']} joined team with ID {form.team_id.data}")
                session["team_id"] = form.team_id.data
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
            if form.new_team_password.data != form.confirm_team_password.data:
                flash("The Passwords did not match!")
                return redirect("/profile/create_team")
            allowed_symbols = "0987654321ABCDEFGHIJKLMNOPQRSTUVWXYabcdefghijklmnopqrstuvwxy-_ "
            if not all(c in allowed_symbols for c in form.new_team_name.data):
                flash("You team name can only contain the characters 0-9, a-Z, - _, and Space")
                return redirect("/profile/create_team")
            
            sql_connection = SQL_Connect()
            if sql_connection.is_up():
                
                #Removing user from a team
                sql_command = f"SELECT members FROM teams WHERE team_id=:team_id"
                data = sql_connection.connection.query(sql_command, team_id=session["team_id"])
                if data.first():
                    current_members = data.first().members.split()
                    if session['username'] in current_members:
                        current_members.remove(session['username'])
                    member_list = " ".join(current_members)
                    sql_command = f"UPDATE teams SET members=:members WHERE team_id=:id"
                    sql_connection.connection.query(sql_command, members=member_list, id=session['team_id'])

                # Creating the New team
                sql_command = "INSERT INTO teams(team_name, members, team_password) VALUES (:team_name, :members, :team_password)"
                team_name = form.new_team_name.data
                members = session["username"]
                team_password = generate_password_hash(form.new_team_password.data)
                sql_connection.connection.query(sql_command, team_name=team_name, members=members, team_password=team_password)

                # Getting the new Teams ID
                sql_command = "SELECT team_id FROM teams where members=:members"
                data = sql_connection.connection.query(sql_command, members=session["username"])
                team_id = data.first().team_id

                # Ensuring the User is associated with their team
                sql_command = f"UPDATE users SET team_id =:team_id WHERE name=:username"
                sql_connection.connection.query(sql_command, team_id=team_id, username=session["username"])

                # Updating the session and then logging it 
                session['team_id'] = team_id
                current_app.logger.info(f"{session['username']} created team with ID {team_id}, name {form.new_team_name.data}")
                flash("Team created and joined team successfully!")
                return redirect("/index")
            else:
                flash("SQL Error 1")
                return redirect("/404")
        else:
            return render_template("create_team.html", form=form)
        
@profile_blueprint.route("/team_id")
def team_id():
    return str(session["team_id"])
