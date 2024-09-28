"""Functionality for interacting with the Mojang API"""

import time
import warnings
from typing import Callable

import requests


def _wrap_request_fail(api_call: Callable) -> Callable:
    def wrapped(*args, **kwargs):
        try:
            return api_call(*args, **kwargs)
        except requests.ConnectionError as bad_connection:
            raise RuntimeError(
                "Could not access Mojang API. Are you connected to the internet?"
            ) from bad_connection
        except requests.Timeout as timeout:
            raise RuntimeError(
                "Connection timed out trying to access Mojang API. Try again later?"
            ) from timeout
        except (
            requests.RequestException,
            requests.JSONDecodeError,
            KeyError,
        ) as bad_request:
            raise RuntimeError(
                "Something went wrong. Please report this problem to"
                " https://github.com/OpenBagTwo/head-hunter/issues/new"
            ) from bad_request

    return wrapped


@_wrap_request_fail
def _get_uuid_from_username(username: str) -> str:
    """Look up a player's UUID fromm their username

    Parameters
    ----------
    username : str
        A player's username

    Returns
    -------
    str
        The player's UUID

    Raises
    ------
    ValueError
        If no player with that username can be found
    RuntimeError
        If anything else goes wrong

    Notes
    -----
    While this query is case-insensitive, this method does not check if the
    provided username is valid
    """
    response = requests.get(
        f"https://api.mojang.com/users/profiles/minecraft/{username}"
    )
    match response.status_code:
        case requests.codes.ok:
            return response.json()["id"]
        case requests.codes.not_found:
            raise ValueError(response.json()["errorMessage"])
        case requests.codes.too_many_requests:
            warnings.warn(
                "Getting rate limited. Sleeping for 10 seconds before trying again."
            )
            time.sleep(10)
            return _get_uuid_from_username(username)
        case _:
            response.raise_for_status()
    raise requests.RequestException()


@_wrap_request_fail
def _get_current_skin_from_uuid(uuid: str) -> str:
    """Get the current skin for the player with the specified UUID

    Parameters
    ----------
    uuid : str
        The player's UUID

    Returns
    -------
    str
        The player's skin, encoded in base64

    Raises
    ------
    ValueError
        If no player with that UUID can be found
    RuntimeError
        If anything else goes wrong
    """
    response = requests.get(
        f"https://sessionserver.mojang.com/session/minecraft/profile/{uuid}"
    )
    match response.status_code:
        case requests.codes.ok:
            return {
                item["name"]: item["value"] for item in response.json()["properties"]
            }["textures"]
        case requests.codes.bad_request:
            raise ValueError(response.json()["errorMessage"])
        case requests.codes.no_content:
            raise ValueError(f"Couldn't find any profile with UUID {uuid}")
        case requests.codes.too_many_requests:
            warnings.warn(
                "Getting rate limited. Sleeping for 10 seconds before trying again."
            )
            time.sleep(10)
            return _get_current_skin_from_uuid(uuid)
        case _:
            response.raise_for_status()
    raise requests.RequestException()


def get_players_current_skin(username: str) -> str:
    """Grab a player's current skin

    Parameters
    ----------
    username : str
        A player's username

    Returns
    -------
    str
        The player's skin, encoded in base64

    Raises
    ------
    ValueError
        If no player with that username can be found
    RuntimeError
        If anything else goes wrong

    Notes
    -----
    While this query is case-insensitive, this method does not check if the
    provided username is valid
    """
    uuid = _get_uuid_from_username(username)
    return _get_current_skin_from_uuid(uuid)
