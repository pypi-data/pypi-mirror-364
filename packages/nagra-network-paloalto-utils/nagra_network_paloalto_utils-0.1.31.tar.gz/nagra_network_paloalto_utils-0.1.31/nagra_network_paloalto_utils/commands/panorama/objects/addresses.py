import csv
import logging
from pathlib import Path

import click
from nagra_network_misc_utils.gitlab import add_mr_comment

# Do not directly import the utilities: This helps for mocking in tests
from nagra_network_paloalto_utils.utils import addresses as addr_utils
from nagra_network_paloalto_utils.utils import git_writer
from nagra_network_paloalto_utils.utils.addresses_remove import (
    addresses_from_csv,
    remove_addresses,
)
from nagra_network_paloalto_utils.utils.common import yamlizer
from nagra_network_paloalto_utils.utils.common.utils import expanded
from nagra_network_paloalto_utils.utils.constants import (
    DEFAULT_GIT_DIR,
    DEFAULT_TERRAFORM_PATH,
    EMAIL_REGEX,
)

log = logging.getLogger(__name__)
# https://stackoverflow.com/questions/66743792/how-to-define-common-python-click-options-for-multiple-commands#:~:text=To%20use%20the%20same%20option%20across%20multiple%20commands,to%20a%20variable%20and%20then%20use%20it%20twice%3A
# @click.group()
# @click.option(
#     "-v",
#     "--verbose",
#     count=True,
#     default=0,
#     help="-v for DEBUG",
# )
# def addresses(verbose):
#     global VERBOSE
#     VERBOSE = verbose


@click.group()
def addresses():
    pass


@addresses.command()
@click.option("-f", "--file", type=Path)
@click.option("-a", "--address-tf-file", type=Path, default=DEFAULT_TERRAFORM_PATH)
@click.pass_obj
def remove(
    obj,
    file=None,
    address_tf_file=None,
):
    addresses = []
    if file:
        addresses.extend(addresses_from_csv(file))

    registry = addr_utils.Addresses(obj.URL, obj.API_KEY, verbose=obj.VERBOSE)
    remove_addresses(
        addresses,
        address_registry=registry,
        address_tf_file=address_tf_file,
    )


@addresses.command()
@click.option("-d", "--dest", type=Path, default="output", required=True)
@click.pass_obj
def export(obj, dest):
    registry = addr_utils.Addresses(obj.URL, obj.API_KEY)
    with Path(dest).open("x") as f:
        writer = csv.writer(f, delimiter=";")
        writer.writerow(("id", "created_by"))
        writer.writerows((key, "gui") for key in registry.addresses)


@addresses.command("generate", help="Generate missing addresses")
@click.option(
    "-f", "--file", type=Path, help="Input file with addresses", required=True
)
@click.option(
    "--repo",
    "repository",
    type=expanded,
    default="https://pano_utils:$GITLAB_TOKEN@gitlab.kudelski.com/network/paloalto/global/objects",
    help="Gitlab repository in which is the file to modify",
)
@click.option(
    "--branch",
    "branch",
    help="Reference of the branch/tag/commit (e.g. 'refs/heads/master' )",
)
@click.option(
    "-o",
    "--output",
    "output",
    default=None,
    help="File in which to output the new tags",
)
@click.option(
    "--commit_message", "commit_message", default="", help="Commit message to use"
)
@click.option(
    "--owner_email",
    "email",
    envvar="GIT_OWNER_EMAIL",
    help="email of the owner for the new tags",
)
@click.option("--test", type=bool, is_flag=True, default=False)
@click.option("--push", type=bool, is_flag=True, default=False)
@click.pass_obj
def cmd_generate_missing_addresses(
    obj,
    file,
    output,
    repository,
    branch,
    commit_message,
    email,
    push,
    test,
):
    repo = git_writer.get_repo(repository, branch=branch)

    log.debug(repo)
    input_objects = addr_utils.extract_addresses(yamlizer.get_yaml_data(file))

    addresses_from_firewall = addr_utils.Addresses(obj.URL, obj.API_KEY)
    to_create = addresses_from_firewall.find_missing(input_objects)
    emails = EMAIL_REGEX.findall(email)
    if not emails:
        log.info(f"Invalid owner email '{email}'")

    addresses_to_create, error_msg = addr_utils.prepare_addresses_to_create(
        addr_utils.check_addresses_to_create_length(to_create),
        emails[0],
    )
    if error_msg:
        # Format message in markdown
        log.error(error_msg)
        error_msg_markdown = (
            error_msg.replace("\n", "  \n")
            # .replace("\t", "")
        )
        add_mr_comment(error_msg_markdown)
        exit(1)
    if not addresses_to_create:
        log.info("No address to create.")
        return
    if test:
        log.info(f"Missing {len(addresses_to_create)} addresses")
        return
    if not repository:
        log.warn("Repository is missing")
        return
    if not output:
        log.error("output parameter is required")
        exit(1)
    # TODO: Check if the objects are already defined in `output`.
    # It may be defined but not pushed
    log.info(f"Creating {len(addresses_to_create)} addresses")
    yamlizer.add_elements_to_file(addresses_to_create, DEFAULT_GIT_DIR / output)
    git_writer.git_commit_repo(repository, output, commit_message, push=push)
    log.info("Successfully created new addresses!\n")
