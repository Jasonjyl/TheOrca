from flask import Flask

import config
from apps.home.view import home_bp
from apps.users.view import user_bp, censor_bp
from apps.works.view import works_bp
from extends import db, bootstrap


def create_app():  # create the app that is connected to the server
    app = Flask(__name__, template_folder='../templates', static_folder='../static')
    app.config.from_object(config.DevelopmentConfig)

    db.init_app(app)  # connect the SQLAlchemy object with the app
    bootstrap.init_app(app)  # bind the bootstrap with the app

    # Blueprint
    app.register_blueprint(user_bp)
    app.register_blueprint(censor_bp)
    app.register_blueprint(works_bp)
    app.register_blueprint(home_bp)
    app.register_blueprint(works_bp)

    return app
