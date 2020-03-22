#!/usr/bin/env python
"""User inputs CLI Module.

This module defines the functions which are used to get the details of the
Meraki devices and the Meraki dashboard when the user inputs from the command
lines.
"""
import getpass
from utilities import utils


def input_get_org(orgs: list) -> dict:
    """Get a specific organization filtered by a unique organization name.

    - User is prompted to enter an specific organization name.
    - orgs (list): obtained via meraki.organizations.getOrganizations().
    -> Return a unique organization dictionary.
    """
    input_message = 'Enter the name of the Meraki dashboard organization: '
    org_name = input(f'{input_message}')
    while org_name is not None:  # org_name is an empty string
        try:
            # Filter organizations list by a unique org name
            org = utils.filter_orgs(
                orgs=orgs, org_name=org_name, unique_org=True)
        except UserWarning as warn:
            print(
                f'-> {warn}\n'
                'Login to your Meraki dashboard, verify a specific '
                'organization and change the name of the duplicated '
                'organization names to a different name.\n')
        except ValueError as err:
            print(f'-> {err}')
        else:
            return org
        org_name = input(f'{input_message}')


def input_api_key() -> str:
    """Get the Meaki dashboard API key from the user's input.

    -> Return the API key (string) with the leading & trailing  whitespace
    removed if the key is not a blank value.
    """
    input_message = "Enter your Meraki's dashboard API Key: "
    api_key = getpass.getpass(f'{input_message}')
    while not api_key or api_key.isspace():
        if api_key.isspace():
            print('-> Data Error: API key contains all whitespace characters.')
        else:
            print("-> Data Error: API key can't be a blank value.")
        api_key = getpass.getpass(f'{input_message}')
    return api_key.strip()


def input_net_name() -> str:
    """Get the network name from the user's input.

    -> Return a network name as a string value.
    -> Raise ValueError if the network name is invalid.
    """
    input_message = 'Enter network name: '
    net_name = input(f'{input_message}').strip()
    while net_name is not None:
        try:
            utils.validate_net_name(net_name)
        except ValueError as err:
            print(f'-> {err}')
            net_name = input(f'{input_message}').strip()
        else:
            return net_name


def input_tags(tag_type: str) -> str:
    """Get the tag(s) from the user's input.
    Note: Tags can be used anywhere within the Meraki dashboard  such as
    organization, network, etc.

    - tag_type (string): used to customize the user's prompt message.
        e.g. network, organization, etc.
    -> Return the tags (string) if the tags are valid.
    -> Raise ValueError if the tags are invalid.
    """
    # Validate the tags and prompt a user to enter the correct tags
    input_message = (
        f'Enter the {tag_type} tags separated by space '
        "'(default: no tags)': ")
    net_tags = input(f'{input_message}').strip()
    while net_tags is not None:
        try:
            utils.validate_tags(net_tags)
        except ValueError as err:
            print(f'-> {err}')
            net_tags = input(f'{input_message}').strip()
        else:
            return net_tags


def input_net_type() -> list:
    """Get the network type from the user's input.

    - User is prompted to enter a specific device code separated by space.
        Device codes: MX/MS/MR/MV/MG/SM
    -> Return the list of network types. e.g. ['applicance', 'switch']
        The network types are matched with a specific device code as below:
        {'mx': 'appliance'}
        {'ms': 'switch'}
        {'mr': 'wireless'}
        {'mv': 'camera'}
        {'sm': 'systemsManager'}
        {'mg': 'cellularGateway'}
    """
    input_message = (
        "-----------------------------------------------------\n"
        "Enter a specific device type for the single network type, or\n"
        "Enter multiple device types separated by space for"
        " the combined hardware network type.\n"
        "The valid device types (case insenstive) are "
        f"{[k.upper() for k, v in utils.PRODUCT_TYPES.items()]}: ")
    device_codes = input((f'{input_message}')).lower()
    while device_codes is not None:
        a_list = list()
        for device_code in device_codes.split():
            try:
                utils.validate_device_code(device_code)
            except ValueError as err:
                print(f'-> {err}')
                a_list = list()  # Reset an empty list
                break
            else:
                a_list.append(device_code)
        if not a_list:
            device_codes = input((f'{input_message}')).lower()
        else:
            return utils.get_dict_values(a_list, utils.PRODUCT_TYPES)
