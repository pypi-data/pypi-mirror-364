import pytest

from magicfeedback_sdk import MagicFeedback


def test_list_report(client):
    """Tests listing report items."""

    filter = {
        "where": {
            "companyId": "MAGICFEEDBACK_DEV_SDK"
        }
    }

    response = client.reports.get(filter)
    assert len(response) > 0

@pytest.fixture
def client():
    """Provides a MagicFeedbackClient instance for testing."""

    client = MagicFeedback('sdk_tester@magicfeedback.io', 'caracter')
    return client