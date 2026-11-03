# Open-source tools for an autonomous research agent

**As of 2026-10-31, LangGraph is the best default foundation for a small custom research agent that needs explicit, controllable steps.** It is a workflow runtime, not a turnkey search-and-citation product. Haystack is a strong alternative when retrieval pipelines are the center of the design; Pydantic AI's Researcher is a quicker typed-Python shortcut, but its harness API is still 0.x. GPT Researcher provides the most research-specific functionality out of the box, but its own security and package metadata caveats make it a conditional prototype choice rather than a production default.

> Historical tool-selection snapshot, not a description of every current feature. The implementation now limits optional model use to query planning and uses application-owned, exact source excerpts for report findings so the model cannot author citations.

## What is in the ecosystem

Agent tooling is a stack, not one package. Frameworks such as LangGraph, CrewAI, and Microsoft Agent Framework control the sequence of model and tool calls. Retrieval-focused libraries such as LlamaIndex and Haystack organize documents and search flows. A separate search provider discovers pages; a crawler or fetcher reads them; and the application must still retain the evidence and check citations. The tools below overlap, but they solve different layers.

For a custom system, use one main orchestrator, one search/fetch path, and an application-owned evidence record. Combining several orchestration frameworks by default adds complexity without filling the main gap: none of the reviewed sources establishes a guarantee that every generated claim is supported by its citation.

## Best fits by use case

### LangGraph: best control backbone

LangGraph is an MIT-licensed, low-level runtime for long-running, stateful agents. Its graph model gives the developer explicit state, nodes, edges, branching, persistence, and interrupts. The official release listing showed version 1.2.19 on 2026-10-30, a recent maintenance signal rather than a quality benchmark. [1] [2] [3]

It does not provide a search engine, crawler, source-quality score, or evidence ledger by itself. Pick it when you want to own the research steps and be able to inspect or resume them. For a prototype, use one graph for query planning, search, retrieval, and synthesis; add durable checkpoints only when runs need recovery or human review.

The current Project 07 implementation keeps the explicit graph and bounded retrieval, but intentionally omits model-authored synthesis; reports use the exact excerpt-backed findings described in the project README.

### Haystack: best retrieval-centered alternative

Haystack is an Apache-2.0 Python framework with composable pipelines, agent tools, document metadata, and retrieval components. Its official Deep Research Agent recipe is unusually close to this task: it divides a question into sub-research, searches in parallel, reads URLs, and writes a cited Markdown report. The recipe is in an experimental Agent Pack, however, and should be treated as a reference implementation rather than a stability promise. [4] [5] [6]

The project was on the 3.x line, with v3.4.1 listed on 2026-10-21. Haystack 3.x also moved selected components into separately installed integrations, so pin the core and integration versions together. [7] [8] It is a strong choice if document retrieval and inspectable pipelines matter more than a low-level custom graph.

### Pydantic AI: fastest typed Python starting point

Pydantic AI is an MIT-licensed Python agent framework with validated tool arguments, structured outputs, and model/provider options. Its separate Harness Researcher bundles web search, URL fetching, and a delegated researcher with citation-oriented instructions. That gives a builder a quicker first version than assembling every part manually. [9] [10]

The stability caveat matters: the main framework had reached stable V2, but Harness Researcher is documented as a 0.x API that may change between minor versions. Local search/fetch fallbacks also do not have every restriction of provider-native tools. Use it for a quick typed prototype, then add your own evidence storage and citation verification. [11] [12]

### GPT Researcher: most research-specific, with material caveats

GPT Researcher already includes planning, parallel research, crawling/retrieval, source exposure, and citation-bearing reports. The official release page showed v3.7.0 in September 2026, and the docs expose URLs and source records. This makes it useful as a reference implementation or a quick research prototype. [13] [14]

Do not treat those citations as proven claim support. More importantly, its security policy says the backend lacks built-in authentication and network access controls and is not hardened for multi-tenant use. Its GitHub root license is Apache-2.0, while `pyproject.toml` declares MIT for the Python package; the release tag also directs users to install package version 0.16.0. Resolve the exact artifact and license before adopting or redistributing it. [15] [16] [17]

## Other useful choices

