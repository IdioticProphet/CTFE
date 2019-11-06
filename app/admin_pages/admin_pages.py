from flask import Blueprint, flash, redirect, session, render_template
from werkzeug import secure_filename
from ..forms import ProblemForm

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
        print(form.validate_on_submit())
        if form.validate_on_submit():
                UPLOAD_FOLDER = "./app/static/uploads/"
                f = request.files["file_field"]
                if allowed_file(f.filename):
                        f.save(os.path.join(UPLOAD_FOLDER, secure_filename(f.filename)))
                return redirect("/404")
        else:
                return render_template("create_problem.html", form=form)
