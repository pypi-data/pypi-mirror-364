import click

from .checks import check_yamls
from .indexes import cmd_check_indexes


@click.group()
def yaml():
    pass


yaml.add_command(check_yamls)
yaml.add_command(cmd_check_indexes)
