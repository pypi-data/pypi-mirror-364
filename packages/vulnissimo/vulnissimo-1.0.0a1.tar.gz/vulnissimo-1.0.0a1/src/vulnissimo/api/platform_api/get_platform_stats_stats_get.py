from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.stats import Stats
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    engine: Union[Unset, Any] = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["engine"] = engine

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/stats",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[HTTPValidationError, Stats]]:
    if response.status_code == 200:
        response_200 = Stats.from_dict(response.json())

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
) -> Response[Union[HTTPValidationError, Stats]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    engine: Union[Unset, Any] = UNSET,
) -> Response[Union[HTTPValidationError, Stats]]:
    """Get platform stats

     Get platform stats

    Args:
        engine (Union[Unset, Any]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[HTTPValidationError, Stats]]
    """

    kwargs = _get_kwargs(
        engine=engine,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: Union[AuthenticatedClient, Client],
    engine: Union[Unset, Any] = UNSET,
) -> Optional[Union[HTTPValidationError, Stats]]:
    """Get platform stats

     Get platform stats

    Args:
        engine (Union[Unset, Any]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[HTTPValidationError, Stats]
    """

    return sync_detailed(
        client=client,
        engine=engine,
    ).parsed


async def asyncio_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    engine: Union[Unset, Any] = UNSET,
) -> Response[Union[HTTPValidationError, Stats]]:
    """Get platform stats

     Get platform stats

    Args:
        engine (Union[Unset, Any]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[HTTPValidationError, Stats]]
    """

    kwargs = _get_kwargs(
        engine=engine,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: Union[AuthenticatedClient, Client],
    engine: Union[Unset, Any] = UNSET,
) -> Optional[Union[HTTPValidationError, Stats]]:
    """Get platform stats

     Get platform stats

    Args:
        engine (Union[Unset, Any]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[HTTPValidationError, Stats]
    """

    return (
        await asyncio_detailed(
            client=client,
            engine=engine,
        )
    ).parsed
