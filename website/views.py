import sqlalchemy as db
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import current_user
from sqlalchemy import and_

from .search_interpreter import Search
from .course import Course
from .get_results import get_db_result, get_comparison, refine

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

    # parse search for instructor picks
    crse_type = request.args.get('ctype')
    instr = request.args.get('instr')

    # parse user query for subject and course
    user_search = Search(user_query)
    if user_search.subject is None or user_search.course is None:
        flash('Unable to parse search query. Please see "How to Use" below and try again.', category='error')
        return redirect(url_for("views.home", user=current_user))

    # get DB results
    result_set = get_db_result(user_search)
    if not result_set:
        flash('No results found. Please try again.', category='error')
        return redirect(url_for("views.home", user=current_user))

    if crse_type:
        result_set = refine(result_set, crse_type, instr)
    comparison_result_set = get_comparison(user_search)

    # generate course object
    course = Course(result_set, user_search.subject, user_search.course, comparison_result_set)
    # send raw db results, course object to search-results
    return render_template("search-results.html", user=current_user, raw_result=result_set, course=course,
                           userQuery=user_query, refined=crse_type is not None, crse_type=crse_type, instr=instr)


@views.route('/add-course')
def add_course():
    """
    add the course to the current user's courses column in the users table (if it is not already there)
    """
    user = request.args.get('user')
