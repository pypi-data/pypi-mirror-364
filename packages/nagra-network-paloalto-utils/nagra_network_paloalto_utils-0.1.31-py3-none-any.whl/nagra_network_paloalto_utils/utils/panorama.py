"""
The Main program to commit the palo alto resources.

:author: Johan Lanzrein
:file: commit.py
"""
import difflib
import logging
import time
from multiprocessing.pool import ThreadPool as Pool
from xml.etree import ElementTree

import requests
import xmltodict
from nagra_panorama_api import Panorama
from nagra_panorama_api.restapi import PanoramaClient
from nagra_panorama_api.xmlapi import XMLApi
from nagra_panorama_api.xmlapi.utils import etree_tostring

from nagra_network_paloalto_utils.utils.constants import MAIN_DEVICE_GROUP

log = logging.getLogger(__name__)


def api_call_status(response_dict: dict) -> str:
    """
    Get the api status.

    :param response_dict: the response from an XML api call
    :return: success or error
    """
    status = response_dict["response"]["@status"]
    if status in ("error", "success"):
        return status
    return None


def indent_text(text, indent=""):
    if not indent:
        return text
    return "\n".join(f"{indent}{line}" for line in text.splitlines())


def lines2str(lines, indent=""):
    if isinstance(lines, dict):
        lines = lines.get("line") or []
    if isinstance(lines, str):
        return indent_text(lines, indent)
    return indent_text("\n".join(lines), indent)


def _handle_device_on_push(device, ignore_not_connected=True):
    res = device.get("result", "")
    if res == "OK":
        return True
    status = device.get("status", "")
    if not status:
        log.warning("Missing status for device")
        return True
    try:
        details = device.get("details", {}).get("msg", "")
        if not isinstance(details, str):
            devicename = device["devicename"]
            serial_no = device["serial-no"]
            errors = lines2str(details.get("errors", ""), indent="\t\t")
            warnings = lines2str(details.get("warnings", ""), indent="\t\t")
            details = f"""\
Device: {devicename} (S/N: {serial_no})
\tErrors:
{errors}
\tWarnings:
{warnings}"""
    except Exception:
        details = "Unkown error"
    if status == "not connected":
        log.warning(details)
        return ignore_not_connected

    if status == "commit succeeded with warnings":
        log.warning(details)
        return True

    if status == "commit failed":
        log.error(details)
        return False

    log.warning(f"unknown status {status}")
    return False


def handle_device_on_push(devices, ignore_not_connected=True):
    success = True
    for d in devices:
        success &= _handle_device_on_push(d, ignore_not_connected=ignore_not_connected)
    return success


def xml2dict(xml):
    return next(iter(xmltodict.parse(ElementTree.tostring(xml)).values()), None)


def _push(
    url,
    api_key,
    devicegroup=None,
    description=None,
    sync=True,
    ignore_not_connected=True,
) -> bool:
    """
    Commit all operation to the given device groups.

    :param device: The device to commit to
    :return: True if an error occured, False otherwise
    """
    if not devicegroup:
        log.error("Missing devicegroup for push.")
        return True
    if sync:
        log.info(f"Starting to push on devicegroup '{devicegroup}'...")
    else:
        log.info(
            f"Fire&forget push on '{devicegroup}'. The results should be effective after a while."
        )

    pano = Panorama(url, api_key=api_key)

    start = time.perf_counter()
    # Commit and wait if you don't want to wait and just fire and forget you can set sync and sync_all to false.
    # it's harder to see if there is any failures if you do that though.
    try:
        # Nb: commit-all is really the command that does the push
        # https://docs.paloaltonetworks.com/pan-os/10-2/pan-os-panorama-api/pan-os-xml-api-request-types/commit-configuration-api/commit-all
        result = pano.commit_all(
            sync=sync,  # Block until the Panorama commit is finished
            sync_all=sync,  # Block until every Firewall commit is finished, requires sync=True
            # exception=True,
            devicegroup=devicegroup,
            description=description,
        )
        if not sync:
            return False

        success = result["success"]
        devices = [xml2dict(d) for d in result["xml"].findall(".//devices/entry")]
        if not success and devices:
            success = handle_device_on_push(
                devices, ignore_not_connected=ignore_not_connected
            )

        log.info(f"Got answer for commit at {devicegroup} : Success {success}")
        message = "".join(result["messages"])
        if message:
            log.info(f"""Got following messages:\n{message}""")
        log.info(
            f"""Push on devicegroup '{devicegroup}' done in {int(round(time.perf_counter() - start))} seconds"""
        )
        return False
    except Exception as e:
        if devicegroup:
            log.error(
                f"Got error while trying to push on devicegroup '{devicegroup}': {e} "
            )
        else:
            log.error(f"Got error while trying to push on all devices: {e} ")
    log.info(
        f"""Push on devicegroup '{devicegroup}' done in {int(round(time.perf_counter() - start))} seconds"""
    )
    return True


