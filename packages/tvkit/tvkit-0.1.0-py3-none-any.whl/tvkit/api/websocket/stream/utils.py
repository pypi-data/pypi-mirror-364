"""
Module providing utility functions for validating exchange symbols and fetching
TradingView indicators and their metadata.

This module contains async functions to:
  - Validate one or more exchange symbols.
  - Fetch a list of TradingView indicators based on a search query.
  - Display the fetched indicators and allow the user to select one.
  - Fetch and prepare indicator metadata for further processing.
"""

import asyncio
import logging
from typing import Any, Dict, List, Optional, Tuple, Union

import httpx


async def validate_symbols(exchange_symbol: Union[str, List[str]]) -> bool:
    """
    Validate one or more exchange symbols asynchronously.

    This function checks whether the provided symbol or list of symbols follows
    the expected format ("EXCHANGE:SYMBOL") and validates each symbol by making a
    request to a TradingView validation URL.

    Args:
        exchange_symbol: A single symbol or a list of symbols in the format "EXCHANGE:SYMBOL".

    Raises:
        ValueError: If exchange_symbol is empty, if a symbol does not follow the "EXCHANGE:SYMBOL" format,
                    or if the symbol fails validation after the allowed number of retries.
        httpx.HTTPError: If there's an HTTP-related error during validation.

    Returns:
        True if all provided symbols are valid.

    Example:
        >>> await validate_symbols("BINANCE:BTCUSDT")
        True
        >>> await validate_symbols(["BINANCE:BTCUSDT", "NASDAQ:AAPL"])
        True
    """
    validate_url: str = (
        "https://scanner.tradingview.com/symbol?"
        "symbol={exchange}%3A{symbol}&fields=market&no_404=false"
    )

    if not exchange_symbol:
        raise ValueError("exchange_symbol cannot be empty")

    symbols: List[str]
    if isinstance(exchange_symbol, str):
        symbols = [exchange_symbol]
    else:
        symbols = exchange_symbol

    async with httpx.AsyncClient(timeout=5.0) as client:
        for item in symbols:
            parts: List[str] = item.split(":")
            if len(parts) != 2:
                raise ValueError(
                    f"Invalid symbol format '{item}'. Must be like 'BINANCE:BTCUSDT'"
                )

            exchange: str
            symbol: str
            exchange, symbol = parts
            retries: int = 3

            for attempt in range(retries):
                try:
                    response: httpx.Response = await client.get(
                        validate_url.format(exchange=exchange, symbol=symbol)
                    )
                    response.raise_for_status()
                except httpx.HTTPStatusError as exc:
                    if exc.response.status_code == 404:
                        raise ValueError(
                            f"Invalid exchange:symbol '{item}' after {retries} attempts"
                        ) from exc

                    logging.warning(
                        "Attempt %d failed to validate exchange:symbol '%s': %s",
                        attempt + 1,
                        item,
                        exc,
                    )

                    if attempt < retries - 1:
                        await asyncio.sleep(1.0)  # Wait briefly before retrying
                    else:
                        raise ValueError(
                            f"Invalid exchange:symbol '{item}' after {retries} attempts"
                        ) from exc
                except httpx.RequestError as exc:
                    logging.warning(
                        "Attempt %d failed to validate exchange:symbol '%s': %s",
                        attempt + 1,
                        item,
                        exc,
                    )

                    if attempt < retries - 1:
                        await asyncio.sleep(1.0)  # Wait briefly before retrying
                    else:
                        raise ValueError(
                            f"Invalid exchange:symbol '{item}' after {retries} attempts"
                        ) from exc
                else:
                    break  # Successful request; exit retry loop

    return True


class IndicatorData:
    """Data structure for TradingView indicator information."""
    
    def __init__(
        self,
        script_name: str,
        image_url: str,
        author: str,
        agree_count: int,
        is_recommended: bool,
        script_id_part: str,
        version: Optional[str] = None,
    ) -> None:
        self.script_name = script_name
        self.image_url = image_url
        self.author = author
        self.agree_count = agree_count
        self.is_recommended = is_recommended
        self.script_id_part = script_id_part
        self.version = version

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "scriptName": self.script_name,
            "imageUrl": self.image_url,
            "author": self.author,
            "agreeCount": self.agree_count,
            "isRecommended": self.is_recommended,
            "scriptIdPart": self.script_id_part,
            "version": self.version,
        }


async def fetch_tradingview_indicators(query: str) -> List[IndicatorData]:
    """
    Fetch TradingView indicators based on a search query asynchronously.

    This function sends a GET request to the TradingView public endpoint for indicator
    suggestions and filters the results by checking if the search query appears in either
    the script name or the author's username.

    Args:
        query: The search term used to filter indicators by script name or author.

    Returns:
        A list of IndicatorData objects containing details of matching indicators.

    Raises:
        httpx.HTTPError: If there's an HTTP-related error during the request.

    Example:
        >>> indicators = await fetch_tradingview_indicators("RSI")
        >>> for indicator in indicators:
        ...     print(f"{indicator.script_name} by {indicator.author}")
    """
    url: str = f"https://www.tradingview.com/pubscripts-suggest-json/?search={query}"

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response: httpx.Response = await client.get(url)
            response.raise_for_status()
            json_data: Dict[str, Any] = response.json()

            results: List[Any] = json_data.get("results", [])
            filtered_results: List[IndicatorData] = []

            for indicator in results:
                if (
                    query.lower() in indicator["scriptName"].lower()
                    or query.lower() in indicator["author"]["username"].lower()
                ):
                    filtered_results.append(
                        IndicatorData(
                            script_name=indicator["scriptName"],
                            image_url=indicator["imageUrl"],
                            author=indicator["author"]["username"],
                            agree_count=indicator["agreeCount"],
                            is_recommended=indicator["isRecommended"],
                            script_id_part=indicator["scriptIdPart"],
                            version=indicator.get("version"),
                        )
                    )

            return filtered_results

    except httpx.RequestError as exc:
        logging.error("Error fetching TradingView indicators: %s", exc)
        return []


