from flask import (
    Blueprint, render_template, request, jsonify, current_app
)

# Create a Blueprint
bp = Blueprint('dashboard', __name__, url_prefix='/')

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

    # Access clients from the application context
    llm_clients = current_app.llm_clients

    if not prompt_text:
        return jsonify({'error': 'No prompt was provided.'}), 400

    for llm in selected_llms:
        try:
            if llm == 'gemini':
                client = llm_clients.get('gemini')
                if not client: raise ValueError("Gemini client not configured.")
                response = client.generate_content(prompt_text)
                responses.append({'llm': 'gemini', 'response': response.text, 'model': 'gemini-1.5-flash-latest'})

            elif llm == 'chatgpt':
                client = llm_clients.get('openai')
                if not client: raise ValueError("OpenAI client not configured.")
                chat_completion = client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt_text}],
                    model="gpt-4o-latest",
                )
                responses.append({'llm': 'chatgpt', 'response': chat_completion.choices[0].message.content, 'model': 'gpt-4o-latest'})

            elif llm == 'claude':
                client = llm_clients.get('anthropic')
                if not client: raise ValueError("Anthropic client not configured.")
                message = client.messages.create(
                    model="claude-3-haiku-latest",
                    max_tokens=2048,
                    messages=[{"role": "user", "content": prompt_text}]
                )
                responses.append({'llm': 'claude', 'response': message.content[0].text, 'model': 'claude-3-haiku-latest'})

            elif llm == 'perplexity':
                client = llm_clients.get('perplexity')
                if not client: raise ValueError("Perplexity client not configured.")
                # The perplexipy library does not currently support specifying a model version.
                # It uses the default model for the authenticated user.
                response_data = client.query(prompt_text)
                responses.append({'llm': 'perplexity', 'response': response_data, 'model': 'default'})

        except Exception as e:
            error_message = f"Error calling {llm.capitalize()}: {str(e)}"
            current_app.logger.error(error_message)
            responses.append({'llm': llm, 'response': f"An error occurred with {llm.capitalize()}. Please check the logs.", 'model': 'unknown'})

    return jsonify(responses)
