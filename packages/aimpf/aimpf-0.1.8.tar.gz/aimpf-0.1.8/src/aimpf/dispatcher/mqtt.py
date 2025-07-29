import logging
import requests
from datetime import datetime
from .dispatcher import Dispatcher

logger = logging.getLogger(__name__)


class DbSubscriber(Dispatcher):
    """
    Base class for database subscribers.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._label = None

    @property
    def label(self):
        """
        The label of the resource.
        """
        return self._label

    @property
    def columns(self) -> list:
        """
        List columns for a resource.

        Returns
        -------
        JSON
            List of columns keyed by table name.

        Raises
        ------
        ValueError
            If the label is not set.
        requests.HTTPError
            If the request fails.
        """
        if self._label is None:
            raise ValueError("Label is not set")
        response = self.auth.get(f"resources/{self._label}/columns")
        response.raise_for_status()
        return response.json()["Messages"]

    def check(self) -> requests.Response:
        """
        Check the health of the server.

        Returns
        -------
        requests.Response
            The response object.
        """
        return self.auth.get("check")

    def is_alive(self) -> bool:
        """
        Verifies that the server is running and accepting API requests.

        Returns
        -------
        bool
            True if the server is running, False otherwise.

        Raises
        ------
        requests.HTTPError
            If the request fails.
        """
        try:
            response = self.check()
            response.raise_for_status()
            return response.json()["health"] == "alive"
        except Exception as e:
            logger.error(f"Error checking {self.label}: {e}")
            return False

    def keywords(
            self,
            *,
            columns: str | list[str] | None=None,
            where: str | None=None,
            start: str | datetime | None=None,
            end: str | datetime | None=None,
            limit: int | None=None) -> dict[str, list]:
        """
        Check the keywords being provided.

        Returns
        -------
        requests.Response
            The response object.
        """
        param_list = []
        if columns:
            # Prepare the column list
            columns_list = columns if isinstance(columns, list) else [columns]
            columns = ",".join(columns_list)
            param_list.append(f"columns={columns}")
        # Build up the parameter string
        if where:
            param_list.append(f"where={where}")
        if start:
            param_list.append(f"from={start}")
        if end:
            param_list.append(f"to={end}")
        if limit:
            param_list.append(f"limit={int(limit)}")
        params = "?" + "&".join(param_list) if param_list else ""
        response = self.auth.get(
            f"keywords{params}")
        response.raise_for_status()
        return response.json()

    def list_resources(self) -> dict:
        """
        List resources available.

        Returns
        -------
        list
            List of resources.

        Raises
        ------
        requests.HTTPError
            If the request fails.
        """
        response = self.auth.get("resources/list")
        response.raise_for_status()
        return response.json()

    def distinct(
            self,
            columns: str | list[str],
            *,
            where: str | None=None,
            start: str | datetime | None=None,
            end: str | datetime | None=None,
            limit: int | None=None) -> dict[str, list]:
        """
        Get distinct values for a column.

        Parameters
        ----------
        columns : str | list
            Column name or list of column names.
        where : str, optional
            Comma-separated list of conditions. Each must match
            <col><op><value> where <col> is a column name in the table, <op>
            is a comparison operator ("=", "<", ">", "<=", ">="), and <value>
            is present in the database. WARNING: This can be quite slow as
            query sanitation can take a very long time.
        start : str or datetime, optional
            Start date or time.
        end : str or datetime, optional
            End date or time.
        limit : int, optional
            Maximum number of distinct values to return.

        Returns
        -------
        dict
            Dictionary of distinct values keyed by column name.

        Raises
        ------
        ValueError
            If the label is not set.
        requests.HTTPError
            If the request fails.
        """
        if self._label is None:
            raise ValueError("Label is not set")
        # Prepare the column list
        columns_list = columns if isinstance(columns, list) else [columns]
        columns = ",".join(columns_list)
        # Build up the parameter string
        param_list = []
        if where:
            param_list.append(f"where={where}")
        if start:
            param_list.append(f"from={start}")
        if end:
            param_list.append(f"to={end}")
        if limit:
            param_list.append(f"limit={int(limit)}")
        params = "?" + "&".join(param_list) if param_list else ""
        response = self.auth.get(
            f"resources/{self._label}/distinct/{columns}{params}")
        response.raise_for_status()
        # Return the response
        # return { col:val for col,val in zip(columns_list, response.json()) }
        return response.json()

    def count(
            self,
            *,
            where: str | None=None,
            start: str | datetime | None=None,
            end: str | datetime | None=None) -> int:
        """
        Get the count of records.

        Parameters
        ----------
        where : str, optional
            Comma-separated list of conditions. Each must match
            <col><op><value> where <col> is a column name in the table, <op>
            is a comparison operator ("=", "<", ">", "<=", ">="), and <value>
            is present in the database. WARNING: This can be quite slow as
            query sanitation can take a very long time.
        start : str or datetime, optional
            Start date or time.
        end : str or datetime, optional
            End date or time.
        limit : int, optional
            Maximum number of distinct values to return.

        Returns
        -------
        int
            The count of rows.

        Raises
        ------
        ValueError
            If the label is not set.
        requests.HTTPError
            If the request fails.
        """
        if self._label is None:
            raise ValueError("Label is not set")
        # Build up the parameter string
        param_list = []
        if where:
            param_list.append(f"where={where}")
        if start:
            param_list.append(f"from={start}")
        if end:
            param_list.append(f"to={end}")
        params = "?" + "&".join(param_list) if param_list else ""
        response = self.auth.get(
            f"resources/{self._label}/count{params}")
        response.raise_for_status()
        # Return the response
        return response.json()[0][0]

    def list(
            self,
            *,
            where: str | None=None,
            start: str | datetime | None=None,
            end: str | datetime | None=None,
            limit: int | None=None) -> list[str]:
        """
        Get the records

        Parameters
        ----------
        where : str, optional
            Comma-separated list of conditions. Each must match
            <col><op><value> where <col> is a column name in the table, <op>
            is a comparison operator ("=", "<", ">", "<=", ">="), and <value>
            is present in the database. WARNING: This can be quite slow as
            query sanitation can take a very long time.
        start : str or datetime, optional
            Start date or time.
        end : str or datetime, optional
            End date or time.
        limit : int, optional
            Maximum number of distinct values to return.

        Returns
        -------
        list
            List of strings representing the records.

        Raises
        ------
        ValueError
            If the label is not set.
        requests.HTTPError
            If the request fails.
        """
        if self._label is None:
            raise ValueError("Label is not set")
        # Build up the parameter string
        param_list = []
        if where:
            param_list.append(f"where={where}")
        if start:
            param_list.append(f"from={start}")
        if end:
            param_list.append(f"to={end}")
        if limit:
            param_list.append(f"limit={int(limit)}")
        params = "?" + "&".join(param_list) if param_list else ""
        response = self.auth.get(
            f"resources/{self._label}/list{params}")
        response.raise_for_status()
        # Return the response
        return response.json()


class Ctxt(DbSubscriber):
    """
    Subscriber for ctxt database.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._label = "ctxt"

class Db41(DbSubscriber):
    """
    Subscriber for db41 database.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._label = "db41"


class Db44(DbSubscriber):
    """
    Subscriber for db44 database.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._label = "db44"
