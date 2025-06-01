#!/usr/bin/env python3
"""Test client module.

This module contains unit tests for the GithubOrgClient class.
The tests use Python's unittest framework and the parameterized library
for test parameterization.
"""
import unittest
from parameterized import parameterized
from unittest.mock import patch, Mock
from client import GithubOrgClient


class TestGithubOrgClient(unittest.TestCase):
    """Test cases for the GithubOrgClient class.
    
    This class contains test cases for the GithubOrgClient methods.
    """

    @parameterized.expand([
        ('google', {'login': 'google'}),
        ('abc', {'login': 'abc'})
    ])
    @patch('client.get_json')
    def test_org(self, org_name, expected_payload, mock_get_json):
        """Test that GithubOrgClient.org returns the correct value.
        
        This test verifies that the org method correctly retrieves
        organization data from the GitHub API.

        Parameters
        ----------
        org_name: str
            The name of the organization to test
        expected_payload: dict
            The expected response payload
        mock_get_json: Mock
            The mocked get_json function
        """
        mock_get_json.return_value = expected_payload
        client = GithubOrgClient(org_name)
        self.assertEqual(client.org, expected_payload)
        mock_get_json.assert_called_once_with(
            f'https://api.github.com/orgs/{org_name}'
        )

    @patch.object(GithubOrgClient, 'org', new_callable=Mock)
    def test_public_repos_url(self, mock_org):
        """Test that _public_repos_url returns the correct value from org payload."""
        payload = {'repos_url': 'https://api.github.com/orgs/testorg/repos'}
        mock_org.return_value = payload
        client = GithubOrgClient('testorg')
        self.assertEqual(client._public_repos_url, payload['repos_url'])
        mock_org.assert_called_once()

    @parameterized.expand([
        ({'license': {'key': 'my_license'}}, 'my_license', True),
        ({'license': {'key': 'other'}}, 'my_license', False),
    ])
    def test_has_license(self, repo, license_key, expected):
        """Test that has_license returns True if repo has the specified license key."""
        client = GithubOrgClient('testorg')
        self.assertEqual(client.has_license(repo, license_key), expected) 