from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import current_user
from sqlalchemy import select, and_
from . import db
from .models import FCQ
from .search_interpreter import Search
import sqlalchemy as db

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
    search_obj = Search(user_query_)
    search_obj.parse_all()
    engine = db.create_engine('sqlite:///website/fcq.db')
    connection = engine.connect()
    metadata = db.MetaData()
    fcq = db.Table('fcq', metadata, autoload=True, autoload_with=engine)
    query = db.select([fcq]).where(and_(fcq.c.Sbjct == search_obj.subject, fcq.c.Crse == search_obj.course))
    result_proxy = connection.execute(query)
    result_set = result_proxy.fetchall()

    return render_template("search-results.html", user=current_user, raw_result=result_set)
