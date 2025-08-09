import os
from flask import Flask

def create_app(test_config=None):
    """Create and configure an instance of the Flask application."""
    app = Flask(__name__, instance_relative_config=True)

    # Set default configuration
    app.config.from_mapping(
        SECRET_KEY='dev', # Change this for production
    )

    if test_config is None:
        # Load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # Load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    with app.app_context():
        # Import and register the dashboard blueprint
        from .routes import dashboard
        app.register_blueprint(dashboard.bp)

        # Import and register the jules blueprint
        from .routes import jules
        app.register_blueprint(jules.bp)

        # Import and register the summary blueprint
        from .routes import summary
        app.register_blueprint(summary.bp)

    return app
