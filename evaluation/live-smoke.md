# Live CLI smoke test

**Run:** 2026-11-02 (local time, UTC+03:00)  
**Question:** “Python urllib request official documentation”  
**Search provider:** DuckDuckGo Lite  
**Limits:** 2 results per task; 2 pages fetched  
**Observed outcome:** The CLI completed its live plan → search → fetch → compare → report path, retrieved two static documentation pages, assigned `[S1]` and `[S2]`, and returned a passing exact-excerpt/source-ID citation audit. The temporary report was deleted after verification; no third-party page text is included here.

Sources fetched:

- [urllib.request — Extensible library for opening URLs](https://docs.python.org/3/library/urllib.request.html)
- [urllib — URL handling modules](https://docs.python.org/3/library/urllib.html)

This is a single integration smoke check, not a repeatability guarantee or a benchmark of search coverage, source authority, factual accuracy, or citation entailment.


## Repeat smoke test — 2026-11-03

**Question:** “Python urllib request official documentation”  
**Search provider:** DuckDuckGo Lite  
**Limits:** 2 results per task; 2 pages fetched  
**Observed outcome:** The updated CLI completed live search, static-page fetch, comparison, and report generation. It retrieved two Python documentation pages, produced two source-backed findings, and passed the citation audit (0 invalid findings). This remains an integration smoke test, not an accuracy or coverage benchmark.

- [urllib.request — Extensible library for opening URLs](https://docs.python.org/3/library/urllib.request.html)
- [urllib — URL handling modules](https://docs.python.org/3/library/urllib.html)
