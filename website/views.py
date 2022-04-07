from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import current_user

from . import db

views = Blueprint('views', __name__)


@views.route('/', methods=["GET", "POST"])
def home():
    if request.method == 'POST':
        query = request.form.get("searchquery")
        return redirect(url_for('views.search_results', user=current_user, query=query))
    return render_template("home.html", user=current_user)


@views.route('/search-results', methods=['GET', 'POST'])
def search_results():
    query = request.args.get('query')
    result = db.engine.execute(query)
    return render_template("search-results.html", user=current_user, query=query, result=result)
