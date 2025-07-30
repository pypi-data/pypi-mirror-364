import click

from .object_deletion_checker import check_delete


@click.group()
def terraform():
    pass


terraform.add_command(check_delete)
