from flask import Flask, render_template, jsonify, flash, redirect, session, request
from .forms import LoginForm, RegisterForm, FlagForm, ProblemForm
from app import app
from .db import SQL_Connect
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
from werkzeug import secure_filename
import os
from .api.api import api
from .basic_pages.pages import pages
#from .error_pages.errors import error

app.register_blueprint(api)
app.register_blueprint(pages)
#app.register_blueprint(errors)

def allowed_file(filename):
        ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/amILoggedIn")
def amI():
        flash(session)
        return render_template("logged_in.html")

   
@app.route("/dashboard", methods=["POST", "GET"])
def dashboard():
        form = FlagForm()
        if 'username' not in session.keys():
                flash("uh-oh you have to login first! Naughty boy.")
                return redirect("/index")
	#get ctf problems
        
        if form.validate_on_submit():
                flash(f"everything went OK {form.flag.data} {dir(form)}")
                return redirect("/404")
        else:
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

@app.route("/profile")
def profile():
    return render_template('profile.html')


@app.route("/admin_dashboard")
def admin_dash():
        if "admin" in session.keys():
                if not session["admin"]:
                        flash("404 Page Not Found")
                        return redirect("/404")
                else:
                        return render_template("admin_dash.html")
        else:
                flash("Page Not Found")
                return redirect("/404")

@app.route("/admin/create_problem", methods=["POST", "GET"])
def create_problem():
        if "admin" not in session.keys():
                flash("404 Page Not Found")
                return redirect("/404")
        else:
                form = ProblemForm()
                print(form.validate_on_submit())
                if form.validate_on_submit():
                        UPLOAD_FOLDER = "./app/static/uploads/"
                        f = request.files["file_field"]
                        if allowed_file(f.filename):
                                f.save(os.path.join(UPLOAD_FOLDER, secure_filename(f.filename)))
                        return redirect("/404")
                else:
                        if not session["admin"]:
                                flash("404 Page Not Found")
                                return redirect("/404")
                        else:
                                return render_template("create_problem.html", form=form)


@app.route("/404")
def error():
    return render_template("404.html", title="Error, your Error is here!")

@app.route("/token")
def token():
        return str(session)

@app.errorhandler(404)  
def not_found(error):
    flash("Oh no that wasnt found!")
    return redirect('/404'), 404

@app.errorhandler(500)
def error500(error):
    flash(f"The error you got was {error.text}")
    return redirect('/404'), 500

