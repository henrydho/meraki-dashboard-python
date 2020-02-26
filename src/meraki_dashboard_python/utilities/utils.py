#!/usr/bin/env python
"""Import required modules."""
import os
import re
from typing import TypedDict, Tuple
import meraki

# Constant variables declaration
API_KEY = os.environ['MERAKI_API_KEY_HH']
# API_KEY = os.environ['MERAKI_API_KEY_SYD_TRAINING']
BASE_URL = "https://api.meraki.com/api/v0"
PRODUCT_TYPES = {
    'mx': 'appliance',
    'ms': 'switch',
    'mr': 'wireless',
    'mv': 'camera',
    'sm': 'systemsManager',
    'mg': 'cellularGateway'
    }
"""
timeZone (string): The timezone of the network.
Refer to 'TZ' column in the table in en.wikipedia.org
"""
DEFAULT_TIME_ZONE = 'Australia/NSW'


def validate_net_name(net_name: str) -> str:
    """Validate a network name.
    ** Network name can only contain letters, numbers, spaces, and
    these characters: [.@#_-]

    - net_name (string): network name being validated.
    -> Return net_name if nework name is valid. Otherwise, raise ValueError.
    """
    if not net_name:
        raise ValueError("Data Error: Network name can't be a blank value!")

    invalid_chars_regex = re.compile(r'[~`!$%^&*()+={}\[\]|\\/:"\',<>?]')
    if invalid_chars_regex.search(net_name) is None:
        return net_name
    raise ValueError(
        'Data Error: Network name can only contain letters, numbers, '
        'spaces, and these characters [.@#_-].')


def validate_tags(tags: str) -> str:
    """Validate tags.
    ** Tags can contain only letters, numbers, dashes, underscores,
    and periods.

    - tags (string): a list of tags separated by space.
    -> Return the network tags if tags are valid. Otherwise, raise ValueError.
    """
    invalid_chars_regex = re.compile(r'[~`!@#$%^&*()+={}\[\]|\\/:"\',<>?]')
    if invalid_chars_regex.search(tags) is None:
        return tags
    raise ValueError(
        'Data Error: Tags can contain only letters, numbers, dashes, '
        'underscores, and periods!')


def validate_device_code(device_code: str) -> str:
    """Validate valid device code.
    ** Valid device codes: [MX, MS, MR, MV, MG, SM]

    - device_code (string): device code
    -> Return device code in lower case if valid. Otherwise, raise ValueError.
    """
    if not device_code.strip():
        raise ValueError("Data Error: Hardware type can't be a blank value!")
    if (device_code.strip()).lower() in PRODUCT_TYPES.keys():
        return (device_code.strip()).lower()
    raise ValueError(
        f"Data Error: Invalid device code '{device_code}'! "
        'Valid device codes are '
        f"{[k.upper() for k, v in PRODUCT_TYPES.items()]}.")


def validate_net_type(net_type: str) -> str:
    """Validate network types.
    ** Valid network types are: [
        'appliance',
        'switch',
        'wireless',
        'camera',
        'systemsManager',
        'cellularGateway'
        ]

    - net_type (string):
        + a specific nework type, or
        + a combined network with the network types separated by space.
    -> Return a string value of netowrk types.
    -> Raise ValueError if network type is valid.
    """
    invalid_chars_regex = re.compile(r'[~`!@#$%^&*()-_+={}\[\]|\\/:"\',<>?.]')
    if invalid_chars_regex.search(net_type) is None:
        net_types = net_type.split()
        for _type in net_types:
            if _type not in PRODUCT_TYPES.values():
                raise ValueError(
                    'Data Error: Network types contain invalid value. '
                    'Valid network types are '
                    f"{[v for k, v in PRODUCT_TYPES.values()]}")
        return ' '.join(net_types)
    raise ValueError(
        "Data Error: Network types contain only alphbetical characters.")


def get_dict_values(dict_keys: list, a_dict: dict) -> list:
    """Get the dictionary's values from a provided list of dictionary's keys.

    - dict_keys (list): a list of dictionary's keys to be filtered out from a
      dictionary _dict.
    _ a_dict (dict): a dictionary to be filtered with a dict_list.
    -> Return a list of values from a_dict filltered by dict_keys.
    """
    a_list = list()
    for key in dict_keys:
        a_list.append(next((v for k, v in a_dict.items() if k == key), None))
    return a_list


