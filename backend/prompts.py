ANTI_CHAOS = {
    "rounds": 1,
    "maxWords": {
        "expand": 400,
        "critique": 100,
        "synth": 250,
    },
}

CRITIQUE_PROMPT = (
    "You are reviewing an idea. List 2 strengths and 1 risk in 100 words or fewer. "
    "Respond plainly without preamble."
)

SYNTHESIS_PROMPT = (
    "Synthesize the brainstorm into: \n"
    "1) Executive Summary (<=250 words) \n"
    "2) 5-8 Key Recommendations \n"
    "3) 3-5 Next Actions \n"
    "Also list 2 key disagreements found and your chosen resolutions. Avoid repetition."
)


def cap_words(text: str, max_words: int) -> str:
    words = text.split()
    if len(words) <= max_words:
        return text
    return " ".join(words[:max_words])