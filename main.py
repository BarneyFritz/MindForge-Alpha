import os
import google.generativeai as genai
import openai
import anthropic
from perplexipy import PerplexityClient
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Load API Keys
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY')
PERPLEXITY_API_KEY = os.environ.get('PERPLEXITY_API_KEY')

# Configure API Libraries
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
if OPENAI_API_KEY:
    openai.api_key = OPENAI_API_KEY
anthropic_client = None
if ANTHROPIC_API_KEY:
    anthropic_client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
perplexity_client = None
if PERPLEXITY_API_KEY:
    perplexity_client = PerplexityClient(PERPLEXITY_API_KEY)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
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
                responses.append({'llm': 'gemini', 'response': response.text})

            elif llm == 'chatgpt':
                if not openai.api_key: raise ValueError("OpenAI API key not configured.")
                chat_completion = openai.chat.completions.create(
                    messages=[{"role": "user", "content": prompt_text}],
                    model="gpt-4o",
                )
                responses.append({'llm': 'chatgpt', 'response': chat_completion.choices[0].message.content})

            elif llm == 'claude':
                if not anthropic_client: raise ValueError("Anthropic API key not configured.")
                message = anthropic_client.messages.create(
                    model="claude-3-haiku-20240307",
                    max_tokens=2048,
                    messages=[{"role": "user", "content": prompt_text}]
                )
                responses.append({'llm': 'claude', 'response': message.content[0].text})

            elif llm == 'perplexity':
                if not perplexity_client: raise ValueError("Perplexity API key not configured.")
                response_data = perplexity_client.query(prompt_text)
                responses.append({'llm': 'perplexity', 'response': response_data})

        except Exception as e:
            error_message = f"Error calling {llm.capitalize()}: {str(e)}"
            print(error_message)
            responses.append({'llm': llm, 'response': error_message})

    return jsonify(responses)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
