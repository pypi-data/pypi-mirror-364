from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...types import UNSET, Response, Unset


def _get_kwargs(
    restaurant_id: int,
    *,
    date_time: str,
    party_size: Union[Unset, int] = 2,
    scan_days: Union[Unset, int] = 1,
    x_org_key: str,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    headers["x-org-key"] = x_org_key

    params: dict[str, Any] = {}

    params["date_time"] = date_time

    params["party_size"] = party_size

    params["scan_days"] = scan_days

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": f"/timeslots/{restaurant_id}",
        "params": params,
    }

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[Any, HTTPValidationError]]:
    if response.status_code == 200:
        response_200 = response.json()
        return response_200
    if response.status_code == 422:
        response_422 = HTTPValidationError.from_dict(response.json())

        return response_422
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[Any, HTTPValidationError]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    restaurant_id: int,
    *,
    client: AuthenticatedClient,
    date_time: str,
    party_size: Union[Unset, int] = 2,
    scan_days: Union[Unset, int] = 1,
    x_org_key: str,
) -> Response[Union[Any, HTTPValidationError]]:
    """Get Restaurant Timeslots

     Get available timeslots for a specific restaurant (Protected endpoint)
    Requires valid API token in Authorization header

    Args:
        restaurant_id (int):
        date_time (str): Date/time in YYYY-MM-DDTHH:MM format
        party_size (Union[Unset, int]): Number of people Default: 2.
        scan_days (Union[Unset, int]): Number of days to scan Default: 1.
        x_org_key (str): The API key for your organization

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, HTTPValidationError]]
    """

    kwargs = _get_kwargs(
        restaurant_id=restaurant_id,
        date_time=date_time,
        party_size=party_size,
        scan_days=scan_days,
        x_org_key=x_org_key,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    restaurant_id: int,
    *,
    client: AuthenticatedClient,
    date_time: str,
    party_size: Union[Unset, int] = 2,
    scan_days: Union[Unset, int] = 1,
    x_org_key: str,
) -> Optional[Union[Any, HTTPValidationError]]:
    """Get Restaurant Timeslots

     Get available timeslots for a specific restaurant (Protected endpoint)
    Requires valid API token in Authorization header

    Args:
        restaurant_id (int):
        date_time (str): Date/time in YYYY-MM-DDTHH:MM format
        party_size (Union[Unset, int]): Number of people Default: 2.
        scan_days (Union[Unset, int]): Number of days to scan Default: 1.
        x_org_key (str): The API key for your organization

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, HTTPValidationError]
    """

    return sync_detailed(
        restaurant_id=restaurant_id,
        client=client,
        date_time=date_time,
        party_size=party_size,
        scan_days=scan_days,
        x_org_key=x_org_key,
    ).parsed


async def asyncio_detailed(
    restaurant_id: int,
    *,
    client: AuthenticatedClient,
    date_time: str,
    party_size: Union[Unset, int] = 2,
    scan_days: Union[Unset, int] = 1,
    x_org_key: str,
) -> Response[Union[Any, HTTPValidationError]]:
    """Get Restaurant Timeslots

     Get available timeslots for a specific restaurant (Protected endpoint)
    Requires valid API token in Authorization header

    Args:
        restaurant_id (int):
        date_time (str): Date/time in YYYY-MM-DDTHH:MM format
        party_size (Union[Unset, int]): Number of people Default: 2.
        scan_days (Union[Unset, int]): Number of days to scan Default: 1.
        x_org_key (str): The API key for your organization

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, HTTPValidationError]]
    """

    kwargs = _get_kwargs(
        restaurant_id=restaurant_id,
        date_time=date_time,
        party_size=party_size,
        scan_days=scan_days,
        x_org_key=x_org_key,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    restaurant_id: int,
    *,
    client: AuthenticatedClient,
    date_time: str,
    party_size: Union[Unset, int] = 2,
    scan_days: Union[Unset, int] = 1,
    x_org_key: str,
) -> Optional[Union[Any, HTTPValidationError]]:
    """Get Restaurant Timeslots

     Get available timeslots for a specific restaurant (Protected endpoint)
    Requires valid API token in Authorization header

    Args:
        restaurant_id (int):
        date_time (str): Date/time in YYYY-MM-DDTHH:MM format
        party_size (Union[Unset, int]): Number of people Default: 2.
        scan_days (Union[Unset, int]): Number of days to scan Default: 1.
        x_org_key (str): The API key for your organization

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, HTTPValidationError]
    """

    return (
        await asyncio_detailed(
            restaurant_id=restaurant_id,
            client=client,
            date_time=date_time,
            party_size=party_size,
            scan_days=scan_days,
            x_org_key=x_org_key,
        )
    ).parsed
