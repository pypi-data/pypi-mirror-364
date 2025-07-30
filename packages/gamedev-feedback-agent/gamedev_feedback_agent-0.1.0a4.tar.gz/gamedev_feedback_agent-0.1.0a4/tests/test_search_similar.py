import pytest
import numpy as np
from unittest.mock import patch, MagicMock
from cli.commands.search_cmd import handle_search_similar, search_similar
from cli.commands import search_cmd


@pytest.fixture
def mock_session():
    with patch("cli.commands.search_cmd.get_session") as mock_get_session:
        mock_session = MagicMock()
        mock_get_session.return_value = mock_session
        yield mock_session

@pytest.fixture
def mock_close_session():
    with patch("cli.commands.search_cmd.close_session") as mock_close:
        yield mock_close

@pytest.fixture
def mock_embedding_model():
    with patch("cli.commands.search_cmd.IntelligenceConfig.get_embedding_model_name") as mock_model:
        mock_model.return_value = "test-model"
        yield mock_model

@pytest.fixture
def mock_get_text_embedding():
    with patch("cli.commands.search_cmd.get_text_embedding") as mock_func:
        mock_func.return_value = ("test-model", [0.1, 0.2, 0.3])
        yield mock_func

class DummyEmbedding:
    def __init__(self, post_id, embedding, model="test-model"):
        self.post_id = post_id
        self.embedding = embedding
        self.model = model

def test_search_similar_text_query(
    capsys, mock_session, mock_close_session, mock_embedding_model, mock_get_text_embedding
):
    dummy_rows = [
        DummyEmbedding(2, [0.1, 0.2, 0.3]),
        DummyEmbedding(3, [0.2, 0.1, 0.4]),
    ]
    mock_session.query.return_value.filter.return_value.all.return_value = dummy_rows
    mock_session.query.return_value.join.return_value.filter.return_value.all.return_value = dummy_rows

    handle_search_similar(["some query", "--limit", "2"])
    captured = capsys.readouterr()
    assert "Found" in captured.out
    assert "[2] Similarity:" in captured.out or "[3] Similarity:" in captured.out

def test_search_similar_post_id(
    capsys, mock_session, mock_close_session, mock_embedding_model
):
    dummy_embedding = DummyEmbedding(1, [0.1, 0.2, 0.3])
    dummy_rows = [
        DummyEmbedding(2, [0.1, 0.2, 0.3]),
        DummyEmbedding(3, [0.2, 0.1, 0.4]),
    ]
    mock_session.query.return_value.filter.return_value.first.return_value = dummy_embedding
    mock_session.query.return_value.filter.return_value.all.return_value = dummy_rows
    mock_session.query.return_value.join.return_value.filter.return_value.all.return_value = dummy_rows

    handle_search_similar(["--post_id", "1", "--limit", "2"])
    captured = capsys.readouterr()
    assert "Found" in captured.out
    assert "[2] Similarity:" in captured.out or "[3] Similarity:" in captured.out

def test_search_similar_missing_args(capsys):
    handle_search_similar([])
    captured = capsys.readouterr()
    assert "You must provide either a text query or a post ID" in captured.out

def test_search_similar_both_args(capsys):
    handle_search_similar(["some query", "--post_id", "1"])
    captured = capsys.readouterr()
    assert "You cannot provide both a text query and a post ID" in captured.out
    
    
    
def test_search_similar_parse_error(capsys):
    # Test parse_args SystemExit (invalid arguments)
    handle_search_similar(["--limit", "not_a_number"])
    captured = capsys.readouterr()
    assert "[Search Similar Parsing Error]" in captured.out

    # Test generic Exception in parse_args
    with patch("argparse.ArgumentParser.parse_args", side_effect=Exception("Mocked error")):
        handle_search_similar(["some query"])
        captured = capsys.readouterr()
        assert "Mocked error" in captured.out or "[Search Similar Parsing Error]" in captured.out
        

def test_search_similar_no_model(capsys, mock_session, mock_close_session):
    # Test when no embedding model is configured
    with patch("cli.commands.search_cmd.IntelligenceConfig.get_embedding_model_name", return_value=None):
        handle_search_similar(["some query"])
        captured = capsys.readouterr()
        assert "[Search Similar Error] No embedding model specified." in captured.out

    # Ensure session is closed
    mock_close_session.assert_called_once()
    
    
def test_handle_search_similar_error(capsys, mock_session, mock_close_session):
    with patch("cli.commands.search_cmd.search_similar", side_effect=Exception("Database error")):
        search_cmd.handle_search_similar(["some query"])
        captured = capsys.readouterr()
        assert "[Search Similar Error] Database error" in captured.out
        
        

