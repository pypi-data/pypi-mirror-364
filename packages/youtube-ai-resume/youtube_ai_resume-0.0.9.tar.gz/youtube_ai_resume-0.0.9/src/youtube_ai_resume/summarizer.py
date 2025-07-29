from __future__ import annotations
from openai import OpenAI
from .config import load

_cfg = load()
DEFAULT_MODEL      = _cfg["openai_model"]
DEFAULT_OUTPUT_LANG = _cfg["output_lang"]

SYSTEM_PROMPT = (
    "You are a professional note-taker. Produce a concise, insightful "
    "summary in {lang}. Use clear paragraphs and bullet points where helpful. "
    "Avoid filler; focus on key ideas, arguments and facts."
)

def summarize(
    transcript: str,
    api_key: str,
    model: str = DEFAULT_MODEL,
    out_lang: str = DEFAULT_OUTPUT_LANG,
) -> str:
    client = OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT.format(lang=out_lang)},
            {"role": "user",   "content": transcript},
        ],
        temperature=0.3,
    )
    return response.choices[0].message.content.strip()
