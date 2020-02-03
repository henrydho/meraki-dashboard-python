#!/usr/bin/env python
"""Import required modules."""
import json
import meraki
from utilities import utils
from utilities import uicli as ui


def create_lab():
    """New lab function."""

    api_key = ui.input_api_key()  # Get API key from user's input
    while api_key:  # API key is not an empty string
        try:
            dashboard = meraki.DashboardAPI(
                api_key=api_key, base_url=utils.BASE_URL, output_log=False)
            # Get a list of organizations
            print(f'Connnecting and logging to Meraki dashboard...')
            orgs = dashboard.organizations.getOrganizations()
        except meraki.exceptions.APIError as api_err:
            print(f"-> Meraki API error: {api_err}")
            api_key = ui.input_api_key()  # Get API key from user's input
        else:
            break

    # Organizations list() filtered by organization name entered from UI
    filtered_orgs = ui.get_filtered_orgs(orgs)
    org_name = filtered_orgs[0]['name']  # Organization name
    org_id = filtered_orgs[0]['id']  # Organization ID
    net_name = ui.input_net_name()  # Network name
    net_tags = ui.input_tags()  # Network tags
    net_type = ui.input_net_type()  # Nework type

    # Create new organization network
    print(f'Creating a new network: \'{net_name}\'...')
    try:
        new_network = dashboard.networks.createOrganizationNetwork(
            organizationId=org_id,
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
            f'The new network \'{net_name}\' is successfully created '
            f'for the \'{org_name}\' organization!')
        print(json.dumps(new_network, indent=4))
