"""
caption.py  –  agora com suporte a legendas auto-geradas.
"""
from __future__ import annotations
from typing import List

from youtube_transcript_api import (
    YouTubeTranscriptApi,
    NoTranscriptFound,
    TranscriptsDisabled,
    VideoUnavailable,
)


def _snippet_to_text(chunk) -> str:
    """
    Aceita tanto dicts {'text': '...'} quanto FetchedTranscriptSnippet.
    """
    if isinstance(chunk, dict):
        return chunk.get("text", "").strip()
    # versões recentes da lib retornam objetos com atributo .text
    return getattr(chunk, "text", "").strip()

def _best_transcript(video_id: str, pref: list[str] | None) -> str:
    """
    Retorna texto puro da melhor legenda disponível.
    Ordem de preferência:
      1. Manual no idioma desejado (pref)
      2. Auto-gerada no idioma desejado (pref)
      3. Qualquer legenda (manual ou auto) existente
    """
    try:
        transcripts = YouTubeTranscriptApi.list_transcripts(video_id)

        transcript = None

        # 1) manual na língua desejada
        if pref:
            try:
                transcript = transcripts.find_manually_created_transcript(pref)
            except Exception:
                pass

        # 2) auto-gerada na língua desejada
        if not transcript and pref:
            try:
                transcript = transcripts.find_generated_transcript(pref)
            except Exception:
                pass

        # 3) pega a primeira legenda disponível
        if not transcript:
            # gera lista de todos os códigos de idioma disponíveis
            all_langs = [t.language_code for t in transcripts]
            transcript = transcripts.find_transcript(all_langs)

        data = transcript.fetch()
        return "\n".join(t for t in (_snippet_to_text(c) for c in data) if t).strip()

    except (NoTranscriptFound, TranscriptsDisabled, VideoUnavailable):
        raise RuntimeError("No captions available for this video.")


# ---- API pública -----------------------------------------------------------

def list_captions(video_id: str) -> List[str]:
    """Lista todos os códigos de idioma (manual + auto-gerado) disponíveis."""
    try:
        tr = YouTubeTranscriptApi.list_transcripts(video_id)
        return [t.language_code for t in tr]
    except (NoTranscriptFound, TranscriptsDisabled, VideoUnavailable):
        return []


def fetch_caption(video_id: str, preferred_langs: list[str] | None = None) -> str:
    return _best_transcript(video_id, preferred_langs)
