import logging

import click

from nagra_network_paloalto_utils.utils.git_writer import (
    get_gitlab_project,
    git_push_folder,
)

log = logging.getLogger(__name__)


@click.command("push_folder")
@click.option(
    "--repository",
    "repo_name",
    help="Name of repository (e.g. network/paloalto/utils)",
)
@click.option(
    "--branch",
    "branch",
    envvar="CI_COMMIT_REF_NAME",
    help="Reference of the branch/tag/commit (e.g. 'refs/heads/master' )",
)
@click.option(
    "--git-server",
    "server",
    help="Name of server (e.g. gitlab.kudelski.com)",
    default="gitlab.kudelski.com",
)
@click.option(
    "-k",
    "--gitlab-api-key",
    "api_key",
    envvar="GITLAB_TOKEN",
    help="Token to access Gitlab API",
)
# @click.pass_obj
def cmd_push_folder(api_key, repo_name, server, branch):
    project = None
    if repo_name and api_key and server:
        project = get_gitlab_project(api_key, repo_name=repo_name, server=server)
    if not git_push_folder(project=project, branch=branch):
        exit(1)