### Microsoft Agent Framework, not archived AutoGen

Microsoft Agent Framework is the active successor to AutoGen and Semantic Kernel. AutoGen's repository is archived and explicitly points new users to the successor. MAF offers Python and .NET workflows, tools, approval gates, resumable execution, and provider-hosted web search where the chosen model provider supports it. The Python release listing showed 1.24.0 on 2026-10-30. [18] [19] [20] [64]

Prefer MAF over AutoGen for a new Microsoft-centered build. Search availability and data handling depend on the model provider; MAF's RAG pattern can use a supplied search adapter, but it is not a general crawler or a claim-level evidence store.

### CrewAI: useful when roles are real

CrewAI is an MIT-licensed framework that combines role-based Crews with event-driven Flows. Its official tool catalog includes search, scraping, and research integrations; Flows add state, routing, and persistence. This fits tasks where separate researcher, analyst, and editor roles materially help. [21] [22] [23]

The trade-off is that multi-role execution can be more moving parts than a bounded one-agent workflow. Its official release page showed v1.15.33 while PyPI showed 1.15.32 in the research snapshot, so lock and verify the installable version. Search and crawl integrations remain separate providers or packages, and citation validation is still application work. [65] [66]

### Hugging Face smolagents: light and flexible

smolagents is an Apache-2.0 lightweight Python framework with search and page-visit tools, and its docs show a multi-agent web-research example. It supports different model providers and has a compact agent loop. [24] [25] [26]

Its v1.26.0 documentation explicitly marks the API experimental. The basic page-visit tool is not a general crawler, and the security guide warns that locally executing model-generated code is not fully secure. It is a good learning or constrained prototype option, but keep untrusted web research away from an unisolated CodeAgent. [25] [27] [67]

### LlamaIndex: strong data and retrieval toolkit

LlamaIndex is an MIT-licensed Python framework for retrieval, data ingestion, agents, and workflows. Its integrations include web search and page readers; its citation query engine and workflow features can help build retrieval-heavy research. The core was at 0.14.25 in the checked release snapshot. [28] [29] [30] [68] [69]

The maintainer README says strategic focus has shifted toward parsing products while the broad framework remains available. Search, crawling, and readers are separate integrations, not one universal web stack. This is a good choice when document and retrieval processing is central, but preserve source metadata and verify citations yourself. [31]

### OpenAI Agents SDK: quick hosted-search path

The OpenAI Agents SDK is open-source under MIT and provides an application-run agent loop, custom tools, guardrails, and human approval. Its direct web-search path uses OpenAI's hosted Responses API tool, which can return source URLs and citation annotations. [32] [33] [34] [75] [76]

The SDK can be used with other model providers, but hosted search and other hosted tools are provider-specific. It also leaves persistence and deployment to the application. Choose it when a hosted search path is acceptable; choose LangGraph or another provider-neutral workflow backbone when search portability and infrastructure control matter more. [70]

### DSPy: optimize the research program, not the web stack

DSPy is an MIT-licensed framework for composing and optimizing language-model programs. Its typed tools and agent loop can help test or improve a research workflow against measured examples, but the builder supplies the web search, crawler, retrieval, and evidence records. The official release page showed version 3.4.1 in October 2026; the 3.4 ReActV2 API was marked experimental with a documented transition in later versions. [35] [36] [37]

Choose DSPy when task evaluation and program optimization are priorities. It is not the first component to add if the immediate gap is reliable source collection.

## Search, crawling, and extraction components

These tools fill the retrieval gaps left by agent frameworks. They work at different layers, so a research agent normally selects one discovery tool and one page-acquisition path rather than installing all of them.

### SearXNG: self-hosted search aggregation

SearXNG is an AGPL-3.0 metasearch engine: it queries configured upstream engines and databases, then returns candidate URLs, snippets, and (where the engine adapter supplies it) engine attribution. It is not a web crawler or full-page extractor. Its API can return JSON, but the instance operator can disable machine-readable formats. The project uses rolling releases rather than formal GitHub Releases, so operators need a deliberate update process. [39] [40] [41] [71] [72]

