import ipaddress
import logging

from nagra_panorama_api import XMLApi
from nagra_panorama_api.xmlapi.utils import el2dict

from .common.utils import BaseRegistry
from .constants import FQDN_REGEX, MAIN_DEVICE_GROUP, SUBNET_REGEX

log = logging.getLogger("addresses.py")


class Addresses(BaseRegistry):
    def get_data2(self):
        client = XMLApi()
        config = client.running_config()
        elements = config.xpath(
            ".//*[self::address or self::address-group or self::external-dynamic-lists or self::external-list]/entry"
        )  #  or self::custom-url-category
        result = []
        for e in elements:
            o = el2dict(e)["entry"]
            name = o.get("@name")
            if not name:
                continue
            source = e.getparent().tag
            o["@source"] = source
            result.append(o)
        return result

    def get_data(self):
        """
        Find all addresses on Panorama

        :return: list of dictonary for addresses and addresses_groups on Panorama
        """

        device_group = MAIN_DEVICE_GROUP
        data = [
            ("addresses", self.client.objects.Addresses),
            ("address_groups", self.client.objects.AddressGroups),
            ("external_dyn_lists", self.client.objects.ExternalDynamicLists),
            # ("custom_url_categories", self.client.objects.CustomURLCategories),
        ]
        result = []
        for source, object_type in data:
            objects = object_type.get(device_group=device_group)
            for o in objects:
                o["@source"] = source
                result.append(o)
        return result

    def find_by_name(self, name):
        if name == "any":
            return "any"
        return super().find_by_name(name)


def extract_addresses(data):
    addresses = []
    for rules in data:
        if rules["rules"] is None:
            continue
        for rule in rules["rules"]:
            addresses.extend(rule["source_addresses"])
            addresses.extend(rule["destination_addresses"])
    return addresses


def is_cidr(value):  # Logic from matthias, seems to be wrong ?
    try:
        ipaddress.ip_network(value, strict=False)
        return False
    except ValueError:
        return True


def remove_cidr_from_addresses(addresses):
    return [address for address in addresses if address and is_cidr(address)]


def get_addresses_to_create(addresses):
    return [name for name, value in addresses.items() if not value]


def check_addresses_to_create_length(addresses_to_create):
    too_long_addresses = [
        address for address in addresses_to_create if len(address) >= 63
    ]
    if len(too_long_addresses) > 0:
        log.error(
            "ERROR: the following addresses are too long (above 63 chars): {}".format(
                too_long_addresses,
            )
        )
        exit(1)
        # raise SyntaxError(
        #     "ERROR: the following addresses are too long (above 63 chars): {}".format(
        #         too_long_addresses,
        #     ),
        # )
    return addresses_to_create


def prepare_addresses_to_create(addresses_to_create, owner):
    addresses_to_return = []
    malformed = []
    for address_to_create in addresses_to_create:
        subnet = SUBNET_REGEX.match(address_to_create)
        if subnet:
            ip, mask = subnet.groups()
            addresses_to_return.append(
                {
                    "name": address_to_create,
                    "owner": owner,
                    "type": "ip-netmask",
                    "value": f"{ip}/{mask}",
                    "tags": ["terraform"],
                },
            )
            continue

        fqdn = FQDN_REGEX.match(address_to_create)
        if fqdn:
            fqdn = fqdn.groups()[0]
            addresses_to_return.append(
                {
                    "name": address_to_create,
                    "owner": owner,
                    "value": fqdn,
                    "tags": ["terraform"],
                },
            )
            continue
        malformed.append(address_to_create)
        # raise SyntaxError(f"ERROR: address {address_to_create} malformed")
    if not malformed:
        return addresses_to_return, None

    malformed_text = "\n".join(f"\t- {addr}" for addr in malformed)
    error_msg = f"""\
The following addresses are malformed:
{malformed_text}

Valid format are (regex, case sensitive):
IP: {SUBNET_REGEX.pattern}
FQDN: {FQDN_REGEX.pattern}

NOTE:
- If the object already exists on panorama, the naming convention is not enforced
- We only check the device-group '{MAIN_DEVICE_GROUP}'.
  => The error might be caused because the object is not in the correct device-group
"""
    return [], error_msg
