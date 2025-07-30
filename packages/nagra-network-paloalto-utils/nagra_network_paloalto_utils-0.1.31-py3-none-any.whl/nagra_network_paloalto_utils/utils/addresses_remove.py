import csv
import logging
from multiprocessing.pool import ThreadPool as Pool
from pathlib import Path

from nagra_network_paloalto_utils.utils.common.yamlizer import STANDARD, read_yaml

from .constants import DEFAULT_TERRAFORM_PATH, MAIN_DEVICE_GROUP

VERBOSE = False
MAX_THREADS = 15


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


def remove_addresses_from_api(registry, addresses):
    addresses = registry.find_by_names(addresses)
    pool_size = min(len(addresses) // 2, MAX_THREADS)
    with Pool(pool_size) as pool:
        return pool.map(lambda a: remove_address_from_api(registry, a), addresses)


log = logging.getLogger("Object Deletion Checker")


def remove_address_from_terraform(to_remove, file):
    data = read_yaml(file)
    for object in data["addresses"]:
        if object["name"] in to_remove:
            data["addresses"].remove(object)
    with Path(file).open("w") as a:
        # a.write("---\n")
        STANDARD.dump(data, a)
    return data


def remove_addresses(
    addresses,
    address_registry=None,
    address_tf_file=DEFAULT_TERRAFORM_PATH,
):
    terraform_addresses, api_addresses = filter_addresses(addresses)
    tasks = [
        lambda: remove_addresses_from_api(address_registry, api_addresses),
        lambda: remove_address_from_terraform(
            terraform_addresses,
            file=address_tf_file,
        ),
    ]

    def call(f):
        return f()

    with Pool(len(tasks)) as pool:
        return pool.map(call, tasks)


def filter_addresses(addresses):
    terraform_addresses = []
    api_addresses = []
    for addr, tag in addresses:
        # tag = addr.get('tag', {})
        if tag == "terraform":
            terraform_addresses.append(addr)
        elif tag == "gui":
            api_addresses.append(addr)
    return terraform_addresses, api_addresses


def addresses_from_csv(file):
    with Path(file).open() as f:
        data = list(csv.reader(f, delimiter=";"))
    return data[1:]  # Remove the header entry


# Documentation
# https://zrh-panorama-01.net.hq.k.grp/PAN_help/en/wwhelp/wwhimpl/js/html/wwhelp.htm#href=objects-external-dynamic-lists.html

# https://stackoverflow.com/questions/66743792/how-to-define-common-python-click-options-for-multiple-commands#:~:text=To%20use%20the%20same%20option%20across%20multiple%20commands,to%20a%20variable%20and%20then%20use%20it%20twice%3A
