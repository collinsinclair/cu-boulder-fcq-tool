class search:
    def __init__(self, userQuery):
        self.userQuery_ = userQuery

    def toSQL(self):
        self.parseCourse()
        self.query_ = f'SELECT * FROM fcq WHERE Sbjct = {self.subject_} AND Crse = {self.courseNumber_};'

    def parseCourse(self):
        if len(self.userQuery_) == 8 and self.userQuery_[:4].isalpha() and self.userQuery_[4:].isnumeric():
            self.subject_ = self.userQuery_[:4].upper()
            self.courseNumber_ = int(self.userQuery_[4:])