def get_partial_tag(
    admin=None,
    description=None,
    excluded_shared_object=False,
    excluded_device_network=False,
):
    if not any((admin, description, excluded_shared_object, excluded_device_network)):
        return ""
    excluded_device_network = (
        "<device-and-network>excluded</device-and-network>"
        if excluded_device_network
        else ""
    )
    excluded_shared_object = (
        "<shared-object>excluded</shared-object>" if excluded_shared_object else ""
    )
    admin = f"<admin><member>{admin}</member></admin>" if admin else ""
    description_tag = f"<description>{description}</description>" if description else ""

    return f"""\
<partial>
    {excluded_device_network}
    {excluded_shared_object}
    {admin}
    {description_tag}
</partial>"""


def commit(
    url,
    api_key,
    admin: str,
    description="Terraform pipeline auto commit",
    verify=False,
) -> str:
    """
    Commit on the panorama
    :param admin: admin name under which to commit
    :param commit_type: the type of commit
    :return: error, fail, success, unchanged or timeout
    """
    api = XMLApi(url, api_key, verify=verify)
    # Check if there are changes pending to commit
    res = api.pending_changes().xpath(".//result/text()")[0]
    if res == "no":
        log.info("No change to commit")
        return "unchanged"
    partial = get_partial_tag(
        admin=admin,
        description=description,
        excluded_device_network=True,
        excluded_shared_object=True,
    )
    cmd = f"<commit>{partial}</commit>"

    # Use this value instead to debug the job result check
    # cmd = "<commit></commit>"

    # Send request to commit and parse response into dictionary
    try:
        res = api._commit_request(cmd)  # noqa
        commit_response = xmltodict.parse(etree_tostring(res))["response"]
        # Commit sent successfully
        line = commit_response["result"]["msg"]["line"]
        log.info(
            f"""Success: {line}""",
        )
        job_id = commit_response["result"]["job"]
    except Exception as e:
        log.warning(e)
        if "No edits" in str(e):
            return "unchanged"
        return "error"
    try:
        delta_seconds = 20
        max_retry = 15
        # Loop to check the job status every 20 seconds until the job
        # is completed, or up to 5 minutes (15 retries)
        for _ in range(max_retry):
            log.info(f"Job pending - waiting {delta_seconds} seconds to check status")
            time.sleep(delta_seconds)
            # Send request and parse response in a dictionary
            job = api.get_job(job_id)
            if not job:
                log.error(f"Job with ID {job_id} does not exist")

            # If job is still pending, continue loop
            if job.result == "PEND":
                log.info(
                    f"Job pending: {job.progress}% completed",
                )
                continue
            if job.result == "OK":
                log.info(f"Commit SUCCEED: {job.details}")
                return "success"
            if job.result == "FAIL":
                log.error(f"Commit FAILED: {job.details}")
                return "fail"
            log.error(f"ERROR: Received unexpected result '{job.result}'")
            return "error"
        log.warning(
            f"Commit pending for {delta_seconds * max_retry // 60} minutes - stopping script"
        )
        return "timeout"
    except Exception as e:
        log.error(f"Error while waiting for job completion: {e}")
        return "error"


def get_edited_device_groups(xmlapi):
    result = xmlapi.uncommited_changes_summary()
    return result.xpath(".//member/text()")


