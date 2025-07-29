import os
from collections import OrderedDict
import json
from functools import partial, update_wrapper
from random import randint
from time import sleep
from typing import Callable, Optional

import requests
import pandas as pd
from dotenv import load_dotenv

load_dotenv()


class Tukan:
    """
    Handles authentication and requests to the TukanMX API.

    This class provides methods for retrieving tables, indicators, and metadata,
    as well as sending and receiving data via POST and GET operations. It also
    provides utility methods for checking the existence of tables and indicators,
    and for parsing hierarchical data structures.

    Attributes:
        token (str): API token for authentication.
        env (str): Base URL for the TukanMX API.
    """

    def __init__(self, token: Optional[str] = None):
        """
        Initialize a new Tukan API client instance.

        Args:
            token (Optional[str]): API token for authentication. If not provided, will use the API_TUKAN environment variable.

        Raises:
            ValueError: If no token is provided and API_TUKAN is not set in the environment.
        """
        env_token = os.getenv("API_TUKAN")
        if token is None and not env_token:
            raise ValueError(
                "Token not provided and not found in environment variables"
            )
        self.token = token or env_token
        self.env = "https://client.tukanmx.com/"

    def __execute_post_operation__(self, payload: dict, source: str):
        """
        Execute a POST request to the TukanMX API.

        Args:
            payload (dict): JSON payload to send in the POST request.
            source (str): API endpoint to post to.

        Returns:
            dict: Parsed JSON response from the API.

        Raises:
            Exception: If the operation is not allowed (HTTP 403).
        """
        target_url = self.env + source
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"token {self.token}",
        }
        request_partial = wrapped_partial(
            requests.request,
            method="POST",
            url=target_url,
            json=payload,
            headers=headers,
            timeout=20,
        )
        response = self.__persistent_request__(request_partial)
        if response.status_code < 300:
            message = response.json()
            return message
        elif response.status_code == 403:
            logger.info(f"{response.text}")
            raise Exception("Operation not allowed on admin. Contact administrator!")
        else:
            message = response.text
            return json.loads(message)

    def __execute_get_operation__(self, source: str, query: dict):
        """
        Execute a GET request to the TukanMX API.

        Args:
            source (str): API endpoint to query.
            query (dict): Query parameters for the GET request.

        Returns:
            dict: Parsed JSON response from the API.
        """
        target_url = self.env + source
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"token {self.token}",
        }
        response = requests.get(url=target_url, params=query, headers=headers)
        if response.status_code < 300:
            message = response.json()
            return message
        else:
            message = response.text
            return json.loads(message)

    def __persistent_request__(self, request_partial: Callable):
        """
        Attempt a request persistently, retrying on failure.

        Args:
            request_partial (Callable): A partial function representing the request to execute.

        Returns:
            requests.Response: The successful response object.
        """
        attempts = 0
        while attempts < 2:
            try:
                response = request_partial()
                if response.status_code < 300:
                    break
            except Exception as e:
                pass
            attempts += 1
            sleep(randint(3, 5))
        return response

    def all_tables(self, page: int = 1, page_size: int = 2_500) -> list[dict]:
        """
        Retrieve a list of all available data tables.

        Args:
            page (int): Page number for pagination.
            page_size (int): Number of tables per page.

        Returns:
            list[dict]: List of table metadata dictionaries.
        """
        payload = {
            "resource": "datatable",
            "operation": "view",
            "page": page,
            "page_size": page_size,
        }
        response = self.__execute_post_operation__(payload, "data/")
        return response["data"]

    def get_table(self, table_name: str) -> dict:
        """
        Retrieve metadata for a specific data table by name or ID.

        Args:
            table_name (str): The name or ID of the data table.

        Returns:
            dict: Metadata dictionary for the table.
        """
        payload = {
            "resource": "datatable",
            "operation": "view",
            "page": "1",
            "page_size": "1",
            "filter_by": {"id": table_name},
        }
        response = self.__execute_post_operation__(payload, "data/")
        return response["data"][0]

    def does_table_exist(self, table_name: str) -> bool:
        """
        Check if a data table exists by name or ID.

        Args:
            table_name (str): The name or ID of the data table.

        Returns:
            bool: True if the table exists, False otherwise.
        """
        try:
            self.get_table(table_name)
            return True
        except IndexError:
            return False

    def get_table_metadata(self, table_name: str, language="en") -> dict:
        """
        Retrieve metadata for a specific table, including columns and references.

        Args:
            table_name (str): The name or ID of the data table.
            language (str): Language for metadata (default is 'en').

        Returns:
            dict: Metadata dictionary for the table.
        """
        payload = {"data": {"id": table_name, "language": language}}
        response = self.__execute_post_operation__(payload, "data/metadata/")
        return response

    def all_indicators(self, page: int = 1, page_size: int = 2_500) -> list[dict]:
        """
        Retrieve all indicators available in the database.

        Args:
            page (int): Page number for pagination (default is 1).
            page_size (int): Number of indicators per page (default is 2,500).

        Returns:
            list[dict]: List of indicator metadata dictionaries.
        """
        payload = {
            "resource": "indicator",
            "operation": "view",
            "page": page,
            "page_size": page_size,
        }
        response = self.__execute_post_operation__(payload, "data/")
        return response["data"]

    def all_indicators_for_table(
        self, table_name: str, page: int = 1, page_size: int = 2_500
    ) -> list[dict]:
        """
        Retrieve all indicators for a specific table.

        Args:
            table_name (str): The name or ID of the data table.
            page (int): Page number for pagination.
            page_size (int): Number of indicators per page.

        Returns:
            list[dict]: List of indicator metadata dictionaries.
        """
        payload = {
            "resource": "indicator",
            "operation": "view",
            "page": page,
            "page_size": page_size,
            "filter_by": {"data_table": table_name},
        }
        response = self.__execute_post_operation__(payload, "data/")
        return response["data"]

    def does_indicator_ref_exist(self, indicator_ref: str) -> bool:
        """
        Check if an indicator reference exists.

        Args:
            indicator_ref (str): The reference ID of the indicator.

        Returns:
            bool: True if the indicator exists, False otherwise.
        """
        try:
            indicator_info = self.get_indicator_by_ref(indicator_ref, page_size=1)
        except IndexError:
            indicator_info = {}
        return bool(indicator_info)

    def get_indicator_by_ref(
        self, indicator_ref: str, page: int = 1, page_size: int = 2_500
    ) -> dict:
        """
        Retrieve indicator metadata by its reference ID.

        Args:
            indicator_ref (str): The reference ID of the indicator.
            page (int): Page number for pagination.
            page_size (int): Number of indicators per page.

        Returns:
            dict: Metadata dictionary for the indicator.
        """
        payload = {
            "resource": "indicator",
            "operation": "view",
            "page": page,
            "page_size": page_size,
            "filter_by": {"ref": indicator_ref},
        }
        response = self.__execute_post_operation__(payload, "data/")
        return response["data"][0]

    def ask_leah(self, query: str, language: str = "en") -> list[dict]:
        """
        Query the Leah endpoint for table suggestions based on a natural language query.

        Args:
            query (str): The question or prompt for Leah.
            language (str): Language for the query (default is 'en').

        Returns:
            dict: Parsed response with table metadata suggestions.
        """
        payload = {"query": query, "language": language}
        response = self.__execute_post_operation__(payload, "leah/")
        parsed_response = parse_leah(response)
        return parsed_response

    def get_tree_for_table(self, table_name: str) -> dict[str, pd.DataFrame]:
        """
        Retrieve hierarchical tree structures for a given table.

        Args:
            table_name (str): The name or ID of the data table.

        Returns:
            dict[str, dict[str, pd.DataFrame]]: Dictionary mapping table references to its reference values with hierarchical information.
        """
        payload = {
            "operation": "view",
            "resource": "tree",
            "filter_by": {"data_table": table_name},
        }
        response = self.__execute_post_operation__(payload, "data/")
        parsed_trees = parse_leah_trees(response["data"][0]["tree"])
        return parsed_trees

    def get_query_from_name_or_id(self, query_name_or_id: str) -> OrderedDict:
        """
        Retrieve a saved query by its name or ID and return its details in an OrderedDict.

        Args:
            query_name_or_id (str): Name or ID of the saved query.

        Returns:
            OrderedDict: Ordered dictionary containing keys 'id', 'name', 'author_name', 'created', and 'query'.
        """
        BODY = {
            "page_size": "10_000",
            "current": "1",
            "order_by": "-updated",
            "tags": "",
            "search": query_name_or_id,
            "api": "visualizations",
            "resource": "queries",
        }
        response = self.__execute_get_operation__("visualizations/queries", BODY)
        data = response["data"][0]
        parsed_data = parse_query_data(data)
        return parsed_data


