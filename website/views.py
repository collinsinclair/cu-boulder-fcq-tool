import sqlalchemy as db
from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import current_user
from sqlalchemy import and_

from .search_interpreter import Search

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

    sections = split_by_section(result_set)
    instructors = get_instructors_by_section(sections)
    course_names = get_course_names(result_set)
    return render_template("search-results.html", user=current_user, raw_result=result_set, sections=sections,
                           course=search_obj.subject + " " + str(search_obj.course), instructors=instructors,
                           cnames=course_names)


def split_by_section(result_set):
    sections = {}
    for row in result_set:
        crse_type = row.CrseType.strip()
        if crse_type not in sections:
            sections[crse_type] = []
        sections[crse_type].append(row)
    return sections


def get_instructors_by_section(sections):
    instructors = {}
    for section in sections:
        instructors[section] = []
        for row in sections[section]:
            name = row.InstructorName.strip()
            if name not in instructors[section]:
                instructors[section].append(name)
    # sort each of the lists alphabetically
    for section in instructors:
        instructors[section].sort()
    return instructors


def get_course_names(result_set):
    course_names = []
    for row in result_set:
        name = row.CrseTitle.strip()
        if name not in course_names:
            course_names.append(name)
    course_names.sort()
    return course_names
