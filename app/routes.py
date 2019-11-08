from flask import Flask, render_template, flash, redirect, session, request
from app.forms import ProblemForm, FlagForm
from app import app
from app.db import SQL_Connect
from werkzeug import secure_filename
import os
from app.api.api import api
from app.basic_pages.pages import pages
from app.admin_pages.admin_pages import admin
from app.profile_pages.profile_pages import profile_blueprint


app.register_blueprint(api)
app.register_blueprint(pages)
app.register_blueprint(admin)
app.register_blueprint(profile_blueprint)
#app.register_blueprint(errors)

@app.route("/amILoggedIn")
def amI():
        flash(session)
        return render_template("logged_in.html")
   

@app.route("/404")
def error():
    return render_template("404.html", title="Error, your Error is here!")

#@app.errorhandler(404)  
#def not_found(error):
#    flash("Oh no that wasnt found!")
#    return redirect('/404'), 404

#@app.errorhandler(500)
#def error500(error):
#    flash(f"The error you got was {error.text}")
#    return redirect('/404'), 500

