from flask import Blueprint, flash, redirect, session, render_template, request
from werkzeug import secure_filename
from ..forms import ProblemForm
from ..db import SQL_Connect
import os

admin = Blueprint("admin", __name__, url_prefix="/admin")

def allowed_file(filename):
        ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def provision_number():
    sql_connection = SQL_Connect()
    sql_command = ("SELECT MAX(ID) AS ID FROM ctf_problems LIMIT 1")
    try:
        output_data = sql_connection.connection.query(sql_command)
    except:
        flash("SQL ERROR 1")
        return redirect("/404") 
    return(output_data.first().ID)

@admin.before_request
def admin1():
    if "admin" not in session.keys():
        flash("Page Not Found")
        return redirect("/404")

@admin.route("/")
@admin.route("/dashboard")
def admin_dash():
        return render_template("admin_dash.html")


@admin.route("/token")
def token():
        return str(session)

@admin.route("/create_problem", methods=["POST", "GET"])
def create_problem():
        form = ProblemForm()
        if form.validate_on_submit():
                sql_connection = SQL_Connect()
                if sql_connection.is_up():
                        UPLOAD_FOLDER = "./app/static/uploads/"
                        f = request.files["file_field"]
                        if allowed_file(f.filename):
                                f.save(os.path.join(UPLOAD_FOLDER, secure_filename(f.filename)))
                        form.unique_id.data = provision_number()+1
                        #Updating the Problem Database
                        sql_command = "INSERT INTO ctf_problems(problem_name, short_summary, summary, unique_id, category) VALUES (:problem_name, :short_summary, :summary, :unique_id, :category)"
                        sql_connection.connection.query(sql_command, problem_name=form.problem_name.data, short_summary=form.short_summary.data, summary=form.summary.data, unique_id=form.unique_id.data, category=form.category.data)
                        #Updating the Flag Database
                        try:
                                sql_command = "INSERT INTO ctf_problem_check(unique_id, flag, score) VALUES (:unique_id, :flag, :points)"
                                sql_connection.connection.query(sql_command, unique_id=form.unique_id.data, flag=form.solution_flag.data, points=form.point_value.data)
                        except:
                                flash("Error! Duplicate Flag")
                                sql_connection.connection.query(f"DELETE FROM ctf_problems WHERE id={form.unique_id.data}")
                                return render_template("create_problem.html", form=form)
                        #Updating the teams database
                        sql_command = f"ALTER TABLE team_solves ADD problem_{form.unique_id.data} BOOLEAN DEFAULT FALSE"
                        sql_connection.connection.query(sql_command)
                        flash("Problem Created successfully.")
                        return redirect("/admin/create_problem")
                else:
                        flash("SQL Error 1")
                        redirect("/404")
        else:
                return render_template("create_problem.html", form=form)

@admin.route("/edit_problem", methods=["GET"])
def edit_problem():
        problem_id = request.args.get("problem_id",None)
        if problem_id is None or not problem_id.isdigit():
                flash("The problem ID was wrong")
                return render_template("edit_problem.html")
        else:
                sql_connection = SQL_Connect()
                sql_command = "SELECT * FROM ctf_problems WHERE unique_id=:unid"
                data=sql_connection.connection.query(sql_command, unid=problem_id)
                if not data.first():
                        flash("Something went wrong with the query. The Id is probably wrong")
                        return render_template("edit_problem.html")
                return render_template("edit_problem.html", problem_query=data.first())
                
