from flask import Flask, jsonify, Blueprint, session, flash
from ..db import *

api = Blueprint("api", "api", url_prefix="/api")

@api.route("/problems")
def app_api():
    sql_connection = SQL_Connect()
    sql_command = ("SELECT * FROM ctf_problems")
    try:
        output_data = sql_connection.connection.query(sql_command)
    except:
        flash("SQL ERROR 1")
        return redirect("/404") 
    return(jsonify(data=output_data.as_dict()))

@api.route("/provision_number")
def provision_number():
    sql_connection = SQL_Connect()
    sql_command = ("SELECT MAX(ID) AS ID FROM ctf_problems LIMIT 1")
    try:
        output_data = sql_connection.connection.query(sql_command)
    except:
        flash("SQL ERROR 1")
        return redirect("/404")
    return(jsonify(data=output_data.as_dict()))

@api.route("/flag_submit")
def flag_submit():
    ...
    # Do stuff here
