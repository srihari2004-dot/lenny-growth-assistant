from app.artifact import sanitize_html


def test_script_and_event_handlers_removed():
    html = '<div onclick="alert(1)">safe</div><script>alert(2)</script><img src="x" onerror="alert(3)">'
    clean = sanitize_html(html)
    assert "<script" not in clean.lower()
    assert "onclick" not in clean.lower()
    assert "onerror" not in clean.lower()
