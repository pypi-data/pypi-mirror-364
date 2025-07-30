import logging

log = logging.getLogger("Checks")


def check_tag_presence(entries, tag):
    for entry in entries:
        name = entry["name"]
        if tag not in entry["tags"]:
            log.error(f"{name} is missing tag {tag}")
            yield name


def check_name_length(entries, max_size):
    for entry in entries:
        name = entry["name"]
        if len(name) > max_size:
            log.error(
                f"{name} is has a name bigger than {max_size}",
            )
            yield name


def check_duplicates(entries):
    objects_list = set()
    for entry in entries:
        if "value" in entry:
            temp_value = (entry["value"],)
        elif "destination" in entry:
            temp_value = (entry["protocol"], entry["destination"])
        else:
            try:
                temp_value = (
                    entry["source_zones"],
                    entry["destination_zones"],
                    entry["source_addresses"],
                    entry["destination_addresses"],
                )
            except KeyError:
                return True
            temp_value += (
                entry.get("applications", ["any"]),
                entry.get("categories", ["any"]),
                entry.get("services", ["application-default"]),
                entry.get("action", "allow"),
            )
        temp_value = tuple(tuple(x) if isinstance(x, list) else x for x in temp_value)
        if temp_value in objects_list:
            log.warning("Duplicate found: {}{}".format(entry["name"], temp_value))
            yield entry["name"]
        objects_list.add(temp_value)
