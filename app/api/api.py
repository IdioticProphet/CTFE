from flask import Flask, jsonify, Blueprint, session, flash, request, current_app
from ..db import *
from operator import itemgetter

api = Blueprint("api", "api", url_prefix="/api")

@api.route("/problems")
def app_api():
    sql_connection = SQL_Connect()
    sql_command = "SELECT * FROM ctf_problems"
    try:
        output_data = sql_connection.connection.query(sql_command)
    except:
        flash("SQL ERROR 1")
        return redirect("/404") 
    return(jsonify(data=output_data.as_dict()))

@api.route("/provision_number")
def provision_number():
    sql_connection = SQL_Connect()
    sql_command = "SELECT MAX(ID) AS ID FROM ctf_problems LIMIT 1"
    try:
        output_data = sql_connection.connection.query(sql_command)
    except:
        flash("SQL ERROR 1")
        return redirect("/404")
    return(jsonify(data=output_data.as_dict()))

@api.route("/flag_submit", methods=["GET"])
def flag_submit():
    problem = request.args.get("unique_id", None)
    team = request.args.get("team_id", None)
    flag = request.args.get("flag", None)
    if problem == None or team == None or flag == None or not problem.isdigit() or not team.isdigit():
        return(jsonify({"response": "206", "description": "an input was incorrect"}))
    sql_connection = SQL_Connect()
    sql_command = "SELECT * FROM ctf_problem_check WHERE unique_id=:problem_id AND flag=:flag"
    data = sql_connection.connection.query(sql_command, problem_id=problem, flag=flag)
    if not data.as_dict(): return(jsonify({"response": "215","description": "The flag is incorrect, or the unique ID was tampered with."}))
    else: score_to_add = data.first().score
    sql_command = f"SELECT problem_{problem} FROM team_solves WHERE team_id={team} AND problem_{problem}=0"
    data = sql_connection.connection.query(sql_command)
    if not data.as_dict():
        # if the problem is all ready solved, the team ID is invalid, or problem id is invalid
        return(jsonify({'response': '216', 'description': 'Problem is already solved, teamID is invalid, or the problemID is invalid. try again'}))
    elif eval(f"data.first().problem_{problem}") == 0:
        # give the team points, set it to 1
        sql_command = f"UPDATE team_solves SET problem_{problem}=1 WHERE team_id={team}"
        sql_connection.connection.query(sql_command)
        sql_command = f"SELECT score FROM teams WHERE id={team}"
        data = sql_connection.connection.query(sql_command)
        current_score = data.first().score
        new_score = current_score+score_to_add
        sql_command = f"UPDATE teams SET score={new_score} WHERE id={team}"
        sql_connection.connection.query(sql_command)
        # Filling in the Scoring_Feed so that we can keep track of who solves what when
        team_name_command= f"SELECT team_name FROM teams WHERE id={team}"
        solved_problem_name_cmd = f"SELECT problem_name FROM ctf_problems WHERE unique_id={problem}"
        score_gained = score_to_add
        team_name = sql_connection.connection.query(team_name_command).first().team_name
        solved_problem_name = sql_connection.connection.query(solved_problem_name_cmd).first().problem_name
        sql_command = "INSERT INTO scoring_feed(team_name, problem_solved, point_value) VALUES ({team_name}, {solved_problem_name}, {score_gained}, {})"
        current_app.logger.info(f"{team_name} solved problem {solved_problem_name}")
        return(jsonify({'response': "202", "description": "problem successfully solved"}))
    else:
        return(jsonify({'response': "404"}))
        
    return(jsonify({'problem': f"problem_{problem}", 'team': team, 'flag': flag}))

@api.route("/return_team_scores", methods=["GET"])
def return_team_scores():
    sql_connection = SQL_Connect()
    sql_command = "SELECT team_name, score FROM teams"
    data = sql_connection.connection.query(sql_command)
    dictionary = sorted(data.as_dict(), key=itemgetter('score'), reverse=True)
    return(jsonify(data=dictionary))
    
