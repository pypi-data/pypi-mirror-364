import requests
import pandas as pd

base_url = 'https://atukpostgrest.clubwise.com/'

def get_access_token(api_token: str, clubcode: str, timeout: int = 10, verbose: bool = False) -> str:
    """
    Fetch access-token from the API.

    Args:
        clubcode (str): The club's unique identifier.
        api_token (str): The authentication token or secret.
        timeout (int): Timeout duration in seconds.
        verbose (bool): If True, print detailed error messages.

    Returns:
        str or None: Access token if successful, otherwise None.
    """
    request_url = base_url + 'access-token'
    request_header = {
        'CW-API-Token': api_token,
        'Content-Type': 'application/json'
    }
    request_payload = {'sClubCode': clubcode}

    try:
        response = requests.post(request_url, json=request_payload, headers=request_header, timeout=timeout)
        response.raise_for_status()
        my_token = response.json().get('access-token')

        if not my_token:
            print("Access token not found in response. Check your club code and API token.")
            return None
        return my_token

    except requests.exceptions.RequestException as e:
        print("Error generating access token.")
        if verbose:
            print(f"Details: {e}")
        return None

def fetch(request: str, api_token: str, access_token: str = None, clubcode: str = None, timeout: int = 10, verbose: bool = False) -> pd.DataFrame:
    """
    Fetch data from the API using either a provided access token,
    or by generating one with a clubcode and static API token.

    Args:
        request (str): The endpoint or request path (e.g., 'players').
        api_token (str): Your static API token.
        access_token (str, optional): If already available, it will be used.
        clubcode (str, optional): Required if access_token is not provided.
        timeout (int): Timeout duration for the request.
        verbose (bool): If True, prints additional error info.

    Returns:
        pd.DataFrame or None: API data as a DataFrame, or None if failed.
    """
    if not access_token:
        if not clubcode:
            raise ValueError("clubcode is required if access_token is not provided.")
        access_token = get_access_token(api_token, clubcode, timeout=timeout, verbose=verbose)
        if not access_token:
            print("Failed to fetch access token. Aborting.")
            return None

    access_headers = {
        'CW-API-Token': api_token,
        'Authorization': f'Bearer {access_token}'
    }
    combined_url = base_url + request

    try:
        response = requests.get(combined_url, headers=access_headers, timeout=timeout)
        response.raise_for_status()
        data = response.json()
        return pd.DataFrame(data)

    except requests.exceptions.RequestException as e:
        print("Error fetching data from API.")
        if verbose:
            print(f"Details: {e}")
        return None
