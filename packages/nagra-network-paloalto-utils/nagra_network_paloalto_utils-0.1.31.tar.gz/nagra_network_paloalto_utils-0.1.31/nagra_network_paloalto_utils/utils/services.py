import logging
import re

from nagra_network_paloalto_utils.utils.constants import (
    MAIN_DEVICE_GROUP,
    SERVICE_REGEX,
)

from .common.utils import BaseRegistry

# if re.match("^blr.*", os.environ["CI_COMMIT_REF_NAME"]):
#     BRANCH = os.environ["CI_COMMIT_REF_NAME"]
# else:
#     BRANCH = None

log = logging.getLogger("services.py")


class Services(BaseRegistry):
    def get_data(self):
        """
        Find all services
        :return: list of all services
        """
        predefined = {
            "location": "predefined",
        }
        return [
            *self.client.objects.Services.get(device_group=MAIN_DEVICE_GROUP),
            *self.client.objects.ServiceGroups.get(device_group=MAIN_DEVICE_GROUP),
            *self.client.objects.Services.get(params=predefined, device_group=""),
        ]

    def find_by_name(self, name):
        if name in ("any", "application-default"):
            return name
        return super().find_by_name(name)


def extract_services(data):
    services = []
    for rules in data:
        if rules["rules"] is None:
            return []
        for rule in rules["rules"]:
            try:
                services.extend(rule["services"])
            except KeyError:
                continue
    return services


def prepare_services_to_create(services, owner):
    services_to_return = []
    for service in services:
        res = SERVICE_REGEX.match(service)
        if res:
            services_to_return.append(
                {
                    "name": service,
                    "protocol": re.findall("(tcp|udp)", service)[0],
                    "destination": "".join(
                        re.findall("(\d{1,5})(-\d{1,5})?", service)[0],
                    ),
                    "tags": [owner, "terraform"],
                },
            )
            continue
        log.error(f"ERROR: service {service} malformed")
        # raise SyntaxError(f"ERROR: service {service} is malformed")
    return services_to_return
