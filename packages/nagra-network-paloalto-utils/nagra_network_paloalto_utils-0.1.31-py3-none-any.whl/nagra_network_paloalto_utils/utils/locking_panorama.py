import logging
import time

import panos.errors

from .panorama import Panorama, check_pending_on_devices

log = logging.getLogger("Panorama locker")


def seconds_to_text(seconds):
    minutes_wait = seconds // 60
    seconds_wait = seconds % 60
    minutes_wait_msg = (
        f"{minutes_wait} minute{'s' if minutes_wait > 1 else ''}"
        if minutes_wait
        else ""
    )
    secondes_wait_msg = (
        f"{seconds_wait} seconde{'s' if seconds_wait > 1 else ''}"
        if seconds_wait
        else ""
    )
    return f"{minutes_wait_msg}{' and ' if minutes_wait_msg and secondes_wait_msg else ''}{secondes_wait_msg}"


def check_lock(
    url, api_key, firewalls, check_pending=False, wait_interval=60, max_tries=60
) -> bool:
    panorama_instance = Panorama(url, api_key=api_key)
    wait_message = seconds_to_text(wait_interval)
    start = time.perf_counter()
    # check if there is a pending change.
    for attempt in range(max_tries):
        if attempt > 0:
            print(f"Trying in {wait_message} again..")
            time.sleep(wait_interval)
        if check_pending and check_pending_on_devices(firewalls, api_key, url):
            log.info("Pending changes.")
            continue
        if (
            panorama_instance.check_config_locks()
        ):  # check_config_locks returns true if there is a lock.
            log.info("Lock is already taken.")
            continue
        return True  # status unchanged AND panorama has no lock.
    duration = time.perf_counter() - start
    wait_message = seconds_to_text(int(duration))
    log.error(
        "Pending changes that need to be committed and pushed on the firewall. "
        f"Tried for {wait_message} can not access firewall",
    )
    return False


def lock_pano(
    panorama_instance: Panorama,
    firewalls=None,
    comment="Terraform pipeline",
):
    """
    if firewalls is specified, the lock is only put on the firewalls
    otherwise, the lock is put on all panorama
    """
    # we can now try and lock.
    if not firewalls:
        panorama_instance.add_config_lock(
            comment=comment,
        )
        return
    for fw in firewalls:
        res = panorama_instance.add_config_lock(
            scope=fw,
            comment=comment,
        )
        if res:
            log.info(f"Lock added on {fw}")
        else:
            log.warning(f"Failed to add lock on {fw}")


def try_lock(
    url, api_key, firewalls, check_pending=False, wait_interval=60, max_tries=60
) -> bool:
    """
    Try to get the config lock of the panorama todo simplify
    :param max_tries: Maximum number of tries to get the config lock.
    :param panorama_instance: the panorama instance to lock
    :return: a status boolean
    """
    panorama_instance = Panorama(url, api_key=api_key)
    attempts = 3
    for _ in range(attempts):
        if not check_lock(
            url,
            api_key,
            firewalls,
            check_pending=check_pending,
            wait_interval=wait_interval,
            max_tries=max_tries,
        ):
            return False
        # we can now try and lock.
        lock_pano(panorama_instance, firewalls)

        log.info("Acquired the panorama config lock")
        if check_pending:
            # check for changes again if someone made some in the meanwhile..
            changed = check_pending_on_devices(firewalls, api_key, url)
            # if we were able to lock we can safely exit.
            if changed:
                log.warn("Changes detected after locking the config")
                # we have pending changes !!!
                # release the lock and restart everything
                unlock_pano(panorama_instance, firewalls)
                continue
        return True
    log.error(f"Unable to take the lock after {attempts} attempts")
    return False


def _unlock_pano(panorama_instance: Panorama, fw=None) -> bool:
    """
    Unlocks a config lock on a panorama. Raise excpetion if the lock can not be removed.
    :param panorama_instance: the panorama to unlock the config lock from.
    """
    try:
        if fw:
            res = panorama_instance.remove_config_lock(scope=fw)
            if res:
                log.info(f"Successfully removed the lock for {fw}")
                return True
        else:
            res = panorama_instance.remove_config_lock()
            if res:
                log.info("Successfully removed the lock")
                return True
    except panos.errors.PanDeviceXapiError as e:
        log.error(e)
    except panos.errors.PanLockError as e:
        log.error(e)
    log.error(f"Could not remove config lock for {fw}")
    return False


def unlock_pano(panorama_instance: Panorama, firewalls) -> bool:
    """
    Unlocks a config lock on a panorama. Raise excpetion if the lock can not be removed.
    :param panorama_instance: the panorama to unlock the config lock from.
    """
    if not firewalls:
        return _unlock_pano(panorama_instance)
    error = False
    for fw in firewalls:
        error &= _unlock_pano(panorama_instance, fw)
    return not error
