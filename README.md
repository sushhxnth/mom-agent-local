# MoM Agent

A local-first, LLM-powered pipeline that ingests raw meeting transcripts and produces structured, hallucination-constrained Minutes of Meeting. No cloud dependency. No data leaves your machine.

---

## What it does

Takes any transcript file — plain text, Word, PDF, or auto-generated exports from Zoom, Teams, or Meet — normalizes it into speaker turns, runs two sequential LLM passes over it, and outputs a clean MoM both to the terminal and as a JSON file.

Pass 1 extracts the structural content: timeline, decisions, action items, open questions. Pass 2 runs sentiment analysis per speaker independently on the same transcript. Results are merged into a single output. The model is instructed at temperature 0.1 with explicit grounding constraints — it only works from what is literally present in the transcript.

---

## Stack

- **Runtime** — Python 3.10+
- **LLM** — Ollama (`llama3.1:8b`) running locally
- **PDF parsing** — `pdfplumber`
- **DOCX parsing** — `python-docx`
- **CLI** — `typer`
- **Terminal output** — `rich`

---

## Requirements

Ollama must be installed and running locally with `llama3.1:8b` pulled.

```bash
ollama pull llama3.1:8b
ollama serve
```

Install Python dependencies:

```bash
pip install python-docx pdfplumber typer rich requests
```

---

## Usage

```bash
python main.py --file path/to/transcript.txt
python main.py --file meeting.pdf
python main.py --file zoom_export.vtt
```

Output is printed to the terminal and saved as JSON under `output/`.

---

## Project Structure

```
mom-agent/
├── main.py                  # CLI entry point
├── config.py                # LLM provider config, swap Ollama -> Gemini/Claude here
├── parsers/
│   ├── __init__.py          # Format detection and parser dispatch
│   ├── txt_parser.py
│   ├── docx_parser.py
│   ├── pdf_parser.py
│   └── auto_parser.py       # Zoom / Teams / Meet format handling
├── agent/
│   ├── normalizer.py        # Produces unified {speaker, timestamp, text} turn list
│   └── mom_agent.py         # Two-pass Ollama extraction logic
├── output/
│   └── writer.py            # Rich terminal display + JSON serialization
└── sample_transcripts/
    └── sample_zoom.txt
```

---

## Output Schema

```json
{
  "meeting_overview": { "attendees", "start_time", "end_time", "total_duration" },
  "topics_discussed": [],
  "timeline": [ { "timestamp", "speaker", "summary", "key_quote" } ],
  "decisions_made": [ { "decision", "decided_by", "timestamp" } ],
  "action_items": [ { "task", "owner", "deadline", "confidence" } ],
  "open_questions": [ { "question", "raised_by" } ],
  "sentiment_summary": [ { "speaker", "overall_sentiment", "reasoning", "notable_moments" } ],
  "meeting_mood": ""
}
```

---

## Swapping the LLM

The provider is fully abstracted in `config.py`. To switch from Ollama to Gemini or Claude, change `PROVIDER`, `MODEL`, and `OLLAMA_URL` there. The rest of the codebase is provider-agnostic.

---

## Roadmap

- Chunking with overlap window for transcripts exceeding context limits
- Prompt templates externalized to YAML config
- Multilingual and code-switched transcript support
- Batch processing across a directory of transcripts
- Portal API integration layer

---

## Constraints

This is a prototype. It processes transcripts that fit within `llama3.1:8b`'s 128k context window — roughly 1 to 2 hours of meeting content. Chunking support is on the roadmap. The model does not guarantee perfect attribution on overlapping or unclear speaker turns; the normalizer flags these as `Unknown`.
