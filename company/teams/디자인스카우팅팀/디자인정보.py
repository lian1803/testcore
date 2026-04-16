"""
디자인정보 — Design Scouting Team Leader & Report Generator
Orchestrates all scouts and generates weekly design briefing
"""

import json
import os
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

try:
    from anthropic import Anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False


class DesignBriefingGenerator:
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.api_key = os.getenv("ANTHROPIC_API_KEY")
        self.client = Anthropic(api_key=self.api_key) if ANTHROPIC_AVAILABLE else None
        self.timestamp = datetime.now()
        self.date_str = self.timestamp.strftime("%Y-%m-%d")

        if not self.api_key:
            print("[WARNING] ANTHROPIC_API_KEY not found in .env")

    def load_scout_results(self):
        """Load results from all scouts"""
        results = {
            "awwwards": None,
            "trends": None,
            "repo": None
        }

        # Load awwwards
        aww_file = self.base_dir / "awwwards_results.json"
        if aww_file.exists():
            with open(aww_file, "r", encoding="utf-8") as f:
                results["awwwards"] = json.load(f)

        # Load trends
        trend_file = self.base_dir / "trends_results.json"
        if trend_file.exists():
            with open(trend_file, "r", encoding="utf-8") as f:
                results["trends"] = json.load(f)

        # Load repo scan
        repo_file = self.base_dir / "repo_results.json"
        if repo_file.exists():
            with open(repo_file, "r", encoding="utf-8") as f:
                results["repo"] = json.load(f)

        return results

    def _extract_gemini_insights(self, awwwards_data: list) -> str:
        """박어워즈 Gemini 분석 결과를 텍스트로 정리"""
        insights = []
        for site in awwwards_data:
            analysis = site.get("gemini_analysis", {})
            if not analysis:
                continue
            name = site.get("name", "Unknown")
            effects = ", ".join(analysis.get("effects", []))
            colors = ", ".join(analysis.get("color_palette", []))
            steal = analysis.get("steal_this", [])
            steal_text = " / ".join(steal[:3]) if steal else ""
            insights.append(f"- **{name}**: 효과=[{effects}] 색상=[{colors}] 훔칠것=[{steal_text}]")
        return "\n".join(insights) if insights else "(Gemini 분석 없음)"

    def generate_briefing_with_claude(self, scout_data: dict) -> str:
        """Use Claude to generate polished briefing"""
        if not self.client or not ANTHROPIC_AVAILABLE:
            print("[WARNING] Claude API unavailable, using template briefing")
            return self._generate_template_briefing(scout_data)

        awwwards_data = scout_data.get('awwwards', []) or []
        gemini_insights = self._extract_gemini_insights(awwwards_data)

        try:
            prompt = f"""
당신은 디자인 트렌드 전문가입니다. 다음 데이터를 바탕으로 한국 B2B 기업을 위한 주간 디자인 트렌드 브리핑을 작성하세요.

# 수집된 데이터

## 레퍼런스 사이트 (박어워즈 + Godly)
{json.dumps(awwwards_data[:4], ensure_ascii=False, indent=2)}

## Gemini Vision 분석 결과 (효과/색상/훔칠것)
{gemini_insights}

## 웹 디자인 트렌드 (서트렌드)
{json.dumps(scout_data.get('trends', {}).get('trends', []), ensure_ascii=False, indent=2)}

## 추천 효과 (김레포)
{json.dumps(scout_data.get('repo', {}).get('recommendations', []), ensure_ascii=False, indent=2)}

# 작성 규칙
- 각 섹션은 3-4문장으로 간결하게
- 실무 팀(Claude 개발팀)이 다음 프로젝트에 즉시 적용 가능한 조언 포함
- Gemini Vision이 발견한 효과/색상/훔칠것을 구체적으로 언급할 것
- 한국 B2B/기업 마케팅 관점에서 쓸 것
- 마크다운 형식 사용

이 형식으로 작성:
# 디자인 스카우팅 브리핑 — {self.date_str}

## 🌐 이번 주 웹 트렌드 TOP 5
[트렌드 5개 + 설명]

## 🏆 레퍼런스 사이트 (Awwwards + Godly)
[사이트 4개 + 무엇이 좋은지 + Gemini가 발견한 효과/색상]

## 🎨 바로 훔칠 수 있는 것들
[Gemini 분석 기반 — 사이트별 훔칠 것 3가지씩]

## 💡 Claude에게 추천
[다음 프로젝트에 어떤 조합으로 쓸지 구체적 제안]
"""

            message = self.client.messages.create(
                model="claude-haiku-4-5-20251001",
                max_tokens=1500,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            return message.content[0].text

        except Exception as e:
            print(f"[ERROR] Claude API error: {e}")
            return self._generate_template_briefing(scout_data)

    def _generate_template_briefing(self, scout_data: dict) -> str:
        """Fallback template briefing"""
        briefing = f"""# Design Scouting Briefing — {self.date_str}

## Top 5 Web Design Trends This Week
"""
        # Add trends if available
        if scout_data.get("trends"):
            for i, trend in enumerate(scout_data["trends"].get("trends", [])[:5], 1):
                briefing += f"\n{i}. **{trend['query'][:40]}...**\n   {trend['result'][:200]}...\n"
        else:
            briefing += "\n(Data collection pending)\n"

        briefing += "\n## Reference Sites\n"
        if scout_data.get("awwwards"):
            for site in scout_data["awwwards"][:3]:
                briefing += f"\n- **{site.get('name', 'Unknown')}** - {site.get('title', 'N/A')}\n  {site.get('description', 'N/A')}\n"
        else:
            briefing += "\n(Data collection pending)\n"

        briefing += "\n## Underused Effects\n"
        if scout_data.get("repo"):
            for rec in scout_data["repo"].get("recommendations", [])[:3]:
                briefing += f"\n- **{rec.get('name', 'Unknown')}** ({rec.get('type', 'N/A')})\n  {rec.get('description', 'N/A')}\n"
        else:
            briefing += "\n(Data collection pending)\n"

        briefing += "\n## Recommendation for Next Project\n\nTry combining the recommended effects for your next project. GLSL shader backgrounds with TextAnimation effects create a modern design system.\n"

        return briefing

    def write_to_report(self, briefing: str):
        """Append briefing to 보고사항들.md"""
        report_path = Path(__file__).parent.parent.parent / "보고사항들.md"

        content = f"\n\n---\n\n## Design Scouting Briefing ({self.date_str})\n\n{briefing}\n\n**Collected by**: Design Scouting Team (Award Sites, Trend Researcher, Repo Scanner, Design Info)\n**Generated at**: {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}\n"

        try:
            if report_path.exists():
                with open(report_path, "a", encoding="utf-8") as f:
                    f.write(content)
            else:
                with open(report_path, "w", encoding="utf-8") as f:
                    f.write("# Reports\n")
                    f.write(content)

            print(f"[SUCCESS] Report saved: {report_path}")
        except Exception as e:
            print(f"[ERROR] Report save failed: {e}")

    def save_briefing(self, briefing: str):
        """Save briefing to local file"""
        briefing_file = self.base_dir / f"briefing_{self.date_str}.md"

        with open(briefing_file, "w", encoding="utf-8") as f:
            f.write(briefing)

        print(f"[SUCCESS] Briefing saved: {briefing_file}")

    def run(self):
        """Execute briefing generation"""
        print("[START] Design info briefing generation starting...")

        # Load scout results
        scout_data = self.load_scout_results()

        # Generate briefing
        print("  [AI] Generating briefing with Claude...")
        briefing = self.generate_briefing_with_claude(scout_data)

        # Save locally
        self.save_briefing(briefing)

        # Append to main report
        self.write_to_report(briefing)

        print(f"\n[SUCCESS] Design info briefing completed")
        return briefing


if __name__ == "__main__":
    generator = DesignBriefingGenerator()
    generator.run()
