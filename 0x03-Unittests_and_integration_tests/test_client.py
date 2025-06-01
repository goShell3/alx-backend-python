#!/usr/bin/env python3
"""Test client module.

Unit tests for the GithubOrgClient class using unittest and parameterized.
"""

import unittest
from unittest.mock import patch, Mock
from parameterized import parameterized, parameterized_class
from client import GithubOrgClient

# Mock fixtures inline
org_payload = {
    'login': 'testorg',
    'repos_url': 'https://api.github.com/orgs/testorg/repos'
}
repos_payload = [
    {'name': 'repo1', 'license': {'key': 'apache-2.0'}},
    {'name': 'repo2', 'license': {'key': 'other'}}
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
        """Test _public_repos_url gets repos_url from org."""
        mock_org.return_value = {
            'repos_url': 'https://api.github.com/orgs/testorg/repos'
        }
        client = GithubOrgClient('testorg')
        self.assertEqual(
            client._public_repos_url,
            'https://api.github.com/orgs/testorg/repos'
        )
        mock_org.assert_called_once()

    @patch('client.get_json')
    def test_public_repos(self, mock_get_json):
        """Test public_repos returns list of repo names."""
        mock_get_json.return_value = repos_payload
        with patch.object(
            GithubOrgClient,
            '_public_repos_url',
            return_value='https://api.github.com/orgs/testorg/repos'
        ):
            client = GithubOrgClient('testorg')
            result = client.public_repos
            self.assertEqual(result, expected_repos)
            mock_get_json.assert_called_once_with(
                'https://api.github.com/orgs/testorg/repos'
            )

    @parameterized.expand([
        ({'license': {'key': 'apache-2.0'}}, 'apache-2.0', True),
        ({'license': {'key': 'mit'}}, 'apache-2.0', False),
    ])
    def test_has_license(self, repo, license_key, expected):
        """Test has_license returns True when license matches."""
        client = GithubOrgClient('testorg')
        self.assertEqual(client.has_license(repo, license_key), expected)


@parameterized_class([
    {
        'org_payload': org_payload,
        'repos_payload': repos_payload,
        'expected_repos': expected_repos,
        'apache2_repos': apache2_repos
    }
])
class TestIntegrationGithubOrgClient(unittest.TestCase):
    """Integration tests for GithubOrgClient."""

    @classmethod
    def setUpClass(cls):
        """Patch requests.get to mock responses for org and repos."""
        cls.get_patcher = patch('requests.get')
        cls.mock_get = cls.get_patcher.start()
        cls.mock_get.return_value.json.side_effect = [
            cls.org_payload,
            cls.repos_payload
        ]

    @classmethod
    def tearDownClass(cls):
        """Stop the patcher."""
        cls.get_patcher.stop()

    def test_public_repos(self):
        """Test public_repos returns expected repos."""
        client = GithubOrgClient('testorg')
        self.assertEqual(client.public_repos, self.expected_repos)
        self.mock_get.assert_called()
