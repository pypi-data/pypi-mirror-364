import logging
from pathlib import Path

import click

from nagra_network_paloalto_utils.utils.checks import (
    check_duplicates,
    check_name_length,
    check_tag_presence,
)
from nagra_network_paloalto_utils.utils.common.yamlizer import get_yaml_data

log = logging.getLogger(__name__)

ENTRIES = {
    "addresses": {
        "tag": "terraform",
        "max_size": 64,
    },
    "services": {
        "tag": "terraform",
        "max_size": 64,
    },
    "tags": {
        "max_size": 64,
    },
}


@click.command("check")
@click.option(
    "-f",
    "--file",
    "source_file",
    type=Path,
    default="data",
    help="Input file with rules",
)
@click.option(
    "--top-level-entry",
    "top_level_entry",
    type=str,
    help="Top level entry of file",
)
@click.option("--tag", help="Tag to check")
@click.option("--max-size", "max_size", type=int, default=None, help="Tag to check")
def check_yamls(source_file, top_level_entry, tag, max_size):
    """
    Used here (updated on 24.11.2023):
    - https://gitlab.kudelski.com/network/paloalto/corporate/nat/-/blob/main/.gitlab-ci.yml?ref_type=heads
    - https://gitlab.kudelski.com/network/paloalto/global/objects/-/blob/master/.gitlab-ci.yml?ref_type=heads
    """
    data = {
        "tag": tag,
        "max_size": max_size,
    }
    default_tag = tag
    default_max_size = max_size
    errors = False
    for file, objects in get_yaml_data(source_file, with_files=True):
        default_loop_data = [(e, d) for e, d in ENTRIES.items() if e in objects]
        loop_data = [(top_level_entry, data)] if top_level_entry else default_loop_data
        for entry, data in loop_data:
            entries = objects[entry] if entry else objects
            tag = default_tag or data.get("tag")
            max_size = default_max_size or data.get("max_size")
            if tag:
                missing_tags = list(check_tag_presence(entries, tag))
                if missing_tags:
                    log.error(
                        f"One or more entry is missing the tag {tag} in file {file}",
                    )
                    errors = True
            if max_size:
                too_long = list(check_name_length(entries, max_size))
                if too_long:
                    log.error(
                        f"One or more entry is bigger than {max_size} chars in file {file}",
                    )
                    errors = True
            duplicates = list(check_duplicates(entries))
            if duplicates:
                log.error(
                    f"The following duplicates have been found in file {file.name}: {duplicates}",
                )
                errors = True
        if errors:
            exit(1)
