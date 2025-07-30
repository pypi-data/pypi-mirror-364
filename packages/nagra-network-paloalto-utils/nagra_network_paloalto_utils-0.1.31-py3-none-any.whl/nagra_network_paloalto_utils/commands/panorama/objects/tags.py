import logging
from pathlib import Path

import click

from nagra_network_paloalto_utils.utils import git_writer
from nagra_network_paloalto_utils.utils import tags as tag_utils
from nagra_network_paloalto_utils.utils.common import remove as remove_utils
from nagra_network_paloalto_utils.utils.common.yamlizer import (
    add_elements_to_file,
    get_yaml_data,
)
from nagra_network_paloalto_utils.utils.constants import (
    DEFAULT_GIT_DIR,
    DEFAULT_TERRAFORM_PATH,
    EMAIL_REGEX,
    MAIN_DEVICE_GROUP,
)

log = logging.getLogger(__name__)


@click.group()
def tags():
    pass


@tags.command()
@click.option("-f", "--file", type=Path)
@click.option(
    "-a", "--tag-tf-file", "tf_file", type=Path, default=DEFAULT_TERRAFORM_PATH
)
@click.pass_obj
def remove(
    obj,
    file=None,
    tf_file=None,
):
    # TODO: Test me
    exit()
    registry = tag_utils.Tags(obj.URL, obj.API_KEY)
    remove_from_tf_file = None

    def remove_from_api(name):
        params = {
            "name": name,
            "location": "device-group",
            "device-group": MAIN_DEVICE_GROUP,
            "output-format": "json",
        }
        registry.client.objects.Tags.delete(params=params)

    if tf_file:

        def remove_from_tf_file(to_remove):
            return remove_utils.remove_from_tf_file(to_remove, tf_file, resource="tags")

    def filter_existing(entries):
        return list(registry.find_by_names(entries).keys())

    remove_utils.remove_from_csv(
        file,
        remove_from_api=remove_from_api,
        remove_from_tf_file=remove_from_tf_file,
        filter_existing=filter_existing,
    )


@tags.command("generate", help="Generate tags")
@click.option("-f", "--file", type=Path, help="Input file with tags")
@click.option(
    "--repo",
    "repository",
    default="https://pano_utils:$GITLAB_TOKEN@gitlab.kudelski.com/network/paloalto/global/objects",
    help="Gitlab repository in which is the file to modify",
)
@click.option(
    "--branch",
    "branch",
    envvar="CI_COMMIT_REF_NAME",
    help="Reference of the branch/tag/commit (e.g. 'refs/heads/master' )",
)
@click.option(
    "-o",
    "--output",
    "output",
    type=Path,
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
def cmd_generate_missing_tags(
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
    input_tags = tag_utils.extract_tags(get_yaml_data(file))
    tags_from_firewall = tag_utils.Tags(obj.URL, obj.API_KEY)
    print("input_tags:", input_tags)
    missing_tags = tags_from_firewall.find_missing(input_tags)
    print("missing_tags:", missing_tags)
    emails = EMAIL_REGEX.findall(email)
    if not emails:
        log.info(f"Invalid owner email '{email}'")
    tags_to_create = [{"name": tag, "owner": emails[0]} for tag in missing_tags]
    if not tags_to_create:
        log.info("No tag to create")
        return
    if test:
        log.info(f"Missing {len(tags_to_create)} tags")
        return
    if not repository:
        log.warn("Repository is missing")
        return
    if not output:
        log.error("output parameter is required")
        exit(1)
    # TODO: Check if the objects are already defined in `output`.
    # It may be defined but not pushed
    log.info(f"Creating {len(tags_to_create)} tag(s)")
    git_writer.get_repo(repository, branch=branch)
    add_elements_to_file(tags_to_create, DEFAULT_GIT_DIR / output)
    git_writer.git_commit_repo(repository, output, commit_message, push=push)
    log.info("Successfully created new tags!\n")
