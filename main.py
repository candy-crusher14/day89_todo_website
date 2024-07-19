from flask import Flask, abort, render_template, redirect, url_for, flash, request
from flask_bootstrap import Bootstrap5
from flask_ckeditor import CKEditor
# from flask_gravatar import Gravatar
from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user, login_required
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship, DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Text, ForeignKey
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from flask_paginate import Pagination, get_page_args
# Import your forms from the forms.py
# from forms import CreatePostForm, RegisterForm, LoginForm, CommentForm
from typing import List
from hashlib import md5
from sqlalchemy.ext.declarative import declarative_base
from flask_migrate import Migrate
from forms import AddTodoForm, LoginForm, RegisterForm
from datetime import datetime
from flask_wtf.csrf import CSRFProtect

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
ckeditor = CKEditor(app)
Bootstrap5(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todo.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# csrf = CSRFProtect(app)


# TODO: Configure Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(UserMixin, db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    email = db.Column(db.String(250), nullable=False, unique=True)
    password = db.Column(db.String(250), nullable=False)
    todos = db.relationship('Todo', backref='user', lazy=True)

class Todo(db.Model):
    __tablename__ = "todos"
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(250), nullable=False)
    status = db.Column(db.String(50), nullable=False, default='On time')
    due_date = db.Column(db.String(10), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)



# with app.app_context():
#     db.create_all()
#
#     # Check if the user already exists
#     user = User.query.filter_by(email='1@gmail.com').first()
#     if not user:
#         # Create a new user if not exists
#         user = User(name='Hammad', password='123', email='1@gmail.com')
#         db.session.add(user)
#         db.session.commit()
#     else:
#         print(f"User {user.email} already exists")
#
#     # Ensure todos are not already in the database
#     if not Todo.query.filter_by(user_id=user.id).all():
#         # Create some todos for the user
#         todos = [
#             Todo(description='Give user ability to sort to-dos by name, due status, or due date', due_date='2024-07-15', user_id=user.id),
#             Todo(description='Give user ability to create different lists with to do tasks', due_date='2024-07-24', user_id=user.id),
#             Todo(description='Allow user to delete lists', due_date='2024-07-20', user_id=user.id),
#             Todo(description='Update the homepage to display all to-do lists and when user clicks on a list, it will take them to a unique page', due_date='2024-07-12', user_id=user.id)
#         ]
#
#         # Add todos to the session and commit
#         db.session.bulk_save_objects(todos)
#         db.session.commit()
#     else:
#         print("Todos for the user already exist")


def calculate_status(due_date):
    today = datetime.today().date()
    due_date = datetime.strptime(due_date, '%Y-%m-%d').date()
    if due_date < today:
        return 'Past due'
    elif due_date == today:
        return 'Due today'
    else:
        return 'On time'


@app.route('/', methods=['GET', 'POST'])
def homepage():
    form = AddTodoForm()
    if current_user.is_authenticated:
        user = User.query.filter_by(name=current_user.name).first()
        if form.validate_on_submit():
            description = form.description.data
            due_date = form.due_date.data
            status = calculate_status(due_date.strftime('%Y-%m-%d'))
            new_todo = Todo(description=description, due_date=due_date.strftime('%Y-%m-%d'), status=status, user_id=current_user.id)
            db.session.add(new_todo)
            db.session.commit()
            return redirect(url_for('homepage'))  # Redirect to avoid form resubmission

        todos = user.todos
        for todo in todos:
            todo.status = calculate_status(todo.due_date)
        return render_template('front_webpage.html', todos=todos, form=form)
    else:
        return redirect(url_for('login'))

