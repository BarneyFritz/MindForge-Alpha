import os
import google.generativeai as genai
import openai
import anthropic
from perplexipy import PerplexityClient
from flask import Blueprint, request, jsonify, current_app

bp = Blueprint('summary', __name__, url_prefix='/api/summary')

# --- Load API Keys and Configure Clients ---
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY')
PERPLEXITY_API_KEY = os.environ.get('PERPLEXITY_API_KEY')

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

def get_critique(llm, text):
    """Gets a critique of the text from the specified LLM."""
    prompt = f"Please provide a brief, professional critique of the following proposal. Highlight its strongest points, its weaknesses, and any contradictions or unclear assumptions. Keep it concise (max 100 words).\n\nPROPOSAL:\n{text}"
    try:
        if llm == 'gemini':
            if not GEMINI_API_KEY: return "Gemini API key not configured."
            model = genai.GenerativeModel('gemini-1.5-flash-latest')
            response = model.generate_content(prompt)
            return response.text
        elif llm == 'chatgpt':
            if not openai_client: return "OpenAI API key not configured."
            chat_completion = openai_client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="gpt-4o-latest",
            )
            return chat_completion.choices[0].message.content
        elif llm == 'claude':
            if not anthropic_client: return "Anthropic API key not configured."
            message = anthropic_client.messages.create(
                model="claude-3-haiku-latest",
                max_tokens=1024,
                messages=[{"role": "user", "content": prompt}]
            )
            return message.content[0].text
        elif llm == 'perplexity':
            if not perplexity_client: return "Perplexity API key not configured."
            # The perplexipy library does not currently support specifying a model version.
            # It uses the default model for the authenticated user.
            response_data = perplexity_client.query(prompt)
            return response_data
    except Exception as e:
        return f"Error calling {llm.capitalize()}: {str(e)}"

@bp.route('/', methods=['POST'])
def summarize():
    """
    Handles the summary generation request, including the Debate & Critique workflow.
    """
    data = request.get_json()
    responses = data.get('responses', {})

    # --- Step 1: Cross-Critique Round ---
    critiques = {}
    llms = list(responses.keys())
    for i, llm in enumerate(llms):
        critiquer = llms[(i + 1) % len(llms)] # Rotate assignments
        critiques[llm] = get_critique(critiquer, responses[llm])

    # --- Step 2: Final Summary Round ---
    final_summary_prompt = "Act as the Lead Architect for the MindForge Alpha project. You have been given multiple proposals and their critiques. Your task is to:\n\n1. Identify areas of agreement and disagreement.\n2. Resolve contradictions where possible.\n3. Produce a concise, high-quality Executive Summary (max 300 words) with:\n   - A brief overview of the consensus direction\n   - Key recommendations\n   - 3–5 clear next actions\n\nWrite in a professional, authoritative tone.\n\n"

    final_summary_prompt += "--- ORIGINAL PROPOSALS ---\n"
    for llm, response in responses.items():
        final_summary_prompt += f"--- Proposal from {llm.upper()} ---\n{response}\n\n"

    final_summary_prompt += "--- CRITIQUES ---\n"
    for llm, critique in critiques.items():
        final_summary_prompt += f"--- Critique of {llm.upper()}'s Proposal ---\n{critique}\n\n"

    try:
        if not openai_client:
            return jsonify({'error': 'OpenAI API key not configured for final summary.'}), 500

        # gpt-5.0 is not yet available, using gpt-4o-latest instead as per user confirmation.
        chat_completion = openai_client.chat.completions.create(
            messages=[{"role": "user", "content": final_summary_prompt}],
            model="gpt-4o-latest",
        )
        summary = chat_completion.choices[0].message.content
        model_used = "gpt-4o-latest"

        return jsonify({'summary': summary, 'model': model_used})

    except Exception as e:
        current_app.logger.error(f"Error during final summary: {str(e)}")
        return jsonify({'error': 'Failed to generate final summary.'}), 500
