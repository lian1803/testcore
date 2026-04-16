"""
서트렌드 — Perplexity Trend Researcher
Searches for current web design trends and insights
"""

import os
import json
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False


class TrendResearcher:
    def __init__(self):
        self.api_key = os.getenv("PERPLEXITY_API_KEY")
        self.base_dir = Path(__file__).parent
        self.results = {
            "trends": [],
            "timestamp": datetime.now().isoformat()
        }

        if not self.api_key:
            print("[WARNING] PERPLEXITY_API_KEY not found in .env")

    def search_trend(self, query: str) -> str:
        """Search for trend using Perplexity API"""
        if not REQUESTS_AVAILABLE or not self.api_key:
            return f"(Skipped: {query})"

        try:
            url = "https://api.perplexity.ai/chat/completions"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": "sonar",
                "messages": [
                    {
                        "role": "user",
                        "content": f"{query}\n\nProvide 3-5 specific, actionable trends with examples."
                    }
                ],
                "temperature": 0.7,
                "max_tokens": 500
            }

            response = requests.post(url, headers=headers, json=payload, timeout=30)

            if response.status_code == 200:
                result = response.json()
                return result["choices"][0]["message"]["content"]
            else:
                return f"API Error: {response.status_code}"

        except Exception as e:
            return f"Error: {str(e)}"

    def run(self):
        """Execute trend research"""
        print("[START] Trend researcher starting...")

        queries = [
            "What are the top web design trends for 2025?",
            "Best practices for SaaS landing page design 2025",
            "Korean B2B agency website design trends 2025"
        ]

        for i, query in enumerate(queries, 1):
            print(f"\n[RESEARCH] Trend {i}/3: {query[:50]}...")
            result = self.search_trend(query)

            self.results["trends"].append({
                "query": query,
                "result": result,
                "fetched_at": datetime.now().isoformat()
            })

            print(f"  [SUCCESS] Got response ({len(result)} chars)")

        # Save results
        results_file = self.base_dir / "trends_results.json"
        with open(results_file, "w", encoding="utf-8") as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2)

        print(f"\n[SUCCESS] Trend researcher completed: {len(self.results['trends'])} trends collected")
        return self.results


if __name__ == "__main__":
    researcher = TrendResearcher()
    researcher.run()