def display_and_select_indicator(indicators: List[IndicatorData]) -> Optional[Tuple[Optional[str], Optional[str]]]:
    """
    Display a list of indicators and prompt the user to select one.

    This function prints the available indicators with numbering, waits for the user
    to input the number corresponding to their preferred indicator, and returns the
    selected indicator's scriptId and version.

    Args:
        indicators: A list of IndicatorData objects containing indicator details.

    Returns:
        A tuple (scriptId, version) of the selected indicator if the selection
        is valid; otherwise, None.

    Example:
        >>> indicators = await fetch_tradingview_indicators("RSI")
        >>> result = display_and_select_indicator(indicators)
        >>> if result:
        ...     script_id, version = result
        ...     print(f"Selected script ID: {script_id}, version: {version}")
    """
    if not indicators:
        print("No indicators found.")
        return None

    print("\n-- Enter the number of your preferred indicator:")
    for idx, item in enumerate(indicators, start=1):
        print(f"{idx}- {item.script_name} by {item.author}")

    try:
        selected_index = int(input("Your choice: ")) - 1
    except ValueError:
        print("Invalid input. Please enter a number.")
        return None

    if 0 <= selected_index < len(indicators):
        selected_indicator = indicators[selected_index]
        print(
            f"You selected: {selected_indicator.script_name} by {selected_indicator.author}"
        )
        return (
            selected_indicator.script_id_part,
            selected_indicator.version,
        )
    else:
        print("Invalid selection.")
        return None


async def fetch_indicator_metadata(script_id: str, script_version: str, chart_session: str) -> Dict[str, Any]:
    """
    Fetch metadata for a TradingView indicator based on its script ID and version asynchronously.

    This function constructs a URL using the provided script ID and version, sends a GET
    request to fetch the indicator metadata, and then prepares the metadata for further
    processing using the chart session.

    Args:
        script_id: The unique identifier for the indicator script.
        script_version: The version of the indicator script.
        chart_session: The chart session identifier used in further processing.

    Returns:
        A dictionary containing the prepared indicator metadata if successful;
        an empty dictionary is returned if an error occurs.

    Raises:
        httpx.HTTPError: If there's an HTTP-related error during the request.

    Example:
        >>> metadata = await fetch_indicator_metadata("PUB;123", "1.0", "session123")
        >>> if metadata:
        ...     print("Metadata fetched successfully")
    """
    url: str = f"https://pine-facade.tradingview.com/pine-facade/translate/{script_id}/{script_version}"

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response: httpx.Response = await client.get(url)
            response.raise_for_status()
            json_data: Dict[str, Any] = response.json()

            metainfo: Optional[Dict[str, Any]] = json_data.get("result", {}).get("metaInfo")
            if metainfo:
                return prepare_indicator_metadata(script_id, metainfo, chart_session)

            return {}

    except httpx.RequestError as exc:
        logging.error("Error fetching indicator metadata: %s", exc)
        return {}


def prepare_indicator_metadata(script_id: str, metainfo: Dict[str, Any], chart_session: str) -> Dict[str, Any]:
    """
    Prepare indicator metadata into the required payload structure.

    This function constructs a dictionary payload for creating a study (indicator) session.
    It extracts default input values and metadata from the provided metainfo and combines them
    with the provided script ID and chart session.

    Args:
        script_id: The unique identifier for the indicator script.
        metainfo: A dictionary containing metadata information for the indicator.
        chart_session: The chart session identifier.

    Returns:
        A dictionary representing the payload required to create a study with the indicator.

    Example:
        >>> metainfo = {"inputs": [{"defval": "test", "id": "in_param1", "type": "string"}]}
        >>> payload = prepare_indicator_metadata("PUB;123", metainfo, "session123")
        >>> print(payload["m"])  # "create_study"
    """
    output_data: Dict[str, Any] = {
        "m": "create_study",
        "p": [
            chart_session,
            "st9",
            "st1",
            "sds_1",
            "Script@tv-scripting-101!",
            {
                "text": metainfo["inputs"][0]["defval"],
                "pineId": script_id,
                "pineVersion": metainfo.get("pine", {}).get("version", "1.0"),
                "pineFeatures": {
                    "v": '{"indicator":1,"plot":1,"ta":1}',
                    "f": True,
                    "t": "text"
                },
                "__profile": {
                    "v": False,
                    "f": True,
                    "t": "bool"
                }
            }
        ]
    }

    # Collect additional input values that start with 'in_'
    in_x: Dict[str, Dict[str, Any]] = {}
    for input_item in metainfo.get("inputs", []):
        if input_item["id"].startswith("in_"):
            in_x[input_item["id"]] = {
                "v": input_item["defval"],
                "f": True,
                "t": input_item["type"]
            }

    # Update the dictionary inside output_data with additional inputs
    for item in output_data["p"]:
        if isinstance(item, dict):
            item.update(in_x)

    return output_data