def init_dashboard_session(authentication) -> TypedDict(
        'DashboardSession', {'dashboardAPI': meraki.DashboardAPI,
                             'organizations': list}):
    """Get authenticated DashboardAPI session.
    ** Note: meraki.APIKeyError only validates blank API key, but does not
      Validate whitepsace characters and throwing Exception.

    - authentication: authentication value
    -> Return a dict() including an authenticated meraki.DashboardAPI object,
       and authorized organizations list if authenticated.
    -> Raise ValueError if API key is not authorised.
    """
    try:
        dashboard = meraki.DashboardAPI(
            api_key=authentication, base_url=BASE_URL, output_log=False)
        orgs = dashboard.organizations.getOrganizations()
    except meraki.APIKeyError:
        pass
    except meraki.exceptions.APIError:
        pass
    else:
        return {'dashboardAPI': dashboard, 'organizations': orgs}
    raise ValueError(
        'Authentication Error: API key is not authorized!')


def filter_orgs(orgs: list, org_name: str,
                unique_org: bool = False) -> Tuple[list, dict]:
    """Get a list of organizations filtered by organization name.
    ** Note: Orginazation name is not unique and not case sensitive.

    - orgs (list): organization list object
    - org_name (string): organization name
    - unique_org (bool): specify if org_name to be uniquely filtered.
    -> Return a unique organization or a list of all organizations having the
       same organization name.
    -> Raised UserWarning if org_name is not unique and unique_org set to True.
    -> Raised ValueError if a provided organization name  does not exist.
    """
    # Get a list of organizations filtered by organization name.
    filtered_orgs = [
        dict(id=org['id'], name=org['name'], url=org['url'])
        for org in orgs if org_name == org['name']
        ]
    if len(filtered_orgs) == 1:
        return filtered_orgs[0]
    if len(filtered_orgs) > 1:
        if unique_org:
            raise UserWarning(
                'Ambiguous Value: There are more than one organization '
                f"named as '{org_name}'!")
        return filtered_orgs
    raise ValueError(
        f"Data Error: The organization named '{org_name}' does not exist!")


def get_org_networks(dashboard: meraki.DashboardAPI, org_name: str) -> list:
    """Get organization's networks filtered by an organization name.
    ** Note: organization name needs to be unique.

    - dashboard (meraki.DashboardAPI object): authenticated DashboardAPI
      session.
    - org_name (string): organization name
    -> Return a list of networks belonging to a provided unique org_name.
    """
    try:
        orgs = dashboard.organizations.getOrganizations()
    except UnboundLocalError as err:
        print(
            '-> Meraki API key error: '
            f'API key contains whitespace characters - {err}')
    except meraki.APIKeyError as err:
        print(f'-> {err}')
    except meraki.APIError as err:
        print(f'-> {err}')
    else:
        try:
            # Get a unique organiation
            org = filter_orgs(orgs=orgs, org_name=org_name, unique_org=True)
        except UserWarning as warn:
            print(f'-> {warn}')
        except ValueError as err:
            print(f'-> {err}')
        else:
            return dashboard.networks.getOrganizationNetworks(org['id'])


def get_networks(org_networks: list, net_name: str,
                 net_type: int = 0) -> Tuple[dict, list, None]:
    """Get the networks of a specific organization by network name.
    ** Note: a combined and standalone network type can have the same network
    name. In other words, the network name is only unique within a combined or
    standalone network type context.

    - org_networks (list): an organization's networks list
    - net_name (string): network name to be filtered
    - net_type (integer): network type to be filtered
        - Combined network type: 2
        - Standalone network type: 1
        - Default network type: 0 (both network types)
    -> Return a specific network as a dictionary value or a list of networks
       if a provided network name (net_name) exist. Otherwise, return None.
    """
    if net_type == 2:  # Filter only combined network type
        return next((
            net for net in org_networks
            if net['name'] == net_name and len(net['productTypes']) > 1), None)
    if net_type == 1:  # Filter only standalone network type
        return next((
            net for net in org_networks if net['name'] == net_name and
            len(net['productTypes']) == 1), None)
    if net_type == 0:  # Filter both combined and standalone network type
        return list(net for net in org_networks if net['name'] == net_name)
    return None
