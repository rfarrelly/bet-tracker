from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def create_app():
    app = Flask(__name__)
    app.config.from_object("config.Config")

    # Initialize the database
    db.init_app(app)

    # Import and register blueprints
    from routes.bet_routes import bet_routes
    from routes.fixture_routes import fixture_routes

    app.register_blueprint(bet_routes, url_prefix="/bets")
    app.register_blueprint(fixture_routes, url_prefix="/fixtures")

    with app.app_context():
        db.create_all()

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
