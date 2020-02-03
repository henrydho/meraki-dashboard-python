#!/usr/bin/env python
"""User inputs CLI Module.

This module defines functions which are used to get information when the
end-user enter details from command line.
"""
import getpass
from utilities import utils


def get_filtered_orgs(orgs: list) -> list:
    """Get an Organization ID filtered by an unique organization name.

    - User is prompted to enter an specific rganization name.
    - orgs (list): obtained via meraki.organizations.getOrganizations().
    -> Return an unique organization.
    """
    org_name = input('Enter the name of Meraki dashboard organization: ')
    while org_name is not None:  # org_name is an empty string
        try:
            # Filtered by org name
            filtered_orgs = utils.get_orgs(orgs, org_name)
        except ValueError as err:
            print(f'-> {err}')
            org_name = input(
                'Enter the name of Meraki dashboard organization: ')
        else:
            if len(filtered_orgs) == 1:
                return filtered_orgs
            print(
                '-> Ambiguious organization name or organization name is '
                'not specified!\n'
                'There are more than one Meraki dashboard organizations '
                f'having the same organization name: \'{org_name}\'.\n'
                'Login to your Meraki dashboard, verify a specific '
                'organization and change the name of the duplicated '
                'organization names to different name.\n')
            org_name = input(
                'Enter the name of Meraki dashboard organization: ')


def input_api_key() -> str:
    """Get Meaki dashboard API key from user's input.

    -> Return the string value of API key with leading whitespace removed
    if the key is not a blank value.
    """
    api_key = getpass.getpass('Enter API Key: ')
    while not api_key:
        print("-> Data Error: API key can't be a blank value.")
        api_key = getpass.getpass('Enter API Key: ')
    return api_key.strip()


def input_net_name() -> str:
    """Get network name from user's input.

    -> Return a network name as string value.
    -> Raise ValueError if network name is invalid
    """
    net_name = input('Enter network name: ').strip()
    while net_name is not None:
        try:
            utils.validate_net_name(net_name)
        except ValueError as err:
            print(f'-> {err}')
            net_name = input('Enter network name: ').strip()
        else:
            return net_name


def input_tags() -> str:
    """Get tags from user's input.

    - Tags can be used anywhere such as organization, network, etc.
    -> Return the network tags as string if tags are valid.
    -> Raise ValueError if tag(s) is invalid.
    """
    # Validate network tags and prompt user to enter correct tags
    net_tags = input(
        'Enter network tags separated by space '
        '(default is no tag): ').strip()
    while net_tags is not None:
        try:
            utils.validate_tags(net_tags)
        except ValueError as err:
            print(f'-> {err}')
            net_tags = input(
                'Enter network tags separated by space '
                '(default is no tag): ').strip()
        else:
            return net_tags


def input_net_type() -> str:
    """Get network type from user's input.

    - User is prompted to enter a specific device code below.
        Device code: MX/MS/MR/MV/MG/SM
    -> Return a specific network type as a string value.
        {'mx': 'appliance'}
        {'ms': 'switch'}
        {'mr': 'wireless'}
        {'mv': 'camera'}
        {'sm': 'systemsManager'}
        {'mg': 'cellularGateway'}
    -> Raise ValueError if device code is invalid.
    """
    # Validate network type and prompt user to enter correct network type
    device_code = (input('Enter network type (MX/MS/MR/MV/MG/SM): '))
    while device_code is not None:
        try:
            net_type = utils.validate_net_type(device_code)
        except ValueError as err:
            print(f'-> {err}')
            device_code = (input('Enter network type (MX/MS/MR/MV/MG/SM): '))
        else:
            return net_type
