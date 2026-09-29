# Adapting the skeleton and connecting models

## Configuration without code changes

Create a workspace with `python -m server.manage workspace my-business "My business"`, provision an admin, then edit title, account labels, unit targets, document sections, sales header aliases, forecasting and AI enablement in Configuration studio. Account IDs are authorization attributes: removal is blocked while referenced. Use additive changes or migrate references deliberately. Config revisions reject concurrent lost updates. Historical conversions do not silently change; reimport to apply current rules.

The template is a safe ordered section list rather than uploaded executable HTML/Jinja code. To support another approved layout, add a typed section to `WorkspaceConfig` and an escaped renderer branch. For editable long-form templates, design a declarative allowlisted schema and tests before accepting user-defined expressions.

## New formats and business datasets

Add an explicit extension to `SUPPORTED`, a payload-signature check and a trusted extractor in `conversion.py`. Emit the existing semantic blocks, preserve source metadata and declare losses in warnings. Never use filename paths, execute Office macros/formulas, resolve XML entities, fetch remote assets, or import Python/JavaScript supplied as source content. Test corrupt/truncated/hostile/large files before enabling the adapter.

Exporters must accept canonical HTML, not bypass it by converting raw source directly. Add an output name/MIME type to `FORMATS` and document round-trip losses. For another business dataset, define its schema, transaction, scope and idempotency key before adding a mapped-table processor. CSV sales ingestion is a reference implementation, not a generic arbitrary-schema database loader.

For OCR, add a trusted local engine/service adapter with source-language selection, timeout, confidence/evidence and review status. Scanned documents/graphs/equations should preserve page images and source locations. Do not promote guessed axes, table cells, mathematical symbols or unit annotations into authoritative measurements. The current implementation preserves these originals and supports explicit image-model requests; it does not include an OCR engine or universal vision understanding.

## Hosted or local models

Keep credentials out of Git, UI config and browser bundles. Enable `ai_enabled` only after choosing a provider and approving its handling of the organization's scoped data.

```powershell
$env:KB_AI_ENDPOINT = "http://127.0.0.1:11434/v1/chat/completions"
$env:KB_AI_MODEL = "your-installed-compatible-model"
# Hosted models: use the provider's HTTPS endpoint and set KB_AI_KEY privately.
python -m uvicorn server.app:app --host 127.0.0.1 --port 8000
```

An OpenAI-compatible server can represent an external API, local model or custom agent. Loopback HTTP is allowed; remote endpoints require HTTPS. Redirects, embedded URL credentials/query strings and environment proxying are disabled. Endpoint choice is an **operator trust boundary**, not an end-user URL input; restrict egress/DNS at deployment. Adapter calls have a 20-second timeout and 128 KB response limit. Provider calls are contract-tested with a fake HTTP model, not with paid/live APIs.

The request supplies system guidance, JSON evidence and optionally a normalized PNG. Text response contract:

```json
{"answer":"Source-grounded text with explicit uncertainty", "citations":["authorized-document-id"]}
```

Endpoints differ in JSON/vision support; select compatible models, and implement another adapter where needed. Image requests may fail safely if the chosen model lacks vision. The API validates text/citation shape and scope, not truth. A valid source citation does not certify an answer.

## Import an existing/custom Python model

Implement `AIAdapter.answer(question, context, image=None) -> dict` in trusted application code. Load weights once in a factory rather than per request. For example, replace the reference factory in `examples/custom_ai.py` with a wrapper around a callable model, then set `KB_AI_FACTORY=examples.custom_ai:build` before starting Python.

The factory can wrap scikit-learn, Transformers, llama.cpp, a custom model or a bounded agent. Those optional frameworks/weights are deliberately not bundled or downloaded automatically. Their license, memory requirements and hardware support remain the operator's responsibility. Never deserialize untrusted pickle/model files, execute code from documents or provide autonomous model tools. Preserve ACL-filtered evidence and the answer/citation contract. Run adapter tests against malformed responses, unknown IDs, timeouts, oversized output and provider exceptions. An adapter cannot bypass the server's citation validation, but trusted factory code has process authority—review it as code.

## Scaling and production extensions

Use a queue and dedicated no-network parser containers for public uploads; enforce CPU/memory/disk quotas per job. Adopt PostgreSQL plus scoped FTS/vector indexes and object storage if volume grows. Enforce ACLs before retrieval and again when hydrating citations. Add OIDC SSO, permissions scoped to approved operations, data retention/deletion and externally monitored audit storage. Replace single-account product ownership with a many-to-many inventory assignment relation when the business requires it.
