import numpy as np
import sqlalchemy as db
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import current_user, login_required

from . import db
from .course import Course
from .get_results import get_db_result, get_comparison, refine
from .models import UserCourses
from .search_interpreter import Search

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
    if user_query is None:
        flash('Empty search query. Please enter a search query and try again', category='error')
        return redirect(url_for("views.home", user=current_user))
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


@views.route('/add-course', methods=["GET", "POST"])
@login_required
def add_course():
    """
    add the course to the current user's courses column in the users table (if it is not already there)
    """
    user = current_user
    subject = request.form['subject'].upper()
    number = request.form['number']
    print('course added:', subject, number)
    course = subject + ' ' + number
    usercourses = UserCourses.query.filter_by(user_id=current_user.id).all()
    for usercourse in usercourses:
        if usercourse.subject == subject and usercourse.number == number:
            flash('Course already added.', category='success')
            return redirect(url_for('views.get_results', user=current_user, user_query=course))
    new_userCourse = UserCourses(subject=subject, number=number, user_id=current_user.id)
    db.session.add(new_userCourse)
    db.session.commit()
    flash("Course added to your schedule.", category='success')
    return redirect(url_for('views.get_results', user=current_user, user_query=course))


@views.route('/my-schedule')
@login_required
def my_schedule():
    # get user's courses from DB
    usercourses = UserCourses.query.filter_by(user_id=current_user.id).all()
    # generate course objects
    courses = []
    for usercourse in usercourses:
        result_set = get_db_result(Search(usercourse.subject + ' ' + usercourse.number))
        comparison_result_set = get_comparison(Search(usercourse.subject + ' ' + usercourse.number))
        courses.append(Course(result_set, usercourse.subject, usercourse.number, comparison_result_set))
    total_hours = np.array([0.0, 0.0, 0.0])
    for course in courses:
        total_hours += course.hpw_means_total
    # round to 2 decimal places
    total_hours = np.round(total_hours, 2)
    return render_template("my-schedule.html", user=current_user, courses=courses, total_hours=total_hours)

@views.route('/remove-course')
@login_required
def remove_course():
    subject = request.args.get('subject')
    number = request.args.get('number')
    usercourse = UserCourses.query.filter_by(user_id=current_user.id, subject=subject, number=number).first()
    db.session.delete(usercourse)
    db.session.commit()
    flash('Course removed from your schedule.', category='success')
    return redirect(url_for('views.my_schedule'))