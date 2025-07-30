# Palo Alto Utility Script

This contains script wrapped inside a single CLI.
The functionalities offered by it are grouped by subcommands:
- panorama:
    Description: Commands to directly interact with panorama
    Subcommands:
    - addresses: Handle the addresses objects
    - applications: Handle the applications objects
    - services: Handle the applications objects
    - tags: Handle the tags objects
    - commit/push: Commit/Push changes on panorama
    - lock/unlock: Set/Unset the lock on panorama
    - list_edited_devicegroups: Output the device groups with uncommited changes
- terraform:
    Description: Commands to manage resources related to terraform
    Subcommands:
    - check-delete: Check if the objects removed from the configuration are used somehwere
- yaml:
    Description: Commands to manipulate yaml files
    Subcommands:
    - check: Check that the data in yaml are correct
    - check_indexes: Take a file (or folder containg files, e.g. 'security-policies/data/') in yaml format defining security policies and check the indexes.

- push_folder: Do a git push on a repository



## Testing
For testing, we are using [pytest](https://docs.pytest.org/en/8.2.x/). We test the CLI well behaviour to ensure non-regression.
The tests are currently run by hand.
Check the `tests/` folder for more information
