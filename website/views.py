import base64
from io import BytesIO

import numpy as np
import sqlalchemy as db
from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import current_user
from matplotlib.figure import Figure
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
    hours_per_week_figs = {}
    for section in sections:
        hours_per_week_figs[section] = plot_hrs_per_week(sections[section])
    return render_template("search-results.html", user=current_user, raw_result=result_set, sections=sections,
                           course=search_obj.subject + " " + str(search_obj.course), instructors=instructors,
                           cnames=course_names, hours_per_week_figs=hours_per_week_figs)


def split_by_section(result_set):
    sections = {}
    for row in result_set:
        crse_type = row.CrseType.strip()
        if crse_type == "":
            continue
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


def convert_scale_to_hours(scale_number):
    try:
        scale_number = float(scale_number)
    except ValueError:
        return np.NaN
    if 1 <= scale_number <= 1.9:
        return (10 / 3) * (scale_number - 1)
    elif 2 <= scale_number <= 2.9:
        return (20 / 9) * scale_number - (4 / 9)
    elif 3 <= scale_number <= 3.9:
        return (20 / 9) * scale_number + (1 / 3)
    elif 4 <= scale_number <= 4.9:
        return (20 / 9) * scale_number + (10 / 9)
    elif 5 <= scale_number <= 5.9:
        return (20 / 9) * scale_number + (17 / 9)
    else:  # if scale_number > 5.9
        return 16


def convert_season_to_year(season):
    if season == 'Fall':
        return 0.75
    elif season == 'Spring':
        return 0.25
    elif season == 'Summer':
        return 0.5


def convert_season_to_index(season):
    return {'Fall': 0, 'Spring': 1, 'Summer': 2}[season]


def average_years(years, hours):
    """
    Given a list of years and a list of hours, if there are any duplicates in the years list, average the hours for
    those duplicate years, then return a years list with all unique years and a corresponding hours list

    Example: if years = [2020, 2021, 2021, 2021, 2022] and hours = [5, 5, 6, 7, 6], average the hours corresponding
    year 2021 (avg(5, 6, 7) = 6) and return [2020, 2021, 2022], [5, 6, 6]
    """
    years_set = set(years)  # remove duplicates
    years_list = list(years_set)  # convert back to list
    years_list.sort()  # sort the list
    hours_list = []
    for year in years_list:
        corresponding_hours = []
        for i in range(len(years)):
            if years[i] == year:
                corresponding_hours.append(hours[i])
        hours_list.append(np.mean(corresponding_hours))
    return years_list, hours_list


def plot_hrs_per_week(result_set):
    # first, order the rows by year and season
    result_set.sort(key=lambda x: (int(x.Year) + convert_season_to_year(x.Term)))
    hrs_per_week = [[], [], []]  # [fall, spring, summer]
    years = [[], [], []]  # [fall, spring, summer]
    for row in result_set:
        hrs_per_week[convert_season_to_index(row.Term)].append(convert_scale_to_hours(row.HrsPerWk))
        years[convert_season_to_index(row.Term)].append(int(row.Year))
    # now average the hours per week for each season
    for i in range(3):
        years[i], hrs_per_week[i] = average_years(years[i], hrs_per_week[i])
    fig = Figure()
    ax = fig.subplots()
    seasons = ['Fall', 'Spring', 'Summer']
    for i in range(3):
        ax.plot(years[i], hrs_per_week[i], label=seasons[i], linestyle='-', marker='o')
    ax.set_xlabel('Year')
    ax.set_ylabel('Hours Per Week')
    ax.legend()
    buf = BytesIO()
    fig.savefig(buf, format="png")
    # Embed the result in the html output.
    data = base64.b64encode(buf.getbuffer()).decode("ascii")
    return data
