# Sugar Dependencies

A working brief for Claude Code.

## Concept

A *sugar dependency* is a small, AI-generated facade that recreates the slice of a third-party library you actually use, implemented over the Python standard library. The goal is to drop a dependency you barely use while keeping the same friendly call sites.

Think of it as semantic tree-shaking at the dependency boundary. JS bundlers tree-shake unused code *inside* a dependency. This goes one level up: it removes the dependency entirely and re-expresses the used slice over a stdlib primitive that was already sufficient.

It is **not** vendoring (copying the whole library into your tree) and **not** dead-code elimination (pruning your own unused code). It is "reimplement the used slice over a primitive that was already enough."

Motivation: reduce supply-chain and maintainer risk (the httpx situation is the prompting example), shrink the transitive dependency tree, and cut dependency sprawl.

## The one distinction that matters

Two operations hide under the word "sugar," with very different risk:

- **Ergonomic sugar (safe).** The library gave you a nicer signature over a capability the stdlib already has the same *engine* for. Example: `httpx.get(url, params=, headers=)` over `urllib.request.urlopen`. Same engine (HTTP over a socket with TLS), nicer call site. Re-skinning only.
- **Engine swap dressed as sugar (risky).** The library's engine does real work the stdlib does not. Reimplementing it makes you the unpaid, untested maintainer of a worse version of that engine. Avoid.

The trap: the number of functions you call is a poor proxy for how much library you depend on. A single `httpx.get` quietly carries gzip/br/zstd decompression, redirect rules across 301/302/303 vs 307/308, cookies, connection pooling, granular timeouts, proxy handling, and `raise_for_status`. Match the signature while silently dropping decompression and you have a latent bug wearing a familiar name.

## Candidate screening

A dependency is a good candidate only when ALL of these hold:

1. The used surface is small (a handful of functions / call shapes).
2. The behavior behind that surface is shallow (no reliance on pooling, async, retries, content codecs, or protocol-level features).
3. The stdlib has a real primitive underneath (HTTP: yes, via `urllib` / `http.client`. Not everything qualifies.)
4. Low call volume, not on a hot path.
5. Few people maintain the calling code, so a vendored facade does not cost team legibility.

If call count is low but each call leans on the engine, it is NOT a candidate.

## Prioritization metric

Rank candidates by: **(transitive subtree removed from the lockfile) / (number of call sites in the codebase).**

- High ratio = fat tree you barely use = best target. (httpx pulls `httpcore`, `h11`, `anyio`, `sniffio`, `idna`, `certifi`; collapsing to `urllib` + `certifi` is a real reduction.)
- Low ratio = used heavily, or already a leaf = leave it alone.

Claude Code can compute both sides: usage count from the codebase, subtree size from the lockfile.

## Workflow for Claude Code

1. **Scan usage.** Find every import and call site of the target dependency. List the distinct call shapes (functions, arguments, return values actually used).
2. **Assess candidacy** against the screening list above. If it fails, say so plainly and stop.
3. **Compute footprint** (subtree removed / call sites) to confirm it is worth doing.
4. **Record characterization tests FIRST.** Capture the real responses the current code receives, using vcrpy (it can record `urllib.request`). These recordings are the contract.
5. **Generate a drop-in facade** over the stdlib that mirrors the original names and signatures. Preserve the import surface so reverting is a one-line import change.
6. **Prove equality.** The facade must reproduce identical output on the recorded traffic.
7. **Parallel-run (recommended).** Run facade and original side by side asserting equality before deleting the dependency.
8. **Swap and remove** the dependency from the project once green.

The tests are where the value is. "AI wrote a wrapper" is a confidence trap. "AI wrote characterization tests, then a wrapper that passes them" is the real deliverable.

## Hard constraints and red flags

- **Async has no stdlib client.** `urllib.request` and `http.client` are synchronous and blocking. `asyncio` gives you async sockets (`asyncio.open_connection` with `ssl=`), not an async HTTP protocol. Options: run the blocking client with `asyncio.to_thread` for occasional calls, or keep a real async client (aiohttp, niquests) for hot paths. Do NOT hand-roll HTTP over `asyncio.open_connection`; that is the engine-swap trap.
- **Security: safe until it makes trust decisions.** Plain `urlopen` with a proper `SSLContext` and no clever URL surgery is fine. The moment the facade follows redirects, builds URLs from user input, or makes verification choices, it is in scope for SSRF, URL-parsing differentials, header injection, and TLS-verification bugs. Audit it like any other security-relevant HTTP code.
- **urllib sharp edges to handle explicitly:**
  - No transparent gzip/deflate decompression (handle `Content-Encoding` yourself).
  - Redirect handling has quirks; do not assume requests/httpx parity.
  - `HTTPError` is both an exception and a response-like object; translate it to a clean exception type.
  - No connection reuse across `urlopen` calls (fine at low volume).
  - Timeout is a single float, not a connect/read split.
  - Cookies and proxies need explicit `http.cookiejar` / handler wiring.
- **TLS roots:** use `certifi` (tiny) or the OS trust store via `ssl.create_default_context()` with no cafile. "Zero dependencies" is not quite reachable for TLS on every platform; certifi exists to paper over OS-store inconsistencies.

## Worked example (the safe case)

Target: a few `httpx.get(...)` calls hitting public GET endpoints.

Replacement: `urllib.request` + certifi behind a `fetch_url(url, *, params=None, headers=None) -> bytes` facade, with a `build_request` helper assembling params and headers via `urlsplit` / `urlunsplit`. Returns the response body. No pooling, no streaming, GET only. This is the proven pattern (see Alex Chan's `chives.fetch`).

## Scope guardrail (restate to Claude Code)

Only the safe, sync, low-volume, well-trodden path. If the analysis shows the dependency leans on its engine, async, or high concurrency, report that and do not generate a facade.
