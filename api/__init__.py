from flask import Flask
from .models import User, Todo
from .extensions import db, migrate, jwt, limiter
from .routes import main
from .config import TestConfig, Config




def create_app(config_name=''):
    app = Flask(__name__)

    if config_name == 'testing':
        app.config.from_object(TestConfig)
    else:
        app.config.from_object(Config)

    #initialise extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    if config_name != 'testing':
        limiter.init_app(app)

    #registers the routes
    app.register_blueprint(main)

    return app 