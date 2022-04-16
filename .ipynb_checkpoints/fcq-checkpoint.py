class Section:
    def __init__(self, term, year, campus, college, dept, subject, course, section, course_title, instructor_name,
                 instructor_group, course_type, course_level, online, enroll, num_resp, resp_rate, hours_per_week,
                 interest, challenge, learned, course_rating, effect, availability, respect, instructor, course_err,
                 instructor_err):
        self.term = term  # fall, spring, summer
        self.year = year  # 4-digit year (e.g., 2019)
        self.campus = campus  # BD = Boulder, CE = Continuing Education
        self.college = college  # 4-letter college code (e.g., BUSN = Business)
        # abbreviated department code (e.g., MB = music)
        self.department = dept
        # 4-letter subject code (e.g., ACCT = Accounting)
        self.subject = subject
        self.course = course  # 4-digit course number
        self.section = section  # section number (e.g., 105, 101R)
        self.courseTitle = course_title  # descriptive course title
        self.instructorName = instructor_name  # instructor name

        self.instructorGroup = instructor_group
        # TTT = Tenured or Tenure-Track, INST = Instructor or Senior Instructor, TA = Teaching Assistant, OTH = Other

        self.courseType = course_type  # e.g., LEC = Lecture
        # Lower (1xxx-2xxx), Upper (3xxx,4xxx), or Graduate (5xxx+)
        self.courseLevel = course_level
        self.online = online  # Y = FCQs were administered online
        self.enrollment = enroll  # number of students enrolled in the course
        self.responses = num_resp  # number of students who completed FCP
        self.responseRate = resp_rate  # percentage of students who completed FCQ

        self.hoursPerWeek = hours_per_week
        # 1.0-1.9 = 0-3 hours per week
        # 2.0-2.9 = 4-6 hours per week
        # 3.0-3.9 = 7-9 hours per week
        # 4.0-4.9 = 10-12 hours per week
        # 5.0-5.9 = 13-15 hours per week
        # 6.0 = 16+ hours per week

        self.interest = interest  # Scale: 1 = lowest, 6 = highest
        self.challenge = challenge  # Scale: 1 = lowest, 6 = highest
        self.learned = learned  # Scale: 1 = lowest, 6 = highest
        self.courseRating = course_rating  # Scale: 1 = lowest, 6 = highest
        self.effect = effect  # Scale: 1 = lowest, 6 = highest
        self.instructorAvailability = availability  # Scale: 1 = lowest, 6 = highest
        self.instructorRespect = respect  # Scale: 1 = lowest, 6 = highest
        self.instructorRating = instructor  # Scale: 1 = lowest, 6 = highest
        self.stdCourseRating = course_err  # standard deviation of course rating
        # standard deviation of instructor rating
        self.stdInstructorRating = instructor_err 


class Sections:
    def __init__(self):
        self.sections = []
        return

    def add_section(self, section: Section):
        self.sections.append(section)

    def search(self, course_id: str, min_year: int = 2010) -> list or None:
        """
Searches all sections for those that match search parameters and returns matching sections or None if no matches.
        :param course_id: alphanumeric course ID (e.g., CSCI1300, csci 1300, etc.)
        :param min_year: earliest year to include in search (e.g., 2015 will search only classes since 2015)
        :return: list of hits if there are any, else None
        """
        hits = []
        subject = course_id[0:4].upper()
        course = course_id[-4:]
        for section in self.sections:
            if section.subject == subject and section.course == course and section.year >= min_year:
                hits.append(section)
        return hits if hits else None


class Course:
    def __init__(self, subject: str, course: str, course_title: str, term: str, year: int, course_type: str,
                 instructor: str):
        self.subject = subject
        self.course = course
        # this is a list in case titles changed over the years
        self.courseTitle = [course_title]
        # counts the terms course was offered
        self.terms = {"Fall": 0, "Spring": 0, "Summer": 0}
        self.terms[term] += 1  # add term from instantiating section
        self.years = [year]  # stores years course was offered
        # stores all class types course has had
        self.courseTypes = [course_type]
        self.instructors = [instructor]
        return


class Courses:
    def __init__(self):
        self.courses = []
        return

    def add_course(self, section: Section) -> None:
        """
Checks if section already had corresponding course and updates accordingly
        :param section: a section object (corresponds to one row of data in spreadsheet)
        :return: None
        """
        found = False  # for use in search below

        # search through current list of courses and EITHER
        # 1. update existing course info with info from section OR
        # 2. if no corresponding course exists, create one
        for existing_course in self.courses:
            assert isinstance(existing_course, Course)

            # 1. update existing course info
            if existing_course.subject == section.subject and existing_course.course == section.course:
                found = True

                # update course title(s)
                # TODO some titles have a space at the front and also have a corresponding all CAPS version -
                # TODO figure out how to fix this
                if section.courseTitle not in existing_course.courseTitle:
                    existing_course.courseTitle.append(section.courseTitle)

                # update course terms (Fall, Spring, Summer)
                existing_course.terms[section.term] += 1

                # update course years offered
                if section.year not in existing_course.years:
                    existing_course.years.append(section.year)

                # add section type to course if not already present
                if section.courseType not in existing_course.courseTypes:
                    existing_course.courseTypes.append(section.courseType)

                # add instructor to course if not already present
                if section.instructorName not in existing_course.instructors:
                    existing_course.instructors.append(section.instructorName)

                break

            # 2. if no corresponding course exists, create one
        if not found:
            self.courses.append(Course(section.subject,
                                       section.course,
                                       section.courseTitle,
                                       section.term,
                                       section.year,
                                       section.courseType,
                                       section.instructorName))
        return

    def populate_courses(self, sections: Sections):
        """
Loops through all of the sections (rows in original spreadsheet) and adds them to the courses object
        :param sections: Sections object
        """
        for section in sections.sections:
            self.add_course(section)
        return

    def print_courses(self):
        """
Mainly for debugging, prints all courses in list
        """
        self.sort_courses()
        for course in self.courses:
            assert isinstance(course, Course)
            print(
                f'{course.subject}{course.course}: {course.courseTitle[0]}; Terms Offered: {course.terms}')


class Instructor:
    def __init__(self):
        return


class Instructors:
    def __init__(self):
        self.instructors = []
        return


class Department:
    def __init__(self):
        return


class Departments:
    def __init__(self):
        self.departments = []
        return