Use a private instance when you want control over search configuration and query handling. Public instances are run by their operators, with varying settings and trust. SearXNG still depends on upstream engines that can block, change, or limit requests; engine labels are provenance hints, not proof that a destination page is reliable.

### Trafilatura: lightweight static-page extraction

Trafilatura is an Apache-2.0 Python library and command-line tool for focused discovery, downloading HTML, extracting article-like text and metadata, and serializing it to formats such as plain text or Markdown. Version 2.3.1 was listed as the latest release in October 2026. It is a good fit for static articles and feeds without operating a browser. [42] [43] [44] [73]

It does not render JavaScript and can perform poorly on catalogs, galleries, short pages, or other non-article layouts. Its crawler and downloader include politeness controls, but access policy, crawl scope, persistence, and evidence records remain the application's responsibility. [45] [46]

### Crawl4AI: browser-capable crawling and extraction

Crawl4AI offers an open-source Python crawler that can render JavaScript and convert pages into Markdown or structured output. Its result model can include requested/final URLs, status, redirects, metadata, and optional browser/network details. The latest observed release was v0.9.5 from 2026-10-14. The checked-in license file combines Apache-2.0 text with an additional project attribution requirement, so do not assume an unmodified Apache license. [47] [48] [49]

Use it when a page needs browser rendering or when its crawling and structured-extraction controls are useful. It is heavier than static HTTP retrieval, robots checks are disabled by default in the documented parameters, and its hosted Cloud service is separate from self-hosting. [50] [51]

### Firecrawl: unified crawl/extraction API

Firecrawl can scrape, crawl, discover pages from links or sitemaps, and extract web content to Markdown or structured output. Its open-source core is AGPL-3.0-or-later; some SDKs and UI components have separate licenses. Self-hosted and Cloud deployments are materially different: the self-host quickstart warns that authentication, durable storage, TLS, and high availability are not provided by the quickstart setup. Its formal release page showed v2.11.0 while generated container tags had advanced separately, so pin the actual artifact. [52] [53] [54] [74]

This can reduce integration work, but it adds a service to operate or a hosted provider to trust. Inspect per-page status and errors, preserve provenance, and review licensing and site access requirements before deployment.

### Scrapy: controlled, site-specific crawling

Scrapy is a BSD-3-Clause Python framework for asynchronous crawls, custom spiders, selectors, structured exports, retries, and per-domain delay/concurrency controls. Release 2.19.0 was published in September 2026. It is a strong choice when sources and page patterns are known and repeatable. [55] [56] [57]

Scrapy does not render JavaScript itself, and multi-server distributed crawling is not built in. Its `ROBOTSTXT_OBEY` fallback setting is false, although generated projects enable it; configure it deliberately and use a browser such as Playwright only for pages where static retrieval is insufficient. [58] [59]

### Playwright: browser rendering, not a crawler

Playwright is an Apache-2.0 browser automation library for Chromium, Firefox, and WebKit. It can render dynamic pages, interact with ordinary page UI, and capture network events and traces. Release 1.64.1 was published in October 2026. It is best used as a selective rendering fallback, because it does not provide search discovery, a crawl frontier, deduplication, or citation management. [60] [61] [62]

The browser runs untrusted page code, so harden its container, limit permissions and network access, and set concurrency and resource budgets. A browser trace is useful debugging evidence, not automatically a durable citation archive. [63]

### Practical retrieval-stack choices

For static article-focused research, use SearXNG for discovery and Trafilatura for selected-page extraction. For recurring research on known domains, use Scrapy and add Playwright only where rendering is necessary. For a higher-level browser-capable acquisition API, choose either Crawl4AI or Firecrawl, not both by default. In every case, retain the original and final URL, retrieval time, status, exact passage, and content identity; then validate claims against those passages.

## Recommendation for the prototype

The prototype in this project uses **LangGraph, Trafilatura, and a replaceable search adapter**. It supports a self-hosted SearXNG JSON endpoint while retaining DuckDuckGo Lite as the no-key demonstration fallback. The fetcher is bounded HTML-only and the evidence record preserves provider, engine, extractor, URL, query, timestamp, and excerpt. It keeps one agent and five visible workflow stages. It defaults to extractive findings, and an optional model is restricted to query planning: it never sees retrieved pages or writes findings or citations.