@patch("cli.commands.search_cmd.IntelligenceConfig.get_embedding_model_name")
@patch("cli.commands.search_cmd.get_text_embedding")
def test_search_similar_text_query_success(mock_get_text_embedding, mock_get_embedding_model, mock_session):
    # Arrange
    mock_get_embedding_model.return_value = "mock-model"
    # Simulate text embedding
    query_vec = np.ones(5).tolist()
    mock_get_text_embedding.return_value = (None, query_vec)

    # Mock DB rows
    emb1 = MagicMock(embedding=np.ones(5))
    emb2 = MagicMock(embedding=2*np.ones(5))
    row_list = [emb1, emb2]
    mock_session.query().join().filter().all.return_value = row_list

    # Act
    results = search_similar(mock_session, text="foo", limit=2)
    
    # Assert
    assert len(results) == 2
    for emb, score in results:
        assert isinstance(score, np.float32) or isinstance(score, float)

@patch("cli.commands.search_cmd.IntelligenceConfig.get_embedding_model_name")
def test_search_similar_post_id_success(mock_get_embedding_model, mock_session):
    mock_get_embedding_model.return_value = "mock-model"
    embedding_vec = np.ones(5).tolist()
    emb_row = MagicMock(embedding=embedding_vec)
    mock_session.query().filter().first.return_value = emb_row
    emb1 = MagicMock(embedding=2*np.ones(5))
    emb2 = MagicMock(embedding=3*np.ones(5))
    mock_session.query().join().filter().all.return_value = [emb1, emb2]
    # Act
    results = search_similar(mock_session, post_id=42, limit=2)
    # Assert
    assert len(results) == 2
    for emb, score in results:
        assert isinstance(score, np.float32) or isinstance(score, float)

@patch("cli.commands.search_cmd.IntelligenceConfig.get_embedding_model_name")
@patch("cli.commands.search_cmd.get_text_embedding")
def test_search_similar_text_query_no_rows(mock_get_text_embedding, mock_get_embedding_model, mock_session, capsys):
    mock_get_embedding_model.return_value = "mock-model"
    mock_get_text_embedding.return_value = (None, np.ones(5).tolist())
    mock_session.query().join().filter().all.return_value = []
    search_similar(mock_session, text="foo")
    out = capsys.readouterr().out
    assert "[Search Similar Error]" in out

@patch("cli.commands.search_cmd.IntelligenceConfig.get_embedding_model_name")
def test_search_similar_post_id_no_embedding(mock_get_embedding_model, mock_session, capsys):
    mock_get_embedding_model.return_value = "mock-model"
    mock_session.query().filter().first.return_value = None
    search_similar(mock_session, post_id=42)
    out = capsys.readouterr().out
    assert "No embedding found" in out

@patch("cli.commands.search_cmd.IntelligenceConfig.get_embedding_model_name")
def test_search_similar_post_id_empty_embedding(mock_get_embedding_model, mock_session, capsys):
    mock_get_embedding_model.return_value = "mock-model"
    emb_row = MagicMock(embedding=[])
    mock_session.query().filter().first.return_value = emb_row
    search_similar(mock_session, post_id=42)
    out = capsys.readouterr().out
    assert "has no embedding vector" in out

@patch("cli.commands.search_cmd.IntelligenceConfig.get_embedding_model_name")
@patch("cli.commands.search_cmd.get_text_embedding")
def test_search_similar_min_similarity_filter(mock_get_text_embedding, mock_get_embedding_model, mock_session):
    mock_get_embedding_model.return_value = "mock-model"
    mock_get_text_embedding.return_value = (None, np.ones(3).tolist())
    emb1 = MagicMock(embedding=np.array([1, 0, 0]))
    emb2 = MagicMock(embedding=np.array([0, 1, 0]))
    emb3 = MagicMock(embedding=np.array([1, 1, 1]))
    mock_session.query().join().filter().all.return_value = [emb1, emb2, emb3]
    # Only emb3 will be close enough if min_similarity > 0.7
    results = search_similar(mock_session, text="foo", min_similarity=0.7)
    # emb3 (vector [1,1,1]) should have higher similarity with [1,1,1] than others
    assert all(score >= 0.7 for _, score in results)



import numpy as np
from unittest.mock import patch, MagicMock

