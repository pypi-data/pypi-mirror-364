import logging
import os

import click
from nagra_panorama_api.utils import clean_url_host

from .git_writer import cmd_push_folder
from .panorama import panorama
from .terraform import terraform
from .yaml import yaml


class AppWide:
    client = None
    VERBOSE = False
    PANORAMA = None
    URL = None
    HOSTNAME = None
    API_KEY = None
    CI_COMMIT_SHA = ""
    CI_PROJECT_TITLE = ""
    CI_COMMIT_REF_NAME = ""

    @classmethod
    def set_url(cls, url):
        url, host, _ = clean_url_host(url.strip())
        cls.URL = url
        cls.HOSTNAME = host


def os_get(var, default=None):
    return os.environ.get(var) or default


# https://stackoverflow.com/questions/66743792/how-to-define-common-python-click-options-for-multiple-commands#:~:text=To%20use%20the%20same%20option%20across%20multiple%20commands,to%20a%20variable%20and%20then%20use%20it%20twice%3A
# https://stackoverflow.com/questions/62274718/how-to-modify-back-the-context-on-a-python-click-program-or-sharing-modified-val
@click.group()
@click.option(
    "-v",
    "--verbose",
    count=True,
    default=0,
    help="-v for DEBUG",
)
@click.pass_context
def main(ctx, verbose):
    obj = AppWide
    ctx.obj = obj
    obj.VERBOSE = verbose
    obj.CI_COMMIT_SHA = os_get("CI_COMMIT_SHA", "test")
    obj.CI_PROJECT_TITLE = os_get("CI_PROJECT_TITLE", "test")
    obj.CI_COMMIT_REF_NAME = os_get("CI_COMMIT_REF_NAME", "test")
    if verbose > 2:
        logging.getLogger().setLevel(logging.DEBUG)


main.add_command(panorama)
main.add_command(terraform)
main.add_command(yaml)
main.add_command(cmd_push_folder)
