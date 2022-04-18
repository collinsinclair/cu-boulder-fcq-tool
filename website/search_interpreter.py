import csv


# A class that interprets a user search query
class Search:
    def __init__(self, user_search):
        self.instructor_name = None
        self.department = []
        self.departments = None
        self.college = None
        self.course = None
        self.subject = None
        self.subjects = []
        self.user_search = user_search
        self.colleges = {"arts sciences arsc": "ARSC", "leeds business busn": "BUSN", "education educ": "EDUC",
                         "engineering engr": "ENGR", "environmental design env environment": "APRL", "law laws": "LAWS",
                         "media communication information cmci info": "CMCI", "music musc": "MUSC"}

    def parse_course(self):
        """
        checks if user_search matches correct pattern (4 letters followed by 4 numbers) and sets fields if so
        examples:
        csci3010, CSCI3010, csci 3010, CSCI 3010 => self.subject = "CSCI", self.course = 3010
        astr3520, ASTR3520, astr 3520, ASTR 3520 => self.subject = "ASTR", self.course = 3520
        anth1170, ANTH1170, anth 1170, ANTH 1170 => self.subject = "ANTH", self.course = 1170
        """
        if self.user_search[:4].isalpha() and self.user_search[-4:].isnumeric():
            self.subject = self.user_search[:4].upper()
            self.course = int(self.user_search[-4:])

    def parse_college(self):
        """
        checks if and word in user_search matches any component of college keyword from colleges and if so sets 
        self.college to the college abbreviation 
        """
        for college in self.colleges:
            college_words = college.split()
            user_search_words = self.user_search.split()
            for word in user_search_words:
                if word.lower() in college_words:
                    self.college = self.colleges[college]
                    break

    def populate_departments(self):
        """
        populates self.departments with dictionary where key is the second column of fcq_departments.csv and value is 
        the first column 
        """
        self.departments = {}
        with open("website/fcq_departments.csv", "r") as f:
            reader = csv.reader(f)
            for row in reader:
                self.departments[row[0] + " " + row[1]] = row[0]

    def parse_department(self):
        """
        checks if words in user_search matches any component of department keyword from departments and if so sets 
        self.department to the department abbreviation 
        """
        self.populate_departments()
        user_words = [word.lower() for word in self.user_search.split()]
        for dept_word_list in self.departments:
            dept_words = dept_word_list.split()
            for word in dept_words:
                if word.lower() in user_words:
                    # add the key to the value in the departments dictionary
                    self.department = self.departments[dept_word_list]

    def parse_instructor(self):
        """
        only run if other fields (subject, course, college, department) are None
        break user_query into individual words and set self.instructor_name to list of words
        """
        self.instructor_name = self.user_search.split()

    def parse_all(self):
        """
        runs all parsing functions in order, stops if any of the fields are not None
        """
        self.parse_course()
        # self.parse_college()
        # self.parse_department()
        # if self.department is None and self.course is None and self.subject is None and self.college is None:
        #     self.parse_instructor()