def wrapped_partial(func, *args, **kwargs) -> Callable:
    """
    Returns a partial function with updated wrapper metadata.

    Args:
        func (Callable): The function to partially apply.
        *args: Positional arguments to pre-fill.
        **kwargs: Keyword arguments to pre-fill.

    Returns:
        Callable: The partially applied function with updated metadata.
    """
    partial_func = partial(func, *args, **kwargs)
    update_wrapper(partial_func, func)
    return partial_func


def parse_leah(response: dict) -> list[dict]:
    """
    Parses a Leah API response into a list of table metadata dictionaries.

    Args:
        response (dict): The Leah API response containing 'openai_completion' and 'optional_tables'.

    Returns:
        list[dict]: List of dictionaries with table 'id', 'description', and 'name'.
    """
    ans = []
    all_tables = response["openai_completion"] + response["optional_tables"]
    for element in all_tables:
        table_metadata = element["metadata"]["data_table"]
        ans.append(
            {
                "id": table_metadata["id"],
                "description": table_metadata["description"],
                "name": table_metadata["name"],
            }
        )
    return ans


def parse_leah_trees(response: dict) -> dict[str, pd.DataFrame]:
    """
    Parses Leah tree responses into a dictionary of DataFrames.

    Args:
        response (dict): Leah tree response mapping keys to tree JSON objects.

    Returns:
        dict[str, pd.DataFrame]: Dictionary mapping keys to DataFrames representing the tree structure.
    """
    ans = {}
    for key, tree in response.items():
        heritage_df = generate_heritage_col_df_from_json(tree)
        ans[key] = heritage_df
    return ans


