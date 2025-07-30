"""
This module provides a service layer for interacting with the Finnomena API.

Classes:
- FinnomenaService: A service class that provides methods to fetch stock lists and financial sheets.

Features:
- Abstracts API calls into easy-to-use methods.
- Handles errors and validations for API responses.
- Provides utility methods for fetching stock data and financial sheets by symbol.

Dependencies:
- thaifin.sources.finnomena.api: For making API calls.
- thaifin.sources.finnomena.model: For data models used in API responses.
"""

from pydantic import UUID4
from thaifin.sources.finnomena.api import get_stock_list, get_financial_sheet
from thaifin.sources.finnomena.model import (
    FinancialSheetsResponse,
    FinnomenaListResponse,
    ListingDatum,
    QuarterFinancialSheetDatum,
)


class FinnomenaService:
    def __init__(self):
        pass

    def get_stock_list(self) -> list[ListingDatum]:
        """Fetch the list of stocks from Finnomena API."""

        result: FinnomenaListResponse = get_stock_list()
        if result.statusCode != 200:
            raise ValueError(
                f"Failed to fetch stock list from Finnomena API. Status code: {result.status}"
            )
        if not result.data:
            raise ValueError("No stock data available in the Finnomena API response.")

        # Extract the list of stock listings
        stocks_list: list[ListingDatum] = result.data

        return stocks_list

    def get_stock(self, symbol: str) -> ListingDatum:
        """
        Get stock data for a given symbol.

        Args:
            symbol (str): The stock symbol.

        Returns:
            ListingDatum: The stock data object corresponding to the given symbol.
        """
        stock_list: list[ListingDatum] = self.get_stock_list()
        try:
            stock: ListingDatum = next(s for s in stock_list if s.name == symbol)

        except StopIteration:
            raise ValueError(f"Stock with symbol {symbol} not found.")

        return stock

    def _get_security_id(self, symbol: str) -> str:
        """
        Get the security ID for a given stock symbol.

        Args:
            symbol (str): The stock symbol.

        Returns:
            str: The security ID of the stock.
        """
        stock: ListingDatum = self.get_stock(symbol)
        if stock:
            return stock.security_id
        raise ValueError(f"Stock with symbol {symbol} not found.")

    def get_financial_sheet(
        self, symbol: str, language: str = "en"
    ) -> list[QuarterFinancialSheetDatum] | list[dict]:
        """
        Fetch financial sheet for a given stock symbol.

        Args:
            symbol (str): The stock symbol.
            language (str): Language for field names ('en' for English, 'th' for Thai). Default is 'en'.

        Returns:
            list[QuarterFinancialSheetDatum] | list[dict]: The financial sheet data for the security.
            Returns Pydantic models for 'en', Thai dictionaries for 'th'.
        """
        if language not in ["en", "th"]:
            raise ValueError("Language must be 'en' or 'th'")

        security_id: str = self._get_security_id(symbol)
        security_uuid: UUID4 = UUID4(security_id)
        result: FinancialSheetsResponse = get_financial_sheet(security_uuid)
        if not result.data:
            raise ValueError(
                f"No financial sheet data available for security ID {security_id}."
            )
        if result.statusCode != 200:
            raise ValueError(
                f"Failed to fetch financial sheet from Finnomena API. Status code: {result.status}"
            )

        fundamental_data: list[QuarterFinancialSheetDatum] = result.data

        if language == "th":
            # Convert to Thai dictionaries
            return [item.to_thai_dict() for item in fundamental_data]

        return fundamental_data
