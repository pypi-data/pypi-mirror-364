# stackgpt/cli.py
import click
import openai
from stack_formatter import format_stack_response
from prompt_templates import STACK_PROMPT_TEMPLATE


def ask_stackgpt(api_key, query):
    openai.api_key = api_key

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful StackOverflow-style assistant."},
            {"role": "user", "content": STACK_PROMPT_TEMPLATE.format(user_input=query)}
        ]
    )
    return response["choices"][0]["message"]["content"].strip()


@click.command()
@click.argument("query", required=False)
@click.option("--file", "file_path", type=click.Path(exists=True), help="Optional file input instead of direct query.")
def run_cli(api_key, query, file_path):
    if file_path:
        with open(file_path, 'r') as f:
            query = f.read()
    elif not query:
        click.echo("\n[⚠️] Please provide a query or use --file option.\n")
        return

    click.echo("\n🤖 StackGPT is thinking...\n")
    try:
        response = ask_stackgpt(api_key, query)
        formatted = format_stack_response(response)
        click.echo(formatted)
    except Exception as e:
        click.echo(f"\n[❌] Error: {str(e)}\n")