def generate_heritage_col_df_from_json(tree_json: dict) -> pd.DataFrame:
    """
    Generates a pandas DataFrame from a heritage tree JSON structure.

    Args:
        tree_json (dict): JSON object representing the heritage tree.

    Returns:
        pd.DataFrame: DataFrame containing the heritage columns merged with display data.
    """
    [ref_name] = tree_json.keys()
    all_ref_lineages, display_map = lineages_of_refs_and_display_map_from_json(
        tree_json
    )
    heritage_df = heritage_df_from_ref_lineages(all_ref_lineages, ref_name)
    display_df = display_df_from_map(display_map, ref_name)
    return pd.merge(heritage_df, display_df, on=ref_name)


def lineages_of_refs_and_display_map_from_json(tree_json: dict) -> tuple[list, list]:
    """
    Extracts all reference lineages and display map from a tree JSON structure.

    Args:
        tree_json (dict): JSON object representing the tree structure.

    Returns:
        tuple[list, list]:
            - List of all reference lineages (each as a list of reference IDs).
            - Display map as a list of tuples (ref_id, data dict).
    """
    [(root_ref, root_ref_info)] = tree_json.items()
    root_ref_node = [root_ref]
    all_nodes = [root_ref_node]
    display_map = [(root_ref, root_ref_info["data"])]
    add_nodes_recursively(
        root_ref_node, root_ref_info["children"], all_nodes, display_map
    )
    return all_nodes, display_map


