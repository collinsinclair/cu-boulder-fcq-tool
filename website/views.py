from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import current_user
from sqlalchemy import select, and_
from . import db
from .models import FCQ
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
        # check that the user's input is valid, then assign the subject and course number variables
        subject_ = user_query_[:4].upper()
        course_number_ = int(user_query_[4:])

        # raw SQL query for raw results
        SQLQuery = f'SELECT * FROM fcq WHERE Sbjct = "{subject_}" AND Crse = {course_number_};'
        raw_result_ = db.session.execute(SQLQuery)

        # parse individual columns from result for summary data
        # stmt = select(FCQ).where(and_(
        #     FCQ.Sbjct == subject_,
        #     FCQ.Crse == course_number_
        # )) # TODO this is the "correct" way, but it's not working so...

        # summary_result_ = Session(engine).execute(stmt)

        enrollment = []
        # for row in raw_result_:
        #     enrollment.append(row[14])

        print(enrollment)
    else:
        raw_result_ = None
    return render_template("search-results.html", user=current_user, raw_result=raw_result_)
