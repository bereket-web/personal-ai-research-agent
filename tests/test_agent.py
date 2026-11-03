from __future__ import annotations

import json
import unittest
from unittest.mock import patch

from research_agent.agent import (
    Evidence,
    FetchedPage,
    Finding,
    ResearchAgent,
    SafePageFetcher,
    SearchHit,
    SearXNGSearch,
    _DDGResultParser,
    _default_tasks,
    _model_tasks,
    audit_citations,
    canonicalize_url,
    create_agent_from_environment,
    validate_public_url,
)


class FakeSearch:
    def __init__(self, hits_by_query: dict[str, list[SearchHit]] | None = None) -> None:
        self.hits_by_query = hits_by_query or {}
        self.calls: list[str] = []

    def search(self, query: str, max_results: int) -> list[SearchHit]:
        self.calls.append(query)
        return self.hits_by_query.get(query, [])[:max_results]


class FakeFetcher:
    def __init__(self, pages: dict[str, str] | None = None, fail: bool = False) -> None:
        self.pages = pages or {}
        self.fail = fail
        self.calls: list[str] = []

    def fetch(self, url: str) -> FetchedPage:
        self.calls.append(url)
        if self.fail:
            raise RuntimeError("synthetic fetch failure")
        return FetchedPage(
            "Research source",
            self.pages.get(url, "This research source contains relevant evidence about the question and its limitations."),
            "2026-11-02T00:00:00+00:00",
        )


class FakeChat:
    def __init__(self, response: str) -> None:
        self.response = response
        self.calls = 0

    def complete(self, system: str, user: str, model: str | None = None) -> str:
        self.calls += 1
        return self.response


