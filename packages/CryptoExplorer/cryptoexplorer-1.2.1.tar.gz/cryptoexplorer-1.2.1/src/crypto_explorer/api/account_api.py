import logging
from abc import ABC, abstractmethod

import pandas as pd

from crypto_explorer.api.moralis_api import MoralisAPI
from crypto_explorer.api.blockscout_api import BlockscoutAPI


class APIHandler(ABC):
    """
    Abstract base class implementing the Chain of Responsibility pattern
    for API handlers. This class provides a framework for chaining
    multiple API handlers together, allowing fallback to alternative
    APIs if the primary API fails.

    Attributes
    ----------
    _next_handler : APIHandler | None
        The next handler in the chain.
    verbose : bool
        Flag to control logging verbosity.
    api_key : str
        API key for authentication.
    logger : logging.Logger
        Logger instance for handling log messages.

    Methods
    -------
    set_next_api(handler: MoralisAPI | BlockscoutAPI)
    -> MoralisAPI | BlockscoutAPI
        Sets the next handler in the chain.
    handle(wallet: str, coin_name: bool = False)
        Processes the request and delegates to next handler on failure.
    get_account_swaps(wallet: str, coin_name: bool = False)
        Abstract method to be implemented by concrete handlers.
    """

    def __init__(self):
        self._next_handler = None
        self.verbose = False
        self.api_key = ""
        self.logger = logging.getLogger("API_Handler")
        formatter = logging.Formatter(
            "%(levelname)s %(asctime)s: %(message)s", datefmt="%H:%M:%S"
        )

        handler = logging.StreamHandler()
        handler.setFormatter(formatter)

        if self.logger.hasHandlers():
            self.logger.handlers.clear()

        self.logger.addHandler(handler)
        self.logger.propagate = False

    def set_next_api(
        self,
        handler: MoralisAPI | BlockscoutAPI,
    ) -> MoralisAPI | BlockscoutAPI:
        """
        Set the next handler in the chain of responsibility.

        Parameters
        ----------
        handler : MoralisAPI | BlockscoutAPI
            The next API handler to be called if this one fails.

        Returns
        -------
        MoralisAPI | BlockscoutAPI
            The handler that was set as next in chain.
        """
        self._next_handler = handler
        return handler

    def handle(self, wallet: str, coin_name: bool = False):
        """
        Process the API request with fallback support.

        Attempts to get account swaps using the current handler.
        If it fails, delegates to the next handler in the chain.

        Parameters
        ----------
        wallet : str
            The wallet address to query.
        coin_name : bool, optional
            Flag to include coin names in the response (default=False).

        Returns
        -------
        dict
            The API response data.

        Raises
        ------
        Exception
            If all handlers in the chain fail.
        """
        try:
            return self.get_account_swaps(wallet, coin_name)
        except Exception as e:
            if self._next_handler:
                self.logger.warning("Moralis API failed")
                self.logger.warning("Error: %s", e)
                return self._next_handler.handle(wallet, coin_name)
            raise e

    @abstractmethod
    def get_account_swaps(self, wallet: str, coin_name: bool = False):
        """
        Abstract method to retrieve account swap information.
        Must be implemented by concrete handler classes.

        Parameters
        ----------
        wallet : str
            The wallet address to query swaps for.
        coin_name : bool, optional
            Flag to include coin names in the response (default=False).

        Returns
        -------
        dict
            The swap transaction data for the wallet.

        Raises
        ------
        NotImplementedError
            If the concrete class does not implement this method.
        """


class MoralisHandler(APIHandler):
    """
    Concrete implementation of APIHandler for the Moralis API service.

    This handler processes requests through the Moralis API and can be
    chained with other handlers for fallback functionality.

    Parameters
    ----------
    api_key : str
        The API key for Moralis authentication.
    verbose : bool, optional
        Whether to enable verbose logging (default=True).

    Attributes
    ----------
    api_key : str
        Stored API key for Moralis authentication.
    verbose : bool
        Flag controlling log verbosity.

    Methods
    -------
    get_account_swaps(wallet: str, coin_name: bool = False) -> dict
        Retrieves swap transactions for a given wallet address using
        Moralis API.
    """

    def __init__(self, api_key: str, verbose: bool = True):
        """
        Initialize the Moralis API handler.

        Parameters
        ----------
        api_key : str
            The API key for Moralis authentication.
        verbose : bool, optional
            Whether to enable verbose logging (default=True).
        """
        super().__init__()
        self.api_key = api_key
        self.verbose = verbose

        if self.verbose:
            self.logger.setLevel(logging.INFO)
        else:
            self.logger.setLevel(logging.WARNING)

    def get_account_swaps(self, wallet: str, coin_name: bool = False):
        """
        Retrieve swap transactions for a wallet using Moralis API.

        Parameters
        ----------
        wallet : str
            The wallet address to query swaps for.
        coin_name : bool, optional
            Flag to include coin names in response (default=False).

        Returns
        -------
        dict
            Swap transaction data from Moralis API.
        """
        moralis_api = MoralisAPI(self.verbose, self.api_key)
        self.logger.info("Running Moralis API...")
        return moralis_api.get_account_swaps(wallet, coin_name)


