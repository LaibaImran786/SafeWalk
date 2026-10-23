"""Optional Gemma 4 integration. All provider details live in this file.

Talks to any OpenAI-compatible /chat/completions endpoint (Ollama, vLLM, LM Studio,
OpenRouter, ...). Configure with GEMMA_API_URL, GEMMA_MODEL and GEMMA_API_KEY in .env.
Verify the exact Gemma 4 model name for your provider before use.

If anything fails, a static tips list is returned instead, so the core safety
workflow never depends on this module.
"""
import os

import httpx

SYSTEM_PROMPT = (
    "You are a calm travel-safety assistant inside the SafeWalk app. Write at most 90 words "
    "of plain, practical text. Never claim the person is safe or in danger, never decide "
    "whether an emergency is real, and never tell the user to ignore the app's alerts."
)

FALLBACK_BRIEFING = (
    "Share your route and expected arrival time with your trusted contact. Make sure your "
    "phone is charged and location access is allowed. Keep to well-lit, busy routes where "
    "you can, and check in when SafeWalk asks."
)
FALLBACK_EXPLANATION = (
    "SafeWalk recorded this alert because a safety check-in was missed or SOS was pressed. "
    "The last known location and time are shown with the alert. Notifications in this "
    "prototype are simulated and are not delivered to the contact."
)


def _config() -> dict:
    return {
        "url": os.getenv("GEMMA_API_URL", "http://localhost:11434/v1/chat/completions"),
        "model": os.getenv("GEMMA_MODEL", "gemma4"),
        "key": os.getenv("GEMMA_API_KEY", ""),
    }


def _ask(prompt: str) -> str:
    cfg = _config()
    headers = {"Content-Type": "application/json"}
    if cfg["key"]:
        headers["Authorization"] = f"Bearer {cfg['key']}"
    body = {
        "model": cfg["model"],
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        "max_tokens": 220,
        "temperature": 0.4,
    }
    resp = httpx.post(cfg["url"], json=body, headers=headers, timeout=20.0)
    resp.raise_for_status()
    text = resp.json()["choices"][0]["message"]["content"].strip()
    if not text:
        raise ValueError("Empty AI response")
    return text


def generate_text(kind: str, traveler_name: str, destination: str,
                  checkin_interval_seconds: int | None, reason: str | None) -> dict:
    if kind == "alert_explanation":
        prompt = (
            f"Explain in plain language why SafeWalk recorded an alert for {traveler_name} "
            f"travelling to {destination}. Reason code: {reason or 'unknown'}. Mention that "
            "notifications are simulated in this prototype."
        )
        fallback = FALLBACK_EXPLANATION
    else:
        prompt = (
            f"Write a short pre-journey safety briefing for {traveler_name} travelling to "
            f"{destination}. Check-ins happen every {checkin_interval_seconds or 'few'} seconds."
        )
        fallback = FALLBACK_BRIEFING
    try:
        return {"text": _ask(prompt), "source": "gemma", "ai_available": True}
    except Exception:  # network, config, parsing: always degrade gracefully
        return {"text": fallback, "source": "fallback", "ai_available": False}
