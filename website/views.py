import sqlalchemy as db
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import current_user
from sqlalchemy import and_

from .search_interpreter import Search
from .course import Course, Comparison
from .get_results import query_db

views = Blueprint('views', __name__)


@views.route('/', methods=["GET", "POST"])
def home():
    if request.method == 'POST':
        user_query = request.form.get("searchquery")
        return redirect(url_for('views.get_results', user=current_user, user_query=user_query))
    return render_template("home.html", user=current_user)


@views.route('get-results')
def get_results():
    # get user query from URL
    user_query = request.args.get('user_query')
    # parse user query for subject and course
    user_search = Search(user_query)
    if user_search.subject is None or user_search.course is None:
        flash('Unable to parse search query. Please see "How to Use" below and try again.', category='error')
        return redirect(url_for("views.home", user=current_user))
    # get DB results
    result_set = query_db(user_search)
    if not result_set:
        flash('No results found. Please try again.', category='error')
        return redirect(url_for("views.home", user=current_user))

    # TODO: encapsulate this
    engine = db.create_engine('sqlite:///website/fcq.db')
    connection = engine.connect()
    metadata = db.MetaData()
    fcq = db.Table('fcq', metadata, autoload=True, autoload_with=engine)
    comparison_query = db.select([fcq]).where(
        and_(fcq.c.Sbjct == user_search.subject, fcq.c.Crse.like('%' + str(user_search.course)[0] + '%')))
    comparison_result_proxy = connection.execute(comparison_query)
    comparison_result_set = comparison_result_proxy.fetchall()

    # generate course object
    course = Course(result_set, user_search.subject, user_search.course, comparison_result_set)
    # send raw db results, course object to search-results
    return render_template("search-results.html", user=current_user, raw_result=result_set, course=course,
                           userQuery=user_query)


@views.route('/add-course')
def add_course():
    """
    add the course to the current user's courses column in the users table (if it is not already there)
    """
    user = request.args.get('user')
    result_set = request.args.get('raw_result')
    course = request.args.get('course')
    user_query_ = request.args.get('userQuery')
    print(course)
    return render_template("search-results.html", user=current_user, raw_result=result_set, course=course,
                           userQuery=user_query_)
