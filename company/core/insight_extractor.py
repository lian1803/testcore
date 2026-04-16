"""
insight_extractor.py — 분석 결과에서 실용적 인사이트 추출 및 저장

사용법:
    from core.insight_extractor import extract_and_save, extract_from_report

    # 단건: 분석 직후 자동 호출
    extract_and_save_single(url, analysis)

    # 배치: 보고사항들.md 전체 파싱해서 인사이트 추출
    extract_and_save()

역할:
1. 보고사항들.md에서 최신 분석 섹션 찾기
2. Gemini Flash로 "바로 써먹을 수 있는 인사이트" 추출
3. knowledge/base/insights_*.md 로 카테고리별 저장
4. 중복 방지 (기존 파일에 새 인사이트만 추가)
"""

import os
import re
from pathlib import Path
from datetime import datetime
import json
from dotenv import load_dotenv

# .env 로드 (독립 실행 시에도 API 키 접근 가능)
load_dotenv(Path(__file__).parent.parent / ".env")

import google.genai as genai

from core.models import GEMINI_FLASH

_KNOWLEDGE_BASE_DIR = Path(__file__).parent.parent / "knowledge" / "base"

# 추출할 카테고리 정의
INSIGHT_CATEGORIES = {
    "카피패턴": "마케팅 카피라이팅 패턴, 문구 구조, 감정 유발 기법",
    "콘텐츠구조": "콘텐츠 구성, 레이아웃 패턴, 섹션 순서, 정보 계층",
    "광고자동화": "광고 시스템 운영, 자동화 방법론, 플랫폼 활용 팁",
    "영업전략": "영업 방법론, 고객 접근, 제안 방법, 클로징 기법",
    "시스템설계": "비즈니스 시스템, AI 자동화, 워크플로우, 팀 구조",
}


def categorize_insight(analysis_text: str, category: str, client) -> str:
    """분석 텍스트에서 특정 카테고리의 인사이트 추출.

    Args:
        analysis_text: 분석 결과 전체 텍스트
        category: 추출할 카테고리
        client: Gemini API 클라이언트

    Returns:
        추출된 인사이트 텍스트
    """
    description = INSIGHT_CATEGORIES.get(category, category)

    prompt = f"""다음은 인스타그램/유튜브/마케팅 분석 결과입니다.

[분석 결과]
{analysis_text[:1500]}

[추출 요청]
"{description}" 관점에서만 **바로 써먹을 수 있는 인사이트**를 추출해주세요.

규칙:
- 이론 금지. "~해야 한다" 같은 당위 금지.
- "이 분석에서 {category} 관련 인사이트가 없다"면 빈 문자열로 응답.
- 구체적 행동/기술만: "어떻게 하는지", "무엇을 하는지"
- 마크다운 불릿 또는 짧은 문장으로
- 1-3개 핵심 항목만 (길수록 나쁨)
- 우선순위: 지금 당장 쓸 수 있는 것 → 나중에 배워야 할 것

예:
- "캡션에 숫자 2-3개 포함 시 CTR 30% 상승" ✅
- "영상 길이 15-30초 권장" ✅
- "마케팅은 중요하다" ❌

응답 (인사이트만, 설명 X):
"""

    response = client.models.generate_content(
        model=GEMINI_FLASH,
        contents=prompt
    )

    return response.text.strip()


def extract_and_save_single(url: str, analysis: str):
    """단건 분석 결과 → 인사이트 추출 및 저장.

    분석 직후 자동 호출되도록 설계.
    """
    client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

    insights = {}
    for category in INSIGHT_CATEGORIES:
        insight = categorize_insight(analysis, category, client)
        if insight:
            insights[category] = insight

    if not insights:
        # 추출된 인사이트 없음
        return

    # knowledge/base/insights_*.md 에 저장
    for category, insight_text in insights.items():
        save_insight(category, insight_text, source_url=url)

    print(f"[인사이트] {url} → {len(insights)}개 카테고리 저장됨")


def save_insight(category: str, insight_text: str, source_url: str = ""):
    """인사이트를 knowledge/base/insights_{카테고리}.md 에 저장.

    기존 파일이 있으면 중복 제거하고 새로운 것만 추가.
    """
    insight_file = _KNOWLEDGE_BASE_DIR / f"insights_{category}.md"

    # 파일 없으면 생성
    if not insight_file.exists():
        _KNOWLEDGE_BASE_DIR.mkdir(parents=True, exist_ok=True)
        header = f"# {category} 인사이트 모음\n\n기획·개발·마케팅 과정에서 실제로 적용한 기법들\n\n"
        with open(insight_file, "w", encoding="utf-8") as f:
            f.write(header)

    # 기존 내용 읽기
    with open(insight_file, "r", encoding="utf-8") as f:
        existing = f.read()

    # 중복 체크: insight_text가 이미 있으면 스킵
    if insight_text in existing:
        return

    # 새 항목 추가
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    source = f"(출처: {source_url})" if source_url else ""

    entry = f"\n## {timestamp} {source}\n{insight_text}\n"

    with open(insight_file, "a", encoding="utf-8") as f:
        f.write(entry)


