from cli.commands.search_cmd import handle_search_hybrid, calculate_keyword_similarity
from unittest.mock import patch, MagicMock
import pytest
import re


@patch("cli.commands.search_cmd.get_session")
@patch("cli.commands.search_cmd.search_similar")
def test_handle_search_hybrid(mock_search_similar, mock_get_session, capsys):
    # Mock session and Post
    mock_session = MagicMock()
    mock_get_session.return_value = mock_session

    # Mock Post model
    class MockPost:
        def __init__(self, post_id, content, translated_content=None):
            self.post_id = post_id
            self.content = content
            self.translated_content = translated_content

    # Prepare semantic results: (MockPost, semantic_score)
    mock_post1 = MockPost(1, "Game is crashing frequently", None)
    mock_post2 = MockPost(2, "Game crashes on startup", "game crashes on startup")
    mock_search_similar.return_value = [(mock_post1, 0.9), (mock_post2, 0.8)]

    # Prepare keyword query results
    mock_session.query.return_value.filter.return_value.all.return_value = [mock_post1, mock_post2]

    # Patch calculate_keyword_similarity to return fixed values
    with patch("cli.commands.search_cmd.calculate_keyword_similarity") as mock_kw_sim:
        mock_kw_sim.side_effect = [0.6, 0.7]

        # Run the function
        handle_search_hybrid(["crashing", "--semantic_weight", "0.5", "--limit", "2"])

        # Capture output
        captured = capsys.readouterr()
        assert "Found 2 posts matching keyword 'crashing':" in captured.out
        assert "[1] Hybrid Score:" in captured.out
        assert "[2] Hybrid Score:" in captured.out
        
        
def test_search_hybrid_invalid_args(capsys):
    # Test with invalid arguments
    handle_search_hybrid(["--invalid_arg"])

    # Capture output
    captured = capsys.readouterr()
    assert "[Search Hybrid Parsing Error] Invalid arguments provided." in captured.out  
    
    
    
def test_search_hybrid_no_keyword_scores(capsys):
    # This test ensures that if a post_id from semantic_results is not present in keyword_results,
    # the code falls back to using only the semantic_score.

    # Mock session and Post
    with patch("cli.commands.search_cmd.get_session") as mock_get_session, \
        patch("cli.commands.search_cmd.search_similar") as mock_search_similar, \
        patch("cli.commands.search_cmd.calculate_keyword_similarity") as mock_kw_sim:

        mock_session = MagicMock()
        mock_get_session.return_value = mock_session

        # Mock Post model
        class MockPost:
            def __init__(self, post_id, content, translated_content=None):
                self.post_id = post_id
                self.content = content
                self.translated_content = translated_content

        # Only one post returned by semantic search
        mock_post1 = MockPost(1, "Game is crashing frequently", None)
        mock_post2 = MockPost(2, "Game crashes on startup", "game crashes on startup")
        mock_search_similar.return_value = [(mock_post1, 0.9), (mock_post2, 0.8)]

        # Only return mock_post1 in keyword query (so post2 will have no keyword score)
        mock_session.query.return_value.filter.return_value.all.return_value = [mock_post1]

        # Only one keyword similarity score for post1
        mock_kw_sim.side_effect = [0.6]

        handle_search_hybrid(["crashing", "--semantic_weight", "0.5", "--limit", "2"])

        captured = capsys.readouterr()
        # Both posts should be printed, but post2 should use only semantic score
        assert "Found 2 posts matching keyword 'crashing':" in captured.out
        assert "[1] Hybrid Score:" in captured.out
        assert "[2] Hybrid Score: 0.8000" in captured.out  # post2 uses only semantic score

