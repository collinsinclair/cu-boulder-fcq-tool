import sqlalchemy as db
from sqlalchemy import and_


def query_db(user_search):
    engine = db.create_engine('sqlite:///website/fcq.db')
    connection = engine.connect()
    metadata = db.MetaData()
    fcq = db.Table('fcq', metadata, autoload=True, autoload_with=engine)
    query = db.select([fcq]).where(and_(fcq.c.Sbjct == user_search.subject, fcq.c.Crse == user_search.course))
    result_proxy = connection.execute(query)
    result_set = result_proxy.fetchall()
    connection.close()
    return result_set
