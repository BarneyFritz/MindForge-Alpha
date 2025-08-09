import os
import google.generativeai as genai
import openai
import anthropic
from perplexipy import PerplexityClient
from flask import (
    Blueprint, render_template, request, jsonify, current_app
)

# Create a Blueprint
bp = Blueprint('dashboard', __name__, url_prefix='/')

# --- Load API Keys and Configure Clients ---
# This logic is now at the module level of the blueprint. It will be executed
# once when the application starts.

GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY')
PERPLEXITY_API_KEY = os.environ.get('PERPLEXITY_API_KEY')

# Configure API libraries
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

openai_client = None
if OPENAI_API_KEY:
    openai_client = openai.OpenAI(api_key=OPENAI_API_KEY)

anthropic_client = None
if ANTHROPIC_API_KEY:
    anthropic_client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

perplexity_client = None
if PERPLEXITY_API_KEY:
    perplexity_client = PerplexityClient(PERPLEXITY_API_KEY)


@bp.route('/')
def home():
    """Renders the main page."""
    return render_template('index.html')


@bp.route('/generate', methods=['POST'])
def generate():
    """Handles the LLM generation request."""
    data = request.get_json()
    prompt_text = data.get('prompt')
    selected_llms = data.get('llms', [])
    responses = []

    if not prompt_text:
        return jsonify({'error': 'No prompt was provided.'}), 400

    for llm in selected_llms:
        try:
            if llm == 'gemini':
                if not GEMINI_API_KEY: raise ValueError("Gemini API key not configured.")
                model = genai.GenerativeModel('gemini-1.5-flash-latest')
                response = model.generate_content(prompt_text)
                responses.append({'llm': 'gemini', 'response': response.text, 'model': 'gemini-1.5-flash-latest'})

            elif llm == 'chatgpt':
                if not openai_client: raise ValueError("OpenAI API key not configured.")
                chat_completion = openai_client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt_text}],
                    model="gpt-4o-latest",
                )
                responses.append({'llm': 'chatgpt', 'response': chat_completion.choices[0].message.content, 'model': 'gpt-4o-latest'})

            elif llm == 'claude':
                if not anthropic_client: raise ValueError("Anthropic API key not configured.")
                message = anthropic_client.messages.create(
                    model="claude-3-haiku-latest",
                    max_tokens=2048,
                    messages=[{"role": "user", "content": prompt_text}]
                )
                responses.append({'llm': 'claude', 'response': message.content[0].text, 'model': 'claude-3-haiku-latest'})

            elif llm == 'perplexity':
                if not perplexity_client: raise ValueError("Perplexity API key not configured.")
                # The perplexipy library does not currently support specifying a model version.
                # It uses the default model for the authenticated user.
                response_data = perplexity_client.query(prompt_text)
                responses.append({'llm': 'perplexity', 'response': response_data, 'model': 'default'})

        except Exception as e:
            error_message = f"Error calling {llm.capitalize()}: {str(e)}"
            current_app.logger.error(error_message)
            responses.append({'llm': llm, 'response': f"An error occurred with {llm.capitalize()}. Please check the logs.", 'model': 'unknown'})

    return jsonify(responses)
