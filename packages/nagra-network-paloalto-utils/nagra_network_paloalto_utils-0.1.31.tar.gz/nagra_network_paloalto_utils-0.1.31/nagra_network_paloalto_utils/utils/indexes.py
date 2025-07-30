import logging
import re

from glom import SKIP, glom

from .common.utils import is_sorted, is_unique

log = logging.getLogger("Index checker")


def extract_indexes(file, data):
    without_index = glom(
        data,
        (
            "rules.*",
            [lambda r: r.get("name", "<no name>") if "index" not in r else SKIP],
        ),
    )
    if without_index:
        log.error(f"""Rules {', '.join(without_index)} are missing an index.""")
        exit(1)

    indexes = glom(data, "rules.*.index")
    not_int = [str(i) for i in indexes if not isinstance(i, int)]
    if not_int:
        log.error(
            f"""Indexes {', '.join(not_int)} in file {file} are not an integer.""",
        )
        exit(1)
    return indexes


def check_format(index):
    return INDEX_FORMAT_REG.match(str(index))


INDEX_FORMAT_REG = re.compile("^\d{4}$")  # 1000 <= index <= 10000


def check_indexes(file, indexes):
    error = False
    invalid_syntax = [i for i in indexes if not check_format(i)]
    if invalid_syntax:
        log.error(
            "Indexes {} in file {} are not formatted properly. It should be composed of four digits.".format(
                "".join(invalid_syntax),
                file,
            ),
        )
        error = True
    if not is_sorted(indexes):
        log.error(f"Indexes in file {file} are not sorted properly.")
        error = True
    if not is_unique(indexes):
        log.error(f"Indexes in file {file} are not unique")
        error = True
    return error
