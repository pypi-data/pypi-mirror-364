from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.search_request import SearchRequest
from ...types import Response


def _get_kwargs(
    *,
    body: SearchRequest,
    x_org_key: str,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    headers["x-org-key"] = x_org_key

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/search",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

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
    *,
    client: AuthenticatedClient,
    body: SearchRequest,
    x_org_key: str,
) -> Response[Union[Any, HTTPValidationError]]:
    """Search Restaurants

     Search OpenTable restaurants (Protected endpoint)
    Requires valid API token in Authorization header

    Args:
        x_org_key (str): The API key for your organization
        body (SearchRequest):

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
    body: SearchRequest,
    x_org_key: str,
) -> Optional[Union[Any, HTTPValidationError]]:
    """Search Restaurants

     Search OpenTable restaurants (Protected endpoint)
    Requires valid API token in Authorization header

    Args:
        x_org_key (str): The API key for your organization
        body (SearchRequest):

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
    body: SearchRequest,
    x_org_key: str,
) -> Response[Union[Any, HTTPValidationError]]:
    """Search Restaurants

     Search OpenTable restaurants (Protected endpoint)
    Requires valid API token in Authorization header

    Args:
        x_org_key (str): The API key for your organization
        body (SearchRequest):

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
    body: SearchRequest,
    x_org_key: str,
) -> Optional[Union[Any, HTTPValidationError]]:
    """Search Restaurants

     Search OpenTable restaurants (Protected endpoint)
    Requires valid API token in Authorization header

    Args:
        x_org_key (str): The API key for your organization
        body (SearchRequest):

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
