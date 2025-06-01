#!/usr/bin/env python3
"""Unit tests for GithubOrgClient class and its utilities
"""

import unittest
from unittest.mock import patch, PropertyMock, MagicMock
from parameterized import parameterized, parameterized_class

from client import GithubOrgClient

import fixtures  # import your fixtures.py file
from client import GithubOrgClient  # your client module

"""Integration test for GithubOrgClient.public_repos method."""
from fixtures import TEST_PAYLOAD


class TestGithubOrgClient(unittest.TestCase):
    """Test cases for GithubOrgClient"""

    @parameterized.expand([
        ("google",),
        ("abc",)
    ])
    @patch("client.get_json")
    def test_org(self, org_name, mock_get_json):
        """Test that GithubOrgClient.org returns correct data"""
        expected_payload = {
            "name": org_name,
            "repos_url": f"https://api.github.com/orgs/{org_name}/repos"
        }
        mock_get_json.return_value = expected_payload

        client = GithubOrgClient(org_name)
        result = client.org

        self.assertEqual(result, expected_payload)
        mock_get_json.assert_called_once_with(
            f"https://api.github.com/orgs/{org_name}"
        )

    def test_public_repos_url(self):
        """Test that _public_repos_url returns expected repos URL"""
        test_url = "https://api.github.com/orgs/testorg/repos"
        with patch(
            "client.GithubOrgClient.org",
            new_callable=PropertyMock
        ) as mock_org:
            mock_org.return_value = {"repos_url": test_url}
            client = GithubOrgClient("testorg")
            self.assertEqual(client._public_repos_url, test_url)

    @patch("client.get_json")
    def test_public_repos(self, mock_get_json):
        """Test that public_repos returns correct repo names"""
        fake_repos_payload = [
            {"name": "repo1"},
            {"name": "repo2"},
            {"name": "repo3"}
        ]
        mock_get_json.return_value = fake_repos_payload

        with patch("client.GithubOrgClient._public_repos_url",
                   new_callable=PropertyMock) as mock_url:
            mock_url.return_value = "https://fakeurl.com/orgs/testorg/repos"
            client = GithubOrgClient("testorg")
            result = client.public_repos()

            self.assertEqual(result, ["repo1", "repo2", "repo3"])
            mock_url.assert_called_once()
            mock_get_json.assert_called_once_with(
                "https://fakeurl.com/orgs/testorg/repos"
            )

    @parameterized.expand([
            ({"license": {"key": "my_license"}}, "my_license", True),
            ({"license": {"key": "other_license"}}, "my_license", False),
        ])
    def test_has_license(self, repo, license_key, expected):
        """Test has_license returns expected boolean for different inputs"""
        result = GithubOrgClient.has_license(repo, license_key)
        self.assertEqual(result, expected)

if __name__ == "__main__":
    unittest.main()


# @parameterized_class([
#     {
#         "org_payload": fixtures.org_payload,
#         "repos_payload": fixtures.repos_payload,
#         "expected_repos": fixtures.expected_repos,
#         "apache2_repos": fixtures.apache2_repos,
#     }
# ])
# class TestIntegrationGithubOrgClient(unittest.TestCase):
#     @classmethod
#     def setUpClass(cls):
#         # Patch 'requests.get' globally for all tests in this class
#         cls.get_patcher = patch('requests.get')
#         cls.mock_get = cls.get_patcher.start()

#         # Define side_effect function for requests.get().json()
#         def side_effect(url, *args, **kwargs):
#             mock_resp = MagicMock()
#             if url == cls.org_payload['repos_url']:
#                 # Return repos_payload when repos_url is requested
#                 mock_resp.json.return_value = cls.repos_payload
#             elif url == f"https://api.github.com/orgs/{cls.org_payload['login']}":
#                 # Return org_payload when org url is requested
#                 mock_resp.json.return_value = cls.org_payload
#             else:
#                 # Default empty list or dict to avoid errors
#                 mock_resp.json.return_value = {}
#             return mock_resp

#         cls.mock_get.side_effect = side_effect

#     @classmethod
#     def tearDownClass(cls):
#         cls.get_patcher.stop()

#     def test_public_repos(self):
#         # Instantiate client with org name
#         client = GithubOrgClient(self.org_payload['login'])

#         # Call public_repos method, which internally calls requests.get mocked above
#         repos = client.public_repos()

#         # Assert the returned repos names match expected repos fixture
#         self.assertEqual(repos, self.expected_repos)

#     def test_public_repos_with_license(self):
#         client = GithubOrgClient(self.org_payload['login'])

#         # Test filtering by license key "apache-2.0"
#         repos = client.public_repos(license_key="apache-2.0")

#         # Should return repos filtered by apache2 license key fixture
#         self.assertEqual(repos, self.apache2_repos)

#!/usr/bin/env python3

class MockResponse:
    """Mock response class to simulate requests.get response."""
    def __init__(self, json_data):
        self.json_data = json_data
    
    def json(self):
        return self.json_data

@parameterized_class(("org_payload", "repos_payload", "expected_repos", "apache2_repos"), TEST_PAYLOAD)
class TestIntegrationGithubOrgClient(unittest.TestCase):
    """Integration test class for GithubOrgClient."""

    @classmethod
    def setUpClass(cls):
        """Set up class fixture before any tests are run."""
        cls.get_patcher = patch('requests.get')
        cls.mock_get = cls.get_patcher.start()

        def get_response(url, *args, **kwargs):
            if url == f"https://api.github.com/orgs/{cls.org_payload['login']}":
                return MockResponse(cls.org_payload)
            elif url == cls.org_payload['repos_url']:
                return MockResponse(cls.repos_payload)
            return MockResponse(None)
        
        cls.mock_get.side_effect = get_response

    @classmethod
    def tearDownClass(cls):
        """Stop the patcher after all tests are run."""
        cls.get_patcher.stop()

    def test_public_repos(self):
        """Test public_repos without license filtering."""
        client = GithubOrgClient(self.org_payload['login'])
        repos = client.public_repos()
        self.assertEqual(repos, self.expected_repos)

    def test_has_license(self):
        """Test public_repos with Apache 2.0 license filtering."""
        client = GithubOrgClient(self.org_payload['login'])
        repos = client.public_repos(license="apache-2.0")
        self.assertEqual(repos, self.apache2_repos)