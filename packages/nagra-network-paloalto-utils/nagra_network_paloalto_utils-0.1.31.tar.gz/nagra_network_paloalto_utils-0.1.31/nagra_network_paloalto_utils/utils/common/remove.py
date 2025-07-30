import csv
import logging
from multiprocessing.pool import ThreadPool as Pool
from pathlib import Path

from nagra_network_paloalto_utils.utils.common.yamlizer import STANDARD, read_yaml
from nagra_network_paloalto_utils.utils.constants import MAIN_DEVICE_GROUP

VERBOSE = False
MAX_THREADS = 15

log = logging.getLogger("Object Deletion Checker")


def remove_address_from_api(registry, address):
    if not address:
        return
    if isinstance(address, str):
        address = registry.find_by_name(address)
    if not address:
        log.warning("address does not exist")
        return
    log.info(f"Trying to delete address: {address}")
    object_type = {
        "addresses": registry.client.objects.Addresses,
        "address_groups": registry.client.objects.AddressGroups,
        "external_dyn_lists": registry.client.objects.ExternalDynamicLists,
    }.get(address["@source"])
    if not object_type:
        log.warning("No matching source for address")
        return
    params = {
        "name": address["@name"],
        "location": "device-group",
        "device-group": MAIN_DEVICE_GROUP,
        "output-format": "json",
    }
    try:
        res = object_type.delete(params=params)
        log.info(f"""Deleted {address["@name"]} => {res}""")
    except Exception as e:
        log.error(f"""Failed to delete {address["@name"]}: {e}""")


def remove_from_tf_file(to_remove, file, resource, key=lambda el: el["name"]):
    data = read_yaml(file)
    elements = data.get(resource)
    if not elements:
        return data
    data[:] = [el for el in elements if key(el) not in to_remove]
    with Path(file).open("w") as a:
        # a.write("---\n")
        STANDARD.dump(data, a)
    return data


def remove_from_api(callback, entries):
    pool_size = min(len(entries) // 2, MAX_THREADS)
    with Pool(pool_size) as pool:
        return pool.map(callback, entries)


def _run_task(f):
    return f()


def run_tasks(tasks):
    if not tasks:
        return []
    if len(tasks) == 1:
        return [tasks[0]()]
    with Pool(len(tasks)) as pool:
        return pool.map(_run_task, tasks)


def remove(
    entries,
    remove_from_api=None,
    remove_from_tf_file=None,
    filter_existing=None,
):
    terraform_entries, api_entries = filter_by_tag(entries)
    tasks = []
    if remove_from_api:
        if filter_existing:
            api_entries = filter_existing(api_entries)
        tasks.append(
            lambda: remove_from_api(api_entries),
        )
    if remove_from_tf_file:
        tasks.append(
            lambda: remove_from_tf_file(terraform_entries),
        )
    return run_tasks(tasks)


def group_by_tag(entries):
    groups = {}
    for name, tag in entries:
        tmp = groups.setdefault(tag, [])
        tmp.append(name)
    return groups


def filter_by_tag(entries):
    groups = group_by_tag(entries)
    terraform_addresses = groups.get("terraform", [])
    api_addresses = groups.get("gui", [])
    return terraform_addresses, api_addresses


def entries_from_csv(file):
    with Path(file).open() as f:
        data = list(csv.reader(f, delimiter=";"))
    return data[1:]  # Remove the header entry


def remove_from_csv(
    csv_file,
    remove_from_api=None,
    remove_from_tf_file=None,
    filter_existing=None,
):
    entries = entries_from_csv(csv_file)
    return remove(entries, remove_from_api, remove_from_tf_file, filter_existing)


# Documentation
# https://zrh-panorama-01.net.hq.k.grp/PAN_help/en/wwhelp/wwhimpl/js/html/wwhelp.htm#href=objects-external-dynamic-lists.html

# https://stackoverflow.com/questions/66743792/how-to-define-common-python-click-options-for-multiple-commands#:~:text=To%20use%20the%20same%20option%20across%20multiple%20commands,to%20a%20variable%20and%20then%20use%20it%20twice%3A
