# File: interactive.py
import typer
import yaml
import os
import tempfile
import subprocess
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from langchain_core.messages import HumanMessage, SystemMessage
from llm_tests.providers import ProviderFactory

app = typer.Typer(help="LLM QA Interactive Studio")
console = Console()


def open_editor(content: str) -> str:
    """Opens the default system editor to modify the prompt (Burp Suite style)."""
    editor = os.environ.get('EDITOR', 'nano')  # Default to nano if not set
    with tempfile.NamedTemporaryFile(suffix=".txt", mode='w+', delete=False) as tf:
        tf.write(content)
        tf_path = tf.name

    try:
        subprocess.call([editor, tf_path])
        with open(tf_path, 'r') as tf:
            new_content = tf.read().strip()
    finally:
        os.remove(tf_path)
    return new_content


@app.command()
def chat(
        provider: str = typer.Option("together", help="LLM Provider"),
        tier: str = typer.Option("lite", help="Model Tier"),
        role: str = typer.Option("general", help="System Persona"),
        prompt: str = typer.Option(None, help="Direct prompt input"),
        file: str = typer.Option(None, help="Path to sideload"),
        intercept: bool = typer.Option(False, help="Enable Burp-style Interception mode"),
):
    """
    Interactive Chat Mode. Use --intercept to edit prompts before sending.
    """
    console.print(
        Panel(f"Config: [bold cyan]{provider}[/] | [bold green]{tier}[/] | [bold magenta]{role}[/]", title="QA Studio",
              border_style="blue"))

    try:
        llm = ProviderFactory.get_provider(provider, tier).get_model()
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        return

    roles = {"general": "You are a helpful assistant.", "wnba_analyst": "WNBA Expert.", "cap_expert": "CBA Expert."}
    system_text = roles.get(role, roles["general"])

    # Determine initial input
    if file:
        with open(file, 'r') as f:
            user_input = f.read()
    elif prompt:
        user_input = prompt
    else:
        user_input = typer.prompt("User")

    # Interactive Loop
    while True:
        # BURP SUITE LOGIC: Intercept
        if intercept:
            console.print("[yellow]⏸️  Intercepting... Opening Editor.[/yellow]")
            user_input = open_editor(user_input)
            console.print(f"[dim]Sending: {user_input}[/dim]")

        # Send to LLM
        messages = [SystemMessage(content=system_text), HumanMessage(content=user_input)]
        with console.status("[bold green]Thinking...[/bold green]", spinner="dots"):
            try:
                response = llm.invoke(messages)
                console.print(Panel(Markdown(response.content), title="AI Response", border_style="green"))
            except Exception as e:
                console.print(f"[bold red]API Error:[/bold red] {e}")

        # Loop continue
        if prompt or file: break  # Exit if one-shot
        try:
            user_input = typer.prompt("User")
        except KeyboardInterrupt:
            break


if __name__ == "__main__":
    app()