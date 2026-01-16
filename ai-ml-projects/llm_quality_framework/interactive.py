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

app = typer.Typer()
console = Console()


def open_editor(content: str) -> str:
    editor = os.environ.get('EDITOR', 'nano')
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
        provider: str = typer.Option("together"),
        tier: str = typer.Option("lite"),
        role: str = typer.Option("general"),
        prompt: str = typer.Option(None),
        file: str = typer.Option(None),
        intercept: bool = typer.Option(False)
):
    llm = ProviderFactory.get_provider(provider, tier).get_model()
    roles = {"general": "Helpful assistant.", "wnba_analyst": "WNBA Expert.", "cap_expert": "CBA Expert."}
    system_text = roles.get(role, roles["general"])

    if file:
        with open(file, 'r') as f:
            user_input = f.read()
    elif prompt:
        user_input = prompt
    else:
        user_input = typer.prompt("User")

    while True:
        if intercept:
            console.print("[yellow]⏸️ Intercepting...[/yellow]")
            user_input = open_editor(user_input)

        with console.status("Thinking..."):
            response = llm.invoke([SystemMessage(content=system_text), HumanMessage(content=user_input)])
            console.print(Panel(Markdown(response.content), title="AI", border_style="green"))

        if prompt or file: break
        user_input = typer.prompt("User")


if __name__ == "__main__": app()