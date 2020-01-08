from flask import Flask, jsonify, Blueprint, session, flash, request, current_app, redirect, send_from_directory
import os
from ..db import *
from operator import itemgetter
from itsdangerous import Signer
from werkzeug.security import check_password_hash, generate_password_hash

api = Blueprint("api", "api", url_prefix="/api")

@api.route("/problems")
def app_api():
    sql_connection = SQL_Connect()
    sql_command = "SELECT * FROM problems"
    if not sql_connection.is_up():
        return jsonify({"response": 405, "description": "SQL_NOT_UP"})
    output_data = sql_connection.connection.query(sql_command)
    return(jsonify(data=output_data.as_dict()))

@api.route("/provision_number")
def provision_number():
    sql_connection = SQL_Connect()
    sql_command = "SELECT MAX(unique_id) AS unique_id FROM problems LIMIT 1"
    if sql_connection.is_up():
        output_data = sql_connection.connection.query(sql_command)
    else:
        flash("SQL ERROR 1")
        return redirect("/404")
    if output_data.first().unique_id:
        return(jsonify(output_data.as_dict()))
    else:
        return(jsonify([{'unique_id': 0}]))

@api.route("/flag_submit", methods=["GET"])
def flag_submit():
    problem = int(request.args.get("unique_id", None))
    team = session["team_id"]
    flag = request.args.get("flag", None)
    if not problem or not team or not flag or type(problem) != int or type(team) != int:
        return(jsonify({"response": "206", "description": "an input was incorrect"}))
    sql_connection = SQL_Connect()
    cmd = "SELECT score FROM problem_check WHERE unique_id=:unid AND flag=:flagge"
    data = sql_connection.connection.query(cmd, unid=problem, flagge=flag)
    current_app.logger.info(data.all())
    if not data.as_dict():
        return(jsonify({"response": "215","description": "The flag is incorrect, or the unique ID was tampered with."}))
    else:
        score_to_add = data.first().score
    # from team solves figure out if problem is solved
    sql_command = "SELECT team_id, unique_id FROM team_solves WHERE team_id=:team_id AND unique_id=:problem_id"
    data = sql_connection.connection.query(sql_command, team_id=team, problem_id=problem)
    if data.as_dict():
        # if the problem is all ready solved, the team ID is invalid, or problem id is invalid
        return(jsonify({'response': '216', 'description': 'Problem is already solved'}))
    else:
        # give the team points, set it to 1
        sql_command = "INSERT INTO team_solves(team_id, unique_id) VALUES (:team_id, :problem_id)"
        sql_connection.connection.query(sql_command, team_id=team, problem_id=problem)
        sql_command = "SELECT score FROM teams WHERE team_id=:team"
        data = sql_connection.connection.query(sql_command, team=team)
        current_score = data.first().score
        new_score = current_score+score_to_add
        sql_command = f"UPDATE teams SET score=:new_score WHERE team_id=:team"
        sql_connection.connection.query(sql_command, new_score=new_score, team=team)
        
        # finding the teamname using your teamid
        team_name_command= f"SELECT team_name FROM teams WHERE team_id=:team"
        team_name = sql_connection.connection.query(team_name_command, team=team).first().team_name

        #obtain the problem name of what was solved
        solved_problem_name_cmd = f"SELECT problem_name FROM ctf_problems WHERE unique_id=:problem"
        solved_problem_name = sql_connection.connection.query(solved_problem_name_cmd, problem=problem).first().problem_name

        #update the scoring feed after a solve
        sql_command = "INSERT INTO scoring_feed(team_name, problem_solved, point_value, new_total) VALUES (:team_name, :problem_solved, :point_value, :new_total)"
        sql_connection.connection.query(sql_command, team_name=team_name, problem_solved=solved_problem_name, point_value=score_to_add, new_total=new_score)
        current_app.logger.info(f"{team_name} solved problem {solved_problem_name}")
        return(jsonify({'response': "202", "description": "problem successfully solved"}))
        

@api.route("/return_team_scores", methods=["GET"])
def return_team_scores():
    sql_connection = SQL_Connect()
    sql_command = "SELECT team_name, score FROM teams"
    data = sql_connection.connection.query(sql_command)
    dictionary = sorted(data.as_dict(), key=itemgetter('score'), reverse=True)
    return(jsonify(data=dictionary))
    
@api.route("/scoring_feed", methods=["GET"])
def return_score_feed():
    sql_connection = SQL_Connect()
    if not sql_connection.is_up():
        return jsonify({"response":405, "description": "SQL_NOT_UP"})
    sql_command="SELECT * FROM scoring_feed"
    data = sql_connection.connection.query(sql_command).as_dict()
    for item in data:
        item["when_solved"] = item["when_solved"].isoformat()
    dictionary = sorted(data, key=itemgetter('team_name'), reverse=True)
    return(jsonify(dictionary))

