#!/usr/bin/env python3
"""Test client module.

This module contains unit tests for the GithubOrgClient class.
The tests use Python's unittest framework and the parameterized library
for test parameterization.
"""

import unittest
from unittest.mock import patch, Mock
from parameterized import parameterized, parameterized_class
from client import GithubOrgClient
from fixture import TEST_PAYLOAD

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

    @patch('client.get_json')
    def test_public_repos(self, mock_get_json):
        """Test that public_repos returns the expected list of repos.
        
        This test verifies that:
        1. The public_repos property returns the expected list of repository names
        2. The _public_repos_url property is called once
        3. The get_json function is called once with the correct URL
        """
        test_payload = [
            {'name': 'repo1', 'license': {'key': 'apache-2.0'}},
            {'name': 'repo2', 'license': {'key': 'mit'}},
            {'name': 'repo3', 'license': {'key': 'apache-2.0'}}
        ]
        mock_get_json.return_value = test_payload
        
        with patch.object(
            GithubOrgClient,
            '_public_repos_url',
            new_callable=Mock,
            return_value='https://api.github.com/orgs/testorg/repos'
        ) as mock_url:
            client = GithubOrgClient('testorg')
            result = client.public_repos
            
            # Test that the result is the expected list of repo names
            self.assertEqual(result, ['repo1', 'repo2', 'repo3'])
            
            # Test that _public_repos_url was called once
            mock_url.assert_called_once()
            
            # Test that get_json was called once with the correct URL
            mock_get_json.assert_called_once_with(
                'https://api.github.com/orgs/testorg/repos'
            )


@parameterized_class([
    {
        'org_payload': TEST_PAYLOAD[0][0],
        'repos_payload': TEST_PAYLOAD[0][1],
        'expected_repos': [repo['name'] for repo in TEST_PAYLOAD[0][1]],
        'apache2_repos': [repo['name'] for repo in TEST_PAYLOAD[0][1] 
                         if repo.get('license', {}).get('key') == 'apache-2.0']
    }
])
class TestIntegrationGithubOrgClient(unittest.TestCase):
    """Integration tests for GithubOrgClient.
    This class tests the GithubOrgClient.public_repos method using fixtures.
    """

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
