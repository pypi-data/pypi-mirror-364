import logging
import os
import re
import time
from typing import Optional

import git
import gitlab
from gitlab.exceptions import GitlabAuthenticationError, GitlabGetError
from nagra_network_misc_utils.backend_checker import check_target_pipeline_status

from .constants import DEFAULT_GIT_DIR

# API_KEY = os.environ["GITLAB_TOKEN"]


# The branch was only usef if this was supposed to be the testing branch
# Do we want to keep that ?
def get_branch(branch=None):
    if branch is None:
        branch = os.environ.get("CI_COMMIT_REF_NAME")
    if branch and re.match("^blr.*"):
        return branch
    return None


log = logging.getLogger("Git writer")


def git_push(repo, project=None):
    if repo.head.commit.diff("origin/" + repo.active_branch.name):
        repo.remote().push()
        time.sleep(10)
        if project:
            return check_target_pipeline_status(project)
        log.info("Successfully pushed!\nWaiting 30s for other pipeline")
        time.sleep(30)
    else:
        log.info("Nothing to push")
    return True


def get_repo(repo, /, dest=DEFAULT_GIT_DIR, branch=None):
    if dest.is_dir():
        log.info("Folder already exist, no need to clone")
        repo = git.Repo.init(dest)
    else:
        try:
            log.debug(f"Cloning {repo} => {dest}")
            repo = git.Repo.clone_from(repo, dest)
        except git.exc.GitCommandError as e:
            log.error(e)
    if branch:
        git_checkout(branch)
    return repo


# project option is currently never used
def git_commit_repo(repo, file_name, commit_message, push=True, project=None):
    if isinstance(repo, str):
        repo = get_repo(repo)
    repo.index.add([file_name])
    repo.index.commit(commit_message)
    if push:
        git_push(repo, project=project)
    return repo


def git_push_folder(project=None, branch=None):
    if not DEFAULT_GIT_DIR.is_dir():
        log.info(
            f"Default folder {DEFAULT_GIT_DIR} does not exist or is not a directory"
        )
        return True
    repo = git.Repo.init(DEFAULT_GIT_DIR)
    if branch:
        git_checkout(branch)
    return git_push(repo=repo, project=project)


def git_checkout(branch):
    repo = git.Git(DEFAULT_GIT_DIR)
    return repo.execute(["git", "checkout", branch])


def get_gitlab_project(
    api_key: str,
    repo_name: Optional[str] = None,
    server: str = "gitlab.kudeslki.com",
):
    gl = gitlab.Gitlab(url=server, private_token=api_key)
    try:
        gl.auth()
    except GitlabAuthenticationError:
        log.error(
            "Authentication Failed. "
            "Check the server and access token passed to the script",
        )
        raise
    if not repo_name:
        return gl
    try:
        repo_name = repo_name.strip("/")
        return gl.projects.get(repo_name)
    except GitlabGetError:
        log.error("Project does not exists")
        raise
