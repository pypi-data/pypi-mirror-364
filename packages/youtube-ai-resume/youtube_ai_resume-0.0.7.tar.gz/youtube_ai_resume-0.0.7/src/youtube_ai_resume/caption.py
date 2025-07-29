"""
captions.py - support for auto-generated captions.
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
    Accept dicts with 'text' key or objects with .text attribute.
    Returns the text content of the caption chunk.
    """
    if isinstance(chunk, dict):
        return chunk.get("text", "").strip()
    # recent versions of the library return objects with .text attribute
    return getattr(chunk, "text", "").strip()

def _best_transcript(video_id: str, pref: list[str] | None) -> str:
    """
    Returns the plain text of the best available caption.
    Preference order:
      1. Manually created caption in the desired language (pref)
      2. Auto-generated caption in the desired language (pref)
      3. Any existing caption (manual or auto)
    """
    try:
        transcripts = YouTubeTranscriptApi.list_transcripts(video_id)

        transcript = None
        # 1) manually created caption in the desired language
        if pref:
            try:
                transcript = transcripts.find_manually_created_transcript(pref)
            except Exception:
                pass

        # 2) auto-generated caption in the desired language
        if not transcript and pref:
            try:
                transcript = transcripts.find_generated_transcript(pref)
            except Exception:
                pass

        # 3) pick the first available caption
        if not transcript:
            # generate list of all available language codes
            all_langs = [t.language_code for t in transcripts]
            transcript = transcripts.find_transcript(all_langs)

        data = transcript.fetch()
        return "\n".join(t for t in (_snippet_to_text(c) for c in data) if t).strip()

    except (NoTranscriptFound, TranscriptsDisabled, VideoUnavailable):
        raise RuntimeError("No captions available for this video.")


# ---- Public API -----------------------------------------------------------

def list_captions(video_id: str) -> List[str]:
    """List all available caption languages for a video."""
    try:
        tr = YouTubeTranscriptApi.list_transcripts(video_id)
        return [t.language_code for t in tr]
    except (NoTranscriptFound, TranscriptsDisabled, VideoUnavailable):
        return []


def fetch_caption(video_id: str, preferred_langs: list[str] | None = None) -> str:
    return _best_transcript(video_id, preferred_langs)
