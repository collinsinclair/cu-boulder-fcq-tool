from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

from . import db
from .models import User

auth = Blueprint('auth', __name__)


@auth.route('/login-signup', methods=['GET', 'POST'])
def login_signup():
    if request.method == 'POST':
        username = request.form.get("username")

        if len(username) < 8:
            # username was too short
            flash("Username must be at least 8 characters.", category='error')

        elif User.query.filter_by(username=username).first():
            # user exists, sending them to login
            return redirect(url_for('auth.login', username=username, user=current_user))

        else:
            # user is new, sending them to sign-up
            return redirect(url_for('auth.sign_up', username=username, user=current_user))

    return render_template('login-signup.html', user=current_user)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    username = request.args.get('username')
    if request.method == 'POST':
        username = request.form.get("username")
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()
        if user:
            # user found
            if check_password_hash(user.password, password):
                # user found and password correct
                flash('You are logged in!', category='success')
                login_user(user, remember=True)
                return redirect(url_for('views.home'))
            else:
                # user found and password incorrect
                flash("Incorrect password.", category='error')
        else:
            # user not found
            flash("Username not found.", category='error')

    return render_template("login.html", user=current_user, username=username)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('views.home'))


@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    username = request.args.get('username')
    if request.method == 'POST':
        username = request.form.get("username")
        password1 = request.form.get("password1")
        password2 = request.form.get("password2")

        user = User.query.filter_by(username=username).first()
        if user:
            flash("username taken, please sign in or choose a different username", category='error')
        elif len(username) < 8:
            flash('username must be at least eight (8) characters', category='error')
        elif len(password1) < 8:
            flash('password must be at least eight (8) characters', category='error')
        elif password1 != password2:
            flash('passwords do not match', category='error')
        else:
            new_user = User(username=username, password=generate_password_hash(password1, method='sha256'))
            db.session.add(new_user)
            db.session.commit()
            flash('Account created!', category='success')
            login_user(user, remember=True)
            return redirect(url_for('views.home'))

    return render_template("sign-up.html", user=current_user, username=username)
