from flask import Flask, jsonify, Blueprint, session, flash, request, current_app
from ..db import *
from operator import itemgetter

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
