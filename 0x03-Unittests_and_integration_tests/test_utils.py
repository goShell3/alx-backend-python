#!/usr/bin/env python3
"""Test utils module.

This module contains unit tests for the utility functions in utils.py.
The tests use Python's unittest framework and the parameterized library
for test parameterization.
"""
import unittest
from parameterized import parameterized
from unittest.mock import patch, Mock
from utils import access_nested_map, get_json, memoize


class TestAccessNestedMap(unittest.TestCase):
    """Test cases for the access_nested_map function.
    
    This class contains test cases for both successful access and error
    cases when accessing nested maps.
    """

    @parameterized.expand([
        ({"a": 1}, ("a",), 1),
        ({"a": {"b": 2}}, ("a",), {"b": 2}),
        ({"a": {"b": 2}}, ("a", "b"), 2)
    ])
    def test_access_nested_map(self, nested_map, path, expected):
        """Test successful access to nested map values.
        
        This test verifies that the access_nested_map function correctly
        retrieves values from nested dictionaries using the provided path.

        Parameters
        ----------
        nested_map: dict
            The nested dictionary to access
        path: tuple
            The path of keys to traverse
        expected: Any
            The expected value at the specified path
        """
        self.assertEqual(access_nested_map(nested_map, path), expected)

    @parameterized.expand([
        ({}, ("a",), "'a'"),
        ({"a": 1}, ("a", "b"), "'b'")
    ])
    def test_access_nested_map_exception(self, nested_map, path, expected_message):
        """Test error cases when accessing nested map.
        
        This test verifies that the access_nested_map function correctly
        raises KeyError with the expected message when attempting to access
        non-existent paths.

        Parameters
        ----------
        nested_map: dict
            The nested dictionary to access
        path: tuple
            The invalid path of keys
        expected_message: str
            The expected error message
        """
        with self.assertRaises(KeyError) as context:
            access_nested_map(nested_map, path)
        self.assertEqual(str(context.exception), expected_message)


class TestGetJson(unittest.TestCase):
    """Test cases for the get_json function.
    
    This class contains test cases for making HTTP requests and
    handling JSON responses using mocked requests.
    """

    @parameterized.expand([
        ("http://example.com", {"payload": True}),
        ("http://holberton.io", {"payload": False})
    ])
    def test_get_json(self, test_url, test_payload):
        """Test successful JSON retrieval from URLs.
        
        This test verifies that the get_json function correctly
        retrieves and parses JSON from remote URLs using mocked
        HTTP requests.

        Parameters
        ----------
        test_url: str
            The URL to fetch JSON from
        test_payload: dict
            The expected JSON response
        """
        with patch('requests.get') as mock_get:
            mock_get.return_value.json.return_value = test_payload
            result = get_json(test_url)
            mock_get.assert_called_once_with(test_url)
            self.assertEqual(result, test_payload)


class TestMemoize(unittest.TestCase):
    """Test cases for the memoize decorator.
    
    This class contains test cases for the memoization functionality
    of the memoize decorator.
    """

    def test_memoize(self):
        """Test memoization of method results.
        
        This test verifies that the memoize decorator correctly
        caches method results and returns the cached value on
        subsequent calls.
        """
        class TestClass:
            def a_method(self):
                return 42

            @memoize
            def a_property(self):
                return self.a_method()

        with patch.object(TestClass, 'a_method') as mock:
            test_class = TestClass()
            test_class.a_property
            test_class.a_property
            mock.assert_called_once()
