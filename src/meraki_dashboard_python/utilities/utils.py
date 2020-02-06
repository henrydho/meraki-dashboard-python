#!/u:sr/bin/env python
"""Import required modules."""
import os
import re
from typing import TypedDict
import meraki

# Constant variables declaration
API_KEY = os.environ['MERAKI_API_KEY_HH']
# API_KEY = os.environ['MERAKI_API_KEY_SYD_TRAINING']
BASE_URL = "https://api.meraki.com/api/v0"
DEVICE_CODES = tuple(('MX', 'MS', 'MR', 'MV', 'MG', 'SM'))
NET_TYPES = tuple((
    {'mx': 'appliance'},
    {'ms': 'switch'},
    {'mr': 'wireless'},
    {'mv': 'camera'},
    {'sm': 'systemsManager'},
    {'mg': 'cellularGateway'}))
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

    - tags (string): a list of tags separated by space
    -> Return network tags: str if tags are valid. Otherwise, raise ValueError.
    """
    invalid_chars_regex = re.compile(r'[~`!@#$%^&*()+={}\[\]|\\/:"\',<>?]')
    if invalid_chars_regex.search(tags) is None:
        return tags
    raise ValueError(
        'Data Error: Tags can contain only letters, numbers, dashes, '
        'underscores, and periods!')


def validate_device_code(device_code: str) -> str:
    """Check valid device code.

    ** Valid device codes: [MX, MS, MR, MV, MG, SM]
    - device_code: string
    -> Return device code in lower case if valid. Otherwise, raise ValueError
    """
    if (device_code.strip()).upper() in DEVICE_CODES:
        return (device_code.strip()).lower()
    raise ValueError(
        f"Data Error: Invalid device code '{device_code.upper()}'! "
        f"Valid device codes are {DEVICE_CODES}.")


def validate_net_type(device_code: str) -> str:
    """Get network type based on a device code.

    ** Valid network types:
    ['appliance','switch','wireless','camera', 'system manager',
    'meraki gateway']

    - device_code (string): [MX, MS, MR, MV, MG, SM]
    -> Return the name of network type if device_code matched.
    -> Raise ValueError if there is no nework type matched with device_code.
    """
    try:
        device_code = validate_device_code(device_code)
    except ValueError as err:
        print(f'-> {err}')
    else:
        # Iterate throught NET_TYPES tubble
        # and get the value of network type.
        for a_dict in NET_TYPES:
            for key, value in a_dict.items():
                if key == device_code:
                    return value
    raise ValueError(
        f"Data Error: There is no network type defined by the device "
        f"code '{device_code.upper()}'.")


def get_filtered_orgs(orgs: list, org_name: str = None) -> list:
    """Get a list of organizations filtered by organization name.

    - orgs: organization list object
    - org_name: string
    -> Return a specific organization or a list of all organizations
        if organzation name is an empty string.
    -> Raised ValueError if organization name does not exist.
    """
    # Get a complete organizations list() without filtering by org_name.
    if not org_name:  # org_name is an empty string
        return orgs  # Original organizations list

    # Get a list of organizations filtered by organization name.
    # Note: Orginazation name is not unique and not case sensitive.
    filtered_orgs = list()
    for org in orgs:
        if org_name == org['name']:
            org_dict = dict(id=org['id'], name=org['name'], url=org['url'])
            filtered_orgs.append(org_dict)

    if filtered_orgs:
        return filtered_orgs
    raise ValueError(
        f"Data Error: The organization '{org_name}' does not exist!")


def get_org_networks(dashboard: meraki.DashboardAPI, org_name: str) -> list:
    """Get organization networks filtered by organization name.

    - dashboard (meraki.DashboardAPI object): authenticated DashboardAPI
      session.
    - org_name (string): organization name
    -> Return a list of networks of the org_name.
    """
    try:
        orgs = dashboard.organizations.getOrganizations()
    except UnboundLocalError as err:
        print(
            'Meraki API key error: '
            f'API key contains whitespace characters - {err}')
    except meraki.APIKeyError as err:
        print(f'-> {err}')
    except meraki.APIError as err:
        print(f'-> {err}')
    else:
        try:
            org = get_filtered_orgs(orgs, org_name)
        except ValueError as err:
            print(f'-> {err}')
        else:
            org_id = org['id']
            org_networks = dashboard.networks.getOrganizationNetworks(org_id)
            return org_networks


def init_dashboard_session(authentication) -> TypedDict(
        'DashSession', {'dashboardAPI': meraki.DashboardAPI,
                        'organizations': list}):
    """Get authenticated DashboardAPI session.

    - authentication: authentication value
    -> Return a dict() including an authenticated meraki.DashboardAPI object,
       and authorized organizations list if authenticated.
    -> Raise ValueError if API key is not authorised.
    * Note: meraki.APIKeyError only validates blank API key, but does not
      Validate whitepsace characters and throwing Exception.
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
        'Authentication error: API key is not authorized!')
