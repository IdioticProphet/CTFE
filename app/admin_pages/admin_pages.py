from flask import Blueprint, flash, redirect, session, render_template, request
from werkzeug import secure_filename
from ..forms import ProblemForm
from ..db import SQL_Connect
import os

admin = Blueprint("admin", __name__, url_prefix="/admin")

def allowed_file(filename):
        ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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
                        #Updating the Problem Database
                        sql_command = "INSERT INTO ctf_problems(problem_name, summary, unique_id, category) VALUES (:problem_name, :summary, :unique_id, :category)"
                        sql_connection.connection.query(sql_command, problem_name=form.problem_name.data, summary=form.summary.data, unique_id=form.unique_id.data, category=form.category.data)
                        #Updating the Flag Database
                        sql_command = "INSERT INTO ctf_problem_check(unique_id, flag, score) VALUES (:unique_id, :flag, :points)"
                        sql_connection.connection.query(sql_command, unique_id=form.unique_id.data, flag=form.solution_flag.data, points=form.point_value.data)
                        #Updating the teams database
                        sql_command = f"ALTER TABLE team_solves ADD problem_{form.unique_id.data} BOOLEAN DEFAULT FALSE"
                        sql_connection.connection.query(sql_command)
                        flash("Problem Created successfully.")
                        return redirect("/create_problem")
                else:
                        flash("SQL Error 1")
                        redirect("/404")
        else:
                return render_template("create_problem.html", form=form)
