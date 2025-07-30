import typer
from yaml_json_diff.diff import compute_diff
from yaml_json_diff.ai_explainer import explain_diff
from rich import print

app = typer.Typer()

@app.command()
def diff(
    file1: str,
    file2: str,
    explain: bool = typer.Option(False, "--explain", "-e", help="Generate AI explanation of the diff using Ollama"),
    model: str = typer.Option("mistral", "--model", "-m", help="Model to use for explanation (default: mistral, check https://github.com/ollama/ollama for available options)")
):
    """
    Show diff between two YAML/JSON files. Use --explain to generate an AI-based summary.
    """
    try:
        result = compute_diff(file1, file2)
        if not result:
            print("[green] No differences found.[/green]")
            return

        print("[yellow] Differences found:[/yellow]")
        print(result)

        if explain:
            print("\n[bold cyan] AI Explanation:[/bold cyan]")
            explanation = explain_diff(result, model=model)
            print(explanation)

    except Exception as e:
        print(f"[red] Error:[/red] {e}")

if __name__ == "__main__":
    app()
