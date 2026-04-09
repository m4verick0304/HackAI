"""
config.py - Central configuration for PrepGenie backend.
Manages API keys and LLM client initialization.
Uses the new google.genai SDK (google-genai package).
"""

import os

# ============================================================
# API KEY CONFIGURATION
# Set your Gemini API key as environment variable:
# export GEMINI_API_KEY="your-key-here"
# ============================================================
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")

# gemini-3-flash-preview has a separate quota (2.0-flash/lite daily limit exhausted)
GEMINI_MODEL = "gemini-3-flash-preview"

_llm_client = None


def get_llm_client():
    """
    Returns initialized Gemini client (google.genai), or None if no API key.
    Uses lazy initialization + singleton pattern.
    """
    global _llm_client

    if not GEMINI_API_KEY:
        return None

    if _llm_client is not None:
        return _llm_client

    try:
        from google import genai
        _llm_client = genai.Client(api_key=GEMINI_API_KEY)
        print(f"[Config] ✅ Gemini LLM client initialized (model: {GEMINI_MODEL})")
        return _llm_client
    except ImportError:
        print("[Config] ⚠️  google-genai not installed. Run: pip3 install google-genai")
        return None
    except Exception as e:
        print(f"[Config] ❌ Failed to initialize LLM client: {e}")
        return None


def generate_text(prompt: str) -> str:
    """
    Helper: send a prompt to Gemini and return the text response.
    Retries on rate-limit (429) and server overload (503) up to 3 attempts.
    Returns empty string on failure (agents fall back to rule-based).
    """
    import time
    client = get_llm_client()
    if not client:
        return ""
    delays = [5, 15]  # Wait 5s then 15s before each retry
    for attempt in range(3):
        try:
            response = client.models.generate_content(
                model=GEMINI_MODEL,
                contents=prompt
            )
            return response.text.strip()
        except Exception as e:
            err = str(e)
            is_retryable = "429" in err or "503" in err or "UNAVAILABLE" in err
            if is_retryable and attempt < 2:
                wait = delays[attempt]
                print(f"[Config] Gemini {('rate-limit' if '429' in err else 'overloaded')} (attempt {attempt+1}), retrying in {wait}s...")
                time.sleep(wait)
                continue
            print(f"[Config] LLM error: {err[:200]}")
            return ""
    return ""
