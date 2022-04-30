from flask_login import UserMixin

from . import db


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    courses = db.Column(db.TEXT)


class UserCourses(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subject = db.Column(db.String(150))
    number = db.Column(db.String(150))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


class FCQ(db.Model):
    Term = db.Column(db.TEXT)
    Year = db.Column(db.INTEGER)
    Campus = db.Column(db.TEXT)
    College = db.Column(db.TEXT)
    Dept = db.Column(db.TEXT)
    Sbjct = db.Column(db.TEXT)
    Crse = db.Column(db.TEXT)
    Sect = db.Column(db.TEXT)
    CrseTitle = db.Column(db.TEXT)
    InstructorName = db.Column(db.TEXT)
    InstrGrp = db.Column(db.TEXT)
    CrseType = db.Column(db.TEXT)
    CrseLvl = db.Column(db.TEXT)
    Onlin = db.Column(db.TEXT)
    Enroll = db.Column(db.TEXT)
    NumResp = db.Column(db.TEXT)
    RespRate = db.Column(db.NUMERIC)
    HrsPerWk = db.Column(db.NUMERIC)
    Interest = db.Column(db.NUMERIC)
    Challenge = db.Column(db.NUMERIC)
    Learned = db.Column(db.NUMERIC)
    Course = db.Column(db.NUMERIC)
    Effect = db.Column(db.NUMERIC)
    Avail = db.Column(db.NUMERIC)
    Respect = db.Column(db.NUMERIC)
    Instr = db.Column(db.NUMERIC)
    SDCrse = db.Column(db.NUMERIC)
    SDInstr = db.Column(db.NUMERIC)
    id = db.Column(db.INTEGER, primary_key=True, nullable=False, unique=True)
