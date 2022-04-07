from os import path

from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
DB_NAME = "fcq.db"


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'csci3010'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    db.init_app(app)

    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    from .models import User

    create_database(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id_):
        return User.query.get(int(id_))

    return app


def create_database(app):
    '''
    This shouldn't be used - the database needs to exist for the app to work (it stores the FCQ data!)
    :param app:
    :return:
    '''
    if not path.exists('website/' + DB_NAME):
        db.create_all(app=app)
        print("Database created.")