def _extract_analysis_sections(content: str) -> list[tuple[str, str]]:
    """보고사항들.md에서 인스타 분석 섹션 파싱.

    지원 형식:
    - ## [인스타 분석] 제목 — 날짜
    - ## 인스타 분석 N/M — 날짜

    각 섹션은:
    **URL**: (Instagram URL)
    **내용**: (설명)
    **분석**:
    (분석 내용)
    ---

    Returns:
        [(url, analysis_text), ...] 리스트. 빈 리스트면 섹션 없음.
    """
    sections = []

    # 헤더 패턴: "## [인스타 분석]" 또는 "## 인스타 분석" 변형
    # re.DOTALL: . 이 개행 문자도 매칭 (섹션 여러 줄 캡처용)
    pattern_header = r"^## (?:\[)?인스타 분석(?:\])?[^\n]*\n(.*?)(?=^##|\Z)"
    for match in re.finditer(pattern_header, content, re.MULTILINE | re.DOTALL):
        section_content = match.group(1)

        # 1단계: 섹션 내에서 URL 찾기
        url_pattern = r"\*\*URL\*\*:\s*(https://www\.instagram\.com/\S+)"
        url_match = re.search(url_pattern, section_content)
        if not url_match:
            continue  # URL 없으면 이 섹션 스킵

        url = url_match.group(1)

        # 2단계: "**분석**:" 또는 "**분석**" 찾기
        analysis_start_idx = section_content.find("**분석**:")
        if analysis_start_idx == -1:
            # "**분석**:" 형식이 아니라면 "**분석**" 만 찾기
            analysis_start_idx = section_content.find("**분석**")
            if analysis_start_idx == -1:
                continue  # 분석 섹션 없음

            # "**분석**" 다음 줄부터 시작
            analysis_start_idx = section_content.find("\n", analysis_start_idx)
            if analysis_start_idx == -1:
                continue
        else:
            # "**분석**:" 찾음 → 콜론 다음부터 시작
            analysis_start_idx += len("**분석**:")

        # 3단계: 분석 내용 끝 지점 찾기 ("---" 또는 파일 끝)
        remaining = section_content[analysis_start_idx:]
        end_idx = remaining.find("---")
        analysis = remaining if end_idx == -1 else remaining[:end_idx]

        analysis = analysis.strip()
        if analysis:  # 공백 아닌 분석만 추가
            sections.append((url, analysis))

    return sections


def extract_and_save():
    """보고사항들.md 전체 파싱 → 모든 분석 결과에서 인사이트 추출.

    배치 작업용. 대량 분석 후 한 번에 지식화.
    """
    report_path = Path(__file__).parent.parent.parent / "보고사항들.md"
    if not report_path.exists():
        print("⚠️  보고사항들.md 없음")
        return

    # 보고사항들.md에서 분석 섹션 파싱
    with open(report_path, "r", encoding="utf-8", errors="replace") as f:
        content = f.read()

    # 분석 섹션 추출
    sections = _extract_analysis_sections(content)

    if not sections:
        print("[배치 완료] 분석 섹션 0개 (또는 파싱 실패)")
        return

    client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
    total_insights = 0

    for url, analysis in sections:
        insights = {}
        for category in INSIGHT_CATEGORIES:
            insight = categorize_insight(analysis, category, client)
            if insight:
                insights[category] = insight
                save_insight(category, insight, source_url=url)

        total_insights += len(insights)

    print(f"[배치 완료] {len(sections)}개 분석에서 {total_insights}개 인사이트 추출 및 저장됨")


def get_latest_insights(category: str, limit: int = 5) -> list[str]:
    """특정 카테고리의 최신 인사이트 몇 개 가져오기.

    팀 지식 주입 시 사용.
    """
    insight_file = _KNOWLEDGE_BASE_DIR / f"insights_{category}.md"
    if not insight_file.exists():
        return []

    try:
        with open(insight_file, "r", encoding="utf-8") as f:
            content = f.read()

        # ## 로 시작하는 섹션들 추출
        sections = re.split(r"^## ", content, flags=re.MULTILINE)[1:]
        return [s.strip() for s in sections[-limit:]]
    except Exception as e:
        print(f"⚠️  {category} 인사이트 읽기 실패: {e}")
        return []
