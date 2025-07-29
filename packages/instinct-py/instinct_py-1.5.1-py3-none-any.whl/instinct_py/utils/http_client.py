"""
HTTP client utility for making API requests to the Instinct device.

This module provides a client for making consistent HTTP requests to the device's API.
"""

from typing import Any, Dict, Optional

import requests


class HttpClient:
    """HTTP client for making API requests to the Instinct device.

    A wrapper around requests to provide consistent handling of
    requests to the Instinct API.
    """

    def get(
        self,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        timeout: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Make a GET request to the Instinct API.

        Parameters
        ----------
        url : str
            The URL to make the request to
        params : Optional[Dict[str, Any]], optional
            Query parameters to include in the request, by default None
        timeout : Optional[float], optional
            Timeout in seconds for the request, by default None

        Returns
        -------
        Dict[str, Any]
            The JSON response from the API

        Raises
        ------
        Exception
            If the request fails
        """
        response = requests.get(url, params=params, timeout=timeout)
        response.raise_for_status()
        return response.json()

    def post(
        self,
        url: str,
        data: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        timeout: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Make a POST request to the Instinct API.

        Parameters
        ----------
        url : str
            The URL to make the request to
        data : Optional[Dict[str, Any]], optional
            Form data to include in the request, by default None
        json : Optional[Dict[str, Any]], optional
            JSON data to include in the request, by default None
        timeout : Optional[float], optional
            Timeout in seconds for the request, by default None

        Returns
        -------
        Dict[str, Any]
            The JSON response from the API

        Raises
        ------
        Exception
            If the request fails
        """
        response = requests.post(url, data=data, json=json, timeout=timeout)
        response.raise_for_status()
        return response.json()

    def patch(
        self,
        url: str,
        data: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        timeout: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Make a PATCH request to the Instinct API.

        Parameters
        ----------
        url : str
            The URL to make the request to
        data : Optional[Dict[str, Any]], optional
            Form data to include in the request, by default None
        json : Optional[Dict[str, Any]], optional
            JSON data to include in the request, by default None
        timeout : Optional[float], optional
            Timeout in seconds for the request, by default None

        Returns
        -------
        Dict[str, Any]
            The JSON response from the API

        Raises
        ------
        Exception
            If the request fails
        """
        response = requests.patch(url, data=data, json=json, timeout=timeout)
        response.raise_for_status()
        return response.json()

    def put(
        self,
        url: str,
        data: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        timeout: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Make a PUT request to the Instinct API.

        Parameters
        ----------
        url : str
            The URL to make the request to
        data : Optional[Dict[str, Any]], optional
            Form data to include in the request, by default None
        json : Optional[Dict[str, Any]], optional
            JSON data to include in the request, by default None
        timeout : Optional[float], optional
            Timeout in seconds for the request, by default None

        Returns
        -------
        Dict[str, Any]
            The JSON response from the API

        Raises
        ------
        Exception
            If the request fails
        """
        response = requests.put(url, data=data, json=json, timeout=timeout)
        response.raise_for_status()
        return response.json()

    def delete(self, url: str, timeout: Optional[float] = None) -> Dict[str, Any]:
        """Make a DELETE request to the Instinct API.

        Parameters
        ----------
        url : str
            The URL to make the request to
        timeout : Optional[float], optional
            Timeout in seconds for the request, by default None

        Returns
        -------
        Dict[str, Any]
            The JSON response from the API

        Raises
        ------
        Exception
            If the request fails
        """
        response = requests.delete(url, timeout=timeout)
        response.raise_for_status()
        return response.json()
