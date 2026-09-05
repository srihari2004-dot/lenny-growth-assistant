# UI/UX Design

## Principles

1. **Grounding is visible.** Sources are shown directly beneath answers.
2. **Model choice is explicit.** The evaluator can see whether the local or cloud provider is active.
3. **Chat is the primary workflow.** No separate research dashboard is required for the MVP.
4. **Artifacts are first-class.** Generated output appears beside the conversation.
5. **Failure is understandable.** Errors are shown in plain language instead of silently falling back to an invented answer.
6. **Responsive by default.** Desktop uses a split chat/artifact layout; smaller screens stack the panels.

## Information architecture

- Header: product name, model/provider toggle, new-chat action.
- Left/main: chat, status, messages, source citations, composer.
- Right: Artifact Viewer and output format actions.

## Interaction states

- Empty chat
- Normal answer
- Retrieval/generation in progress
- Error
- Artifact empty state
- Artifact rendered
- Mobile stacked layout

## Accessibility

- Semantic headings
- Visible labels
- Keyboard-friendly textarea
- Enter to send, Shift+Enter for newline
- Buttons remain text-labelled
- High contrast
- iframe has a descriptive title
- No reliance on color alone for system state

## Artifact safety UX

The viewer intentionally does not expose a “run HTML” toggle. Generated HTML is displayed as sanitized content in a sandboxed frame. This keeps the default path safe while still satisfying the in-app rendering requirement.
