import sys
import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

import parsers
from agent.normalizer import normalize, turns_to_text, get_speakers
from agent.mom_agent   import run
from output.writer     import display, save_json

app     = Console()
cli     = typer.Typer(add_completion=False)
console = Console()


@cli.command()
def main(
    file: str = typer.Option(..., "--file", "-f", help="Path to transcript file"),
):
    console.print(f"\n[bold blue]MoM Agent[/bold blue] — processing [cyan]{file}[/cyan]\n")

    #  Parse
    with Progress(SpinnerColumn(), TextColumn("{task.description}"), console=console) as p:
        task = p.add_task("Reading transcript...", total=None)
        try:
            raw_text = parsers.load(file)
        except FileNotFoundError as e:
            console.print(f"[red]Error:[/red] {e}")
            raise typer.Exit(1)
        except ValueError as e:
            console.print(f"[red]Unsupported format:[/red] {e}")
            raise typer.Exit(1)
        p.update(task, description="[green]✓ Transcript loaded[/green]")

    if not raw_text.strip():
        console.print("[red]Error:[/red] File appears to be empty or unreadable.")
        raise typer.Exit(1)

    # Normalize 
    with Progress(SpinnerColumn(), TextColumn("{task.description}"), console=console) as p:
        task = p.add_task("Normalizing transcript...", total=None)
        turns          = normalize(raw_text)
        transcript_text = turns_to_text(turns)
        speakers       = get_speakers(turns)
        p.update(task, description=f"[green]✓ Found {len(turns)} speaker turns, {len(speakers)} speakers[/green]")

    if not speakers:
        console.print(
            "[yellow]Warning:[/yellow] No speaker structure detected. "
            "MoM will treat the whole text as one block."
        )

    #  LLM Extraction (2 passes) 
    console.print("\n[dim]Sending to Ollama — this may take 20–60 seconds...[/dim]\n")

    with Progress(SpinnerColumn(), TextColumn("{task.description}"), console=console) as p:
        task = p.add_task("Pass 1 — Extracting timeline, decisions, action items...", total=None)
        try:
            mom = run(transcript_text, speakers)
        except RuntimeError as e:
            console.print(f"\n[red]Agent Error:[/red] {e}")
            raise typer.Exit(1)
        p.update(task, description="[green]✓ Extraction + sentiment complete[/green]")

    # Output 
    display(mom, source_file=file)

    saved = save_json(mom, source_file=file)
    console.print(f"[bold green]✓ JSON saved:[/bold green] {saved}\n")


if __name__ == "__main__":
    cli()
