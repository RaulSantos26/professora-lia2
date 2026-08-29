import json
import re
from urllib.parse import quote
from urllib.request import Request, urlopen


class WikimediaVisualReferenceTool:
    """
    Internal, allow-listed research tool. It supplies visual context only;
    it never fetches arbitrary web pages or injects external HTML.
    """

    _terms = (
        "Perseu",
        "Medusa",
        "Atena",
        "Hermes",
        "Pegaso",
    )

    def research(
        self,
        *,
        evidenceContext: str,
        instruction: str,
    ) -> list[dict]:
        corpus = f"{instruction}\n{evidenceContext}".casefold()
        matches = [
            term for term in self._terms
            if term.casefold() in corpus
        ][:2]

        references = []

        for term in matches:
            url = (
                "https://pt.wikipedia.org/api/rest_v1/"
                f"page/summary/{quote(term)}"
            )

            try:
                request = Request(
                    url,
                    headers={"User-Agent": "ProfessoraLia/2.0 visual-research"},
                )
                with urlopen(request, timeout=4) as response:
                    payload = json.loads(response.read().decode("utf-8"))

                references.append(
                    {
                        "title": str(payload.get("title") or term),
                        "summary": str(payload.get("extract") or "")[:700],
                        "pageUrl": (
                            "https://pt.wikipedia.org/wiki/"
                            + quote(str(payload.get("titles", {}).get(
                                "canonical",
                                term,
                            )))
                        ),
                        "thumbnailUrl": (
                            payload.get("thumbnail") or {}
                        ).get("source"),
                        "source": "Wikimedia / Wikipedia",
                    }
                )
            except Exception:
                continue

        return references
