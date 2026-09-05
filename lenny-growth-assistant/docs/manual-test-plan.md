# Manual UI test plan

1. Start Docker Compose and Ollama.
2. Open the web app.
3. Confirm “Ollama · local demo” is selected.
4. Ask a transcript-grounded question.
5. Verify the answer includes source titles.
6. Ask a follow-up that depends on the previous turn.
7. Click “+ New chat”; verify the new session has no previous messages.
8. Generate HTML; verify it appears in the Artifact Viewer without navigating away.
9. Generate Markdown; verify it renders as formatted content.
10. Attempt a malicious artifact during development, e.g. `<script>alert(1)</script>`; verify it is not executed/rendered.
11. Switch to Anthropic only when an API key is configured.
12. Stop Ollama and verify the UI receives a useful availability error rather than a fake answer.
13. Check `/health`.
14. Run automated tests.
