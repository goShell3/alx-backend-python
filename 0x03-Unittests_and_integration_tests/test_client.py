#!/usr/bin/env python3
"""Test client module.

This module contains unit tests for the GithubOrgClient class.
The tests use Python's unittest framework and the parameterized library
for test parameterization.
"""
import unittest
from parameterized import parameterized, parameterized_class
from unittest.mock import patch, Mock
from client import GithubOrgClient
from fixtures import org_payload, repos_payload, expected_repos, apache2_repos


class TestGithubOrgClient(unittest.TestCase):
    """Test cases for the GithubOrgClient class."""

    @parameterized.expand([
        ('google', {'login': 'google'}),
        ('abc', {'login': 'abc'})
    ])
    @patch('client.get_json')
    def test_org(self, org_name, expected_payload, mock_get_json):
        """Test that GithubOrgClient.org returns the correct value."""
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

    @patch('client.get_json')
    def test_public_repos(self, mock_get_json):
        """Test that public_repos returns the correct list of repos."""
        mock_get_json.return_value = [
            {'name': 'repo1'},
            {'name': 'repo2'}
        ]
        with patch.object(GithubOrgClient, '_public_repos_url',
                          return_value='http://some_url'):
            client = GithubOrgClient('testorg')
            self.assertEqual(client.public_repos, ['repo1', 'repo2'])
            mock_get_json.assert_called_once_with('http://some_url')

    @parameterized.expand([
        ({'license': {'key': 'my_license'}}, 'my_license', True),
        ({'license': {'key': 'other'}}, 'my_license', False),
    ])
    def test_has_license(self, repo, license_key, expected):
        """Test that has_license returns True if repo has the specified license key."""
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
        """Set up the test class by mocking requests.get to return fixtures."""
        cls.get_patcher = patch('requests.get')
        cls.mock_get = cls.get_patcher.start()
        cls.mock_get.return_value.json.side_effect = [
            cls.org_payload,
            cls.repos_payload
        ]

    @classmethod
    def tearDownClass(cls):
        """Tear down the test class by stopping the patcher."""
        cls.get_patcher.stop()

    def test_public_repos(self):
        """Test that public_repos returns the expected list of repos."""
        client = GithubOrgClient('testorg')
        self.assertEqual(client.public_repos, self.expected_repos)
        self.mock_get.assert_called()
