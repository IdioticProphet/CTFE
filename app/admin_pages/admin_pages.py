from flask import Blueprint
from app import app

admin = Blueprint("admin", __name__, url_prefix="/admin")

def allowed_file(filename):
        ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
@admin.route("/admin")
@admin.route("/admin/dashboard")
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

@admin.route("/token")
def token():
        return str(session)

@admin.route("/admin/create_problem", methods=["POST", "GET"])
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

    
    
    
