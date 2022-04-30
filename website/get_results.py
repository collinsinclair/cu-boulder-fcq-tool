import sqlalchemy as db
from sqlalchemy import and_


def get_db_result(user_search):
    engine = db.create_engine('sqlite:///website/fcq.db')
    connection = engine.connect()
    metadata = db.MetaData()
    fcq = db.Table('fcq', metadata, autoload=True, autoload_with=engine)
    query = db.select([fcq]).where(and_(fcq.c.Sbjct == user_search.subject, fcq.c.Crse == user_search.course))
    result_proxy = connection.execute(query)
    result_set = result_proxy.fetchall()
    connection.close()
    return result_set


def get_comparison(user_search):
    engine = db.create_engine('sqlite:///website/fcq.db')
    connection = engine.connect()
    metadata = db.MetaData()
    fcq = db.Table('fcq', metadata, autoload=True, autoload_with=engine)
    comparison_query = db.select([fcq]).where(
        and_(fcq.c.Sbjct == user_search.subject, fcq.c.Crse.like('%' + str(user_search.course)[0] + '%')))
    comparison_result_proxy = connection.execute(comparison_query)
    comparison_result_set = comparison_result_proxy.fetchall()
    connection.close()
    return comparison_result_set


def refine(result_set: list, crse_type, instr) -> list:
    refined_set = []
    for row in result_set:
        rows_course_type = row.CrseType
        if ((crse_type == rows_course_type) and (instr == row.InstructorName)) or (crse_type != rows_course_type):
            refined_set.append(row)
            continue
    return refined_set
