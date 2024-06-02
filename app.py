from flask import Flask, render_template, redirect, session, flash
from flask_debugtoolbar import DebugToolbarExtension
from models import connect_db, db, User, Feedback
from forms import RegisterForm, LoginForm, FeedbackForm

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
    form = RegisterForm()

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
        flash("Welcome! Account created successfully!", "success")
        return redirect(f"/users/{new_user.username}")

    return render_template("register.html", form=form)


@app.route("/login", methods=["GET", "POST"])
def show_login_form():
    """Shows user the login form/allows them to log in."""
    form = LoginForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        user = User.authenticate(username, password)
        if user:
            flash(f"Welcome back, {user.username}!", "success")
            session["user_id"] = user.username
            return redirect(f"/users/{user.username}")
        else:
            flash("Invalid username/password.", "danger")

    return render_template("login.html", form=form)


@app.route("/logout")
def logout_user():
    session.pop("user_id")
    flash("Successfully logged out!", "info")
    return redirect("/")


@app.route("/users/<username>")
def show_user_info(username):
    """Displays user's information."""
    if "user_id" not in session:
        flash("Please log in!", "danger")
        return redirect("/login")

    user = User.query.get_or_404(username)
    return render_template("user.html", user=user)


@app.route("/users/<username>/delete", methods=["POST"])
def delete_user(username):
    """Deletes user from db."""
    user = User.query.get_or_404(username)

    if user.username != session["user_id"]:
        flash("Cannot delete another user's account!", "danger")
        return redirect(f"/users/{session["user_id"]}")
    
    session.pop("user_id")
    db.session.delete(user)
    db.session.commit()
    flash("User account deleted", "info")
    return redirect("/")


@app.route("/users/<username>/feedback/add", methods=["GET", "POST"])
def create_new_feedback(username):
    """Allows user to make new feedback."""
    if "user_id" not in session:
        flash("Please log in to submit feedback!", "danger")
        return redirect("/login")

    form = FeedbackForm()
    user = User.query.get_or_404(username)

    if form.validate_on_submit():
        title = form.title.data
        content = form.content.data
        new_feedback = Feedback(title=title, content=content, username=user.username)

        db.session.add(new_feedback)
        db.session.commit()
        return redirect(f"/users/{user.username}")

    return render_template("feedback.html", form=form, user=user)


@app.route("/feedback/<int:feedback_id>/update", methods=["GET", "POST"])
def update_feedback(feedback_id):
    """Allows user to edit their feedback."""
    if "user_id" not in session:
        flash("Please log in to submit feedback!", "danger")
        return redirect("/login")

    form = FeedbackForm()
    feedback = Feedback.query.get_or_404(feedback_id)
    user = User.query.get_or_404(session["user_id"])

    if feedback.username != user.username:
        flash("Cannot edit another user's feedback!", "danger")
        return redirect(f"/users/{user.username}")

    if form.validate_on_submit():
        title = form.title.data
        content = form.content.data

        feedback.title = title
        feedback.content = content
        db.session.commit()
        return redirect(f"/users/{user.username}")

    return render_template("feedback.html", form=form, feedback=feedback)


@app.route("/feedback/<int:feedback_id>/delete", methods=["POST"])
def delete_feedback(feedback_id):
    """Allows user to delete their feedback."""
    if "user_id" not in session:
        flash("Please log in to submit feedback!", "danger")
        return redirect("/login")

    feedback = Feedback.query.get_or_404(feedback_id)
    user = User.query.get_or_404(session["user_id"])

    if feedback.username != user.username:
        flash("Cannot delete another user's feedback!", "danger")
        return redirect(f"/users/{user.username}")

    db.session.delete(feedback)
    db.session.commit()

    return redirect(f"/users/{user.username}")