def add_nodes_recursively(
    ancestry: list[str], sons: list, all_nodes: list, display_map: list
):
    """
    Recursively traverses and collects nodes and display data from a tree structure.

    Args:
        ancestry (list[str]): The lineage of ancestor references leading to the current node.
        sons (list): List of child nodes (as dicts).
        all_nodes (list): Accumulator for all reference lineages.
        display_map (list): Accumulator for display map tuples (ref_id, data dict).
    """
    for son in sons:
        [(son_ref_id, son_ref_info)] = son.items()
        sons_heritage = ancestry + [son_ref_id]
        display_map.append((son_ref_id, son_ref_info["data"]))
        all_nodes.append(sons_heritage)
        grand_children = son_ref_info.get("children", [])
        add_nodes_recursively(sons_heritage, grand_children, all_nodes, display_map)


def heritage_df_from_ref_lineages(
    all_ref_lineages: list, ref_name: str
) -> pd.DataFrame:
    """
    Generates a DataFrame from a list of reference lineages.

    Args:
        all_ref_lineages (list): List of reference lineages (each as a list of reference IDs).
        ref_name (str): Name of the reference column.

    Returns:
        pd.DataFrame: DataFrame with columns for each ancestor and the reference itself.
    """
    max_num_ancestors = len(max(all_ref_lineages, key=len)) - 1
    col_names = ref_col_names(ref_name, max_num_ancestors)
    col_names_to_refs = []
    for lineage in all_ref_lineages:
        lineage_with_all_levels = right_fill_ancestor_ref(lineage, max_num_ancestors)
        col_names_to_refs.append(dict(zip(col_names, lineage_with_all_levels)))
    return pd.DataFrame(col_names_to_refs)


def ref_col_names(ref_name: str, max_num_ancestors: int) -> list:
    """
    Generates column names for ancestor references and the main reference.

    Args:
        ref_name (str): Name of the reference column.
        max_num_ancestors (int): Maximum number of ancestor levels.

    Returns:
        list: List of column names for each ancestor and the reference.
    """
    ancestor_cols = [f"{ref_name}_p{n}" for n in range(max_num_ancestors)]
    return ancestor_cols + [ref_name]


def right_fill_ancestor_ref(lineage: list[str], max_num_ancestors: int) -> list[str]:
    """
    Fills the ancestor portion of a lineage to a fixed length with None values.

    Args:
        lineage (list[str]): List of reference IDs representing a lineage.
        max_num_ancestors (int): The total number of ancestor columns required.

    Returns:
        list[str]: The lineage, right-filled with None for missing ancestors.
    """
    ancestors = lineage[:-1]
    ancestors_fill = ancestors + ([None] * (max_num_ancestors - len(ancestors)))
    return ancestors_fill + [lineage[-1]]


def display_df_from_map(display_map: list, ref_name: str) -> pd.DataFrame:
    """
    Generates a pandas DataFrame from a display map.

    Args:
        display_map (list): List of tuples (ref_id, data dict) for each node in the tree.
        ref_name (str): Name of the reference column.

    Returns:
        pd.DataFrame: DataFrame containing reference IDs and their associated display data.
    """
    data = [{ref_name: ref, **data} for ref, data in display_map]
    return pd.DataFrame(data)


def parse_query_data(data: dict) -> OrderedDict:
    """
    Parse a query data dictionary and return an OrderedDict with selected keys.

    Args:
        data (dict): Dictionary containing query data as returned by the API.

    Returns:
        OrderedDict: Ordered dictionary with keys 'id', 'name', 'author_name', 'created', and 'query'.
    """
    data["query"] = parse_query(data["query"])
    ordered_keys = ["id", "name", "author_name", "created", "updated", "query"]
    ordered_pairs = [(key, data[key]) for key in ordered_keys]
    ordered_data = OrderedDict(ordered_pairs)
    return ordered_data


def parse_query(query: dict) -> dict:
    parsed_query = {
        "table_name": query["select"][0]["table"],
        "where": query["where"],
        "group_by": query["iterate"][0]["group_by"],
        "aggregate": query["iterate"][0]["aggregate"],
        "language": query["language"],
    }
    return parsed_query
