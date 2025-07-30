from pathlib import Path

import ruamel.yaml as yaml


def get_yaml_parser(typ=None):
    parser = yaml.YAML(typ=typ)
    parser.sort_base_mapping_type_on_output = False
    parser.block_seq_indent = 4
    parser.sequence_dash_offset = 2
    parser.indent(mapping=2, sequence=4, offset=2)
    parser.line_break = 121
    parser.width = 4096
    parser.compact_seq_seq = True
    parser.compact_seq_map = True
    # parser.explicit_start = False  ?
    parser.explicit_start = True
    parser.brace_single_entry_mapping_in_flow_sequence = True
    return parser


# Instantiate yaml class as safe for first reading of the file
SAFE = get_yaml_parser(typ="safe")  # Normal parser

# Instantiate yaml class as round-trip for first writing the new elements and all subsequent use of file
STANDARD = get_yaml_parser()  # Parser with comments
# Instantiate yaml class as round-trip for first writing the new elements and all subsequent use of file
STANDARD_NO_START = get_yaml_parser()  # Parser with comments
STANDARD_NO_START.explicit_start = False


def add_elements_to_file(elements, file, filter_existing=True, key=lambda e: e["name"]):
    """
    This function appends elements as a list already indented.
    This does not take anything else into consideration, like the structure or keys
    """
    if filter_existing:
        elements = list(({key(e): e for e in elements}).values())
        data = read_yaml(Path(file))
        existing_elements = {key(e) for v in data.values() for e in v}
        elements = [e for e in elements if key(e) not in existing_elements]
    if not elements:
        return
    # This allows to put well-formatted new element at the end of the file
    # This is not a safe way to do it but it prevent rewriting data that is correct
    with Path(file).open("a") as a:
        STANDARD_NO_START.dump(elements, a)
    # cleanup(file)


def read_yaml(file: Path):
    """
    Handle scenario where the yaml file contains multiple documents (separated by "---"), e.g.

    a: "hello"
    ---
    b: "World"
    """
    data = [d for d in SAFE.load_all(file.read_text()) if d]
    if not data:
        return None
    return data[0]


def is_yaml_file(file):
    return file.suffix in (".yml", ".yaml")


def find_yaml_files(path):
    if is_yaml_file(path):
        yield path
    if path.is_dir():
        for p in path.iterdir():
            if is_yaml_file(p):
                yield p


def get_yaml_data(file, /, with_files=False):
    file = Path(file).resolve()
    for f in find_yaml_files(file):
        data = read_yaml(f)
        if with_files:
            yield f, data
        else:
            yield data
