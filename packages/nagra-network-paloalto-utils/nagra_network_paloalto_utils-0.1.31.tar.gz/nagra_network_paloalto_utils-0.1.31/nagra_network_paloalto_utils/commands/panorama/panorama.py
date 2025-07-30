import ast
import json
import logging
from pathlib import Path

import click
from nagra_panorama_api.xmlapi import XMLApi

from nagra_network_paloalto_utils.utils.locking_panorama import try_lock, unlock_pano
from nagra_network_paloalto_utils.utils.panorama import (
    Panorama,
    commit,
    get_all_device_groups,
    get_devices_to_push,
    push,
)

log = logging.getLogger(__name__)


@click.command(
    "lock",
    help="""\
Lock Palo Alto Panorama.
The command takes a json-formatted list of firewall to lock. (default to all)""",
)
@click.option(
    "--firewalls",
    envvar="FIREWALLS",
    type=ast.literal_eval,
    default=None,
)
@click.option(
    "--all-separately",
    "separately",
    type=bool,
    is_flag=True,
    default=False,
    help="Lock all firewalls but individually",
)
@click.option("--wait-interval", type=int, default=60)
@click.option("--max-retries", type=int, default=10)
@click.pass_obj
def cmd_lock(obj, firewalls, separately, wait_interval, max_retries):
    if separately and not firewalls:
        firewalls = get_all_device_groups(obj.URL, obj.API_KEY)
    if not try_lock(
        obj.URL,
        obj.API_KEY,
        firewalls=firewalls,
        wait_interval=wait_interval,
        max_tries=max_retries,
    ):
        exit(1)


@click.command(
    "unlock",
    help="""\
Unlock Palo Alto Panorama.
The command takes a json-formatted list of firewall to lock. (default to all)""",
)
@click.option(
    "--firewalls",
    envvar="FIREWALLS",
    type=ast.literal_eval,
    default=None,
)
@click.option(
    "--all-separately",
    "separately",
    type=bool,
    is_flag=True,
    default=False,
    help="Unlock all firewalls but individually",
)
@click.pass_obj
def cmd_unlock(obj, firewalls, separately):
    panorama_instance = Panorama(obj.URL, api_key=obj.API_KEY)
    if separately and not firewalls:
        firewalls = get_all_device_groups(obj.URL, obj.API_KEY)
    if not unlock_pano(panorama_instance, firewalls):
        exit(1)


@click.command(
    "list_edited_devicegroups",
    help="Output list of device groups with uncommited changes",
)
@click.option(
    "--admin-name",
    "commiter_name",
    envvar="PANOS_ADMIN_NAME",
    help="The admin name under which to commit",
)
@click.option(
    "--out",
    type=Path,
    default=None,
    help="Output devicegroups with changes to commit into a json file",
)
@click.pass_obj
def cmd_list_edited_devicegroups(obj, commiter_name, out):
    """
    makes a partial commit under the admin name

    :return:
    """
    api = XMLApi(obj.URL, obj.API_KEY)
    result = api.uncommited_changes_summary(
        admin=commiter_name,
    )
    members = result.xpath(".//member/text()")
    if out:
        with out.open("w") as f:
            json.dump(members, f)
        return
    if members:
        print("\n".join(members))


@click.command("commit", help="Commit changes to Palo Alto Panorama")
@click.option(
    "--admin-name",
    "commiter_name",
    envvar="PANOS_ADMIN_NAME",
    help="The admin name under which to commit",
    required=True,
)
@click.option(
    "--out",
    type=Path,
    default=None,
    help="Output devicegroups with changes to commit into a json file",
)
@click.pass_obj
def cmd_commit(obj, commiter_name, out):
    """
    makes a partial commit under the admin name

    :return:
    """
    description = "Automatic commit from {} {}.(Commit SHA : {})".format(
        obj.CI_PROJECT_TITLE,
        obj.CI_COMMIT_REF_NAME,
        obj.CI_COMMIT_SHA,
    )
    if out:
        api = XMLApi(obj.URL, obj.API_KEY)
        result = api.uncommited_changes_summary(admin=commiter_name)
        members = result.xpath(".//member/text()")
        with out.open("w") as f:
            json.dump(members, f)

    res = commit(
        obj.URL,
        obj.API_KEY,
        commiter_name,
        description=description,
    )
    if res in ("fail", "error"):
        log.error(
            "Error. This is most likely because someone else is performing maintenance on the firewall."
            " You will need to manually commit-all",
        )
        exit(1)
    if res == "success":
        log.info("Commit done.")
    if res == "unchanged":
        log.info("Same configuration nothing to commit")
        # We should revert the changes..
        # revert_config(obj.URL, obj.API_KEY, commiter_name)
        return


# https://click.palletsprojects.com/en/8.0.x/options/#callbacks-and-eager-options
# https://stackoverflow.com/questions/47631914/how-to-pass-several-list-of-arguments-to-click-option
class PythonLiteralOption(click.Option):
    def type_cast_value(self, ctx, value):
        try:
            return ast.literal_eval(value)
        except Exception:  # noqa
            pass
        if isinstance(value, str):
            value = value.strip()
        if not value:
            return None
        return [d.strip() for d in value.split(",")]


@click.command("push", help="Push changes to Firewalls")
@click.option(
    "--devicegroups",
    "devicegroups",
    envvar="FIREWALLS",
    # type=ast.literal_eval,
    cls=PythonLiteralOption,
    default=None,
)
@click.option(
    "--admin",
    "admin",
    envvar="PANOS_ADMIN_NAME",
    help="The admin name that is pushing",
)
@click.option(
    "--push-all",
    "push_all",
    type=bool,
    is_flag=True,
    default=False,
    help="Push on all devices instead of just the one of the push scope",
)
@click.option(
    "--sync/--no-sync",  # True/False flags
    "sync",
    type=bool,
    is_flag=True,
    default=True,
    help="Wait for job completion",
)
@click.pass_obj
def cmd_push(obj, devicegroups, admin, push_all, sync):
    """
    makes a partial commit under the admin name

    :return:
    """
    devicegroups = get_devices_to_push(
        obj.URL,
        obj.API_KEY,
        devicegroups=devicegroups,
        admin=admin,
        push_scope_only=(not push_all),
    )
    if not devicegroups:
        log.info("Empty list of device group provided: no push to do")
        return
    error = push(obj.URL, obj.API_KEY, devicegroups, sync=sync)
    exit(1 if error else 0)
