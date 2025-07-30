import logging

from nagra_network_paloalto_utils.utils.constants import MAIN_DEVICE_GROUP

from .common.utils import BaseRegistry

log = logging.getLogger(__name__)


class Applications(BaseRegistry):
    def get_data(self):
        """
        Find all applications
        :return: list of all applications
        """
        predefined = {
            "location": "predefined",
        }
        return [
            *self.client.objects.Applications.get(device_group=MAIN_DEVICE_GROUP),
            *self.client.objects.Applications.get(params=predefined, device_group=""),
        ]


def extract_applications(data):
    applications = []
    for rules in data:
        if rules["rules"] is None:
            continue
        for rule in rules["rules"]:
            try:
                applications.extend(rule["applications"])
            except KeyError:
                continue
    return applications
