import re
from typing import Optional


TURN_PATTERN = re.compile(
    r'^\[?(\d{1,2}:\d{2}(?::\d{2})?)\]?\s+([^:\n]{2,50}):\s+(.+)$'
    r'|'
    r'^([^:\n]{2,50}):\s+(.+)$'
)

def normalize(raw_text: str) -> list[dict]:
    lines  = raw_text.splitlines()
    turns  = []
    current: Optional[dict] = None

    for line in lines:
        line = line.strip()
        if not line:
            continue

        m = TURN_PATTERN.match(line)
        if m:
            if current:
                turns.append(current)

            if m.group(1):  
                current = {
                    "timestamp": m.group(1),
                    "speaker":   m.group(2).strip(),
                    "text":      m.group(3).strip(),
                }
            else:           
                current = {
                    "timestamp": "",
                    "speaker":   m.group(4).strip(),
                    "text":      m.group(5).strip(),
                }
        else:
            if current:
                current["text"] += " " + line
            else:
               
                current = {"timestamp": "", "speaker": "Unknown", "text": line}

    if current:
        turns.append(current)

    # Fallback: if we got nothing structured, return as one block
    if not turns:
        return [{"timestamp": "", "speaker": "Unknown", "text": raw_text.strip()}]

    return turns


def turns_to_text(turns: list[dict]) -> str:
    """
    Convert normalized turns back to a clean readable string
    for feeding into the LLM prompt.
    """
    lines = []
    for t in turns:
        ts      = f"[{t['timestamp']}] " if t["timestamp"] else ""
        lines.append(f"{ts}{t['speaker']}: {t['text']}")
    return "\n".join(lines)


def get_speakers(turns: list[dict]) -> list[str]:
    """Return unique list of speakers in order of first appearance."""
    seen = []
    for t in turns:
        if t["speaker"] not in seen and t["speaker"] != "Unknown":
            seen.append(t["speaker"])
    return seen