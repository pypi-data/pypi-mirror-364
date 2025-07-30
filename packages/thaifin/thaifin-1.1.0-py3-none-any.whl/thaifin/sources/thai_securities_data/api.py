"""
This module provides functions to interact with the Thai Securities Data API.

Functions:
- get_meta_data(language: str) -> MetaData: Fetches metadata for Thai securities, including market and sector data.
- get_securities_data(language: str) -> List[SecurityData]: Retrieves detailed securities data from the API.

Features:
- Caching: Results are cached for 24 hours to reduce API calls.
- Retry Logic: Automatically retries failed requests with exponential backoff.

Dependencies:
- cachetools: For caching API responses.
- tenacity: For implementing retry logic.
- httpx: For making HTTP requests.
- pydantic: For data validation and parsing.
"""

from cachetools import cached, TTLCache
from tenacity import retry, stop_after_attempt, wait_exponential
import httpx
from typing import List

from thaifin.sources.thai_securities_data.models import MetaData, SecurityData

# Base URL for Thai Securities Data API
base_url = "https://raw.githubusercontent.com/lumduan/thai-securities-data/main"


@cached(cache=TTLCache(maxsize=1000, ttl=24 * 60 * 60))  # 24 hours cache
@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10),
    reraise=True,
)
def get_meta_data(language: str) -> MetaData:
    """
    Get metadata for Thai Securities Data.

    Returns:
        MetaData: Metadata object containing last updated time, total securities, market and sector data.

    Raises:
        ValueError: If there is an issue with the API response or data validation.
    """
    if language not in ["en", "th"]:
        raise ValueError("Language must be either 'en' or 'th'.")

    url = f"{base_url}/metadata_{language}.json"

    try:
        with httpx.Client() as client:
            response = client.get(url)
            response.raise_for_status()
        return MetaData.model_validate_json(response.text)

    except httpx.RequestError as e:
        raise ValueError(f"An error occurred while requesting metadata: {e}") from e
    except httpx.HTTPStatusError as e:
        raise ValueError(
            f"HTTP error occurred: {e.response.status_code} - {e.response.text}"
        ) from e
    except Exception as e:
        raise ValueError(f"An unexpected error occurred: {e}") from e


@cached(cache=TTLCache(maxsize=1000, ttl=24 * 60 * 60))  # 24 hours cache
@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10),
    reraise=True,
)
def get_securities_data(language: str) -> List[SecurityData]:
    """
    Get securities data from Thai Securities Data API.

    Returns:
        List[SecurityData]: List of SecurityData objects containing information about securities.

    Raises:
        ValueError: If there is an issue with the API response or data validation.
    """
    if language not in ["en", "th"]:
        raise ValueError("Language must be either 'en' or 'th'.")

    url = f"{base_url}/thai_securities_all_{language}.json"

    try:
        with httpx.Client() as client:
            response = client.get(url)
            response.raise_for_status()
        securities_data = response.json()
        return [
            SecurityData.model_validate(item)
            for item in securities_data
            if isinstance(item, dict)
        ]

    except httpx.RequestError as e:
        raise ValueError(
            f"An error occurred while requesting securities data: {e}"
        ) from e
    except httpx.HTTPStatusError as e:
        raise ValueError(
            f"HTTP error occurred: {e.response.status_code} - {e.response.text}"
        ) from e
    except Exception as e:
        raise ValueError(f"An unexpected error occurred: {e}") from e
