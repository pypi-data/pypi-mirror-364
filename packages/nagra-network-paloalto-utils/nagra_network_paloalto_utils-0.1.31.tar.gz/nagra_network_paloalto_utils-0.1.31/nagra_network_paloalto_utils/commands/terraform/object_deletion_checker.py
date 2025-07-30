import logging

import click
from nagra_network_misc_utils.gitlab import add_mr_comment

from nagra_network_paloalto_utils.utils.object_deletion_checker import (
    get_all_used_objects,
    get_objects_to_delete,
)

log = logging.getLogger(__name__)


@click.command()
@click.argument("planfile", type=click.Path(exists=True), default="plan.tfplan.txt")
@click.option("--url", envvar="PANOS_HOSTNAME", help="", required=True)
@click.option("--api-key", envvar="PANOS_API_KEY", help="", required=True)
@click.pass_obj
def check_delete(obj, planfile, url, api_key):
    """
    Check if the objects removed from the configuration are used somehwere
    """
    obj.set_url(url)
    obj.API_KEY = api_key.strip()

    objects_to_check = get_objects_to_delete(planfile)

    if not objects_to_check:
        log.info("No objects to delete")
        return
    log.info(f"Attempting to delete the following objects: {objects_to_check}")

    log.info("Checking panorama for existing relations...")
    used_objects = get_all_used_objects(obj.URL, obj.API_KEY)
    objects_in_use = list(set(used_objects) & set(objects_to_check))

    if objects_in_use:
        error_msg = f"Some objects that you are trying to delete are still in use: {', '.join(objects_in_use)}"
        log.error(error_msg)
        add_mr_comment(error_msg)
        exit(1)
    log.info("None of the object to delete are in use.")
