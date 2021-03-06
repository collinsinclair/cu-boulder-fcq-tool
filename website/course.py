import base64
from io import BytesIO

import numpy as np
from matplotlib.figure import Figure


def split_by_section(result_set):
    """
    Splits the result set into a dictionary of sections, where each section is a list of rows.
    :param result_set: list
    :return: dictionary
    """
    sections = {}
    for row in result_set:
        crse_type = row.CrseType.strip()
        if crse_type == "":
            continue
        if crse_type not in sections:
            sections[crse_type] = []
        sections[crse_type].append(row)
    sort_order = ['LEC', 'DSC', 'REC', 'LAB', 'MLS', 'SEM', 'FLD', 'WKS', 'STU', 'PRA', 'INT', 'CLN', 'RSC', 'OTH',
                  'DIS', 'IND']
    # sort the sections by the order in sort_order
    sections = {key: value for key, value in sorted(sections.items(), key=lambda item: sort_order.index(item[0]))}
    return sections


def convert_scale_to_hours(scale_number):
    """
    Converts the 1-6 Likert score from the FCQ data to hours
    :param scale_number: float
    :return: float
    """
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
    """
    For plotting - converts a season to a fraction of the way through a year
    :param season: string
    :return: float
    """
    if season == 'Fall':
        return 0.75
    elif season == 'Spring':
        return 0.25
    elif season == 'Summer':
        return 0.5


def convert_season_to_index(season):
    """

    :param season:
    :return:
    """
    return {'Fall': 0, 'Spring': 1, 'Summer': 2}[season]


class Course:
    """
    A class that represents a single course from CU computing and containing the information needed for the front end.
    Objects of this class contain all available information about a course (e.g., all instructors, every response
    ever recorded, etc.)
    """

    def __init__(self, result_set, subject, course_number, comparison_set):

        # store values from object creation
        self.result_set = result_set
        self.courseTitle = subject + " " + str(course_number)
        self.comparison_sections = split_by_section(comparison_set)

        # Get values for the course
        self.course_names = self.get_course_names()
        self.sections = split_by_section(self.result_set)
        self.instructors = self.get_instructors_by_section()

        # initialize empty dictionaries
        self.hours_per_week_figs = {}
        self.hpw_means_per_section = {}

        # populate hours per week dicts
        for section in self.sections:
            years, hrs_per_week, hpw_mean_list = self.prepare_lists(self.sections[section])
            self.hpw_means_per_section[section] = hpw_mean_list
            self.hours_per_week_figs[section] = self.plot_by_term(years, hrs_per_week, "Hours Per Week")

        self.hpw_means_total = np.array([0.0, 0.0, 0.0])
        for section in self.hpw_means_per_section:
            for i in range(3):
                if not np.isnan(self.hpw_means_per_section[section][i]):  # if not a nan
                    self.hpw_means_total[i] += self.hpw_means_per_section[section][i]  # add to total
        for i in range(len(self.hpw_means_total)):  # round to 2 decimal places
            self.hpw_means_total[i] = round(self.hpw_means_total[i], 2)

        self.enrollment_means = [0, 0, 0]

        self.challenge_per_section = self.get_challenge_per_section()
        self.challenge_figs_per_section = self.plot_challenge_comparison()

    def get_challenge_per_section(self):
        challenge_per_section = {}
        for section in self.sections:
            challenge_per_section[section] = []
            for row in self.sections[section]:
                # try:
                challenge_per_section[section].append(row.Challenge)
                # except ValueError:
                #     challenge_per_section[section].append(float(row.Challenge))
        return challenge_per_section

    def plot_challenge_comparison(self):
        challenges_per_section = {}
        for section in self.sections:
            single_years, single_challenge = self.prepare_lists_for_challenge(self.sections[section])
            years, challenge = self.prepare_lists_for_challenge(self.comparison_sections[section])
            fig = Figure()
            ax = fig.subplots(3, 1, sharex='col')
            seasons = ['Fall', 'Spring', 'Summer']
            for i in range(3):
                ax[i].plot(single_years[i], single_challenge[i], label=f'{self.courseTitle}', linestyle='-',
                           marker='o')
                ax[i].plot(years[i], challenge[i], label=f'Department', linestyle='-', marker='o')
                ax[i].set_title(seasons[i])
            ax[0].legend()
            ax[2].set_xlabel('Year')
            fig.supylabel('Challenege')
            buf = BytesIO()
            fig.tight_layout()
            fig.savefig(buf, format="png", dpi=300)
            # Embed the result in the html output.
            data = base64.b64encode(buf.getbuffer()).decode("ascii")
            challenges_per_section[section] = data
        return challenges_per_section

    def get_instructors_by_section(self):
        """
        Returns a dictionary of sections, where each section is a list of the (unique) instructors who have taught that
        section.
        :return: dictionary
        """
        instructors = {}
        for section in self.sections:
            instructors[section] = []
            for row in self.sections[section]:
                name = row.InstructorName.strip()
                if name not in instructors[section]:
                    instructors[section].append(name)
        # sort each of the lists alphabetically
        for section in instructors:
            instructors[section].sort()
        return instructors

    def get_course_names(self):
        """
        Returns a list of the course names in the result set.
        :return: list
        """
        course_names = []
        for row in self.result_set:
            name = row.CrseTitle.strip()
            if name not in course_names:
                course_names.append(name)
        course_names.sort()
        return course_names

    def plot_by_term(self, years, hrs_per_week, ylabel):
        seasons = ['Fall', 'Spring', 'Summer']
        fig = Figure()
        ax = fig.subplots()
        for i in range(3):
            ax.plot(years[i], hrs_per_week[i], label=seasons[i], linestyle='-', marker='o')
        ax.set_xlabel('Year')
        ax.set_ylabel(ylabel)
        ax.legend()
        buf = BytesIO()
        fig.savefig(buf, format="png", dpi=300)
        # Embed the result in the html output.
        data = base64.b64encode(buf.getbuffer()).decode("ascii")
        return data

    def average_years(self, years, hours):
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
                    try:
                        corresponding_hours.append(float(hours[i]))
                    except ValueError:
                        corresponding_hours.append(np.NaN)
            hours_list.append(np.nanmean(corresponding_hours))
        return years_list, hours_list

    def prepare_lists(self, result_set):

        # first, order the rows by year and season
        result_set.sort(key=lambda x: (int(x.Year) + convert_season_to_year(x.Term)))

        # initialize empty lists to hold the data
        hrs_per_week = [[], [], []]  # [fall, spring, summer]
        years = [[], [], []]  # [fall, spring, summer]

        # iterate through the whole result set and
        for row in result_set:
            hrs_per_week[convert_season_to_index(row.Term)].append(convert_scale_to_hours(row.HrsPerWk))
            years[convert_season_to_index(row.Term)].append(int(row.Year))

        # now average the hours per week for each season
        for i in range(3):
            years[i], hrs_per_week[i] = self.average_years(years[i], hrs_per_week[i])
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

    def prepare_lists_for_challenge(self, result_set):
        # first, order the rows by year and season
        result_set.sort(key=lambda x: (int(x.Year) + convert_season_to_year(x.Term)))
        challenge = [[], [], []]  # [fall, spring, summer]
        years = [[], [], []]  # [fall, spring, summer]
        for row in result_set:
            challenge[convert_season_to_index(row.Term)].append(row.Challenge)
            years[convert_season_to_index(row.Term)].append(int(row.Year))
        # now average the challenge for each season
        for i in range(3):
            years[i], challenge[i] = self.average_years(years[i], challenge[i])
        return years, challenge
