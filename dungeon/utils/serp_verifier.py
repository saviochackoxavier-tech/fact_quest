"""Live fact-check evidence via SerpApi (Google Search, India locale)."""
import os

try:  # google-search-results package
    from serpapi import GoogleSearch
except Exception:  # pragma: no cover
    GoogleSearch = None

# Active hackathon key. The SERPAPI_KEY environment variable overrides it.
# Do not push this file to a public repository with a live key inside.
SERPAPI_KEY = os.environ.get("SERPAPI_KEY", "3907bb691bd278d5f4172c4596f312ad7008958dd0a9f9f142eab6faa8e0b0de")

FALSE_KEYWORDS = ["fake", "hoax", "false", "debunked", "misleading", "rumor", "scam"]


def verify_claim_with_serpapi(claim_text):
    """
    Queries SerpApi Google Search to fetch live verification data
    for the game's fact-checking combat engine.
    """
    params = {
        "engine": "google",
        "q": claim_text + " fact check",
        "api_key": SERPAPI_KEY,
        "gl": "in",
        "hl": "en",
    }
    try:
        if GoogleSearch is None:
            raise RuntimeError("google-search-results is not installed")
        results = GoogleSearch(params).get_dict()
        if results.get("error"):
            raise RuntimeError(results["error"])

        organic = results.get("organic_results", [])
        snippets = [i.get("snippet", "") for i in organic[:4]]
        sources = [i.get("link", "") for i in organic[:4]]
        titles = [i.get("title", "") for i in organic[:4]]

        # Heuristic for game mechanics based on debunking keywords
        combined = " ".join(snippets + titles).lower()
        matches = sum(1 for kw in FALSE_KEYWORDS if kw in combined)
        truth_score = max(5, min(95, 100 - matches * 20)) if organic else 50

        return {"success": True, "snippets": snippets, "sources": sources, "titles": titles,
                "truth_score": truth_score, "total_results": len(organic)}
    except Exception as e:
        return {"success": False, "error": str(e), "snippets": [], "sources": [],
                "titles": [], "truth_score": 50, "total_results": 0}
