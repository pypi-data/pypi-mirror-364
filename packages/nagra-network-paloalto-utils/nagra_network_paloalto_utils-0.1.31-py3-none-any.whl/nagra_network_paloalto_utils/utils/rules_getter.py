import logging

from nagra_panorama_api.restapi import PanoramaClient

log = logging.getLogger("Rules Getter")


def get_security_rules(host, api_key, device_group):
    """
    Function to get all security rules in Panorama
    """
    client = PanoramaClient(host, api_key)
    security_post_rules = client.policies.SecurityPostRules.get(
        device_group=device_group
    )
    if not security_post_rules:
        log.warning(f"Device group {device_group} has no Security Post Rules")
    yield from security_post_rules
    security_pre_rules = client.policies.SecurityPreRules.get(device_group=device_group)
    if not security_pre_rules:
        log.warning(f"Device group {device_group} has no Security Pre Rules")
    yield from security_pre_rules


def get_nat_rules(host, api_key, device_group):
    """
    Function to get all NAT rules in Panorama
    """
    client = PanoramaClient(host, api_key)

    nat_post_rules = client.policies.NATPostRules.get(device_group=device_group)
    yield from nat_post_rules
    nat_pre_rules = client.policies.NATPreRules.get(device_group=device_group)
    yield from nat_pre_rules


def get_pbf_rules(host, api_key, device_group):
    """
    Function to get all PBF rules in Panorama
    """
    client = PanoramaClient(host, api_key)

    pbf_post_rules = client.policies.PolicyBasedForwardingPostRules.get(
        device_group=device_group
    )
    yield from pbf_post_rules
    pbf_pre_rules = client.policies.PolicyBasedForwardingPreRules.get(
        device_group=device_group
    )
    yield from pbf_pre_rules


def get_all_rules(url, api_key, device_group):
    log.info("Retrieving security rules...")
    sr = get_security_rules(url, api_key, device_group)
    log.info("Done retrieving security rules")
    yield from sr

    log.info("Retrieving nat rules...")
    nat = get_nat_rules(url, api_key, device_group)
    log.info("Done retrieving nat rules")
    yield from nat

    log.info("Retrieving pbg rules...")
    pbf = get_pbf_rules(url, api_key, device_group)
    log.info("Done retrieving pbg rules")
    yield from pbf


# def get_all_rules(url, api_key, device_group):
#     if isinstance(device_group, str):
#         device_group = [device_group]
#     def call(dg):
#         return _get_all_rules(url, api_key, dg)
#     log.info("Getting all Security, NAT and PBF rules")
#     with Pool(len(device_group)) as pool:
#         yield from (d for l in pool.imap(call, device_group) for d in l)
