"""
services/gemini.py — Gemini AI service using the new google.genai SDK
"""

import os
import asyncio
from typing import Optional

from google import genai
from google.genai import types

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
GEMINI_MODEL   = "gemini-2.0-flash"

_client: Optional[genai.Client] = None


def _get_client() -> Optional[genai.Client]:
    """Lazy-initialised singleton client."""
    global _client
    if not GEMINI_API_KEY:
        return None
    if _client is None:
        _client = genai.Client(api_key=GEMINI_API_KEY)
    return _client


def _to_sdk_history(history: list[dict]) -> list[types.Content]:
    """Convert simple {role, content} dicts to SDK Content objects."""
    contents = []
    for msg in history:
        role = msg.get("role", "user")
        text = msg.get("content", "") or "".join(msg.get("parts", []))
        if role in ("user", "model") and text:
            contents.append(
                types.Content(role=role, parts=[types.Part(text=text)])
            )
    return contents


async def get_ai_response(
    prompt: str,
    history: Optional[list[dict]] = None,
    system: str = "",
) -> str:
    """
    Async wrapper around the google.genai generate_content call.
    Returns the model's text, or a descriptive error string.
    """
    client = _get_client()
    if not client:
        return (
            "[Gemini not configured] Set the GEMINI_API_KEY environment variable "
            "to enable AI responses."
        )

    # Build contents list: history + current user turn
    contents: list[types.Content] = []
    if history:
        contents.extend(_to_sdk_history(history))
    contents.append(
        types.Content(role="user", parts=[types.Part(text=prompt)])
    )

    # Build config — attach system instruction if provided
    config = types.GenerateContentConfig(
        system_instruction=system if system else None,
        temperature=0.7,
        max_output_tokens=2048,
    )

    delays = [5, 15]
    for attempt in range(3):
        try:
            response = await asyncio.to_thread(
                client.models.generate_content,
                model=GEMINI_MODEL,
                contents=contents,
                config=config,
            )
            return response.text.strip()

        except Exception as exc:
            err = str(exc)
            is_retryable = "429" in err or "503" in err or "UNAVAILABLE" in err
            if is_retryable and attempt < 2:
                wait = delays[attempt]
                print(f"[Gemini] {'Rate limit' if '429' in err else 'Overloaded'} "
                      f"(attempt {attempt + 1}), retrying in {wait}s…")
                await asyncio.sleep(wait)
                continue
            if "429" in err:
                return "[Rate limit] Gemini API quota exceeded. Please wait and retry."
            if "503" in err or "UNAVAILABLE" in err:
                return "[Unavailable] Gemini is temporarily overloaded. Please retry shortly."
            return f"[AI Error] {err[:300]}"

    return "[AI Error] Maximum retries exceeded."