def test_search_hybrid_no_combined_results(capsys):
    # Test when both semantic_results and keyword_results are empty
    with patch("cli.commands.search_cmd.get_session") as mock_get_session, \
        patch("cli.commands.search_cmd.search_similar") as mock_search_similar:
        mock_session = MagicMock()
        mock_get_session.return_value = mock_session
        mock_search_similar.return_value = []

        handle_search_hybrid(["crashing"])
        captured = capsys.readouterr()
        assert "[Search Hybrid Error] No semantic results found for keyword" in captured.out

def test_search_hybrid_limit(capsys):
    # Test that limit argument works as expected
    with patch("cli.commands.search_cmd.get_session") as mock_get_session, \
        patch("cli.commands.search_cmd.search_similar") as mock_search_similar, \
        patch("cli.commands.search_cmd.calculate_keyword_similarity") as mock_kw_sim:

        mock_session = MagicMock()
        mock_get_session.return_value = mock_session

        class MockPost:
            def __init__(self, post_id, content, translated_content=None):
                self.post_id = post_id
                self.content = content
                self.translated_content = translated_content

        mock_post1 = MockPost(1, "Game is crashing frequently", None)
        mock_post2 = MockPost(2, "Game crashes on startup", "game crashes on startup")
        mock_post3 = MockPost(3, "Game lags", None)
        mock_search_similar.return_value = [(mock_post1, 0.9), (mock_post2, 0.8), (mock_post3, 0.7)]

        mock_session.query.return_value.filter.return_value.all.return_value = [mock_post1, mock_post2, mock_post3]
        mock_kw_sim.side_effect = [0.6, 0.7, 0.5]

        handle_search_hybrid(["crashing", "--semantic_weight", "0.5", "--limit", "2"])
        captured = capsys.readouterr()
        assert "Found 2 posts matching keyword 'crashing':" in captured.out
        assert captured.out.count("Hybrid Score:") == 2

def test_search_hybrid_keyword_similarity_exception(capsys):
    # Test if calculate_keyword_similarity raises an exception
    with patch("cli.commands.search_cmd.get_session") as mock_get_session, \
        patch("cli.commands.search_cmd.search_similar") as mock_search_similar, \
        patch("cli.commands.search_cmd.calculate_keyword_similarity", side_effect=Exception("kw error")):

        mock_session = MagicMock()
        mock_get_session.return_value = mock_session

        class MockPost:
            def __init__(self, post_id, content, translated_content=None):
                self.post_id = post_id
                self.content = content
                self.translated_content = translated_content

        mock_post1 = MockPost(1, "Game is crashing frequently", None)
        mock_search_similar.return_value = [(mock_post1, 0.9)]
        mock_session.query.return_value.filter.return_value.all.return_value = [mock_post1]

        handle_search_hybrid(["crashing"])
        captured = capsys.readouterr()
        assert "[Search Hybrid Parsing Error]" in captured.out


def test_calculate_keyword_similarity():
    # Exact match
    assert calculate_keyword_similarity("Game is crashing frequently", "crashing") > 0.0
    # Case insensitivity
    assert calculate_keyword_similarity("Game is crashing frequently", "CRASHING") > 0.0
    # Multiple keyword tokens
    assert calculate_keyword_similarity("Game is crashing frequently", "game crashing") > 0.0
    # No overlap
    assert calculate_keyword_similarity("Game is crashing frequently", "unrelated") == 0.0
    # Empty keyword
    assert calculate_keyword_similarity("Game is crashing frequently", "") == 0.0
    # Empty content
    assert calculate_keyword_similarity("", "crashing") == 0.0
    # Both empty
    assert calculate_keyword_similarity("", "") == 0.0
    # Partial overlap
    assert calculate_keyword_similarity("Game is crashing frequently", "game bug") > 0.0
    # Keyword longer than content
    assert calculate_keyword_similarity("crashing", "crashing frequently") > 0.0
    
    assert calculate_keyword_similarity(None, None) == 0.0
    assert calculate_keyword_similarity("", None) == 0.0
    assert calculate_keyword_similarity(None, "") == 0.0