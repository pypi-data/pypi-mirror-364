from cli.commands import analyze_cmd
import pytest
from unittest.mock import MagicMock, patch



@pytest.fixture
def mock_session():
    """Fixture to create a mock session."""
    return MagicMock()

@pytest.fixture
def mock_post():
    """Fixture to create a mock post."""
    post = MagicMock()
    post.post_id = 1
    post.content = "This is a test post."
    return post

def test_analyze_cmd_lang_detection(mock_session, mock_post):
    """Test analyze command with language detection."""
    with patch("cli.commands.analyze_cmd.detect_post_language_all") as mock_detect_lang:
        analyze_cmd.handle(["language-detect"])
        mock_detect_lang.assert_called_once_with(False)
        