import sqlalchemy as db
from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import current_user
from sqlalchemy import and_

from .search_interpreter import Search
from .course import Course

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
    pname = request.args.get('pname')
    search_obj = Search(user_query_)
    search_obj.parse_all()  # right now, this is really just parsing the subject and course number
    engine = db.create_engine('sqlite:///website/fcq.db')
    connection = engine.connect()
    metadata = db.MetaData()
    fcq = db.Table('fcq', metadata, autoload=True, autoload_with=engine)
    query = db.select([fcq]).where(and_(fcq.c.Sbjct == search_obj.subject, fcq.c.Crse == search_obj.course))
    result_proxy = connection.execute(query)
    result_set = result_proxy.fetchall()
    course = Course(result_set, search_obj.subject, search_obj.course)
    # sections = split_by_section(result_set)
    # instructors = get_instructors_by_section(sections)
    # course_names = get_course_names(result_set)
    # hours_per_week_figs = {}
    # hpw_means_per_section = {}
    # for section in sections:
    #     years, hrs_per_week, hpw_mean_list = prepare_lists(sections[section])
    #     hpw_means_per_section[section] = hpw_mean_list
    #     hours_per_week_figs[section] = plot_hrs_per_week(years, hrs_per_week)
    # hpw_means_total = [0, 0, 0]
    # for section in hpw_means_per_section:
    #     for i in range(3):
    #         if not np.isnan(hpw_means_per_section[section][i]):
    #             hpw_means_total[i] += hpw_means_per_section[section][i]
    # for i in range(len(hpw_means_total)):
    #     hpw_means_total[i] = round(hpw_means_total[i], 2)
    return render_template("search-results.html", user=current_user, raw_result=result_set, course=course)
