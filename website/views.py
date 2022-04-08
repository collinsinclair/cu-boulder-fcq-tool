from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import current_user

from . import db
from .search_interpreter import search

views = Blueprint('views', __name__)


@views.route('/', methods=["GET", "POST"])
def home():
    if request.method == 'POST':
        userQuery = request.form.get("searchquery")
        return redirect(url_for('views.search_results', user=current_user, userQuery=userQuery))
    return render_template("home.html", user=current_user)


@views.route('/search-results', methods=['GET', 'POST'])
def search_results():
    user_query_ = request.args.get('userQuery')
    if len(user_query_) == 8 and user_query_[:4].isalpha() and user_query_[4:].isnumeric():
        subject_ = user_query_[:4].upper()
        courseNumber_ = int(user_query_[4:])
        SQLQuery = f'SELECT * FROM fcq WHERE Sbjct = "{subject_}" AND Crse = {courseNumber_};'
        result = db.engine.execute(SQLQuery)
    else:
        result = None
    return render_template("search-results.html", user=current_user, result=result)
