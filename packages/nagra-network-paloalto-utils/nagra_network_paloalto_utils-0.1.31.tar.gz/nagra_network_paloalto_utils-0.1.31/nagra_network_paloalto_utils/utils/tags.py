import logging

from nagra_network_paloalto_utils.utils.constants import MAIN_DEVICE_GROUP

from .common.utils import BaseRegistry

# if re.match("^blr.*", os.environ["CI_COMMIT_REF_NAME"]):
#     BRANCH = os.environ["CI_COMMIT_REF_NAME"]
# else:
#     BRANCH = None


log = logging.getLogger("tags.py")


class Tags(BaseRegistry):
    def get_data(self):
        """
        Find all tags

        :param address: FQDN address
        :return: list of 1 element containing the address object ( empty if no address object )
        """
        return self.client.objects.Tags.get(device_group=MAIN_DEVICE_GROUP)


def create_missing_tags(tags, mail):
    return [{"name": name, "owner": mail} for name, value in tags.items() if not value]


def extract_tags(data):
    tags = set()
    for rules in data:
        if rules["rules"] is None:
            continue
        for rule in rules["rules"]:
            tags.update(rule["tags"])
    return list(tags)
