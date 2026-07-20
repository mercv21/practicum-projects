from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from .config import Config

db = SQLAlchemy()
migrate = Migrate()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    migrate.init_app(app, db)

    from . import api_views, error_handlers, views
    app.register_blueprint(views.bp)
    app.register_blueprint(api_views.bp)
    error_handlers.register_error_handlers(app)

    return app


app = create_app()
