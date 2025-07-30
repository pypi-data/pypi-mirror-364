import click

from .objects import inject
from .panorama import (
    cmd_commit,
    cmd_list_edited_devicegroups,
    cmd_lock,
    cmd_push,
    cmd_unlock,
)


@click.group()
@click.option("--url", envvar="PANOS_HOSTNAME", help="", required=True)
@click.option("--api-key", envvar="PANOS_API_KEY", help="", required=True)
@click.pass_obj
def panorama(obj, url, api_key):
    obj.set_url(url)
    obj.API_KEY = api_key.strip()


# panorama.add_command(objects)
inject(panorama)
panorama.add_command(cmd_lock)
panorama.add_command(cmd_unlock)
panorama.add_command(cmd_list_edited_devicegroups)
panorama.add_command(cmd_commit)
panorama.add_command(cmd_push)
