import click
from .bot import run

@click.command()
def run_bot():
    """Run the bot."""
    run()

if __name__ == '__main__':
    run_bot()
