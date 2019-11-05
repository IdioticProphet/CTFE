from flask import render_template, flash, redirect, Blueprint
from app import app, db

errors = Blueprint("errors", __name__, url_prefix="/error")

@errors.errorhandler(404)  
def not_found(error):
    flash("Oh no that wasnt found!")
    return redirect('/404'), 404

@errors.errorhandler(500)
def error500(error):
    flash(f"The error you got was {error.text}")
    return redirect('/404'), 500
