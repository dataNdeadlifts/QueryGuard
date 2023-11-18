import logging

from sql_enforcer.cli import cli

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    cli()
