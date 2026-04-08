import json
import os
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box
from rich.text import Text
from config import OUTPUT_DIR

console = Console()

SENTIMENT_COLOURS = {
    "Positive":   "green",
    "Neutral":    "cyan",
    "Concerned":  "yellow",
    "Conflicted": "magenta",
    "Negative":   "red",
}


def _sentiment_badge(label: str) -> Text:
    colour = SENTIMENT_COLOURS.get(label, "white")
    return Text(f" {label} ", style=f"bold {colour}")


# Terminal display 

def display(mom: dict, source_file: str) -> None:
    console.print()
    console.rule("[bold blue] MOM Ptype [/bold blue]")
    console.print()

    # Meeting Overview
    overview = mom.get("meeting_overview", {})
    attendees = ", ".join(overview.get("attendees", [])) or "Not detected"
    start     = overview.get("start_time", "") or "—"
    end       = overview.get("end_time",   "") or "—"
    duration  = overview.get("total_duration", "") or "—"

    console.print(Panel(
        f"[bold]Source:[/bold]    {source_file}\n"
        f"[bold]Attendees:[/bold] {attendees}\n"
        f"[bold]Start:[/bold]     {start}    [bold]End:[/bold] {end}\n"
        f"[bold]Duration:[/bold]  {duration}",
        title="[bold]Meeting Overview[/bold]",
        border_style="blue",
    ))

    # Topics Discussed
    topics = mom.get("topics_discussed", [])
    if topics:
        console.print("\n[bold underline] Topics Discussed[/bold underline]")
        for i, topic in enumerate(topics, 1):
            console.print(f"  {i}. {topic}")

    #Timeline 
    timeline = mom.get("timeline", [])
    if timeline:
        console.print("\n[bold underline] Discussion Timeline[/bold underline]")
        table = Table(box=box.SIMPLE_HEAVY, show_header=True, header_style="bold cyan")
        table.add_column("Time",    style="dim",         width=10)
        table.add_column("Speaker", style="bold",        width=20)
        table.add_column("Summary",                      width=45)
        table.add_column("Key Quote", style="italic dim", width=35)

        for entry in timeline:
            table.add_row(
                entry.get("timestamp", "—") or "—",
                entry.get("speaker",   "—"),
                entry.get("summary",   "—"),
                f'"{entry.get("key_quote", "")}"' if entry.get("key_quote") else "—",
            )
        console.print(table)

    
    decisions = mom.get("decisions_made", [])
    if decisions:
        console.print("\n[bold underline] Decisions Made[/bold underline]")
        for d in decisions:
            ts = f"[dim]{d.get('timestamp', '')}[/dim]  " if d.get("timestamp") else ""
            console.print(
                f"  {ts}[bold]{d.get('decided_by', 'Group')}:[/bold] {d.get('decision', '')}"
            )

    # Action Items - can an confidence metric also here
    actions = mom.get("action_items", [])
    if actions:
        console.print("\n[bold underline] Action Items[/bold underline]")
        table = Table(box=box.SIMPLE_HEAVY, show_header=True, header_style="bold green")
        table.add_column("Owner",    style="bold",  width=20)
        table.add_column("Task",                    width=45)
        table.add_column("Deadline", style="dim",   width=15)

        for a in actions:
            table.add_row(
                 a.get("owner",    "TBD"),
                 a.get("task",     "—"),
                 a.get("deadline", "—") or "—",
        )
    console.print(table)

    # Open Questions
    questions = mom.get("open_questions", [])
    if questions:
        console.print("\n[bold underline] Open / Unresolved Questions[/bold underline]")
        for q in questions:
            console.print(
                f"  • [dim]{q.get('raised_by', '?')}:[/dim] {q.get('question', '')}"
            )

    # Sentiment Summary
    sentiments = mom.get("sentiment_summary", [])
    if sentiments:
        console.print("\n[bold underline]🎭 Speaker Sentiment[/bold underline]")
        for s in sentiments:
            badge     = _sentiment_badge(s.get("overall_sentiment", "Neutral"))
            speaker   = s.get("speaker", "Unknown")
            reasoning = s.get("reasoning", "")
            console.print(f"  [bold]{speaker}[/bold]  ", end="")
            console.print(badge, end="")
            console.print(f"  [dim]{reasoning}[/dim]")

    mood = mom.get("meeting_mood", "")
    if mood:
        console.print(f"\n[bold]Overall Meeting Mood:[/bold] [italic]{mood}[/italic]")

    console.print()
    console.rule("[dim][/dim]")
    console.print()


# JSON save

def save_json(mom: dict, source_file: str) -> str:
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    base      = os.path.splitext(os.path.basename(source_file))[0]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_path  = os.path.join(OUTPUT_DIR, f"{base}_MoM_{timestamp}.json")

    payload = {
        "generated_at":  datetime.now().isoformat(),
        "source_file":   source_file,
        "minutes":       mom,
    }

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)

    return out_path
