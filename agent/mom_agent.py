import json
import requests
from config import OLLAMA_URL, MODEL, TEMPERATURE



SYSTEM_PROMPT = """You are a precise, professional meeting analyst.
Your job is to extract structured information from meeting transcripts.

STRICT RULES — you must follow these without exception:
1. Only use information explicitly stated in the transcript. Never infer or assume.
2. If something is not mentioned, leave the field as an empty list or null.
3. Always respond with valid JSON only — no explanation, no markdown, no preamble.
4. Use the speaker's exact name as it appears in the transcript.
5. For quotes, use the speaker's actual words from the transcript.
6. Timestamps must be taken directly from the transcript. If none exist, use "".
"""

EXTRACTION_PROMPT = """Analyze this meeting transcript and extract the following.
Respond ONLY with a valid JSON object — nothing else.

TRANSCRIPT:
{transcript}

SPEAKERS PRESENT: {speakers}

Extract this exact JSON structure:
{{
  "meeting_overview": {{
    "attendees": ["list of all speaker names"],
    "start_time": "first timestamp or empty string",
    "end_time": "last timestamp or empty string",
    "total_duration": "calculated or empty string"
  }},
  "topics_discussed": [
    "topic 1", "topic 2"
  ],
  "timeline": [
    {{
      "timestamp": "HH:MM:SS or empty",
      "speaker": "speaker name",
      "summary": "one sentence summary of what they said",
      "key_quote": "most important verbatim phrase (under 20 words)"
    }}
  ],
  "decisions_made": [
    {{
      "decision": "what was decided",
      "decided_by": "speaker name or group",
      "timestamp": "when it was decided or empty"
    }}
  ],
  "action_items": [
    {{
      "task": "what needs to be done",
      "owner": "who is responsible",
      "deadline": "mentioned deadline or null",
      "confidence": "high | medium | low"
    }}
  ],
  "open_questions": [
    {{
      "question": "unresolved question",
      "raised_by": "speaker name"
    }}
  ]
}}"""

SENTIMENT_PROMPT = """Analyze the sentiment of each speaker in this meeting transcript.
Respond ONLY with a valid JSON object — nothing else.

TRANSCRIPT:
{transcript}

SPEAKERS: {speakers}

For each speaker, determine their overall sentiment and any topic-specific sentiment.
Use ONLY these sentiment labels: Positive | Neutral | Concerned | Conflicted | Negative

Return this exact structure:
{{
  "sentiment_summary": [
    {{
      "speaker": "speaker name",
      "overall_sentiment": "one of the 5 labels",
      "reasoning": "one sentence explaining why, based only on their words",
      "notable_moments": [
        {{
          "timestamp": "when or empty",
          "sentiment": "label",
          "quote": "short verbatim quote showing this sentiment"
        }}
      ]
    }}
  ],
  "meeting_mood": "overall meeting atmosphere in one sentence"
}}"""


# ── Ollama caller 
def _call_ollama(system: str, user: str) -> dict:
    """
    Send a prompt to Ollama and return parsed JSON response.
    Raises RuntimeError if the model doesn't return valid JSON.
    """
    payload = {
        "model":  MODEL,
        "format": "json",
        "stream": False,
        "options": {"temperature": TEMPERATURE},
        "messages": [
            {"role": "system",  "content": system},
            {"role": "user",    "content": user},
        ],
    }

    try:
        resp = requests.post(OLLAMA_URL, json=payload, timeout=600)
        resp.raise_for_status()
    except requests.exceptions.ConnectionError:
        raise RuntimeError(
            "Cannot connect to Ollama. Is it running? Try: ollama serve"
        )
    except requests.exceptions.Timeout:
        raise RuntimeError("Ollama timed out. The transcript may be too long.")

    raw_content = resp.json()["message"]["content"]

    raw_content = raw_content.strip()
    if raw_content.startswith("```"):
        raw_content = raw_content.split("```")[1]
        if raw_content.startswith("json"):
            raw_content = raw_content[4:]
    raw_content = raw_content.strip()

    try:
        return json.loads(raw_content)
    except json.JSONDecodeError as e:
        raise RuntimeError(
            f"Model returned invalid JSON.\nError: {e}\nRaw response:\n{raw_content[:500]}"
        )


# ── Public API 

def extract(transcript_text: str, speakers: list[str]) -> dict:
    """Pass 1: Extract MoM structure from transcript."""
    prompt = EXTRACTION_PROMPT.format(
        transcript=transcript_text,
        speakers=", ".join(speakers) if speakers else "Unknown"
    )
    return _call_ollama(SYSTEM_PROMPT, prompt)


def analyze_sentiment(transcript_text: str, speakers: list[str]) -> dict:
    """Pass 2: Analyze per-speaker sentiment."""
    prompt = SENTIMENT_PROMPT.format(
        transcript=transcript_text,
        speakers=", ".join(speakers) if speakers else "Unknown"
    )
    return _call_ollama(SYSTEM_PROMPT, prompt)


def run(transcript_text: str, speakers: list[str]) -> dict:
    """
    Run both passes and return a single combined MoM dict.
    This is the main entry point called by main.py.
    """
    extraction  = extract(transcript_text, speakers)
    sentiment   = analyze_sentiment(transcript_text, speakers)

    return {**extraction, **sentiment}