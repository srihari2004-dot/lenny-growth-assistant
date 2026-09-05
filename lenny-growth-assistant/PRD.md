# PRD — The Lenny Growth Assistant

## 1. Discovery brief

### User and problem

Primary users are product managers, growth practitioners, founders, and internal product/growth teams who want to turn a large archive of Lenny's interviews into practical answers.

Their job is not “chat with an LLM.” Their job is to quickly answer questions such as:
- What approaches do experienced product leaders recommend for activation?
- How do different guests think about product-market fit?
- Can I turn the research into a usable memo or essay?

The assistant removes transcript-search overhead while preserving trust through source attribution.

### Success metric

Primary MVP metric: **grounded answer rate** — at least 90% of evaluation questions should either contain a relevant source citation or explicitly state that the transcript corpus does not support the answer.

Operational metric: median response time under 15 seconds on the local demo hardware for a small retrieval set, excluding first-model-load time.

### Assumptions

- The public starter dataset is sufficient for evaluation.
- Users prefer source-grounded answers over broad general knowledge.
- A local Ollama model is required for offline/reproducible evaluation.
- PostgreSQL is the system of record.
- A single anonymous user is sufficient for the take-home MVP.
- Production SSO and tenant isolation are future work.

### Scope choices

Included:
- RAG
- independent sessions
- persisted conversation
- model/provider toggle
- source citations
- Ship 30 for 30 writing skill
- HTML/Markdown artifacts
- sandboxed artifact viewer
- tests and operational docs

Excluded:
- auth/SSO
- multi-tenant permissions
- streaming
- external web search
- background queues
- full production observability stack

The exclusions reduce complexity while preserving the assignment's core evaluation areas.

## 2. User flows

### Grounded Q&A

Create session → ask question → embed question → retrieve transcript chunks → generate answer → persist answer + sources → display citations.

### Follow-up

User asks question → assistant stores turn → next question retrieves new evidence while preserving prior conversational context.

### Artifact

User asks a question → assistant answers → user selects artifact format → writing/artifact skill transforms the grounded conversation → sanitize HTML → render in viewer.

## 3. Acceptance criteria

- [ ] FastAPI API is documented and typed.
- [ ] Each session has independent context.
- [ ] Conversations persist in PostgreSQL.
- [ ] Transcript chunks are embedded and searchable.
- [ ] Every grounded answer exposes source metadata.
- [ ] Unsupported questions receive a clear limitation response.
- [ ] Ollama is the required demo provider.
- [ ] Cloud provider can be selected without changing application code.
- [ ] Ship 30 skill is encoded as a reusable skill.
- [ ] HTML artifacts are sanitized and sandboxed.
- [ ] One-command Docker startup exists.
- [ ] Health endpoint exists.
- [ ] Automated tests cover critical behavior.
- [ ] README enables evaluator setup.

## 4. Risks and trade-offs

### Hallucination

Risk: model invents product advice.

Mitigation: retrieval-first prompt, low temperature, explicit unsupported-answer rule, source display.

### Local model quality

Risk: small local model may be weaker than Claude.

Mitigation: retrieve concise, high-signal excerpts; keep generation task structured; allow cloud provider toggle.

### Latency

Risk: local embedding + generation is slow on laptops.

Mitigation: small top-k, bounded context, modest chunk size, no unnecessary agent loops.

### Data leakage

Risk: sensitive data accidentally enters logs or source control.

Mitigation: dataset excluded from Git, secrets excluded, agent transcript sanitization instructions.

### Unsafe artifact rendering

Risk: generated HTML executes active content.

Mitigation: allowlist sanitizer plus sandboxed iframe with no script permissions.

## 5. Implementation plan

1. Bootstrap Docker/Postgres.
2. Add transcript ingestion and embeddings.
3. Add retrieval and provider abstraction.
4. Add session/chat APIs.
5. Add UI.
6. Add Ship 30 skill and artifact viewer.
7. Add tests/security checks.
8. Validate with manual demo plan.