def check_pending_on_devices(
    devices: list,
    api_key,
    url,
    verify=False,
    timeout=None,
) -> bool:
    """
    Check if there is any pending changes specifically on a list of devices.

    :param devices: The devices to look up for
    :return: True if there are any pending changes.
    """
    api = XMLApi(url, api_key, verify=verify, timeout=timeout)
    members = get_edited_device_groups(api)
    if not members:
        return False
    if MAIN_DEVICE_GROUP in devices:  # here MAIN_DEVICE_GROUP acts as "any"
        return True
    return bool(set(devices) & set(members))


def check_pending(url, api_key, verify=False, timeout=None) -> str:
    """
    Function to check if there are pending changes
    :return: "success" if changes are pending, return "error" if no changes
    """

    # Build URL
    api = XMLApi(url, api_key, verify=verify)
    pending = api.pending_changes().xpath("response/result/text()")
    return {
        "no": "error",
        "yes": "success",
    }[pending]


def config_diff(url, api_key, verify=False, timeout=None) -> str:
    """
    Function to compare candidate and running configurations

    :return: error string
    """
    if check_pending(url, api_key) == "error":
        log.info("No pending changes")
        return "error"

    api = XMLApi(url, api_key, verify=verify)
    # Send request for Candidate config, put response in a file
    candidate = etree_tostring(api.candidate_config())
    running = etree_tostring(api.running_config())

    # Running diff on the two files
    diff = difflib.context_diff(
        running.splitlines(),
        candidate.splitlines(),
        fromfile="Running",
        tofile="Candidate",
        n=3,
    )
    log.info("".join(list(diff)))
    return None


def revert_config(url, api_key, admin, verify=False, timeout=None) -> str:
    """
    Function to revert the pending changes (back to the running configuration)

    :param admin: The admin name under which to revert.
    """
    if check_pending(url, api_key) == "error":
        log.info("No change to revert")
        return "error"

    # Payload to revert
    payload_revert = {
        "type": "op",
        "key": api_key,
        "cmd": f"<revert><config><partial><admin><member>{admin}</member></admin></partial></config></revert>",
    }
    # Send request and put output in a dictionary
    response = requests.get(url, params=payload_revert, verify=verify, timeout=timeout)
    contents = xmltodict.parse(response.text)
    if api_call_status(contents) == "success":
        result = contents["response"]["result"]
        log.info(
            f"SUCCESS: {result}",
        )
        return None
    if api_call_status(contents) == "error":
        log.error(f"Could not revert the config : {contents}")
        return None
    return None


def get_all_device_groups(url, api_key, with_devices=None) -> list:
    """
    Function to get all devices registered in Panorama
    """
    # device-groups with devices
    # "/config/devices/entry/device-group/entry/devices/entry/parent::devices/parent::entry/@name"
    # All devices
    # /config/devices/entry/device-group/entry/devices

    client = PanoramaClient(url, api_key)
    devices = client.panorama.DeviceGroups.get()
    if with_devices is not None:
        with_devices = bool(with_devices)
        devices = [d for d in devices if bool(d.get("devices")) == with_devices]
    return [g["@name"] for g in devices]


def get_devices_to_push(
    url, api_key, devicegroups=None, admin=None, push_scope_only=False
) -> list:
    """
    Function to get all devices registered in Panorama
    """
    client = XMLApi(url, api_key)
    scope = client.get_push_scope_devicegroups(admin=admin) if push_scope_only else None
    if scope is not None and devicegroups is not None:
        scope = set(scope) & set(devicegroups)
    return client.get_devicegroups_name(parents=scope, with_connected_devices=True)


def push(
    url,
    api_key,
    devicegroups,
    description=None,
    branch=None,
    commit_sha=None,
    sync=True,
):
    if not devicegroups:
        return _push(url, api_key, description=description)

    # Sort the devices groups: this will help troubleshooting
    devicegroups = sorted(devicegroups)

    if not description:
        if branch and commit_sha:
            description = (
                f"Palo Alto pipeline update from {branch} (Commit Sha {commit_sha})"
            )
        else:
            description = "Automatic Palo Alto pipeline update"
    log.info(f"Number of firewalls to push to: {len(devicegroups)}")
    log.debug("\n".join(devicegroups))

    with Pool(len(devicegroups)) as pool:
        results = pool.map(
            lambda d: _push(
                url, api_key, devicegroup=d, description=description, sync=sync
            ),
            devicegroups,
        )
    error = any(results)
    if error:
        log.error("Push has failed on one or more Firewall")
    return error
