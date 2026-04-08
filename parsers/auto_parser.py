import re

ZOOM_LINE = re.compile(
    r'^(\d{1,2}:\d{2}:\d{2})\s+(.+?):\s+(.+)$'
)

TEAMS_SPEAKER = re.compile(
    r'^(.+?)\s{2,}(\d{1,2}:\d{2}(?::\d{2})?(?:\s?[AP]M)?)$'
)

MEET_LINE = re.compile(
    r'^(?:\[?(\d{1,2}:\d{2}(?::\d{2})?)\]?\s+)?([A-Z][^:]{1,40}):\s+(.+)$'
)


def _detect_format(lines: list[str]) -> str:
    for line in lines[:30]:
        if ZOOM_LINE.match(line.strip()):
            return "zoom"

    for i, line in enumerate(lines[:30]):
        if TEAMS_SPEAKER.match(line.strip()) and i + 1 < len(lines):
            return "teams"
    return "generic"


def _parse_zoom(lines: list[str]) -> str:
    out = []
    for line in lines:
        m = ZOOM_LINE.match(line.strip())
        if m:
            ts, speaker, text = m.group(1), m.group(2), m.group(3)
            out.append(f"[{ts}] {speaker}: {text}")
        elif line.strip():
            # continuation of previous speaker turn
            out.append(f"  {line.strip()}")
    return "\n".join(out)


def _parse_teams(lines: list[str]) -> str:
    out = []
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        m = TEAMS_SPEAKER.match(line)
        if m and i + 1 < len(lines):
            speaker, ts = m.group(1).strip(), m.group(2).strip()
            i += 1
            text_lines = []
            while i < len(lines) and not TEAMS_SPEAKER.match(lines[i].strip()):
                if lines[i].strip():
                    text_lines.append(lines[i].strip())
                i += 1
            if text_lines:
                out.append(f"[{ts}] {speaker}: {' '.join(text_lines)}")
        else:
            if line:
                out.append(line)
            i += 1
    return "\n".join(out)


def _parse_generic(lines: list[str]) -> str:
    """Handles Meet and any other Speaker: text format."""
    out = []
    for line in lines:
        m = MEET_LINE.match(line.strip())
        if m:
            ts      = m.group(1) or ""
            speaker = m.group(2).strip()
            text    = m.group(3).strip()
            prefix  = f"[{ts}] " if ts else ""
            out.append(f"{prefix}{speaker}: {text}")
        elif line.strip():
            out.append(line.strip())
    return "\n".join(out)


def parse(file_path: str) -> str:
    with open(file_path, "r", encoding="utf-8", errors="replace") as f:
        raw = f.read()

    lines = raw.splitlines()
    fmt   = _detect_format(lines)

    if fmt == "zoom":
        return _parse_zoom(lines)
    elif fmt == "teams":
        return _parse_teams(lines)
    else:
        return _parse_generic(lines)