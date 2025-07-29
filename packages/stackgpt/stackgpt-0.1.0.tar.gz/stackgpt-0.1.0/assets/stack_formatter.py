# stackgpt/stack_formatter.py

from rich.markdown import Markdown
from rich.console import Console

console = Console()

def format_stack_response(response: str) -> str:
    """
    Formats the GPT response using rich Markdown for terminal output.

    Args:
        response (str): The raw response from the GPT API.

    Returns:
        str: Empty string, as printing is handled directly by rich.
    """
    markdown = Markdown(response)
    console.print(markdown)
    return ""
