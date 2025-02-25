from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def create_app():
    app = Flask(__name__)
    app.config.from_object("config.Config")

    # Initialize the database
    db.init_app(app)

    # Import and register blueprints inside the function to avoid circular imports
    from routes.bet_routes import bet_routes
    from routes.fixture_routes import fixture_routes

    app.register_blueprint(bet_routes)
    app.register_blueprint(fixture_routes)

    with app.app_context():
        db.create_all()

    return app
