#!/usr/bin/env python3
"""Unit tests for GithubOrgClient class and its utilities."""

import unittest
from unittest.mock import patch, PropertyMock, MagicMock
from parameterized import parameterized, parameterized_class

from client import GithubOrgClient
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
            "repos_url": (
                f"https://api.github.com/orgs/{org_name}/repos"
            )
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

        with patch(
            "client.GithubOrgClient._public_repos_url",
            new_callable=PropertyMock
        ) as mock_url:
            mock_url.return_value = (
                "https://fakeurl.com/orgs/testorg/repos"
            )
            client = GithubOrgClient("testorg")
            result = client.public_repos()

            self.assertEqual(result, [
                "repo1", "repo2", "repo3"
            ])
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


class MockResponse:
    """Mock response class to simulate requests.get response."""

    def __init__(self, json_data):
        self.json_data = json_data

    def json(self):
        """Return the mocked JSON response."""
        return self.json_data


@parameterized_class(
    ("org_payload", "repos_payload", "expected_repos", "apache2_repos"),
    TEST_PAYLOAD
)
class TestIntegrationGithubOrgClient(unittest.TestCase):
    """Integration test class for GithubOrgClient."""

    @classmethod
    def setUpClass(cls):
        """Set up class fixture before any tests are run."""
        cls.get_patcher = patch("requests.get")
        cls.mock_get = cls.get_patcher.start()

        def get_response(url, *args, **kwargs):
            expected_org_url = (
                f"https://api.github.com/orgs/"
                f"{cls.org_payload['login']}"
            )
            if url == expected_org_url:
                return MockResponse(cls.org_payload)
            elif url == cls.org_payload["repos_url"]:
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


if __name__ == "__main__":
    unittest.main()
