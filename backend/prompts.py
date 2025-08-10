CRITIQUE_PROMPT = (
    "You will critique another model's idea.\n"
    "Task: List 2 strengths and 1 risk.\n"
    "Limit to 100 words total. Be concrete."
)

SYNTHESIS_PROMPT = (
    "Synthesize the brainstorm into:\n"
    "- Executive Summary (<=250 words)\n"
    "- 5–8 Key Recommendations\n"
    "- 3–5 Next Actions\n"
    "Also list the top disagreements you observed (at least 2) and the chosen resolutions.\n"
    "Be concise and avoid repetition."
)

ANTI_CHAOS = {
    "rounds": 1,
    "maxWords": {"expand": 400, "critique": 100, "synth": 250},
}