from flask import Flask, render_template, redirect, session, flash
from flask_debugtoolbar import DebugToolbarExtension
from models import connect_db, db, User
from forms import UserForm

app = Flask(__name__)
app.debug = True
app.config["SQLALCHEMY_DATABASE_URI"] = "postgres:///hash_auth_exercise"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True
app.config["SECRET_KEY"] = "abc123"
app.config["DEBUG_TB_INTERCEPT_REDIRECTS"] = False

connect_db(app)
db.create_all()

toolbar = DebugToolbarExtension(app)


@app.route("/")
def register_redirect():
    """Redirects user to the registration form."""
    return redirect("/register")


@app.route("/register", methods=["GET", "POST"])
def new_user_registration():
    """Shows user registration form and allows them to sign up."""
    form = UserForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        email = form.email.data
        first_name = form.first_name.data
        last_name = form.last_name.data
        new_user = User.register(username, password, email, first_name, last_name)

        db.session.add(new_user)
        db.session.commit()
        session["user_id"] = new_user.username
        flash("Welcome! Account created successfully!")
        return redirect("/secret")

    return render_template("register.html", form=form)


@app.route("/login", methods=["GET", "POST"])
def show_login_form():
    form = UserForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        user = User.authenticate(username, password)
        if user:
            flash(f"Welcome back, {user.username}!")
            session["user_id"] = user.username
            return redirect("/secret")
        else:
            form.username.errors = ["Invalid username/password"]

    return render_template("login.html", form=form)


@app.route("/secret")
def show_secret():
    if "user_id" not in session:
        flash("Please log in!")
        return redirect("/login")
    return render_template("secret.html")
