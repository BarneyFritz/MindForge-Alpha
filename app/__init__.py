import os
from flask import Flask
import google.generativeai as genai
import openai
import anthropic
from perplexipy import PerplexityClient

def create_app(test_config=None):
    """Create and configure an instance of the Flask application."""
    app = Flask(__name__, instance_relative_config=True)

    # Set default configuration
    app.config.from_mapping(
        SECRET_KEY='dev', # Change this for production
        GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY'),
        OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY'),
        ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY'),
        PERPLEXITY_API_KEY = os.environ.get('PERPLEXITY_API_KEY'),
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

    # --- LLM Client Initialization ---
    # Store clients in a dictionary on the app object
    app.llm_clients = {}

    # Configure Gemini
    if app.config['GEMINI_API_KEY']:
        genai.configure(api_key=app.config['GEMINI_API_KEY'])
        # The genai library uses a global configuration, but we can
        # store the model object for convenience.
        app.llm_clients['gemini'] = genai.GenerativeModel('gemini-1.5-flash-latest')

    # Configure OpenAI
    if app.config['OPENAI_API_KEY']:
        app.llm_clients['openai'] = openai.OpenAI(api_key=app.config['OPENAI_API_KEY'])

    # Configure Anthropic
    if app.config['ANTHROPIC_API_KEY']:
        app.llm_clients['anthropic'] = anthropic.Anthropic(api_key=app.config['ANTHROPIC_API_KEY'])

    # Configure Perplexity
    if app.config['PERPLEXITY_API_KEY']:
        app.llm_clients['perplexity'] = PerplexityClient(app.config['PERPLEXITY_API_KEY'])


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