class ResearchAgentTests(unittest.TestCase):
    def setUp(self) -> None:
        self.noop_validator = lambda _url: None

    def test_ddg_parser_extracts_title_url_and_snippet(self) -> None:
        html = """
        <table><tr><td><a class="result-link" href="//duckduckgo.com/l/?uddg=https%3A%2F%2Fexample.org%2Fguide&amp;rut=abc">Guide title</a></td></tr>
        <tr><td class="result-snippet">A useful <b>guide</b> snippet.</td></tr></table>
        """
        parser = _DDGResultParser()
        parser.feed(html)
        self.assertEqual(parser.results[0]["title"], "Guide title")
        self.assertEqual(parser.results[0]["url"], "https://example.org/guide")
        self.assertEqual(parser.results[0]["snippet"], "A useful guide snippet.")

    def test_searxng_parser_preserves_engine_attribution(self) -> None:
        payload = {"results": [{
            "title": "Primary source",
            "url": "https://example.org/docs?utm_source=test",
            "content": "A useful search excerpt.",
            "engines": ["engine-a", "engine-b"],
        }]}
        hits = SearXNGSearch.parse_results(payload, "agent research", 3)
        self.assertEqual(hits[0].provider, "searxng")
        self.assertEqual(hits[0].engines, ("engine-a", "engine-b"))
        self.assertEqual(hits[0].url, "https://example.org/docs")

    def test_searxng_rejects_credentialed_instance_urls(self) -> None:
        with self.assertRaises(ValueError):
            SearXNGSearch("https://user:pass@example.org")

    def test_canonical_url_removes_tracking_fragment_and_credentials(self) -> None:
        self.assertEqual(
            canonicalize_url("https://Example.org/a?utm_source=x&keep=1#section"),
            "https://example.org/a?keep=1",
        )
        self.assertEqual(canonicalize_url("https://user:pass@example.org/"), "")

    def test_public_url_guard_rejects_local_and_non_http_destinations(self) -> None:
        for url in ("http://127.0.0.1/admin", "http://localhost/", "file:///etc/passwd", "http://[::1]/"):
            with self.subTest(url=url), self.assertRaises(ValueError):
                validate_public_url(url)

    def test_safe_fetcher_extracts_static_html_and_drops_navigation(self) -> None:
        body = b"""<html><head><title>Page title</title></head><body>
        <nav>Navigation text that should be dropped.</nav>
        <article><h1>Research evidence</h1><p>This paragraph contains useful source
        content about agent frameworks and their retrieval workflows.</p></article>
        <script>ignoreThis();</script></body></html>"""

        class Headers:
            def get_content_type(self):
                return "text/html"

            def get_content_charset(self):
                return "utf-8"

        class Response:
            headers = Headers()

            def __enter__(self):
                return self

            def __exit__(self, *args):
                return False

            def read(self, limit):
                return body[:limit]

        class Opener:
            def open(self, request, timeout):
                return Response()

        with patch("research_agent.agent.validate_public_url"), patch(
            "research_agent.agent.build_opener", return_value=Opener()
        ):
            page = SafePageFetcher().fetch("https://example.org/page")
        self.assertEqual(page.extractor, "trafilatura")
        self.assertIn("useful source content", page.text)
        self.assertNotIn("Navigation text", page.text)
        self.assertNotIn("ignoreThis", page.text)

    def test_default_plan_breaks_question_into_distinct_research_angles(self) -> None:
        tasks = _default_tasks("How do research agents handle citations?")
        self.assertEqual(len(tasks), 3)
        self.assertIn("direct evidence", tasks[0].purpose)
        self.assertIn("primary", tasks[1].purpose)
        self.assertIn("contrary", tasks[2].purpose)
        self.assertLessEqual(max(len(task.query) for task in tasks), 220)

    def test_long_question_keeps_distinct_bounded_search_angles(self) -> None:
        tasks = _default_tasks("citation research " * 30)
        self.assertEqual(len(tasks), 3)
        self.assertEqual(len({task.query for task in tasks}), 3)
        self.assertLessEqual(max(len(task.query) for task in tasks), 220)

    def test_model_planner_is_structured_and_bounded(self) -> None:
        chat = FakeChat(json.dumps({"tasks": [
            {"purpose": "primary", "query": "official research standards"},
            {"purpose": "limits", "query": "research limitations"},
            {"purpose": "extra", "query": "an extra task"},
            {"purpose": "ignored", "query": "a fourth task"},
        ]}))
        tasks = _model_tasks("Research agent", chat, "test-model")
        self.assertEqual(len(tasks), 3)
        self.assertEqual(tasks[0].query, "official research standards")
        self.assertEqual(chat.calls, 1)

    def test_model_planner_rejects_unstructured_response(self) -> None:
        with self.assertRaises(ValueError):
            _model_tasks("Research agent", FakeChat("no JSON here"), None)

    def test_model_opt_in_without_key_falls_back_to_local_planner(self) -> None:
        with patch.dict("os.environ", {}, clear=True):
            agent = create_agent_from_environment(use_model=True)
        self.assertIsNone(agent.chat_client)

    def test_query_attribution_survives_multi_query_result_interleaving(self) -> None:
        tasks = _default_tasks("How do research agents handle citations?")
        hits_by_query = {}
        pages = {}
        for index, task in enumerate(tasks, 1):
            url = f"https://source{index}.example.org/article"
            hits_by_query[task.query] = [SearchHit(f"Source {index}", url, "", task.query)]
            pages[url] = f"Source {index} explains research citation provenance and evidence quality in detail."
        result = ResearchAgent(
            FakeSearch(hits_by_query), FakeFetcher(pages), url_validator=self.noop_validator
        ).research("How do research agents handle citations?", max_pages=3)
        self.assertEqual([item.query for item in result.evidence], [task.query for task in tasks])
        self.assertEqual([item.source_id for item in result.evidence], ["S1", "S2", "S3"])

    def test_malformed_search_url_is_skipped_without_aborting_run(self) -> None:
        query = "How does this system work?"
        hit = SearchHit("Malformed", "http://[", "", query)
        result = ResearchAgent(FakeSearch({query: [hit]}), FakeFetcher()).research(query, max_pages=1)
        self.assertEqual(result.evidence, [])
        self.assertTrue(any("malformed URL" in warning for warning in result.warnings))

    def test_report_findings_are_exact_source_excerpts_with_code_assigned_ids(self) -> None:
        query = "How do research agents handle citations?"
        excerpt = "A research system should keep evidence provenance and show citations with each factual result."
        hit = SearchHit("Guide", "https://example.org/guide", "", query)
        result = ResearchAgent(
            FakeSearch({query: [hit]}), FakeFetcher({hit.url: excerpt}), url_validator=self.noop_validator
        ).research(query, max_pages=1)
        self.assertTrue(result.citation_audit.passed)
        self.assertEqual(result.findings, [Finding(text=excerpt, source_ids=("S1",))])
        self.assertEqual(result.evidence[0].source_id, "S1")
        markdown = result.to_markdown()
        self.assertIn(r"each factual result\. [S1]", markdown)
        self.assertIn("exact excerpt provenance", markdown)
        structured = result.to_dict()
        self.assertIn("citation_audit", structured)
        self.assertEqual(json.loads(json.dumps(structured))["findings"][0]["source_ids"], ["S1"])

    def test_audit_rejects_invented_text_and_unknown_citation_ids(self) -> None:
        evidence = [Evidence("S1", "Guide", "https://example.org", "q", "t", "Exact source passage.", "page_fetch")]
        fabricated = Finding("A claim not present in the source.", ("S1",))
        unknown_id = Finding("Exact source passage.", ("S99",))
        for finding in (fabricated, unknown_id):
            audit = audit_citations([finding], evidence)
            self.assertFalse(audit.passed)
            self.assertEqual(audit.invalid_findings, 1)
        self.assertEqual(audit_citations([unknown_id], evidence).unknown_source_ids, ("S99",))

        second_evidence = Evidence("S2", "Other guide", "https://other.example.org", "q", "t", "Different passage.", "page_fetch")
        multi_source = Finding("Exact source passage.", ("S1", "S2"))
        self.assertFalse(audit_citations([multi_source], [*evidence, second_evidence]).passed)

    def test_model_can_only_change_plan_not_findings_or_citations(self) -> None:
        answer = "A source reports an exact research finding about citations and evidence provenance."
        fake_chat = FakeChat(json.dumps({"tasks": [{"purpose": "search", "query": "research citation evidence"}]}))
        query = "How do citations work?"
        hit = SearchHit("Guide", "https://example.org/guide", "", "research citation evidence")
        result = ResearchAgent(
            FakeSearch({hit.query: [hit]}),
            FakeFetcher({hit.url: answer}),
            chat_client=fake_chat,
            url_validator=self.noop_validator,
        ).research(query, use_model=True, max_pages=1)
        self.assertEqual(result.mode, "model-assisted-planning+extractive-report")
        self.assertEqual(fake_chat.calls, 1)
        self.assertEqual(result.findings[0].text, answer)
        self.assertEqual(result.findings[0].source_ids, ("S1",))
        self.assertTrue(result.citation_audit.passed)

    def test_invalid_url_is_skipped_without_using_its_snippet_as_citation(self) -> None:
        hit = SearchHit("Local target", "http://127.0.0.1/secret", "A plausible but untrusted search snippet that is long enough.", "q")
        result = ResearchAgent(
            FakeSearch({"How does this system work?": [hit]}),
            FakeFetcher(),
            url_validator=lambda _url: (_ for _ in ()).throw(ValueError("private destination")),
        ).research("How does this system work?", max_pages=1)
        self.assertEqual(result.evidence, [])
        self.assertIn("non-public or invalid URL", result.warnings[0])
        self.assertTrue(result.citation_audit.passed)

    def test_fetch_failure_may_keep_only_a_labeled_search_snippet(self) -> None:
        query = "How do research agents handle citations?"
        snippet = "A search provider excerpt describes evidence provenance and citation records, but the source page was unavailable."
        hit = SearchHit("Unreachable", "https://example.org/unreachable", snippet, query)
        result = ResearchAgent(
            FakeSearch({query: [hit]}), FakeFetcher(fail=True), url_validator=self.noop_validator
        ).research(query, max_pages=1)
        self.assertEqual(result.evidence[0].retrieval_method, "search_snippet_fallback")
        self.assertEqual(result.evidence[0].extractor, "search_snippet")
        self.assertTrue(result.citation_audit.passed)

    def test_page_fetch_count_is_capped(self) -> None:
        query = "How do research agents handle citations?"
        hits = [SearchHit(f"Page {index}", f"https://example.org/{index}", "", query) for index in range(5)]
        result = ResearchAgent(
            FakeSearch({query: hits}), FakeFetcher(), url_validator=self.noop_validator
        ).research(query, max_pages=2)
        self.assertEqual(len(result.evidence), 2)
        self.assertEqual(len(result.evidence), len(result.findings))

    def test_source_comparison_is_explicitly_heuristic(self) -> None:
        tasks = _default_tasks("How do research agents handle citations?")[:2]
        hits_by_query = {
            tasks[0].query: [SearchHit("A", "https://a.example.org", "", tasks[0].query)],
            tasks[1].query: [SearchHit("B", "https://b.example.org", "", tasks[1].query)],
        }
        pages = {
            "https://a.example.org/": "Research agents preserve evidence and citation provenance for each report finding.",
            "https://b.example.org/": "Research systems compare evidence and citation provenance across sources.",
        }
        result = ResearchAgent(
            FakeSearch(hits_by_query), FakeFetcher(pages), url_validator=self.noop_validator
        ).research("How do research agents handle citations?", max_pages=2)
        self.assertEqual(len(result.comparisons), 1)
        self.assertIn("not evidence of factual agreement", result.comparisons[0].interpretation)
        self.assertGreaterEqual(result.comparisons[0].jaccard_similarity, 0)

    def test_markdown_escapes_untrusted_passages_and_keeps_only_generated_citation(self) -> None:
        malicious = "Citation text [S99](https://evil.example) <script>alert(1)</script> is untrusted."
        evidence = [Evidence("S1", "<img src=x onerror=alert(1)>\nTitle", "https://example.org", "q", "t", malicious, "page_fetch")]
        finding = Finding(malicious, ("S1",))
        from research_agent.agent import CitationAudit, ResearchResult

        result = ResearchResult(
            question="question", tasks=[], queries=[], answer="", evidence=evidence,
            comparisons=[], findings=[finding], citation_audit=CitationAudit(True, 1, 0, (), ("S1",)),
            warnings=[], mode="local-extractive",
        )
        markdown = result.to_markdown()
        self.assertIn(r"\[S99\]", markdown)
        self.assertIn(r"\<script\>", markdown)
        self.assertIn("[S1]", markdown)
        self.assertNotIn("<script>alert", markdown)


if __name__ == "__main__":
    unittest.main()
