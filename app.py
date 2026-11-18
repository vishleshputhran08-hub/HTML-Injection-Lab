import secrets
from functools import wraps

from flask import Flask, redirect, render_template, request, session, url_for

LAB_USERNAME = "bee"
LAB_PASSWORD = "bug"

app = Flask(__name__)
app.config["SECRET_KEY"] = secrets.token_hex(32)
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("authenticated"):
            return redirect(url_for("login"))
        return view(*args, **kwargs)

    return wrapped


@app.after_request
def add_lab_headers(response):
    if response.mimetype == "text/html":
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate"
    response.headers["X-Content-Type-Options"] = "nosniff"
    return response


@app.route("/")
def index():
    if session.get("authenticated"):
        return redirect(url_for("portal"))
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    username = ""
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        if username == LAB_USERNAME and password == LAB_PASSWORD:
            session.clear()
            session["authenticated"] = True
            session["username"] = username
            return redirect(url_for("portal"))
        error = "Invalid username or password."
    return render_template("login.html", error=error, username=username)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/portal")
@login_required
def portal():
    return render_template("portal.html")


@app.route("/htmli_get.php", methods=["GET"])
@login_required
def htmli_get():
    submitted = bool(request.args)
    return render_template(
        "htmli_get.html",
        firstname=request.args.get("firstname", ""),
        lastname=request.args.get("lastname", ""),
        submitted=submitted,
    )


@app.route("/htmli_post.php", methods=["GET", "POST"])
@login_required
def htmli_post():
    submitted = request.method == "POST" and bool(request.form)
    return render_template(
        "htmli_post.html",
        firstname=request.form.get("firstname", "") if request.method == "POST" else "",
        lastname=request.form.get("lastname", "") if request.method == "POST" else "",
        submitted=submitted,
    )


if __name__ == "__main__":
    import os

    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        debug=False,
    )
