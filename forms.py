from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, EmailField, PasswordField, DateField
from wtforms.validators import DataRequired, URL, Email
from flask_ckeditor import CKEditorField


# WTForm for creating a blog post
class AddTodoForm(FlaskForm):
    description = StringField('Description', validators=[DataRequired()])
    due_date = DateField('Due Date', format='%Y-%m-%d', validators=[DataRequired()])
    submit = SubmitField('Add Todo!')


# TODO: Create a RegisterForm to register new users
class RegisterForm(FlaskForm):
    name = StringField('Your name', validators=[DataRequired()])
    email = EmailField('Your email', validators=[DataRequired(), Email(message='Input valid Email.')])
    password = PasswordField('Set password', validators=[DataRequired()])
    submit = SubmitField('Register')


# TODO: Create a LoginForm to login existing users

class LoginForm(FlaskForm):
    email = EmailField('Your email', validators=[DataRequired(), Email(message='Input valid Email.')])
    password = PasswordField('Set password', validators=[DataRequired()])
    submit = SubmitField('Login')


# TODO: Create a CommentForm so users can leave comments below posts


