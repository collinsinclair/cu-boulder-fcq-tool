import base64
from io import BytesIO

import numpy as np
from matplotlib.figure import Figure


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


def plot_hrs_per_week(years, hrs_per_week):
    seasons = ['Fall', 'Spring', 'Summer']
    fig = Figure()
    ax = fig.subplots()
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


def prepare_lists(result_set):
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
    # compute mean of most recent 3 years for each season
    hpw_means = []
    for i in range(3):
        current_list = hrs_per_week[i].copy()
        last_3 = []
        while (len(last_3) < 3) and (len(current_list) > 0):
            val = current_list.pop()
            if not np.isnan(val):
                last_3.append(val)
        hpw_means.append(round(np.mean(last_3), 2))
    return years, hrs_per_week, hpw_means


class Course:
    def __init__(self, result_set, subject, course_number):
        self.result_set = result_set
        self.courseTitle = subject + " " + str(course_number)
        self.sections = split_by_section(self.result_set)
        self.instructors = get_instructors_by_section(self.sections)
        self.course_names = get_course_names(self.result_set)
        self.hours_per_week_figs = {}
        self.hpw_means_per_section = {}

        for section in self.sections:
            years, hrs_per_week, hpw_mean_list = prepare_lists(self.sections[section])
            self.hpw_means_per_section[section] = hpw_mean_list
            self.hours_per_week_figs[section] = plot_hrs_per_week(years, hrs_per_week)
        self.hpw_means_total = [0, 0, 0]
        for section in self.hpw_means_per_section:
            for i in range(3):
                if not np.isnan(self.hpw_means_per_section[section][i]):
                    self.hpw_means_total[i] += self.hpw_means_per_section[section][i]
        for i in range(len(self.hpw_means_total)):
            self.hpw_means_total[i] = round(self.hpw_means_total[i], 2)