@api.route("/leave_team", methods=["GET"])
def leave_team():
    team_id = session["team_id"]
    uuid = session["user_id"]
    sql_connection = SQL_Connect()
    if not sql_connection.is_up():
        return jsonify({"response": 405, "description": "SQL_NOT_UP"})
    # Changing the teams table
    sql_command = "SELECT members FROM teams WHERE team_id=:TID"
    data = sql_connection.connection.query(sql_command, TID=team_id).first()
    if not data:
        return jsonify({"response": 406, "description": "somehow that person was not in a team..."})
    new_member_list = data.members.split(" ").remove(session["username"])
    if new_member_list:
        new_members = "".join(new_member_list)
    else:
        new_members = ""
    if new_members == data.members:
        return jsonify({"response": 406, "description": "somehow that person was not in that team..."})
    sql_command = "UPDATE teams SET members=:newmembers WHERE team_id=:TID"
    sql_connection.connection.query(sql_command, newmembers=new_members, TID=team_id)
    # Changing the users table
    sql_command = "UPDATE users SET team_id=0 WHERE id=:uuid"
    sql_connection.connection.query(sql_command, uuid=uuid)
    # Update the session
    session["team_id"] = 0
    # Reuturn our success
    return jsonify({"response": 201, "description": "It Worked!"})

@api.route("/join_team", methods=["GET"])
def join_team():
    new_team_id = request.args.get("team_id")
    new_team_password = request.args.get("team_password")
    if not new_team_id.isnumeric():
        flash("Team ID Needs to be a number!")
        return jsonify({"response": "215", "description": "Team ID is not a number"})
    uuid = session["user_id"]
    sql_connection = SQL_Connect()
    if not sql_connection.is_up():
        return jsonify({"response": 405, "description": "SQL_NOT_UP"})
    sql_command = "SELECT * FROM teams WHERE team_id=:nTID"
    data = sql_connection.connection.query(sql_command, nTID=new_team_id)
    if check_password_hash(data.first().team_password, new_team_password):
        sql_command = "SELECT members FROM teams where team_id=:id"
        data = sql_connection.connection.query(sql_command, id=new_team_id)
        member_list = data.first().members
        #making the new list of users
        if session["username"] not in member_list.split():
            member_list += f" {session['username']}"
        #Updating teams to use the new list
        sql_command = "UPDATE teams SET members=:new_list WHERE team_id=:id"
        sql_connection.connection.query(sql_command, new_list=member_list, id=new_team_id)

        # Make user use new team ID
        sql_command = "UPDATE users SET team_id=:new_id WHERE id=:user_id"
        sql_connection.connection.query(sql_command, new_id=new_team_id, user_id=session["user_id"])
        current_app.logger.info(f"{session['username']} joined team with ID {new_team_id}")
        session["team_id"] = new_team_id
        flash("Joined Team Successfully")
        return jsonify({"response": 201, "Description": "It Worked!"})
    else:
        flash("Password is incorrect")

@api.route("/change_password")
def change_password():
    user_id = session["user_id"]
    current_password = request.args.get("current_password")
    new_password = request.args.get("new_password")
    if not current_password or not user_id or not current_password:
        return jsonify({"response": 400, "description": "Missing Arguments"})
    sql_connection = SQL_Connect()
    if not sql_connection.is_up():
        return jsonify({"response": 401, "description": "SQL_NOT_UP"})
    sql_command = "SELECT password FROM users WHERE id=:uuid"
    data = sql_connection.connection.query(sql_command, uuid=user_id)
    if data.first() == "":
        return jsonify({"response": 400, "description": "Username Error"})
    pwdhash = data.first().password
    if not check_password_hash(pwdhash, current_password):
        return jsonify({"response": 400, "description": "Passwords do not match"})
    sql_command = "UPDATE users SET password=:password WHERE id=:uuid"
    sql_connection.connection.query(sql_command, password=new_password, uuid=user_id)
    return jsonify({"response": 200, "description": "Password Successfully Changed"})

UPLOAD_DIRECTORY = "./app/static/uploads/"
@api.route("/files")
def list_files():
    """Endpoint to list files on the server."""
    files = []
    for filename in os.listdir(UPLOAD_DIRECTORY):
        path = os.path.join(UPLOAD_DIRECTORY, filename)
        if os.path.isfile(path):
            files.append(filename)
    return jsonify(files)

@api.route("/files/<filename>", methods=["POST"])
def post_file(filename):
    if "/" in filename:
        return jsonify({"response": 400, "description": "Bad Filename"})
    with open(os.path.join(UPLOAD_DIRECTORY, filename), "wb") as fp:
        fp.write(request.data)
        return jsonify({"response": 200, "description": "File Created"})

@api.route("/files/<path:path>", methods=["GET"])
def get_file(path):
    return send_from_directory(os.path.abspath(UPLOAD_DIRECTORY), path, as_attachment=True)
