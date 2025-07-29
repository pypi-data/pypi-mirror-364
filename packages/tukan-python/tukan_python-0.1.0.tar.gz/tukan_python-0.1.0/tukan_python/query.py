from collections import defaultdict
from typing import Literal, Optional

import pandas as pd

from tukan_python.tukan import Tukan


class Query:
    """
    Helper class for building and executing queries against the TukanMX API.

    This class allows flexible construction of query payloads, including filters,
    groupings, and aggregations. It supports saving, executing, and reconstructing
    queries from names, IDs, or payloads.

    Attributes:
        Tukan (Tukan): Instance of the Tukan API client.
        table_name (str): Name of the data table to query.
        where (list[dict]): List of filter conditions.
        group_by (list[dict]): List of group-by conditions.
        aggregate (list[dict]): List of aggregate operations.
        language (str): Language for the query results.
    """

    def __init__(
        self,
        table_name: str,
        token: Optional[str] = None,
        where: Optional[list[dict]] = None,
        group_by: Optional[list[dict]] = None,
        aggregate: Optional[list[dict]] = None,
        language: str = "en",
    ):
        """
        Initialize a new Query instance.

        Args:
            table_name (str): Name of the data table to query.
            token (Optional[str]): API token for authentication.
            where (Optional[list[dict]]): List of filter conditions.
            group_by (Optional[list[dict]]): List of group-by conditions.
            aggregate (Optional[list[dict]]): List of aggregate operations.
            language (str): Language for the query results.
        """
        self.table_name = table_name
        self.Tukan = Tukan(token)
        self.__set_metadata__()
        self.where = where if where is not None else []
        self.group_by = group_by if group_by is not None else []
        self.aggregate = aggregate if aggregate is not None else []
        self.language = language

    def __set_metadata__(self) -> dict:
        """
        Get the metadata for the table.

        Returns:
            dict: Table metadata.
        """
        meta = self.Tukan.get_table_metadata(self.table_name)
        dt_to_refs = defaultdict(set)
        for ref in meta["data_table_references"]:
            dt_to_refs[ref["type"]].add(ref["id"])

        self.dtypes_to_refs = dt_to_refs
        self.all_indicators = meta["indicators"]

    def get_table_name(self) -> str:
        """
        Get the name of the table for the query.

        Returns:
            str: The name of the table.
        """
        return self.table_name

    def set_where(self, where: list[dict]) -> None:
        """
        Set the filter conditions for the query.

        Args:
            where (list[dict]): List of filter conditions.
        """
        self.where = where
        return self

    def get_where(self) -> list[dict]:
        """
        Get the filter conditions for the query.

        Returns:
            list[dict]: List of filter conditions.
        """
        return self.where

    def add_filter(self, filter: dict) -> None:
        """
        Add a filter condition to the query.

        Args:
            filter (dict): Filter condition to add.
        """
        self.where.append(filter)
        return self

    def add_date_filter(
        self, reference: str, date_from: str, date_to: Optional[str] = None
    ) -> None:
        """
        Add a date filter to the query. Dates should be in ISO format (YYYY-MM-DD).

        Args:
            reference (str): Reference field for the date filter.
            date_from (str): Start date for the filter.
            date_to (Optional[str]): End date for the filter (optional).
        """
        dt_filter = {"reference": reference, "from": date_from}
        if date_to is not None:
            dt_filter["to"] = date_to
        self.where.append(dt_filter)
        return self

    def add_numeric_filter(
        self,
        reference: str,
        lte: Optional[float] = None,
        eq: Optional[float] = None,
        gte: Optional[float] = None,
    ) -> None:
        """
        Add a numeric filter to the query.

        Args:
            reference (str): Reference field for the numeric filter.
            lte (Optional[float]): Less-than-or-equal value.
            eq (Optional[float]): Equal value.
            gte (Optional[float]): Greater-than-or-equal value.
        """
        self.__validate_numeric_filter__(lte, eq, gte)
        nm_filter = {"reference": reference, "lte": lte, "eq": eq, "gte": gte}
        nm_filter = {k: v for k, v in nm_filter.items() if v is not None}
        self.where.append(nm_filter)
        return self

    def __validate_numeric_filter__(
        self,
        lte: Optional[float] = None,
        eq: Optional[float] = None,
        gte: Optional[float] = None,
    ) -> None:
        """
        Validate the numeric filter arguments.

        Args:
            lte (Optional[float]): Less-than-or-equal value.
            eq (Optional[float]): Equal value.
            gte (Optional[float]): Greater-than-or-equal value.

        Raises:
            ValueError: If the filter arguments are invalid.
        """
        if eq is None and lte is None and gte is None:
            raise ValueError("At least one of eq, lte, or gte must be specified")
        elif eq is not None and (lte is not None or gte is not None):
            raise ValueError("The eq parameter cannot be used with lte or gte")

    def add_standard_filter(self, reference: str, value: list[str]) -> None:
        """
        Add a standard (categorical) filter to the query.

        Args:
            reference (str): Reference field for the filter.
            value (list[str]): List of values to filter by.
        """
        self.where.append({"reference": reference, "value": value})
        return self

    def set_group_by(self, group_by: list[dict]) -> None:
        """
        Set the group-by conditions for the query.

        Args:
            group_by (list[dict]): List of group-by conditions.
        """
        self.group_by = group_by
        return self

    def get_group_by(self) -> list[dict]:
        """
        Get the group-by conditions for the query.

        Returns:
            list[dict]: List of group-by conditions.
        """
        return self.group_by

    def add_to_group_by(self, group_by: dict) -> None:
        """
        Add a group-by condition to the query.

        Args:
            group_by (dict): Group-by condition to add.
        """
        self.group_by.append(group_by)
        return self

    def add_non_date_reference_to_group_by(self, reference: str) -> None:
        """
        Add a non-date reference to the group-by conditions.

        Args:
            reference (str): Reference field to group by.
        """
        self.group_by.append({"reference": reference})
        return self

    def add_date_reference_to_group_by(
        self,
        reference: str,
        level: Literal["yearly", "quarterly", "monthly", "as_is"] = "as_is",
    ) -> None:
        """
        Add a date reference to the group-by conditions with a specified granularity.

        Args:
            reference (str): Reference field to group by.
            level (Literal): Granularity level ('yearly', 'quarterly', 'monthly', 'as_is').
        """
        self.__validate_date_filter__(level)
        dt_filter = {"reference": reference, "level": level}
        self.group_by.append(dt_filter)
        return self

    def __validate_date_filter__(
        self, level: Literal["yearly", "quarterly", "monthly", "as_is"]
    ) -> None:
        """
        Validate the date filter granularity level.

        Args:
            level (Literal): Granularity level to validate.

        Raises:
            ValueError: If the level is invalid.
        """
        if level not in {"yearly", "quarterly", "monthly", "as_is"}:
            raise ValueError(
                "Invalid level. Must be 'yearly', 'quarterly', 'monthly', or 'as_is'"
            )

    def set_aggregate(self, aggregate: list[dict]) -> None:
        """
        Set the aggregate operations for the query.

        Args:
            aggregate (list[dict]): List of aggregate operations.
        """
        self.aggregate = aggregate
        return self

    def get_aggregate(self) -> list[dict]:
        """
        Get the aggregate operations for the query.

        Returns:
            list[dict]: List of aggregate operations.
        """
        return self.aggregate

    def add_aggregate(self, indicator: str, operations: list[str]) -> None:
        """
        Add an aggregate operation for a specific indicator.

        Args:
            indicator (str): Indicator to aggregate.
            operations (list[str]): List of operations (e.g., ['sum', 'avg', 'identity']).
        """
        self.__validate_aggregate__(operations)
        self.aggregate.append({"indicator": indicator, "operations": operations})
        return self

    def __validate_aggregate__(self, operations: list[str]) -> None:
        """
        Validate the aggregate operations.

        Args:
            operations (list[str]): List of aggregate operations.

        Raises:
            ValueError: If operations are empty or invalid.
        """
        if len(operations) == 0:
            raise ValueError("At least one operation must be specified")
        elif {*operations} - {"sum", "avg", "identity"}:
            raise ValueError("Invalid operation. Must be 'sum', 'avg', or 'identity'")

    def set_language(self, language: str) -> None:
        """
        Set the language for the query results.

        Args:
            language (str): The language code (e.g., 'en', 'es').
        """
        self.language = language
        return self

    def get_language(self) -> str:
        """
        Get the language for the query results.

        Returns:
            str: The language code.
        """
        return self.language

    def __get_select__(self) -> list[dict]:
        """
        Get the select clause for the query.

        Returns:
            list[dict]: List containing the table and indicators to select.
        """
        indicators = [x["indicator"] for x in self.aggregate]
        return [{"table": self.table_name, "indicators": indicators}]

    def __get_iterate__(self) -> list[dict]:
        """
        Get the iterate clause for the query.

        Returns:
            list[dict]: List containing group-by and aggregate operations.
        """
        return [{"group_by": self.group_by, "aggregate": self.aggregate}]

    def __str__(self) -> str:
        """
        Return the string representation of the query payload.

        Returns:
            str: Stringified query payload.
        """
        payload_info = {
            "table_name": self.table_name,
            "language": self.language,
            "where": self.where,
            "group_by": self.group_by,
            "aggregate": self.aggregate,
        }
        return str(payload_info)

    def __request_payload__(self) -> dict:
        """
        Construct the full query payload as a dictionary.

        Returns:
            dict: The query payload.
        """
        return {
            "select": self.__get_select__(),
            "where": self.where,
            "iterate": self.__get_iterate__(),
            "language": self.language,
        }

    def set_aggregate_for_all_indicators(self, operations: list[str]) -> None:
        """
        Set the aggregate to identity for all indicators in the current table.
        """
        all_indicators = self.__all_indicators_refs_for_table__()
        self.aggregate = [
            {"indicator": indicator, "operations": operations}
            for indicator in all_indicators
        ]
        return self

    def set_groupby_for_all_columns(self) -> None:
        """
        Set group-by for all references (columns) in the current table.
        """
        references = self.__all_non_date_references__()
        non_date_group_by = [{"reference": reference} for reference in references]
        date_group_by = [
            {"reference": reference, "level": "as_is"}
            for reference in self.dtypes_to_refs["DT"]
        ]
        group_by = [*non_date_group_by, *date_group_by]
        self.set_group_by(group_by)
        return self

    def __all_non_date_references__(self) -> list[str]:
        """
        Get all reference columns for the current table.

        Returns:
            list[str]: List of reference column names.
        """
        non_dt_ref_groups = [
            values for key, values in self.dtypes_to_refs.items() if key != "DT"
        ]
        return [*set.union(*non_dt_ref_groups)]

    def __all_indicators_refs_for_table__(self) -> list[str]:
        """
        Get all indicator references for the current table.

        Returns:
            list[str]: List of indicator reference names.
        """
        all_indicators = [indicator["ref"] for indicator in self.all_indicators]
        return all_indicators

    def save_query(self, name: str) -> str:
        """
        Save the current query to the server with the given name.

        Args:
            name (str): Name to save the query as.

        Returns:
            str: Server response.
        """
        BODY = {
            "data_table": self.table_name,
            "language": self.language,
            "name": name,
            "query": self.__request_payload__(),
        }

        response = self.Tukan.__execute_post_operation__(BODY, "visualizations/query/")

        return response

    def execute_query(
        self, mode: Literal["vertical", "horizontal"] = "vertical"
    ) -> dict:
        """
        Execute the query on the server and return the results.

        Args:
            mode (Literal): Output mode, 'vertical' or 'horizontal'.

        Returns:
            dict: Dictionary containing indicators and the result DataFrame.
        """
        payload = self.__request_payload__()
        payload["mode"] = mode
        response = self.Tukan.__execute_post_operation__(payload, "data/new_retrieve/")
        df = pd.DataFrame(response["data"])
        return {"indicators": response["indicators"], "df": df}


