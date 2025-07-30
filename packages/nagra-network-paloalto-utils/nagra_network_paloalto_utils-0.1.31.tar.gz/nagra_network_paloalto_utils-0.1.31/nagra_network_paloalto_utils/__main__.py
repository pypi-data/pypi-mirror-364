import logging

import urllib3
from nagra_network_misc_utils.logger import set_default_logger

from nagra_network_paloalto_utils.commands import main

set_default_logger()
logging.getLogger().setLevel(logging.INFO)

# Disable HTTPS verification warnings
urllib3.disable_warnings()

if __name__ == "__main__":
    main()
