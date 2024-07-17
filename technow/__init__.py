import os
from flask import Flask
from .extensions import db
from .routes import main #,login
from flask_login import LoginManager
from .models import User

login_manager=LoginManager()
@login_manager.user_loader
def load_user(username):
    return User.query.filter_by(username=username).first()

def create_app():
    app=Flask(__name__)
    app.secret_key = 'myappsecretkey' 
    app.config['DEBUG'] = True
    app.config["SQLALCHEMY_DATABASE_URI"]=os.environ.get("DATAI_DB")
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    login_manager.init_app(app)
    app.register_blueprint(main)

    return app