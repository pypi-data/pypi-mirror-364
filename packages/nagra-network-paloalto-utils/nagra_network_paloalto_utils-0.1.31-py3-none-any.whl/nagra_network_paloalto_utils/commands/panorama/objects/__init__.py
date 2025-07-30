from .addresses import addresses
from .applications import applications
from .services import services
from .tags import tags


def inject(group):
    group.add_command(addresses)
    group.add_command(services)
    group.add_command(tags)
    group.add_command(applications)


# @click.group()
# def objects():
#     pass
#
# inject(objects)
