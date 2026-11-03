# Design decisions

## Keep the agent bounded and inspectable

The graph has explicit planning, search, page-fetch, source-comparison, and report stages. One run is ephemeral and synchronous; there is no database, scheduled execution, or delegated multi-agent crew. This keeps resource use and source provenance visible while avoiding complexity without measured benefit.

## Make the model optional—and keep it out of the citation path

The default planner generates three fixed research angles. A user may opt in to an OpenAI-compatible model for query planning, but the model never sees fetched page text and never writes final findings or citations. Search queries are bounded and treated as data. This deliberately favors verifiable excerpts over fluent but potentially unsupported synthesis.

## Application-owned evidence ledger

Each retrieved page or fallback snippet becomes a structured evidence record. IDs are assigned after retrieval; report findings are copied from those excerpts and cite their application-assigned IDs. The citation audit requires known IDs and exact excerpt equality. This eliminates fabricated source IDs and free-form model claims from the report's findings, but it does not prove that the source itself is accurate or that a human-drawn inference is entailed.

## Replaceable search with conservative fetching

DuckDuckGo Lite provides a no-key demonstration path; its public HTML is an unstable interface. A configured SearXNG JSON endpoint is supported as an alternative. The fetcher reads only bounded static HTML, uses Trafilatura with a standard-library fallback, and skips local/private URL targets. Redirect destinations are checked again. DNS rebinding and network-level routing cannot be solved by application checks alone, so production use still needs egress controls.

## Compare sources without overstating the result

The report records pairwise token-set Jaccard overlap. It labels that result as lexical similarity only; it does not declare corroboration, contradiction, independence, authority, or factual accuracy. Those judgments require a stronger benchmark and often human review.

## Test mechanics, not truth

Offline tests use deterministic fake adapters and synthetic passages to test task planning, query attribution, URL validation, HTML extraction, caps, report structure, and citation audits. Passing tests establish expected program behavior, not search quality or factual correctness. Live search is an optional smoke check because public endpoints may rate-limit or change their HTML.