class BlockscoutHandler(APIHandler):
    """
    Concrete implementation of APIHandler for the Blockscout API
    service.

    This handler processes blockchain data requests through the
    Blockscout API and can be chained with other handlers for fallback
    functionality.

    Parameters
    ----------
    verbose : bool, optional
        Whether to enable verbose logging (default=True).

    Attributes
    ----------
    verbose : bool
        Flag controlling log verbosity level.
    logger : logging.Logger
        Logger instance inherited from APIHandler.

    Methods
    -------
    get_account_swaps(wallet: str, coin_name: bool = False)
    -> pd.DataFrame
        Retrieves swap transactions for a given wallet address using
        Blockscout API.
    """

    def __init__(self, verbose: bool = True):
        """
        Initialize the Blockscout API handler.

        Parameters
        ----------
        verbose : bool, optional
            Whether to enable verbose logging (default=True).
        """
        super().__init__()
        self.verbose = verbose

        if self.verbose:
            self.logger.setLevel(logging.INFO)
        else:
            self.logger.setLevel(logging.WARNING)

    def get_account_swaps(self, wallet: str, coin_name: bool = False):
        """
        Retrieve swap transactions for a wallet using Blockscout API.

        Parameters
        ----------
        wallet : str
            The wallet address to query transactions for.
        coin_name : bool, optional
            Flag to include coin names in response (default=False).

        Returns
        -------
        pd.DataFrame
            DataFrame containing swap transaction data from Blockscout
            API.
        """
        self.logger.info("Running Blockscout API...")

        blockscout_api = BlockscoutAPI(self.verbose)
        transactions = blockscout_api.get_account_transactions(
            wallet, coin_name
        )

        return pd.DataFrame(transactions)


class AccountAPI:
    """
    A high-level API handler that implements the Chain of Responsibility
    pattern to fetch wallet swap transactions from multiple blockchain
    data providers.

    Uses [`MoralisHandler`](api/account_api.py) as primary provider with
    [`BlockscoutHandler`](api/account_api.py) as fallback.

    Parameters
    ----------
    api_key : str
        The API key for Moralis authentication.
    verbose : bool, optional
        Whether to enable verbose logging
        (default=True).

    Attributes
    ----------
    api_key : str
        Stored API key for Moralis authentication.
    verbose : bool
        Flag controlling log verbosity.
    """
    def __init__(self, api_key: str, verbose: bool = True):
        """
        Initialize the AccountAPI handler.

        Parameters
        ----------
        api_key : str
            The API key for Moralis authentication.
        verbose : bool, optional
            Whether to enable verbose logging
            (default=True).
        """
        self.api_key = api_key
        self.verbose = verbose

    def get_wallet_swaps(self, wallet: str, coin_name: bool = False):
        """
        Retrieve swap transactions for a wallet address using chained
        API providers.

        Parameters
        ----------
        wallet : str
            The wallet address to query transactions for.
        coin_name : bool, optional
            Flag to include coin names in response
            (default=False).

        Returns
        -------
        pd.DataFrame
            DataFrame containing swap transaction data. Falls back to
            Blockscout if Moralis fails.
        """
        moralis = MoralisHandler(self.api_key, self.verbose)
        blockscout = BlockscoutHandler(self.verbose)

        moralis.set_next_api(blockscout)

        return moralis.handle(wallet, coin_name)

    def get_buys(
        self,
        wallet_address: str,
        asset_name: str = "WBTC",
    ) -> pd.DataFrame:
        dataframe = self.get_wallet_swaps(
            wallet_address,
            coin_name=True,
        )

        buys = (
            dataframe.query(f"to_coin_name == '{asset_name}'")
            .iloc[::-1]
            .reset_index(drop=True)
        )

        buys.index = buys.index + 1
        return buys

    def get_sells(
        self,
        wallet_address: str,
        asset_name: str = "WBTC",
    ) -> pd.DataFrame:
        dataframe = self.get_wallet_swaps(
            wallet_address,
            coin_name=True,
        )

        sells = (
            dataframe.query(f"from_coin_name == '{asset_name}'")
            .iloc[::-1]
            .reset_index(drop=True)
        )

        sells.index = sells.index + 1
        return sells
