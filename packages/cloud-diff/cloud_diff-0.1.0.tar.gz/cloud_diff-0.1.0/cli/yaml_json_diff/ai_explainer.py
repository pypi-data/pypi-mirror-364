import subprocess

def is_ollama_installed() -> bool:
    try:
        subprocess.run(["ollama", "--version"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except FileNotFoundError:
        return False
    except subprocess.CalledProcessError:
        return False


def explain_diff(diff_text: str, model: str = "mistral") -> str:

    if not is_ollama_installed():
            return "[red]Ollama is not installed. Please install it from https://ollama.com/download[/red]"


    prompt = (
        "You are a helpful assistant that explains differences between JSON or YAML files. "
        "Please describe the following diff output in simple, human-readable language:\n\n"
        f"{diff_text}\n\n"
        "Avoid technical syntax and focus on what changed, what was added or removed, etc."
    )

    try:
        result = subprocess.run(
            ["ollama", "run", model],
            input=prompt.encode(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True
        )
        return result.stdout.decode().strip()
    except subprocess.CalledProcessError as e:
        return f"[red]Failed to run Ollama model '{model}': {e.stderr.decode().strip()}[/red]"
