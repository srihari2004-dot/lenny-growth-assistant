from app.agent import build_context


def test_context_has_source_metadata():
    result = build_context([{
        "title": "Test Episode",
        "guest": "Test Guest",
        "source_path": "podcasts/test.md",
        "relevance": 0.9,
        "text": "A useful product insight.",
        "chunk_id": 1,
    }])
    assert "Test Episode" in result
    assert "A useful product insight." in result
    assert "Test Guest" in result