def create_identity_query_for_table_with_date_filters(
    table_name: str,
    language: Literal["en", "es"],
    from_date: str,
    to_date: str,
) -> dict:
    """
    Create an identity query for a table with date filters applied.

    Args:
        table_name (str): Name of the table.
        language (Literal): Language for the query.
        from_date (str): Start date for the filter.
        to_date (str): End date for the filter.
    """
    query = create_identity_query_for_table(table_name, language)
    for date_ref in query.dtypes_to_refs["DT"]:
        query.add_date_filter(date_ref, from_date, to_date)
    return query


def create_identity_query_for_table(
    table_name: str, language: Literal["en", "es"]
) -> dict:
    """
    Create an identity query for a table (all indicators, all references, group by all columns).

    Args:
        table_name (str): Name of the table.
        language (Literal): Language for the query.
    """
    query = Query(table_name)
    query.set_aggregate_for_all_indicators(["identity"])
    query.set_language(language)
    query.set_groupby_for_all_columns()
    return query


def create_query_from_query_id_or_name(query_id_or_name: str) -> Query:
    """
    Create Query instance from a query ID or name on the server.

    Args:
        query_id_or_name (str): The query's ID or name.
    """
    query = Tukan().get_query_from_name_or_id(query_id_or_name)["query"]
    query = create_query_from_payload(query)
    return query


def create_query_from_payload(payload: dict) -> Query:
    """
    Create Query instance from a query payload dictionary.

    Args:
        payload (dict): The query payload.
    """
    query = Query(payload["table_name"])
    query.set_where(payload["where"])
    query.set_group_by(payload["group_by"])
    query.set_aggregate(payload["aggregate"])
    query.set_language(payload["language"])
    return query
