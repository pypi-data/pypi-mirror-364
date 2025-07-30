import re
from pathlib import Path

MAIN_DEVICE_GROUP = "DG1_GLOBAL"

DEFAULT_GIT_DIR = Path("./working_git")
DEFAULT_TERRAFORM_PATH = DEFAULT_GIT_DIR / "data/addresses.yml"

IP_REGEX_STR = (
    "(?:(?:[0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}"
    "(?:[0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])"
)
SUBNET_REGEX_STR = f"({IP_REGEX_STR})(?:\-(3[0-2]|[1-2][0-9]|[0-9]))"
SUBNET_REGEX = re.compile(f"^ip_{SUBNET_REGEX_STR}$")
FQDN_REGEX = re.compile("fqdn_(\S*\.*\S)+")

EMAIL_REGEX = re.compile(
    "[\w\.]+@[\w\.]+"
)  # This is simplified a lot. We kept it as it was for retrocompatilibity
SERVICE_REGEX = re.compile("service-(tcp|udp|https)(_\d{1,5})(-\d{1,5})?")