@app.route('/<int:id>')
def complete(id):
    todo = Todo.query.filter_by(id=id).first()

    db.session.delete(todo)
    db.session.commit()

    return redirect(url_for('homepage'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    register_form = RegisterForm()
    if register_form.validate_on_submit():
        user = db.session.execute(db.select(User).where(User.email == register_form.email.data)).scalar()
        if not user:
            new_user = User(
                name=register_form.name.data,
                email=register_form.email.data,
                password=register_form.password.data,

            )
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)
            return redirect(url_for('homepage', logged_in=current_user.is_authenticated))
        else:
            flash(message='Email is already registered. Login instead.')
            return redirect(url_for('login'))

    return render_template("register.html", form=register_form)


@app.route('/login', methods=["GET", "POST"])
def login():
    login_form = LoginForm()
    if login_form.validate_on_submit():
        login_email = login_form.email.data
        login_passowrd = login_form.password.data
        user = db.session.execute(db.select(User).where(User.email == login_email)).scalar()
        if user and login_passowrd == user.password:
            login_user(user)
            return redirect(url_for('homepage'))
        elif not user:
            flash(message='Email is not registered.')
            return redirect(url_for('register'))
        elif not check_password_hash(password=login_passowrd, pwhash=user.password):
            flash(message='Incorrect Password')
            return redirect(url_for('login'))

    return render_template("login.html", form=login_form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('homepage'))




if __name__ == "__main__":
    app.run(debug=True)





# CREATE DATABASE
# class Base(DeclarativeBase):
#     pass
#
#
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'

#     with app.app_context():
#         db.create_all()

# db = SQLAlchemy(model_class=Base)
# db.init_app(app)
#
# # TODO: Configure Flask-Login
# login_manager = LoginManager()
# login_manager.init_app(app)
#
#
# @login_manager.user_loader
# def load_user(user_id):
#     return User.query.get(int(user_id))
#
# def admin_only(func):
#     @wraps(func)
#     def decorated_function(*args, **kwargs):
#         if current_user.is_authenticated and current_user.id == 1:
#             return func(*args, **kwargs)
#         else:
#             return abort(403)
#
#     return decorated_function
#
#     # return the_wrapper_around_the_original_function
#
#
# class User(UserMixin, db.Model):
#     __tablename__ = "user"
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(250), nullable=False)
#     email = db.Column(db.String(250), nullable=False, unique=True)
#     password = db.Column(db.String(250), nullable=False, unique=True)
#     comments = db.relationship('Comment', backref='user', lazy=True)
#
# class Cafe(db.Model):
#     __tablename__ = "cafe"
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(250), nullable=False)
#     map_url = db.Column(db.String(500), nullable=False)
#     img_url = db.Column(db.String(500), nullable=False)
#     location = db.Column(db.String(250), nullable=False)
#     has_sockets = db.Column(db.Boolean, nullable=False)
#     has_toilet = db.Column(db.Boolean, nullable=False)
#     has_wifi = db.Column(db.Boolean, nullable=False)
#     can_take_calls = db.Column(db.Boolean, nullable=False)
#     seats = db.Column(db.String(250), nullable=True)
#     coffee_price = db.Column(db.String(250), nullable=True)
#     comments = db.relationship('Comment', backref='cafe', lazy=True)
#
# class Comment(db.Model):
#     __tablename__ = "comment"
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.Text, nullable=False)
#     text = db.Column(db.Text, nullable=False)
#     user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
#     cafe_id = db.Column(db.Integer, db.ForeignKey('cafe.id'), nullable=False)
#
#
#
# @app.route('/')
# def home_page():
#     page, per_page, offset = get_page_args(page_parameter='page', per_page_parameter='per_page', default_per_page=10)
#     total = Cafe.query.count()
#     cafes = Cafe.query.offset(offset).limit(per_page).all()
#
#     pagination = Pagination(page=page, per_page=per_page, total=total, css_framework='bootstrap4')
#
#     return render_template('front_webpage.html', cafes=cafes, page=page,
#                            per_page=per_page,
#                            pagination=pagination,
#                            current_user = current_user
#                            )
#
# @app.route('/cafe/<int:cafe_id>', methods=['GET','POST'])
# def show_info(cafe_id):
#     cafe = Cafe.query.get_or_404(cafe_id)
#     comment_form = CommentForm()
#     comments = Comment.query.filter_by(cafe_id=cafe_id).all()
#     user = User.query.filter_by(id=cafe_id)
#
#     if comment_form.validate_on_submit():
#
#         add_comment(cafe_id, text=comment_form.comment.data, name = current_user.name)
#
#     return render_template('show_info.html', cafe=cafe,form = comment_form,
#                            current_user = current_user,
#                            comments = comments,
#                            user = user
#                            )
#
# @app.route('/addcafe', methods=['GET','POST'])
# def add_cafe():
#     form = AddCafeForm()
#     if form.validate_on_submit():
#         cafe_name = request.form['name']
#         cafe_map_url = request.form['map_url']
#         cafe_img_url = request.form['img_url']
#         cafe_location = request.form['location']
#         has_sockets = bool(request.form.get('has_sockets'))
#         has_toilet = bool(request.form.get('has_toilet'))
#         has_wifi = bool(request.form.get('has_wifi'))
#         can_take_calls = bool(request.form.get('can_take_calls'))
#         cafe_seats = request.form['seats']
#         cafe_coffee_price = request.form['coffee_price']
#         new_cafe = Cafe(
#             name=cafe_name,
#             map_url=cafe_map_url,
#             img_url=cafe_img_url,
#             location=cafe_location,
#             has_sockets=has_sockets,
#             has_toilet=has_toilet,
#             has_wifi=has_wifi,
#             can_take_calls=can_take_calls,
#             seats=cafe_seats,
#             coffee_price=cafe_coffee_price
#         )
#         db.session.add(new_cafe)
#         db.session.commit()
#
#         return redirect(url_for('home_page'))
#
#     return render_template('addcafe.html', form=form)
#
#
# @admin_only
# @app.route('/delete_cafe/<int:cafe_id>', methods=['GET','POST'])
# def delete_cafe(cafe_id):
#     cafe = Cafe.query.get(cafe_id)
#     db.session.delete(cafe)
#     db.session.commit()
#     return redirect(url_for('home_page'))
#
#
# @app.route('/update_cafe/<int:cafe_id>', methods=['GET', 'POST'])
# def update_cafe(cafe_id):
#     form = AddCafeForm()
#     if form.validate_on_submit():
#         cafe = Cafe.query.get_or_404(cafe_id)
#         cafe.name = request.form['name']
#         cafe.map_url = request.form['map_url']
#         cafe.img_url = request.form['img_url']
#         cafe.location = request.form['location']
#         cafe.has_sockets = bool(request.form.get('has_sockets'))
#         cafe.has_toilet = bool(request.form.get('has_toilet'))
#         cafe.has_wifi = bool(request.form.get('has_wifi'))
#         cafe.can_take_calls = bool(request.form.get('can_take_calls'))
#         cafe.seats = request.form['seats']
#         cafe.coffee_price = request.form['coffee_price']
#         db.session.commit()
#         return redirect(url_for('home_page'))
#
#     return render_template('addcafe.html', form=form)
#
#
#
# @app.route('/add_comment/<int:cafe_id>', methods=['GET','POST'])
# def add_comment(cafe_id, text, name):
#     comment_text = text
#         # request.form['comment_text']
#     user_id = current_user.id
#         # cafe_id
#     new_comment = Comment(name=name,text=comment_text, user_id=user_id, cafe_id=cafe_id)
#     db.session.add(new_comment)
#     db.session.commit()
#     return redirect(url_for('show_info', cafe_id=cafe_id))
#
#
#
# @app.route('/register', methods=['GET', 'POST'])
# def register():
#     register_form = RegisterForm()
#     if register_form.validate_on_submit():
#         user = db.session.execute(db.select(User).where(User.email == register_form.email.data)).scalar()
#         if not user:
#             new_user = User(
#                 name=register_form.name.data,
#                 email=register_form.email.data,
#                 password=generate_password_hash(register_form.password.data,
#                                                 salt_length=8
#                                                 )
#             )
#             db.session.add(new_user)
#             db.session.commit()
#             login_user(new_user)
#             return redirect(url_for('home_page', logged_in=current_user.is_authenticated))
#         else:
#             flash(message='Email is already registered. Login instead.')
#             return redirect(url_for('login'))
#
#     return render_template("register.html", form=register_form)
#
#
# @app.route('/login', methods=["GET", "POST"])
# def login():
#     login_form = LoginForm()
#     if login_form.validate_on_submit():
#         login_email = login_form.email.data
#         login_passowrd = login_form.password.data
#         user = db.session.execute(db.select(User).where(User.email == login_email)).scalar()
#         if user and check_password_hash(password=login_passowrd, pwhash=user.password):
#             login_user(user)
#             return redirect(url_for('home_page'))
#         elif not user:
#             flash(message='Email is not registered.')
#             return redirect(url_for('register'))
#         elif not check_password_hash(password=login_passowrd, pwhash=user.password):
#             flash(message='Incorrect Password')
#             return redirect(url_for('login'))
#
#     return render_template("login.html", form=login_form)
#
#
# @app.route('/logout')
# def logout():
#     logout_user()
#     return redirect(url_for('home_page'))
