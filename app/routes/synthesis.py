from flask import Blueprint, request, jsonify, current_app
import openai
import os

# Blueprint for synthesis routes
bp = Blueprint('synthesis', __name__, url_prefix='/api')

# The meta-prompt template as specified
META_PROMPT_TEMPLATE = """You are the MindForge Consensus Engine.

You have been given four different responses to the same user prompt from four separate expert AI systems.

Your task:

Read and analyze all responses.

Identify the strongest, most useful, and most unique ideas from each.

Merge them into a single unified Master Plan that preserves nuance but eliminates repetition.

Resolve any contradictions by choosing the most logical or widely supported approach.

Present the Master Plan in this structure:

Executive Summary (3–4 sentences)

Key Recommendations (numbered list)

Proposed Next Actions (clear, actionable steps)

Use concise, professional language.

Output ONLY the Master Plan in valid Markdown format.

Response A:
{response_a}

Response B:
{response_b}

Response C:
{response_c}

Response D:
{response_d}
"""

@bp.route('/synthesis', methods=['POST'])
def synthesize():
    """
    Receives four AI responses, synthesizes them into a Master Plan using GPT-4o,
    and returns the result.
    """
    # 1. Get data from the request
    data = request.get_json()
    if not data or 'responses' not in data:
        return jsonify({"error": "Invalid payload. 'responses' object is required."}), 400

    responses = data.get('responses')

    # 2. Get OpenAI API Key
    api_key = os.environ.get('OPENAI_API_KEY')
    if not api_key:
        current_app.logger.error("OPENAI_API_KEY environment variable not set.")
        return jsonify({"error": "Server configuration error: Missing API key."}), 500

    # 3. Format the meta-prompt
    try:
        full_prompt = META_PROMPT_TEMPLATE.format(
            response_a=responses.get('a', ''),
            response_b=responses.get('b', ''),
            response_c=responses.get('c', ''),
            response_d=responses.get('d', '')
        )
    except KeyError:
        return jsonify({"error": "Invalid 'responses' object. Keys 'a', 'b', 'c', 'd' are required."}), 400

    # 4. Call OpenAI API
    try:
        client = openai.OpenAI(api_key=api_key)
        chat_completion = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": full_prompt}]
        )
        synthesis_text = chat_completion.choices[0].message.content

        # 5. Return the synthesis
        return jsonify({"synthesis": synthesis_text})

    except openai.APIError as e:
        current_app.logger.error(f"OpenAI API Error: {e}")
        return jsonify({"error": f"An error occurred with the OpenAI API: {e}"}), 502
    except Exception as e:
        current_app.logger.error(f"An unexpected error occurred: {e}")
        return jsonify({"error": "An unexpected server error occurred."}), 500
