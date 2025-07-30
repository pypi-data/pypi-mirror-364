from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.booking_request import BookingRequest
from ...models.http_validation_error import HTTPValidationError
from ...types import Response


def _get_kwargs(
    *,
    body: BookingRequest,
    x_org_key: str,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    headers["x-org-key"] = x_org_key

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/book",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[Any, HTTPValidationError]]:
    if response.status_code == 201:
        response_201 = response.json()
        return response_201
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
    *,
    client: AuthenticatedClient,
    body: BookingRequest,
    x_org_key: str,
) -> Response[Union[Any, HTTPValidationError]]:
    """Book Reservation Endpoint

     Book a reservation at a restaurant (Protected endpoint)
    Uses the new standalone booking script

    Args:
        x_org_key (str): The API key for your organization
        body (BookingRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, HTTPValidationError]]
    """

    kwargs = _get_kwargs(
        body=body,
        x_org_key=x_org_key,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    body: BookingRequest,
    x_org_key: str,
) -> Optional[Union[Any, HTTPValidationError]]:
    """Book Reservation Endpoint

     Book a reservation at a restaurant (Protected endpoint)
    Uses the new standalone booking script

    Args:
        x_org_key (str): The API key for your organization
        body (BookingRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, HTTPValidationError]
    """

    return sync_detailed(
        client=client,
        body=body,
        x_org_key=x_org_key,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    body: BookingRequest,
    x_org_key: str,
) -> Response[Union[Any, HTTPValidationError]]:
    """Book Reservation Endpoint

     Book a reservation at a restaurant (Protected endpoint)
    Uses the new standalone booking script

    Args:
        x_org_key (str): The API key for your organization
        body (BookingRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, HTTPValidationError]]
    """

    kwargs = _get_kwargs(
        body=body,
        x_org_key=x_org_key,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    body: BookingRequest,
    x_org_key: str,
) -> Optional[Union[Any, HTTPValidationError]]:
    """Book Reservation Endpoint

     Book a reservation at a restaurant (Protected endpoint)
    Uses the new standalone booking script

    Args:
        x_org_key (str): The API key for your organization
        body (BookingRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, HTTPValidationError]
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
            x_org_key=x_org_key,
        )
    ).parsed