@patch("cli.commands.search_cmd.IntelligenceConfig.get_embedding_model_name")
@patch("cli.commands.search_cmd.get_text_embedding")
def test_search_similar_platform_filter(mock_get_text_embedding, mock_get_embedding_model):
    from cli.commands.search_cmd import search_similar

    session = MagicMock()

    mock_get_embedding_model.return_value = "mock-model"
    mock_get_text_embedding.return_value = (None, np.ones(3).tolist())

    # 1. Mock platform_ids as [(1,)] (will be unpacked to [1])
    session.query().filter().all.return_value = [(1,)]

    # 2. Mock embedding rows via the correct chain
    emb1 = MagicMock(embedding=np.ones(3))
    emb2 = MagicMock(embedding=np.array([2, 2, 2]))
    # Chain: .query().join().filter().filter().all()
    session.query().join().filter().filter().all.return_value = [emb1, emb2]

    # Call the function
    results = search_similar(session, text="foo", platform=["reddit"])
    print("RESULTS:", results)

    # Now you should have a list, not None
    assert results is not None
    assert len(results) == 2
    assert all(isinstance(t[1], float) or isinstance(t[1], np.float32) for t in results)
    
    
def test_search_similar_no_platform_found():
    from cli.commands.search_cmd import search_similar
    session = MagicMock()

    # Mock no platform IDs found
    session.query().filter().all.return_value = []

    # Call the function with a platform that doesn't exist
    results = search_similar(session, text="foo", platform=["nonexistent_platform"])

    # Expect results to be empty
    assert results == None
    session.query().filter().all.assert_called_once()  # Ensure the query was made
    
def test_search_similar_no_model_found(capsys):
    from cli.commands.search_cmd import search_similar
    session = MagicMock()

    with patch("cli.commands.search_cmd.IntelligenceConfig.get_embedding_model_name", return_value=None):
        results = search_similar(session, text="foo")

    assert results is None
    captured = capsys.readouterr()
    assert "[Search Similar Error] No embedding model specified." in captured.out
    
    with patch("cli.commands.search_cmd.IntelligenceConfig.get_embedding_model_name", return_value=None):
        results = search_similar(session, post_id=1)
    
    assert results is None
    captured = capsys.readouterr()
    assert "[Search Similar Error] No embedding model specified." in captured.out
    
    
def test_search_similar_post_id_and_platform(capsys):
    from cli.commands.search_cmd import search_similar
    session = MagicMock()

    # Mock embedding model
    with patch("cli.commands.search_cmd.IntelligenceConfig.get_embedding_model_name", return_value="mock-model"):
        # Mock post_id embedding
        emb_row = MagicMock(embedding=np.ones(3).tolist())
        session.query().filter().first.return_value = emb_row

        # Mock platform IDs
        session.query().filter().all.return_value = [(1,)]

        # Mock embedding rows
        emb1 = MagicMock(embedding=np.array([1, 0, 0]))
        emb2 = MagicMock(embedding=np.array([0, 1, 0]))
        session.query().join().filter().filter().all.return_value = [emb1, emb2]

        results = search_similar(session, post_id=42, platform=["reddit"])

    assert results is not None
    assert len(results) == 2
    for emb, score in results:
        assert isinstance(score, float) or isinstance(score, np.float32)
        
        
        
def test_search_similar_post_id_no_posts_found(capsys):
    from cli.commands.search_cmd import search_similar
    session = MagicMock()
    
    mock_embedding = MagicMock(embedding=np.ones(3).tolist())

    # Mock embedding model
    with patch("cli.commands.search_cmd.IntelligenceConfig.get_embedding_model_name", return_value="mock-model"):
        # Mock no posts found for the given post_id
        session.query().filter().first.return_value = mock_embedding
        session.query().join().filter().all.return_value = []

        results = search_similar(session, post_id=42)

    assert results is None
    captured = capsys.readouterr()
    assert "[Search Similar Error] No available posts found for post ID 42." in captured.out
    
    
def test_search_similar_text_no_text():
    from cli.commands.search_cmd import search_similar
    session = MagicMock()

    # Mock embedding model
    with patch("cli.commands.search_cmd.IntelligenceConfig.get_embedding_model_name", return_value="mock-model"):
        results = search_similar(session, text=None)

    assert results is None
    # Ensure no query was made since text is None
    session.query().join().filter().all.assert_not_called()
    

def test_search_similar_text_no_embedding_for_query(capsys):
    from cli.commands.search_cmd import search_similar
    session = MagicMock()

    # Mock embedding model
    with patch("cli.commands.search_cmd.IntelligenceConfig.get_embedding_model_name", return_value="mock-model"), \
            patch("cli.commands.search_cmd.get_text_embedding", return_value=(None, None)):
        results = search_similar(session, text="text failed to generate embedding")

    assert results is None
    # Ensure no query was made since text is None
    session.query().join().filter().all.assert_not_called()
    