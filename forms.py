from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, EmailField
from wtforms.validators import InputRequired, Email, Length


class RegisterForm(FlaskForm):
    username = StringField(
        "Username", validators=[InputRequired(), Length(min=1, max=20)]
    )
    password = PasswordField("Password", validators=[InputRequired()])
    email = EmailField("Email", validators=[Email(), Length(max=50)])
    first_name = StringField(
        "First Name", validators=[InputRequired(), Length(min=1, max=30)]
    )
    last_name = StringField(
        "Last Name", validators=[InputRequired(), Length(min=1, max=30)]
    )


class LoginForm(FlaskForm):
    username = StringField(
        "Username", validators=[InputRequired(), Length(min=1, max=20)]
    )
    password = PasswordField("Password", validators=[InputRequired()])


class FeedbackForm(FlaskForm):
    title = StringField("Title", validators=[InputRequired(), Length(max=100)])
    content = StringField("Content", validators=[InputRequired()])
