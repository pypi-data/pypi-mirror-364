import logging
from pathlib import Path

import click

from nagra_network_paloalto_utils.utils.applications import (
    Applications,
    extract_applications,
)
from nagra_network_paloalto_utils.utils.common.yamlizer import get_yaml_data

log = logging.getLogger(__name__)


@click.group()
def applications():
    pass


@applications.command("generate")
@click.option("-f", "--file", type=Path, help="Input file with applications")
@click.option("--test", type=bool, is_flag=True, default=False)
# @click.option("--push", type=bool, is_flag=True, default=False)
@click.pass_obj
def generate_missing(
    obj,
    file,
    # push=False,
    test=False,
):
    if not test:
        log.error(
            "Only 'test' mode is allowed for the moment. Please add the '--test' flag"
        )
    data = list(get_yaml_data(file))
    input_objects = extract_applications(data)

    applications_from_firewall = Applications(obj.URL, obj.API_KEY)
    to_create = applications_from_firewall.find_missing(input_objects)
    if to_create:
        log.error(f"Some applications do not exist: {to_create}")
        exit(1)
        # raise ValueError

    log.info("No application missing to create")
