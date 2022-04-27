import sqlalchemy as db
from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import current_user
from sqlalchemy import and_

from .search_interpreter import Search
from .course import Course, Comparison

views = Blueprint('views', __name__)


@views.route('/', methods=["GET", "POST"])
def home():
    if request.method == 'POST':
        user_query = request.form.get("searchquery")
        return redirect(url_for('views.search_results', user=current_user, userQuery=user_query))
    return render_template("home.html", user=current_user)


@views.route('/search-results', methods=['GET', 'POST'])
def search_results():
    user_query_ = request.args.get('userQuery')
    search_obj = Search(user_query_)
    search_obj.parse_all()  # right now, this is really just parsing the subject and course number
    engine = db.create_engine('sqlite:///website/fcq.db')
    connection = engine.connect()
    metadata = db.MetaData()
    fcq = db.Table('fcq', metadata, autoload=True, autoload_with=engine)
    query = db.select([fcq]).where(and_(fcq.c.Sbjct == search_obj.subject, fcq.c.Crse == search_obj.course))
    result_proxy = connection.execute(query)
    result_set = result_proxy.fetchall()

    # query that returns all the courses with the same Sbjct and thousands place of Crse (e.g., if Crse is 3010,
    # then all courses with Crse 3xxx)
    comparison_query = db.select([fcq]).where(
        and_(fcq.c.Sbjct == search_obj.subject, fcq.c.Crse.like('%' + str(search_obj.course)[0] + '%')))
    comparison_result_proxy = connection.execute(comparison_query)
    comparison_result_set = comparison_result_proxy.fetchall()
    course = Course(result_set, search_obj.subject, search_obj.course, comparison_result_set)

    return render_template("search-results.html", user=current_user, raw_result=result_set, course=course,
                           userQuery=user_query_)


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
