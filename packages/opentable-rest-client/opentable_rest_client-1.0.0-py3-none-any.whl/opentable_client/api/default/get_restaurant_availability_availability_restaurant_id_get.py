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
    party_size: Union[Unset, int] = 2,
    days: Union[Unset, int] = 7,
    start_hour: Union[Unset, int] = 17,
    end_hour: Union[Unset, int] = 21,
    start_date: Union[None, Unset, str] = UNSET,
    x_org_key: str,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    headers["x-org-key"] = x_org_key

    params: dict[str, Any] = {}

    params["party_size"] = party_size

    params["days"] = days

    params["start_hour"] = start_hour

    params["end_hour"] = end_hour

    json_start_date: Union[None, Unset, str]
    if isinstance(start_date, Unset):
        json_start_date = UNSET
    else:
        json_start_date = start_date
    params["start_date"] = json_start_date

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": f"/availability/{restaurant_id}",
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
    party_size: Union[Unset, int] = 2,
    days: Union[Unset, int] = 7,
    start_hour: Union[Unset, int] = 17,
    end_hour: Union[Unset, int] = 21,
    start_date: Union[None, Unset, str] = UNSET,
    x_org_key: str,
) -> Response[Union[Any, HTTPValidationError]]:
    """Get Restaurant Availability

     Get comprehensive availability for a restaurant over multiple days (Protected endpoint)
    Uses the more robust availability checker with multi-day scanning
    Requires valid API token in Authorization header

    Args:
        restaurant_id (int):
        party_size (Union[Unset, int]): Number of people Default: 2.
        days (Union[Unset, int]): Number of days to scan ahead Default: 7.
        start_hour (Union[Unset, int]): Starting hour (24h format) Default: 17.
        end_hour (Union[Unset, int]): Ending hour (24h format) Default: 21.
        start_date (Union[None, Unset, str]): Start date (YYYY-MM-DD, defaults to today)
        x_org_key (str): The API key for your organization

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, HTTPValidationError]]
    """

    kwargs = _get_kwargs(
        restaurant_id=restaurant_id,
        party_size=party_size,
        days=days,
        start_hour=start_hour,
        end_hour=end_hour,
        start_date=start_date,
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
    party_size: Union[Unset, int] = 2,
    days: Union[Unset, int] = 7,
    start_hour: Union[Unset, int] = 17,
    end_hour: Union[Unset, int] = 21,
    start_date: Union[None, Unset, str] = UNSET,
    x_org_key: str,
) -> Optional[Union[Any, HTTPValidationError]]:
    """Get Restaurant Availability

     Get comprehensive availability for a restaurant over multiple days (Protected endpoint)
    Uses the more robust availability checker with multi-day scanning
    Requires valid API token in Authorization header

    Args:
        restaurant_id (int):
        party_size (Union[Unset, int]): Number of people Default: 2.
        days (Union[Unset, int]): Number of days to scan ahead Default: 7.
        start_hour (Union[Unset, int]): Starting hour (24h format) Default: 17.
        end_hour (Union[Unset, int]): Ending hour (24h format) Default: 21.
        start_date (Union[None, Unset, str]): Start date (YYYY-MM-DD, defaults to today)
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
        party_size=party_size,
        days=days,
        start_hour=start_hour,
        end_hour=end_hour,
        start_date=start_date,
        x_org_key=x_org_key,
    ).parsed


async def asyncio_detailed(
    restaurant_id: int,
    *,
    client: AuthenticatedClient,
    party_size: Union[Unset, int] = 2,
    days: Union[Unset, int] = 7,
    start_hour: Union[Unset, int] = 17,
    end_hour: Union[Unset, int] = 21,
    start_date: Union[None, Unset, str] = UNSET,
    x_org_key: str,
) -> Response[Union[Any, HTTPValidationError]]:
    """Get Restaurant Availability

     Get comprehensive availability for a restaurant over multiple days (Protected endpoint)
    Uses the more robust availability checker with multi-day scanning
    Requires valid API token in Authorization header

    Args:
        restaurant_id (int):
        party_size (Union[Unset, int]): Number of people Default: 2.
        days (Union[Unset, int]): Number of days to scan ahead Default: 7.
        start_hour (Union[Unset, int]): Starting hour (24h format) Default: 17.
        end_hour (Union[Unset, int]): Ending hour (24h format) Default: 21.
        start_date (Union[None, Unset, str]): Start date (YYYY-MM-DD, defaults to today)
        x_org_key (str): The API key for your organization

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, HTTPValidationError]]
    """

    kwargs = _get_kwargs(
        restaurant_id=restaurant_id,
        party_size=party_size,
        days=days,
        start_hour=start_hour,
        end_hour=end_hour,
        start_date=start_date,
        x_org_key=x_org_key,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    restaurant_id: int,
    *,
    client: AuthenticatedClient,
    party_size: Union[Unset, int] = 2,
    days: Union[Unset, int] = 7,
    start_hour: Union[Unset, int] = 17,
    end_hour: Union[Unset, int] = 21,
    start_date: Union[None, Unset, str] = UNSET,
    x_org_key: str,
) -> Optional[Union[Any, HTTPValidationError]]:
    """Get Restaurant Availability

     Get comprehensive availability for a restaurant over multiple days (Protected endpoint)
    Uses the more robust availability checker with multi-day scanning
    Requires valid API token in Authorization header

    Args:
        restaurant_id (int):
        party_size (Union[Unset, int]): Number of people Default: 2.
        days (Union[Unset, int]): Number of days to scan ahead Default: 7.
        start_hour (Union[Unset, int]): Starting hour (24h format) Default: 17.
        end_hour (Union[Unset, int]): Ending hour (24h format) Default: 21.
        start_date (Union[None, Unset, str]): Start date (YYYY-MM-DD, defaults to today)
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
            party_size=party_size,
            days=days,
            start_hour=start_hour,
            end_hour=end_hour,
            start_date=start_date,
            x_org_key=x_org_key,
        )
    ).parsed
