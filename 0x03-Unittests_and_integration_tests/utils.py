#!/usr/bin/env python3
"""Generic utilities for github org client.

This module provides utility functions for accessing nested maps,
making HTTP requests, and memoizing method results.
"""
import requests
from functools import wraps
from typing import (
    Mapping,
    Sequence,
    Any,
    Dict,
    Callable,
    TypeVar,
    cast
)

__all__ = [
    "access_nested_map",
    "get_json",
    "memoize",
]

T = TypeVar('T')

def access_nested_map(nested_map: Mapping, path: Sequence) -> Any:
    """Access nested map with key path.
    
    This function traverses a nested dictionary using a sequence of keys
    and returns the value at the specified path. If any key in the path
    doesn't exist, it raises a KeyError.

    Parameters
    ----------
    nested_map: Mapping
        A nested map to access
    path: Sequence
        A sequence of keys representing a path to the value

    Returns
    -------
    Any
        The value at the specified path

    Raises
    ------
    KeyError
        If any key in the path doesn't exist

    Example
    -------
    >>> nested_map = {"a": {"b": {"c": 1}}}
    >>> access_nested_map(nested_map, ["a", "b", "c"])
    1
    """
    for key in path:
        if not isinstance(nested_map, Mapping):
            raise KeyError(key)
        nested_map = nested_map[key]

    return nested_map


def get_json(url: str) -> Dict:
    """Get JSON from remote URL.
    
    This function makes an HTTP GET request to the specified URL
    and returns the JSON response as a dictionary.

    Parameters
    ----------
    url: str
        The URL to fetch JSON from

    Returns
    -------
    Dict
        The JSON response as a dictionary

    Raises
    ------
    requests.RequestException
        If the request fails
    ValueError
        If the response is not valid JSON
    """
    response = requests.get(url)
    return response.json()


def memoize(fn: Callable[..., T]) -> Callable[..., T]:
    """Decorator to memoize a method.
    
    This decorator caches the result of a method call and returns
    the cached value on subsequent calls with the same arguments.

    Parameters
    ----------
    fn: Callable[..., T]
        The method to memoize

    Returns
    -------
    Callable[..., T]
        The memoized method

    Example
    -------
    class MyClass:
        @memoize
        def a_method(self):
            print("a_method called")
            return 42
    >>> my_object = MyClass()
    >>> my_object.a_method
    a_method called
    42
    >>> my_object.a_method
    42
    """
    attr_name = "_{}".format(fn.__name__)

    @wraps(fn)
    def memoized(self: Any) -> T:
        """Memoized wrapper function.
        
        This function checks if the result is already cached and returns it.
        If not, it calls the original method and caches the result.

        Returns
        -------
        T
            The memoized result
        """
        if not hasattr(self, attr_name):
            setattr(self, attr_name, fn(self))
        return cast(T, getattr(self, attr_name))

    return property(memoized)