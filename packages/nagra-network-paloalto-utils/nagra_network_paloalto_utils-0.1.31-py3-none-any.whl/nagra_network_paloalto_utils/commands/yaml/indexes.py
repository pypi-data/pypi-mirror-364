import logging
from pathlib import Path

import click

from nagra_network_paloalto_utils.utils.common.yamlizer import get_yaml_data
from nagra_network_paloalto_utils.utils.indexes import check_indexes, extract_indexes

log = logging.getLogger(__name__)

HELP = """\
Take a file (or folder containg files, e.g. 'security-policies/data/') in yaml format defining security policies and check the indexes.
"""


@click.command("check_indexes", help=HELP)
@click.argument("file", type=Path)
def cmd_check_indexes(file):
    """
    check yaml definition of security rules and ensure that
    - the index is in the correct format (4 digits)
    - The entries are sorted by their indexes

    Below an example of file
    rules:
    -   name: ...
        index: 2000     <------------------
        description: ...
        source_zones: ...
        source_addresses:...
        destination_zones: ...
        destination_addresses: ...
        applications: ...
        services: ...
        tags: ...
    """
    input_indexes = (
        (f, extract_indexes(f, data))
        for f, data in get_yaml_data(file, with_files=True)
    )
    errors = False
    for file, indexes in input_indexes:
        errors &= check_indexes(file, indexes)
    if errors:
        log.error("Some Indexes are wrong. Please correct this before committing")
        exit(1)
    else:
        log.info("All indexes are fine.")
