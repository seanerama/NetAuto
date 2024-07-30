import requests
from requests.auth import HTTPBasicAuth
import yaml
import logging

# Load the config file
with open("config.yaml", "r") as file:
    config = yaml.safe_load(file)

# Configure logging
logging.basicConfig(filename='dnac_apis.log', level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

username = config['dna_center']['api_username']
password = config['dna_center']['api_password']
host = config['dna_center']['base_url']




def get_dna_center_token():
    """
    Authenticate with Cisco DNA Center and retrieve auth token.

    :param host: Cisco DNA Center host 
    :param username: Username for authentication
    :param password: Password for authentication
    :return: Authentication token or None if authentication fails
    """
    url = f"https://{host}/dna/system/api/v1/auth/token"
    headers = {
        'content-type': "application/json",
    }

    try:
        response = requests.post(url, headers=headers, auth=HTTPBasicAuth(username, password), verify=False)  # `verify=False` disables SSL verification
        if response.status_code == 200:
            # The token is usually in the JSON response, so we parse it.
            logger.info("Successfully obtained DNA Center token")
            logger.info(response.json())
            token = response.json()['Token']  # Adjust the key based on the actual response structure
            return token
        else:
            print(f"Failed to obtain token: {response.status_code} - {response.text}")
            logger.error(f"Failed to obtain token: {response.status_code} - {response.text}")
            return None
    except requests.RequestException as e:
        print(f"Request failed: {e}")
        logger.error(f"Request failed: {e}")
        return None
    
def fetch_devices_from_dnac(token, offset=1, limit=500):
    # Prepare the URL for the request
    url = f"https://{host}/dna/intent/api/v1/network-device"
    # Prepare your query parameters. If you have specific values for these parameters, you can replace 'None'
    # with the actual values you wish to query by.
    params = {
        "hostname": None,
        "managementIpAddress": None,
        "macAddress": None,
        "locationName": None,
        "serialNumber": None,
        "location": None,
        "family": None,
        "type": None,
        "series": None,
        "collectionStatus": None,
        "collectionInterval": None,
        "notSyncedForMinutes": None,
        "errorCode": None,
        "errorDescription": None,
        "softwareVersion": None,
        "softwareType": None,
        "platformId": None,
        "role": None,
        "reachabilityStatus": None,
        "upTime": None,
        "associatedWlcIp": None,
        "license.name": None,
        "license.type": None,
        "license.status": None,
        "module+name": None,
        "module+equipmenttype": None,
        "module+servicestate": None,
        "module+vendorequipmenttype": None,
        "module+partnumber": None,
        "module+operationstatecode": None,
        "id": None,
        "deviceSupportLevel": None,
        "offset": offset,
        "limit": limit
    }

    # Filter out None values, as we don't want to send them in the request
    params = {k: v for k, v in params.items() if v is not None}

    # Headers including the authentication token
    headers = {
        'x-auth-token': token, 
        'content-type': 'application/json'
    }

    # Make the GET request
    response = requests.get(url, headers=headers, params=params, verify=False)  # `verify=False` disables SSL verification

    # Check if the request was successful

    if response.status_code == 200:
        return response.json()['response']  # Assuming 'response' is the key containing device info
    else:
        print(f"Failed to fetch devices: {response.status_code} - {response.text}")
        return None
    
def fetch_device_from_hostname(hostname, token):

    # Prepare the URL for the request
    url = f"https://{host}/dna/intent/api/v1/network-device"
    # Prepare your query parameters. If you have specific values for these parameters, you can replace 'None'
    # with the actual values you wish to query by.
    params = {
        "hostname": hostname,
    }


    # Headers including the authentication token
    headers = {
        'x-auth-token': token, 
        'content-type': 'application/json'
    }

    # Make the GET request
    response = requests.get(url, headers=headers, params=params, verify=False)  # `verify=False` disables SSL verification

    # Check if the request was successful

    if response.status_code == 200:
        device = response.json()['response']  # Assuming 'response' is the key containing device info
        return device
    else:
        print(f"Failed to fetch devices: {response.status_code} - {response.text}")
        return None
    return

def fetch_device_count(token):
    
    """
    Fetch the total count of devices from Cisco DNA Center.
    :return: Total count of devices or None if request fails
    """
    url = f"https://{host}/dna/intent/api/v1/network-device/count"
    headers = {
        'content-type': "application/json",
        'x-auth-token': token
    }

    response = requests.get(url, headers=headers, verify=False)  # verify=False for development/testing
    if response.status_code == 200:
        return response.json().get('response')  # Assuming 'response' contains the count
    else:
        print(f"Failed to fetch device count: {response.status_code} - {response.text}")
        return None
    
def fetch_all_devices(token):

    """
    Fetch all devices from Cisco DNA Center using pagination.

    :param host: Cisco DNA Center host
    :param token: Authentication token
    :return: List of all devices
    """
    total_devices = fetch_device_count(token)
    if total_devices is None:
        return []

    devices = []
    pages = (total_devices // 500) + (1 if total_devices % 500 > 0 else 0)

    for page in range(pages):
        offset = page * 500 + 1
        page_devices = fetch_devices_from_dnac(token, offset=offset, limit=500)
        if page_devices:
            devices.extend(page_devices)
        else:
            break  # Stop if a request fails

    return devices