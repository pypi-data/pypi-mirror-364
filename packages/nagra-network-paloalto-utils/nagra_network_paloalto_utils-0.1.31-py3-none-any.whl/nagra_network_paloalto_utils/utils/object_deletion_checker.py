import logging
import re
from pathlib import Path

from . import rules_getter
from .panorama import get_all_device_groups

# PLAN = os.environ["PLAN"]

log = logging.getLogger("Object Deletion Checker")

# TF_PLAN_SUMMARY_REG = re.compile("Plan: \d* to add, \d* to change, \d* to destroy.\s")
# TF_UNCHANGED_REG = re.compile("\s*# \(\d* unchanged (blocks|attributes) hidden\)\s")
# TF_MUTATED_REG = re.compile('(^\s*# module(.\d*)*\["\S*"\] will be (updated in-place|created))')
# TF_DESTROYED_REG = re.compile("""(\s*# module(.\d*)*\["([^"]*)"\] will be destroyed)""")
TF_DESTROYED_REG = re.compile("""\s*# module.*\["([^"]*)"\] will be destroyed""")


def get_objects_to_delete(plan_file):
    with Path(plan_file).open() as tf:
        lines = tf.readlines()
    # Nb: Currently, the key used for the module is the name of the object
    # We can simply parse the line containing the acction (update,create,destroy)
    return list(
        filter(
            None,
            (
                # Retrieve the names in quotes for entry to delete
                next(iter(TF_DESTROYED_REG.findall(line)), None)
                for line in lines
            ),
        )
    )


def get_all_used_objects(url, api_key):
    dgs = get_all_device_groups(url, api_key)

    data = rules_getter.get_all_rules(url, api_key, dgs)
    used_objects = set()

    for rule in data:
        used_objects.update(rule["source"]["member"])
        used_objects.update(rule["destination"]["member"])
        # For NAT
        if rule.get("destination-translation"):
            used_objects.update(
                rule["destination-translation"]["translated-address"],
            )
        if rule.get("source-translation"):
            try:
                used_objects.update(
                    rule["source-translation"]["static-ip"]["translated-address"],
                )
            except KeyError:
                continue

    return list(used_objects)
