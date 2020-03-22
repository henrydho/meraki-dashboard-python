#!/usr/bin/env python
"""Import required modules."""
import json
import meraki
from utilities import utils
from utilities import userinputcli as uicli  # Userinput CLI module


def create_network():
    """Create a new network."""

    api_key = uicli.input_api_key()  # Get API key from user's input
    while api_key:
        try:
            dashboard_session = utils.init_dashboard_session(auth=api_key)
        except ValueError as err:
            print(err)
            api_key = uicli.input_api_key()  # Get API key from user's input
        else:
            break

    dashboard = dashboard_session['dashboardAPI']  # Persistent dashboard API
    orgs = dashboard_session['organizations']  # List of organizations
    org = uicli.input_get_org(orgs)  # Get a specific organization
    net_name = uicli.input_net_name()  # Network name
    net_tags = uicli.input_tags(tag_type='network')  # Network tags
    net_type = ' '.join(uicli.input_net_type())  # Nework type

    # Create a new Meraki network
    print(f"Creating a new Meraki network: '{net_name}'...\n")
    try:
        new_network = dashboard.networks.createOrganizationNetwork(
            organizationId=org['id'],
            name=net_name,
            type=net_type,
            tags=net_tags,
            timeZone=utils.DEFAULT_TIME_ZONE)
    except meraki.APIError as err:
        print(
            f'-> Meraki API error: '
            f"{err.message['errors'][0]}")
    else:
        print(
            f"The new Mereaki network '{net_name}' is successfully created "
            f"for the organization '{org['name']}'!")
        print(json.dumps(new_network, indent=4))


def create_lab():
    """Default lab"""
    create_network()
