"""Chat command implementation using biochatter."""

import os
from importlib.util import find_spec

import click


# Check if biochatter is available
HAS_BIOCHATTER = find_spec("biochatter") is not None

if HAS_BIOCHATTER:
    from biochatter.llm_connect import GptConversation


@click.command()
@click.option(
    "--model-name",
    "-m",
    default="gpt-4o-mini",
    help="LLM model to use (default: gpt-4o-mini)",
)
@click.option(
    "--prompts",
    "-p",
    default=None,
    help="Custom system prompts for the chat",
)
@click.option(
    "--interactive/--no-interactive",
    "-i/-n",
    default=True,
    help="Run in interactive mode (default: True)",
)
@click.option(
    "--correct/--no-correct",
    "-c/-nc",
    default=False,
    help="Correct the output of the LLM (default: False)",
)
@click.option(
    "--api-key",
    "-k",
    default=None,
    help="API key for the LLM",
)
@click.pass_context
def chat(
    ctx: click.Context,
    model_name: str,
    prompts: dict | None,
    interactive: bool,
    correct: bool,
    api_key: str | None,
) -> None:
    """
    Start a chat session with biochatter.

    This command provides an interface to the biochatter library, allowing
    interactive conversations with LLMs about biomedical knowledge.

    Args:
        ctx: The click context.
        model_name: The name of the LLM model to use.
        prompts: A dictionary of prompts for the chat. Use
            'primary_model_prompts' as the key for system prompts.
        interactive: Whether to run in interactive mode.
        correct: Whether to correct the output of the LLM.
        api_key: The API key for the LLM.

    """
    if not HAS_BIOCHATTER:
        click.echo(
            "Error: biochatter is not installed. Install it with: pip install biotope[chat]",
            err=True,
        )
        ctx.exit(1)

    try:
        # Initialize biochatter with the specified model
        conversation = GptConversation(
            model_name=model_name,
            prompts=prompts,
            correct=correct,
        )

        if api_key:
            conversation.set_api_key(api_key)
        else:
            conversation.set_api_key(os.getenv("OPENAI_API_KEY"))

        if not api_key and not os.getenv("OPENAI_API_KEY"):
            click.echo(
                "No API key provided. "
                "Please provide an API key using the --api-key option or set the OPENAI_API_KEY environment variable.",
                err=True,
            )
            ctx.exit(1)

        if interactive:
            click.echo("Starting interactive chat session (Ctrl+C to exit)")
            click.echo("----------------------------------------")

            while True:
                # Get user input
                user_input = click.prompt("You", type=str)

                if user_input.lower() in ["exit", "quit"]:
                    break

                # Get response from biochatter
                response, _, _ = conversation.query(user_input)
                click.echo("\nAssistant: " + response + "\n")

        else:
            # Read from stdin for non-interactive mode
            user_input = click.get_text_stream("stdin").read().strip()
            response, _, _ = conversation.query(user_input)
            click.echo(response)

    except KeyboardInterrupt:
        click.echo("\nChat session ended.")
    except Exception as e:
        click.echo(f"Error: {e!s}", err=True)
        ctx.exit(1)
