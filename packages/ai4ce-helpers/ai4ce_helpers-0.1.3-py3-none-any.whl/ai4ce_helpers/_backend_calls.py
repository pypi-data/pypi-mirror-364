import os
from pathlib import Path
import time
import httpx
import toml
import streamlit as st

# Set backend base url, depending on whether the app is running in
# a docker container (which is most likely the unified interface.)
def check_if_backend_in_docker(PORT: int = 8000) -> str:
    """Check if the backend is running in a Docker container.
    If streamlit is started as part of docker, it will most likely have an environment variable set for the backend URL.
    If not, the backend is assumed to be running on localhost.

    Args:
        PORT (int): The port on which the backend is running.
    Returns:
        str: The URL of the backend.
    """
    if os.environ.get("BACKEND_URL"):
        return f"{os.environ.get("BACKEND_URL")}/api"
    if Path("/.dockerenv").exists():
        return f"http://backend:{PORT}/api"
    return f"http://localhost:{PORT}/api"

BACKEND_URL = check_if_backend_in_docker()


def check_backend_availability():
    """Check check every 5 seconds if the backend is available.
    Wait a max of 30 seconds before giving up. Display loading message
    during check, remove loading message once backend is available. Display
    error message if backend is not available.
    """
    backend_available = False
    timeout = 30

    backend_url = check_if_backend_in_docker().removesuffix("/api")

    # display loading message
    checking = st.warning("Waiting for backend...")

    while not backend_available and timeout > 0:
        try:
            response = httpx.get(backend_url, timeout=1)
            if response.status_code == 200:
                backend_available = True
        except httpx.TimeoutException:
            time.sleep(5)

        timeout -= 5
    if not backend_available:
        checking.empty()
        st.error(f"Backend is not available at {backend_url}")
    else:
        # remove loading message
        checking.empty()


def _backend_GET(
        endpoint: str,
        headers: dict = {"accept": "application/json, application/toml"}
        ) -> tuple[int, dict | str]:
    """An internal function to make the development of get functions easier.

    Params:
        endpoint(str): the URL of the backend endpoint to post to

    Returns:
        dict: json response from the backend
    """


    try:
        response = httpx.get(url=f"{BACKEND_URL}{endpoint}", headers=headers, follow_redirects=True)
        # print(response.url)  # For Debugging
        # print(response.json())  # For Debugging
        # print(response.status_code)  # For Debugging

        # Raises an HTTPError if the response status code is 4xx or 5xx
        response.raise_for_status()
        if response.status_code == 200:
            return (response.status_code, toml.loads(response.text) if response.headers['content-type'] == 'application/toml' else response.json())
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 500:
            print(f"Server Error (500):{e.response.text}")
            return (e.response.status_code, "Server Error: 500")
        elif e.response.status_code == 422:
            print(f"Unprocessable Content (422): {e.response.text}")
            return (e.response.status_code, "A problem with the payload itself.")
        else:
            print(f"Error ({e.response.status_code}): {e.response.text}")
            return (e.response.status_code, e.response.json())
    except httpx.RequestError as e:
        print(f"An error occurred while requesting {e.request.url!r}.")
        return (500, f"Request Error: {e}")
    return (500, "An unknown error occurred.")

def _backend_POST(
        endpoint: str,
        data: dict,
        headers: dict = {"Content-Type": "application/json", "accept": "application/json"}
        ) -> tuple[int, dict | str]:
    """An internal function to make the development of posting functions easier.

    Params:
        endpoint(str): the URL of the backend endpoint to post to
        data(dict): the concent to put into the backend

    Returns:
        dict: json response from the backend

    Catches:
        httpx.HTTPStatusError: if the response status code is 4xx or 5xx
        httpx.RequestError: if there is a problem with the request
    """

    # Make the POST request
    try:
        response = httpx.post(url=f"{BACKEND_URL}{endpoint}",
                              json=data,
                              headers=headers,
                              follow_redirects=True
                              )
        response.raise_for_status()
        if response.status_code == 201:
            return (response.status_code, response.json())
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 500:
            print(f"Server Error (500):{e.response.text}")
            return (e.response.status_code, "Server Error: 500")
        elif e.response.status_code == 422:
            print(f"Unprocessable Content (422): {e.response.text}")
            return (e.response.status_code, "A problem with the payload itself.")
        else:
            print(f"Error ({e.response.status_code}): {e.response.text}")
            return (e.response.status_code, e.response.json())
    except httpx.RequestError as e:
        print(f"An error occurred while requesting {e.request.url!r}.")
        return (500, f"Request Error: {e}")
    return (500, "An unknown error occurred.")

def _backend_PUT(
        endpoint: str,
        data: dict,
        headers: dict = {"Content-Type": "application/json", "accept": "application/json"}
        ) -> tuple[int, dict | str]:
    """An internal function to make the development of PUT functions/update easier.

    Params:
        endpoint(str): the URL of the backend endpoint to post to
        data(dict): the concent to put into the backend
        headers(dict | None): headers to include in the request

    Returns:
        dict: html response from the backend
    """


    # Make the PUT request
    try:
        response = httpx.put(url=f"{BACKEND_URL}{endpoint}",
                             json=data,
                             headers=headers
                             )
        response.raise_for_status()
        if response.status_code == 200:
            return (response.status_code, toml.loads(response.text) if response.headers['content-type'] == 'application/toml' else response.json())
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 500:
            print(f"Server Error (500):{e.response.text}")
            return (e.response.status_code, "Server Error: 500")
        elif e.response.status_code == 422:
            print(f"Unprocessable Content (422): {e.response.text}")
            return (e.response.status_code, "A problem with the payload itself.")
        else:
            print(f"Error ({e.response.status_code}): {e.response.text}")
            return (e.response.status_code, e.response.json())
    except httpx.RequestError as e:
        print(f"An error occurred while requesting {e.request.url!r}.")
        return (500, f"Request Error: {e}")
    return (500, "An unknown error occurred.")