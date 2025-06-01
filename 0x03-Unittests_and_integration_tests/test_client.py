#!/usr/bin/env python3
"""Test client module.

This module contains unit tests for the GithubOrgClient class.
"""

import unittest
from unittest.mock import patch, Mock
from parameterized import parameterized, parameterized_class
from client import GithubOrgClient

# Mock fixtures directly to avoid import error
org_payload = {'login': 'testorg', 'repos_url': 'http://api.github.com/orgs/testorg/repos'}
repos_payload = [
    {'name': 'repo1', 'license': {'key': 'apache-2.0'}},
    {'name': 'repo2', 'license': {'key': 'other'}},
]
expected_repos = ['repo1', 'repo2']
apache2_repos = ['repo1']


class TestGithubOrgClient(unittest.TestCase):
    """Unit tests for GithubOrgClient."""

    @parameterized.expand([
        ('google', {'login': 'google'}),
        ('abc', {'login': 'abc'})
    ])
    @patch('client.get_json')
    def test_org(self, org_name, expected_payload, mock_get_json):
        """Test GithubOrgClient.org returns correct payload."""
        mock_get_json.return_value = expected_payload
        client = GithubOrgClient(org_name)
        self.assertEqual(client.org, expected_payload)
        mock_get_json.assert_called_once_with(
            f'https://api.github.com/orgs/{org_name}'
        )

    @patch.object(GithubOrgClient, 'org', new_callable=Mock)
    def test_public_repos_url(self, mock_org):
        """Test that _public_repos_url returns the repos URL from org payload."""
        mock_org.return_value = {'repos_url': 'https://api.github.com/orgs/testorg/repos'}
        client = GithubOrgClient('testorg')
        self.assertEqual(
            client._public_repos_url,
            'https://api.github.com/orgs/testorg/repos'
        )
        mock_org.assert_called_once()

    @patch('client.get_json')
    def test_public_repos(self, mock_get_json):
        """Test that public_repos returns the expected list of repository names."""
        mock_get_json.return_value = repos_payload
        with patch.object(GithubOrgClient, '_public_repos_url',
                          return_value='http://api.github.com/orgs/testorg/repos'):
            client = GithubOrgClient('testorg')
            self.assertEqual(client.public_repos, expected_repos)
            mock_get_json.assert_called_once_with(
                'http://api.github.com/orgs/testorg/repos'
            )

    @parameterized.expand([
        ({'license': {'key': 'apache-2.0'}}, 'apache-2.0', True),
        ({'license': {'key': 'mit'}}, 'apache-2.0', False),
    ])
    def test_has_license(self, repo, license_key, expected):
        """Test has_license correctly identifies license key."""
        client = GithubOrgClient('testorg')
        self.assertEqual(client.has_license(repo, license_key), expected)


@parameterized_class([{
    'org_payload': org_payload,
    'repos_payload': repos_payload,
    'expected_repos': expected_repos,
    'apache2_repos': apache2_repos
}])
class TestIntegrationGithubOrgClient(unittest.TestCase):
    """Integration tests for GithubOrgClient."""

    @classmethod
    def setUpClass(cls):
        """Patch requests.get to return mocked org and repo payloads."""
        cls.get_patcher = patch('requests.get')
        cls.mock_get = cls.get_patcher.start()
        cls.mock_get.return_value.json.side_effect = [
            cls.org_payload,
            cls.repos_payload
        ]

    @classmethod
    def tearDownClass(cls):
        """Stop patcher."""
        cls.get_patcher.stop()

    def test_public_repos(self):
        """Test public_repos returns expected repo list."""
        client = GithubOrgClient('testorg')
        self.assertEqual(client.public_repos, self.expected_repos)
        self.mock_get.assert_called()