The key requirement for any next version is an evidence check stronger than “this source ID exists.” The application should retain the passage or quote behind each claim, check that the cited passage supports the claim, and test source coverage and citation completeness on labeled tasks. Treat retrieved pages as untrusted input, constrain network access, and add a human review step before acting on consequential research.

## References

[1]: https://docs.langchain.com/oss/python/langgraph/overview "LangGraph overview"
[2]: https://github.com/langchain-ai/langgraph/blob/main/LICENSE "LangGraph MIT license"
[3]: https://github.com/langchain-ai/langgraph/releases "LangGraph releases"
[4]: https://github.com/deepset-ai/haystack/blob/main/LICENSE "Haystack Apache-2.0 license"
[5]: https://docs.haystack.deepset.ai/docs/deep-research-agent "Haystack Deep Research Agent"
[6]: https://docs.haystack.deepset.ai/docs/agents "Haystack Agents"
[7]: https://github.com/deepset-ai/haystack/releases "Haystack releases"
[8]: https://docs.haystack.deepset.ai/docs/migration "Haystack migration guide"
[9]: https://github.com/pydantic/pydantic-ai/blob/main/LICENSE "Pydantic AI MIT license"
[10]: https://pydantic.dev/docs/ai/harness/researcher/ "Pydantic AI Researcher"
[11]: https://pydantic.dev/docs/ai/capabilities/web-search/ "Pydantic AI web search"
[12]: https://github.com/pydantic/pydantic-ai/blob/main/docs/version-policy.md "Pydantic AI version policy"
[13]: https://docs.gptr.dev/docs/gpt-researcher/getting-started/introduction "GPT Researcher introduction"
[14]: https://github.com/assafelovic/gpt-researcher/releases "GPT Researcher releases"
[15]: https://github.com/assafelovic/gpt-researcher/blob/master/LICENSE "GPT Researcher repository license"
[16]: https://github.com/assafelovic/gpt-researcher/blob/main/pyproject.toml "GPT Researcher package metadata"
[17]: https://github.com/assafelovic/gpt-researcher/blob/main/SECURITY.md "GPT Researcher security policy"
[18]: https://github.com/microsoft/autogen "Microsoft AutoGen repository and archive notice"
[19]: https://learn.microsoft.com/en-us/agent-framework/overview/ "Microsoft Agent Framework overview"
[20]: https://learn.microsoft.com/en-us/agent-framework/agents/tools/web-search "Microsoft Agent Framework web search"
[21]: https://github.com/crewAIInc/crewAI/blob/main/LICENSE "CrewAI MIT license"
[22]: https://docs.crewai.com/v1.15.33/en/tools/search-research/overview "CrewAI search and research tools"
[23]: https://docs.crewai.com/v1.15.33/en/concepts/flows "CrewAI Flows"
[24]: https://github.com/huggingface/smolagents/blob/main/LICENSE "smolagents Apache-2.0 license"
[25]: https://huggingface.co/docs/smolagents/v1.26.0/en/reference/default_tools "smolagents built-in tools"
[26]: https://huggingface.co/docs/smolagents/v1.26.0/en/examples/multiagents "smolagents multi-agent research example"
[27]: https://huggingface.co/docs/smolagents/v1.26.0/en/tutorials/secure_code_execution "smolagents secure code execution"
[28]: https://github.com/run-llama/llama_index/blob/main/LICENSE "LlamaIndex MIT license"
[29]: https://developers.llamaindex.ai/python/framework/ "LlamaIndex framework"
[30]: https://developers.llamaindex.ai/python/llamaagents/workflows/ "LlamaIndex Workflows"
[31]: https://github.com/run-llama/llama_index "LlamaIndex repository README"
[32]: https://github.com/openai/openai-agents-python/blob/main/LICENSE "OpenAI Agents SDK MIT license"
[33]: https://openai.github.io/openai-agents-python/tools/ "OpenAI Agents SDK tools"
[34]: https://developers.openai.com/api/docs/guides/tools-web-search "OpenAI web search"
[35]: https://github.com/stanfordnlp/dspy/blob/main/LICENSE "DSPy MIT license"
[36]: https://dspy.ai/current/diving-deeper/tools/ "DSPy tools"
[37]: https://dspy.ai/current/diving-deeper/react/ "DSPy ReAct"
[38]: https://github.com/stanfordnlp/dspy/releases "DSPy releases"
[39]: https://github.com/searxng/searxng "SearXNG repository and license metadata"
[40]: https://docs.searxng.org/dev/search_api.html "SearXNG Search API"
[41]: https://docs.searxng.org/own-instance.html "Why use a private SearXNG instance?"
[42]: https://raw.githubusercontent.com/adbar/trafilatura/master/LICENSE "Trafilatura Apache-2.0 license"
[43]: https://trafilatura.readthedocs.io/ "Trafilatura documentation"
[44]: https://github.com/adbar/trafilatura/releases/tag/v2.3.1 "Trafilatura v2.3.1 release"
[45]: https://trafilatura.readthedocs.io/en/latest/crawls.html "Trafilatura web crawling"
[46]: https://trafilatura.readthedocs.io/en/latest/troubleshooting.html "Trafilatura extraction troubleshooting"
[47]: https://github.com/unclecode/crawl4ai/blob/main/LICENSE "Crawl4AI license text"
[48]: https://github.com/unclecode/crawl4ai/releases/tag/v0.9.5 "Crawl4AI v0.9.5 release"
[49]: https://docs.crawl4ai.com/core/quickstart/ "Crawl4AI Quick Start"
[50]: https://docs.crawl4ai.com/api/parameters/ "Crawl4AI API parameters"
[51]: https://docs.crawl4ai.com/core/self-hosting/ "Crawl4AI self-hosting"
[52]: https://github.com/firecrawl/firecrawl/blob/main/LICENSE "Firecrawl core license"
[53]: https://github.com/firecrawl/firecrawl "Firecrawl repository and open-source/hosted distinction"
[54]: https://docs.firecrawl.dev/contributing/self-host "Firecrawl self-hosting guide"
[55]: https://raw.githubusercontent.com/scrapy/scrapy/master/LICENSE "Scrapy BSD-3-Clause license"
[56]: https://docs.scrapy.org/en/latest/intro/overview.html "Scrapy overview"
[57]: https://docs.scrapy.org/en/latest/news.html "Scrapy 2.19.0 release notes"
[58]: https://docs.scrapy.org/en/latest/topics/settings.html "Scrapy settings and robots behavior"
[59]: https://docs.scrapy.org/en/latest/topics/dynamic-content.html "Scrapy dynamic-content guidance"
[60]: https://github.com/microsoft/playwright/blob/main/LICENSE "Playwright Apache-2.0 license"
[61]: https://github.com/microsoft/playwright "Playwright repository"
[62]: https://github.com/microsoft/playwright/releases "Playwright releases"
[63]: https://playwright.dev/docs/docker "Playwright Docker and security guidance"
[64]: https://github.com/microsoft/agent-framework/releases/latest "Microsoft Agent Framework latest release"
[65]: https://github.com/crewAIInc/crewAI/releases "CrewAI releases"
[66]: https://pypi.org/project/crewai/1.15.32/ "CrewAI 1.15.32 on PyPI"
[67]: https://huggingface.co/docs/smolagents/v1.26.0/en/reference/agents "smolagents Agents API and stability note"
[68]: https://github.com/run-llama/llama_index/releases "LlamaIndex releases"
[69]: https://pypi.org/project/llama-index-core/ "LlamaIndex core on PyPI"
[70]: https://developers.openai.com/api/docs/guides/agents "OpenAI agent runtime options"
[71]: https://github.com/searxng/searxng/releases "SearXNG formal releases"
[72]: https://github.com/searxng/searxng/blob/master/LICENSE "SearXNG AGPL-3.0 license"
[73]: https://github.com/adbar/trafilatura "Trafilatura repository and historical license note"
[74]: https://github.com/firecrawl/firecrawl/releases "Firecrawl formal releases"
[75]: https://openai.github.io/openai-agents-python/human_in_the_loop/ "OpenAI Agents SDK human-in-the-loop"
[76]: https://openai.github.io/openai-agents-python/guardrails/ "OpenAI Agents SDK guardrails"
