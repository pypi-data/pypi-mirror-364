"""
speech.py – sintetiza e toca uma narração do resumo via Google Cloud TTS.
"""

from __future__ import annotations
import os, pathlib, tempfile, time
from typing import Optional

from playsound import playsound
from google.cloud import texttospeech

from .config import load

import re

_cfg = load()

# Voz padrão (PT-BR masculina).  Troque conforme necessidade.
DEFAULT_LANG  = _cfg.get("output_lang", "pt-BR")
# DEFAULT_VOICE = _cfg.get("google_voice", "pt-BR-Neural2-B")
DEFAULT_VOICE = _cfg.get("google_voice", "pt-BR-Chirp3-HD-Orus")
DEFAULT_GENDER = texttospeech.SsmlVoiceGender.MALE
DEFAULT_RATE   = 1        # 25 % mais rápido

_MARKUP = re.compile(r"[*_`~>#\-\[\]\(\)]")

def sanitize(txt: str) -> str:
    # 1) remove markdown, 2) normaliza espaços
    return re.sub(r"\s+", " ", _MARKUP.sub("", txt)).strip()

def _client() -> texttospeech.TextToSpeechClient:
    cred_path = os.path.expanduser(_cfg["google_credentials"])
    if os.path.isfile(cred_path):
        return texttospeech.TextToSpeechClient.from_service_account_file(cred_path)
    return texttospeech.TextToSpeechClient()


def speak(
    text: str,
    *,
    lang: str = DEFAULT_LANG,
    voice_name: str = DEFAULT_VOICE,
    gender: texttospeech.SsmlVoiceGender = DEFAULT_GENDER,
    rate: float = DEFAULT_RATE,
) -> pathlib.Path:
    """
    Sintetiza `text`, grava MP3 num tmp e toca.
    Retorna o caminho do arquivo gerado.
    """
    text = sanitize(text)
    if not text.strip():
        raise ValueError("Texto vazio não pode ser narrado.")

    client = _client()

    request = texttospeech.SynthesizeSpeechRequest(
        input=texttospeech.SynthesisInput(text=text),
        voice=texttospeech.VoiceSelectionParams(
            language_code=lang,
            name=voice_name,
            ssml_gender=gender,
        ),
        audio_config=texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3,
            speaking_rate=rate,
        ),
    )

    response = client.synthesize_speech(request)
    tmp = pathlib.Path(tempfile.gettempdir()) / f"yair_{int(time.time())}.mp3"
    tmp.write_bytes(response.audio_content)

    playsound(str(tmp))
    return tmp
