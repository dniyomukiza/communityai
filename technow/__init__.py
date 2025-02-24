import os
from flask import Flask
from .extensions import db
from .routes import main #,login
from flask_login import LoginManager
from .models import User
from datetime import timedelta
from flask_ckeditor import CKEditor
login_manager=LoginManager()

'''
@login_manager.user_loader
def load_user(username):
    return User.query.filter_by(username=username).first()'''
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def create_app():
    app=Flask(__name__)
    creditor = CKEditor()
    app.secret_key = os.environ.get("SECRET_KEY") 
    app.config["SQLALCHEMY_DATABASE_URI"]=os.environ.get("DATAI_DB")
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['REMEMBER_COOKIE_DURATION'] = timedelta(days=7)
    app.config['REMEMBER_COOKIE_SECURE'] = True
    app.config['CKEDITOR_SERVE_LOCAL'] = True
    app.config['CKEDITOR_PKG_TYPE'] = 'basic'

    db.init_app(app)
    login_manager.init_app(app)
    app.register_blueprint(main)
    creditor.init_app(app)

    return app