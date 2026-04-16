"""
ops_loop.py — Layer 4: 운영 루프

배포 후 매일/매주 돌아가는 자동 루프.
콘텐츠 생성 + 영업 메시지 + 성과 추적.

사용법:
    python -m core.ops_loop daily "프로젝트명"   # 매일 루프
    python -m core.ops_loop weekly "프로젝트명"  # 매주 루프

또는 코드에서:
    from core.ops_loop import daily_loop, weekly_loop
"""
import os
import sys
import requests
import anthropic
from datetime import datetime
from dotenv import load_dotenv
from core.context_loader import inject_context
from core.research_loop import research_before_task
from core.models import CLAUDE_SONNET
from core.self_improve import post_run_review
from core.auto_publish import PublishQueue, PublishChannel, PublishStatus, publish_all

load_dotenv()


def _send_discord(title: str, content: str):
    """디스코드 웹훅으로 알림 전송."""
    webhook_url = os.getenv("DISCORD_WEBHOOK_URL")
    if not webhook_url:
        return
    try:
        # 디스코드 메시지 2000자 제한 — 요약본만 전송
        summary = content[:1500].strip()
        if len(content) > 1500:
            summary += "\n\n... (전체 내용은 보고사항들.md 확인)"
        payload = {
            "embeds": [{
                "title": f"📋 {title}",
                "description": summary,
                "color": 0x5865F2,
                "footer": {"text": datetime.now().strftime("%Y-%m-%d %H:%M")}
            }]
        }
        requests.post(webhook_url, json=payload, timeout=10)
    except Exception as e:
        print(f"[디스코드 알림 실패] {e}")

MODEL = CLAUDE_SONNET
REPORT_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "보고사항들.md")
TEMPLATES_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "knowledge", "ops_templates")


def _get_client():
    return anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


def _load_competitor_patterns(max_entries: int = 5) -> str:
    """경쟁사패턴_DB.md에서 최근 패턴 로드. daily_loop 콘텐츠 생성 컨텍스트로 주입."""
    db_path = os.path.join(TEMPLATES_DIR, "marketing", "경쟁사패턴_DB.md")
    if not os.path.exists(db_path):
        return ""
    try:
        with open(db_path, encoding="utf-8") as f:
            content = f.read()
        # 최근 N개 항목만 (## 단위로 분할)
        sections = [s.strip() for s in content.split("## ") if s.strip() and not s.startswith("---") and not s.startswith("name:")]
        recent = sections[-max_entries:] if len(sections) > max_entries else sections
        if not recent:
            return ""
        return "## 경쟁사 최신 패턴 (참고용)\n\n" + "\n\n---\n\n".join(["## " + s for s in recent])
    except Exception:
        return ""


def _load_template(template_path: str) -> dict:
    """ops_templates/에서 템플릿 로드. frontmatter + 본문 + 채점기준 분리.

    Returns:
        {"prompt": str, "scoring": str, "metadata": dict}
    """
    import json
    import re

    full_path = os.path.join(TEMPLATES_DIR, template_path)
    if not os.path.exists(full_path):
        print(f"⚠️ 템플릿 파일 없음: {template_path}")
        return {"prompt": "", "scoring": "", "metadata": {}}

    with open(full_path, encoding="utf-8") as f:
        content = f.read()

    # --- frontmatter --- 분리
    frontmatter_match = re.match(r'^---\n(.*?)\n---\n', content, re.DOTALL)
    metadata = {}
    main_content = content

    if frontmatter_match:
        frontmatter_text = frontmatter_match.group(1)
        main_content = content[frontmatter_match.end():]

        # YAML 파싱 (간단한 버전)
        for line in frontmatter_text.split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                metadata[key.strip()] = value.strip().strip('"\'')

    # ## 채점 기준 섹션 분리
    scoring_match = re.search(r'## 채점 기준\n(.*?)(?=\n## |\Z)', main_content, re.DOTALL)
    scoring = ""
    prompt = main_content

    if scoring_match:
        scoring = scoring_match.group(1).strip()
        prompt = main_content[:scoring_match.start()] + main_content[scoring_match.end():]

    return {
        "prompt": prompt.strip(),
        "scoring": scoring.strip(),
        "metadata": metadata
    }


def _load_template_index() -> dict:
    """ops_templates/_index.json 로드."""
    index_path = os.path.join(TEMPLATES_DIR, "_index.json")
    if os.path.exists(index_path):
        try:
            import json
            with open(index_path, encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"templates": [], "metadata": {}}


def _get_daily_hook_pattern() -> str:
    """요일별 훅 패턴 자동 선택 (hook_library.md 기반)."""
    from datetime import datetime

    hook_map = {
        0: "숫자/계산유도형",      # 월요일: 주간 시작 에너지
        1: "팁/노하우형",          # 화요일: 학습욕
        2: "공감+질문형",          # 수요일: 중간점검
        3: "숫자/계산유도형",      # 목요일: 기대감
        4: "논쟁/대립형",          # 금요일: 회복욕
        5: "비밀공개형",           # 토요일: 가치감
        6: "결과먼저형",           # 일요일: 영감
    }

    today = datetime.now().weekday()
    pattern = hook_map.get(today, "숫자/계산유도형")
    print(f"  📅 오늘의 훅 패턴: {pattern}")
    return pattern


def _save_to_report(title: str, content: str):
    """보고사항들.md에 추가."""
    date_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    entry = f"\n\n## {title} — {date_str}\n\n{content}\n\n---\n"
    try:
        existing = ""
        if os.path.exists(REPORT_PATH):
            with open(REPORT_PATH, encoding="utf-8") as f:
                existing = f.read()
        if "---" in existing:
            parts = existing.split("---", 1)
            new_content = parts[0] + "---\n" + entry + parts[1]
        else:
            new_content = existing + entry
        with open(REPORT_PATH, "w", encoding="utf-8") as f:
            f.write(new_content)
    except Exception as e:
        print(f"⚠️ 보고서 저장 실패: {e}")


def _load_project_context(project_name: str) -> str:
    """프로젝트 폴더에서 컨텍스트 로드."""
    team_root = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "team")
    # 프로젝트 폴더 찾기
    for folder in os.listdir(team_root):
        if project_name.lower() in folder.lower():
            project_dir = os.path.join(team_root, folder)
            context_parts = []
            for fname in ["CLAUDE.md", "PRD.md", "런칭준비.md"]:
                fpath = os.path.join(project_dir, fname)
                if os.path.exists(fpath):
                    with open(fpath, encoding="utf-8") as f:
                        context_parts.append(f.read()[:1000])
            return "\n\n".join(context_parts)
    return ""


def _load_ops_config(project_name: str) -> dict:
    """ops_config.json 또는 marketing_config.json에서 프로젝트 설정 로드.

    우선순위: ops_config.json > marketing_config.json (하위호환)
    """
    import json

    # 1. ops_config.json 시도
    ops_config_path = os.path.join(os.path.dirname(__file__), "ops_config.json")
    if os.path.exists(ops_config_path):
        try:
            with open(ops_config_path, encoding="utf-8") as f:
                config = json.load(f)
            for proj_key, proj_config in config.get("projects", {}).items():
                if project_name.lower() in proj_key.lower() or proj_key.lower() in project_name.lower():
                    if proj_config.get("status") == "active":
                        return proj_config
        except Exception:
            pass

    # 2. marketing_config.json 폴백 (기존 호환성)
    return _load_marketing_config(project_name)


def _load_marketing_config(project_name: str) -> dict:
    """marketing_config.json에서 프로젝트 채널 설정 로드 (폴백용)."""
    config_path = os.path.join(os.path.dirname(__file__), "marketing_config.json")
    if not os.path.exists(config_path):
        return {}
    try:
        import json
        with open(config_path, encoding="utf-8") as f:
            config = json.load(f)
        for proj_key, proj_config in config.get("projects", {}).items():
            if project_name.lower() in proj_key.lower() or proj_key.lower() in project_name.lower():
                if proj_config.get("status") == "active":
                    return proj_config
    except Exception:
        pass
    return {}


# ── 매일 루프 ──────────────────────────────────────────────────

# DEPRECATED: 이제 knowledge/ops_templates/general/범용_콘텐츠.md에서 로드됨
# DAILY_CONTENT_PROMPT는 _get_generic_content_prompt()로 대체됨

# DEPRECATED: 이제 knowledge/ops_templates/에서 .md 파일로 로드됨
# 레거시 호환성을 위해 유지하지만, 새 코드는 _get_template_prompt() 사용
# 채널별 전용 프롬프트 (전문가 수준 2026-04)
_LEGACY_CHANNEL_PROMPTS = {
    "인스타": """너는 '인스타그램 셀러 마케팅' 전문가다. (참고: hook_library.md 최신 훅 패턴)

오늘의 인스타그램 콘텐츠를 마케팅 대행사 시니어 수준(8.5/10)으로 만들어줘.

톤: {tone} | 포맷: {format} | 해시태그 기반: {hashtags}

AIDA 구조 필수:
1. **Attention (훅 — 3초)**:
   - 충격적 질문 / 숫자 / 반전 중 하나로 "멈추게" 하기
   - 예: "GA4 30분 + 메타 20분 = 월 28시간 낭비?"

2. **Interest (본문 — 3~5줄)**:
   - 공감 문구 + 구체적 해결책 + 증거(숫자/사례)
   - 문장길이 변동: 짧은 문장 40% + 긴 문장 40% + 질문 20%
   - 저장 유도 문구 포함 ("이거 나중에 필요할 것 같으니 저장해두세요")

3. **Desire (사회적 증명)**:
   - "1,200+ 마케터" / "월 4.7시간 절약" 같은 구체적 수치
   - 고객 후기 1줄 (실명, 구체적 변화)

4. **Action (CTA)**:
   - 구체적 행동: "링크인바이오에서 무료 14일 체험"
   - 긴급성 + 희소성: "선착순 10명", "오늘까지만"

해시태그 전략 (SEO + 노출):
- 대형 해시태그(팔로우 100만+): 3개
- 중형 해시태그(팔로우 10만+): 7개
- 소형 해시태그(팔로우 1만+): 5개
- 브랜드/고유: 3개
총 18개 (인스타 25개 제한 내)

복붙 가능한 완성본. 이모지 적절히 활용.""",

    "블로그": """너는 네이버 블로그 '콘텐츠 랭킹(C-Rank)' 최적화 전문가다.

오늘의 블로그 포스트를 마케팅 대행사 수준으로 만들어줘.

SEO 키워드: {keywords} | 포맷: {format}

## 네이버 블로그 상위노출 공식 (C-Rank + DIA 적용)

**제목 (20~30자)**:
- 키워드 + 지역/목적 + 연도/숫자
- 예: "2025년 인스타 마케팅 SEO 최적화 완전가이드"
- 클릭유도 제목 금지 (네이버 패널티)

**도입부 (100~150자, 공감 우선)**:
- 독자의 고통/상황 구체적 묘사 (3줄)
- "이 글을 읽으면 뭘 해결할 수 있나" 예고
- 개인적 관찰/날짜 삽입 (AI 탐지 회피)
- 예: "2025년 3월, 우리 팀이 처음 GA4를 다시 본지..."

**본문 구조 (1,500~3,000자)**:
- **H2 소제목 4~5개** (매 200~300자마다)
- 각 소제목 후 **이미지 1개** (ALT: 키워드 + 설명)
- 소제목 당 핵심 1개 + 구체적 사례 1개 + 액션 1개
- 문체 다양화: 문장길이 변동, 동의어 교체, 1인칭 경험 삽입
- 리스트 최소화 (50% 이하), 스토리 흐름 우선

**출력 형식**:
---
## 제목: [SEO 최적화 제목]

## H2 소제목 1: [구체적 주제]
[도입 공감 문장]
[구체적 설명 + 데이터]
[개인 경험 또는 사례]
[액션 아이템 1개]

[이미지 ALT: "키워드 + 설명"]

## H2 소제목 2: [다른 각도]
[비슷 패턴 반복...]

...

## 마무리: [액션 + CTA]
- 이 글에서 배운 3가지 실행 항목
- [제품/서비스] 무료 상담 링크
---

AI 탐지 회피:
- 반복 단어 금지 (동의어 5종 로테이션)
- 개인 경험 70% 이상 (AI 초안 30% 이하)
- 질문/감탄문 자연스럽게 분산
- 완성 후 반드시 인간이 편집
""",

    "유튜브": """너는 유튜브 '쇼츠 바이럴' 콘텐츠 제작 전문가다.

오늘의 유튜브 숏폼(15~60초) 스크립트를 만들어줘.

톤: {tone} | 포맷: {format}

## 유튜브 쇼츠 필승 공식

**0-3초 훅 (필수)**:
- 트렌드 오디오 또는 시각적 충격
- 텍스트 오버레이: "이 기법으로 -5kg", "GA4 대시보드 30초", "월 1천만원 된 비결"
- 최고 중요: 이 3초가 완전시청률 80% 결정

**3-30초 본론 (핵심)**:
- 문제 제시 → 해결책 → 결과 구조
- 언어: 구어체 + 감정 표현 풍부
- 효과: 텍스트 오버레이 + 음성 나레이션 동시
- 비주얼: 전후 비교 / 데이터 시각화 / 실제 결과물

**25-60초 CTA**:
- "링크 바이오 클릭" 또는 "댓글로 공유해봐요"
- 긴급성 강조: "오늘까지만", "선착순"
- 음성 + 텍스트 동시

**자막 (필수)**:
- 90% 이상 시청자가 음소거로 봄 → 자막 거의 모든 정보 포함
- 가독성: 노란색/흰색, 큰 폰트, 3초당 1~2줄

**완성본 형식**:
---
[0-3초]
🔥 팔로우 0에서 3개월 만에 무료 체험 200명

[3-30초]
(자막 전체, 음성나레이션 스크립트)

[25-60초]
🎯 CTA 오버레이 + 음성
---

**효과 지표**: 완전시청률 90%+ 목표, 공유율 최소 2배""",

    "네이버카페": """너는 네이버 커뮤니티 '신뢰 콘텐츠' 작성 전문가다.

오늘의 네이버 카페 포스팅을 마케팅 대행사 수준으로 만들어줘.

키워드: {keywords}

## 네이버 카페 고성과 공식

**제목 (광고처럼 안 보이게)**:
- 일반형: "[팁] 2025년 인스타 마케팅 3가지 트렌드"
- 질문형: "혹시 인스타도 GA4 연동하고 계신가요?"
- 경험형: "강남 카페 6개월 경영해보니 알게 된 것"

**본문 구조 (1,000~1,500자)**:
- **도입**: 친근한 인사 + 문제 제기 (100자)
- **정보성**: 구체적 팁 3~5개 (800자)
  - 각 팁마다 "왜 효과적인가" 설명
  - 숫자/사례 포함 (신뢰도↑)
- **마무리**: 개인 의견 + 질문 유도 (100자)
  - "혹시 다르게 하시는 분 있나요?" (댓글 유도)

**광고 금지 원칙**:
- 상품명 언급 NO (블로그 URL 링크 자연스럽게)
- 가격 정보 NO
- 과장 금지 ("무조건", "100% 효과" 피함)
- 구매 강요 NO

**신뢰도 극대화**:
- 실명 또는 스토리(개인 경험) 삽입
- 구체적 수치 (감으로 말하지 말기)
- 정보 출처 명시 (크레딧)
- 실패 경험도 솔직하게

**완성본 형식**:
---
## 제목: [광고 아닌 정보성]

안녕하세요. [소개]입니다.

[상황 또는 문제 제기]

## 실제 했던 것:
1. [팁] - [이유 + 효과]
2. [팁] - [이유 + 효과]
3. [팁] - [이유 + 효과]

혹시 다르게 하시는 분 있나요?
(관련 블로그 자연스럽게 링크)
---
""",

    "메타광고": """너는 '메타(Facebook/Instagram) 광고' 성과 최적화 전문가다.

오늘의 메타 광고 크리에이티브를 마케팅 대행사 수준으로 만들어줘.

톤: {tone} | 타겟: {target_persona}

## Meta 광고 AIDA 크리에이티브 공식

**헤드라인 3가지 버전 (각 40자 이내)**:
1. 숫자형: "80% OFF? 오늘까지만 🔥"
2. 질문형: "아직도 엑셀로 데이터 관리하세요?"
3. 결과형: "월 1천만원 달성 가능한 이유"

**본문 (125자 이내, AIDA 순서)**:
- A(훅): 1줄 — 문제/충격/혜택 중 하나
- I(흥미): 2줄 — 솔루션 + 증거(숫자/UGC)
- D(욕망): 1줄 — 사회적 증명
- A(행동): 긴급성/희소성

**예시**:
"피부 고민? 7일 만에 맑아짐.
10만 리뷰 인증!
지금 구매 GO 💥"

(125자 정확히 맞추기)

**CTA 버튼 선택**:
- 상품 판매: "지금 구매" / "쇼핑하기"
- 리드: "연락처 등록" / "무료 상담"
- 방문: "링크 클릭" / "자세히 보기"
- 다운로드: "앱 설치" / "PDF 받기"

**타겟 설정 제안**:
- 관심사: [관련 상품/서비스 + 라이프스타일]
- 행동: [구매 경험자 / 페이지 방문자]
- 데모그래픽: [성별/연령/지역]
- Lookalike: 기존 고객 1% 오디언스

**완성본 형식**:
---
## 헤드라인:
1️⃣ "80% OFF? 오늘까지만 🔥"
2️⃣ "아직도 엑셀로 데이터 관리하세요?"
3️⃣ "월 1천만원 달성 가능한 이유"

## 본문 (A/B 2버전):
V1: "피부 고민? 7일 만에 맑아짐. 10만 리뷰 인증! 지금 구매 GO 💥"
V2: "운동 싫어? 10분 홈트로 -5kg. 실제 후기로 증명. 지금 신청하기"

## CTA: "지금 구매" / "무료 상담"

## 타겟: [구체적 페르소나 기반]
---
""",
}


def _get_template_prompt(channel_name: str, config: dict = None) -> tuple[str, str]:
    """채널별 템플릿 프롬프트 로드 (새로운 방식).

    Returns:
        (prompt, scoring_prompt)
    """
    # 1. 템플릿 인덱스에서 매칭되는 템플릿 찾기
    index = _load_template_index()
    template_meta = None

    for tmpl in index.get("templates", []):
        if channel_name in tmpl.get("channels", []):
            template_meta = tmpl
            break

    # 2. 찾지 못하면 기본값으로 인스타 사용
    if not template_meta:
        print(f"⚠️ 템플릿 '{channel_name}' 없음, 기본값(인스타) 사용")
        template_meta = {"path": "marketing/인스타_캐러셀.md"}

    # 3. 템플릿 파일 로드
    template_data = _load_template(template_meta["path"])
    prompt = template_data["prompt"]
    scoring = template_data["scoring"]

    # 4. 포맷 변수 대체 (config가 있으면)
    if config:
        try:
            prompt = prompt.format(
                tone=config.get("tone", "전문적+친근"),
                format=config.get("format", "캐러셀"),
                hashtags=", ".join(config.get("hashtags_base", [])),
                keywords=", ".join(config.get("keywords", [])),
                target_persona=config.get("target_persona", ""),
            )
        except KeyError:
            pass  # 포맷 변수가 없으면 그냥 사용

    return prompt, scoring


def _get_generic_content_prompt() -> tuple[str, str]:
    """범용 콘텐츠 프롬프트 로드 (마케팅 설정이 없을 때).

    Returns:
        (prompt, None) — 범용은 채점기준이 필요 없음
    """
    template_data = _load_template("general/범용_콘텐츠.md")
    return template_data["prompt"], template_data["scoring"]


def _queue_contents_for_publish(content_response: str, marketing_config: dict):
    """생성된 콘텐츠를 발행 큐에 추가."""
    queue = PublishQueue()

    # 간단한 파싱: 각 채널별 섹션 분리
    # 실제로는 더 정교한 파싱이 필요할 수 있음
    sections = content_response.split("##")

    for section in sections:
        section = section.strip()
        if not section:
            continue

        lines = section.split("\n")
        section_title = lines[0].strip() if lines else ""

        # 채널명 감지
        if "인스타" in section_title:
            # 캡션 추출
            caption_lines = [l for l in lines[1:] if l.strip() and not l.startswith("#")]
            caption = "\n".join(caption_lines)
            if caption:
                queue.add_instagram(caption=caption)
                print(f"  ✓ 인스타 콘텐츠 큐에 추가")

        elif "블로그" in section_title:
            # 제목과 본문 추출
            content = "\n".join(lines[1:])
            if "제목:" in content:
                try:
                    title_start = content.find("제목:") + len("제목:")
                    title_end = content.find("\n", title_start)
                    title = content[title_start:title_end].strip()
                    body = content[title_end:].strip()
                    queue.add_blog(title=title, body=body)
                    print(f"  ✓ 블로그 콘텐츠 큐에 추가: {title}")
                except:
                    pass

        elif "카카오" in section_title or "DM" in section_title or "영업" in section_title:
            # 메시지 추출
            msg_lines = [l for l in lines[1:] if l.strip() and not l.startswith("#")]
            message = "\n".join(msg_lines)
            if message:
                queue.add_kakao(message=message)
                print(f"  ✓ 카카오톡 메시지 큐에 추가")


def _build_task_prompt(task: dict, project_info: dict) -> tuple[str, str]:
    """태스크 설정 기반으로 프롬프트 구성 (새로운 방식).

    Returns:
        (prompt, scoring_prompt)
    """
    template_path = task.get("template", "marketing/인스타_캐러셀.md")
    template_data = _load_template(template_path)
    prompt = template_data["prompt"]
    scoring = template_data["scoring"]

    # 포맷 변수 대체
    try:
        prompt = prompt.format(
            tone=task.get("config", {}).get("tone", "전문적+친근"),
            format=task.get("config", {}).get("format", "캐러셀"),
            hashtags=", ".join(task.get("config", {}).get("hashtags_base", [])),
            keywords=", ".join(task.get("config", {}).get("keywords", [])),
            target_persona=project_info.get("target_persona", ""),
        )
    except KeyError:
        pass

    return prompt, scoring


def _build_channel_prompt(channel: dict, project_info: dict) -> str:
    """태스크 설정 기반으로 프롬프트 구성. template 필드 우선, 없으면 이름으로 매칭."""
    # 1. template 필드가 있으면 직접 로드 (ops_config 방식)
    template_path = channel.get("template")
    if template_path:
        template_data = _load_template(template_path)
        prompt = template_data["prompt"]
        config = channel.get("config", channel)
        try:
            prompt = prompt.format(
                tone=config.get("tone", "전문적+친근"),
                format=config.get("format", "캐러셀"),
                hashtags=", ".join(config.get("hashtags_base", config.get("hashtags", []))),
                keywords=", ".join(config.get("keywords", [])),
                target_persona=project_info.get("target_persona", ""),
            )
        except (KeyError, IndexError):
            pass
        return prompt

    # 2. 폴백: 채널 이름으로 인덱스 매칭 (기존 방식)
    channel_name = channel.get("name", "인스타")
    prompt, _ = _get_template_prompt(channel_name, channel)
    return prompt


def daily_loop(project_name: str, auto_publish_mode: bool = False):
    """매일 콘텐츠 생성 루프.

    Args:
        project_name: 프로젝트명
        auto_publish_mode: True면 자동 발행, False면 큐에만 저장
    """
    client = _get_client()
    print(f"\n{'='*60}")
    print(f"📅 매일 운영 루프: {project_name}")
    print(f"{'='*60}")

    project_context = _load_project_context(project_name)
    marketing_config = _load_ops_config(project_name)

    # 태스크/채널별 맞춤 생성 vs 범용 생성
    tasks = marketing_config.get("tasks") or marketing_config.get("channels") or []
    if marketing_config and tasks:
        channels = tasks
        print(f"  태스크별 맞춤 생성 ({len(channels)}개: {[c['name'] for c in channels]})")
        full_response = _daily_loop_by_channel(
            project_name, project_context, marketing_config, channels, client
        )
    else:
        print("  범용 생성 모드 (마케팅 설정 없음)")
        full_response = _daily_loop_generic(project_name, project_context, client)

    # 보고사항들.md에 저장
    _save_to_report(f"매일 운영 루프 ({project_name})", full_response)
    print(f"\n📋 보고사항들.md에 저장 완료")

    # 자동 발행 (optional)
    if auto_publish_mode:
        _queue_contents_for_publish(full_response, marketing_config)
        publish_result = publish_all(PublishQueue())
        _save_to_report(f"자동 발행 결과 ({project_name})", str(publish_result))

    # 디스코드 알림
    _send_discord(f"매일 운영 루프 — {project_name}", full_response)

    # 자기 점검
    try:
        post_run_review("매일 운영 루프", {"project": project_name}, full_response)
    except Exception:
        pass

    return full_response


def _quality_check_and_retry(content: str, channel: str, project_context: str,
                            marketing_config: dict, client, max_retry: int = 2) -> tuple[str, float]:
    """생성된 콘텐츠 품질 체크. 7점 미만이면 재생성 (최대 2회).

    Returns:
        (최종 콘텐츠, 품질 점수)
    """

    # 템플릿에서 채점 기준 로드
    _, scoring_prompt = _get_template_prompt(channel)
    if not scoring_prompt:
        scoring_prompt = "이 콘텐츠의 마케팅 효과를 0~10점으로 평가해줘. [점수]/10"

    # 1차 채점
    score_response = ""
    with client.messages.stream(
        model=MODEL,
        max_tokens=300,
        system="너는 마케팅 대행사의 품질 관리자야. 엄격하게 평가해.",
        messages=[{"role": "user", "content": f"{scoring_prompt}\n\n콘텐츠:\n{content[:1000]}"}],
        temperature=0.3,
    ) as stream:
        for text in stream.text_stream:
            score_response += text

    # 점수 추출
    try:
        score_line = [line for line in score_response.split('\n') if '/' in line][0]
        score = float(score_line.split('/')[0].strip())
    except:
        score = 7.5  # 파싱 실패하면 중간값

    print(f"  ├─ 품질 평가: {score}/10")

    # 7점 미만이면 재생성
    if score < 7.0 and max_retry > 0:
        # 피드백 추출
        feedback_lines = [line for line in score_response.split('\n') if '다시 작성' in line or '피드백' in line.lower()]
        feedback = feedback_lines[0] if feedback_lines else "더 나은 버전을 만들어주세요"

        print(f"  ├─ 재생성 진행 (남은 시도: {max_retry - 1})")

        retry_prompt = CHANNEL_PROMPTS.get(channel, "")
        retry_system = inject_context(
            f"""이전 콘텐츠 문제: {feedback}

더 나은 버전을 만들어줘.

{retry_prompt}"""
        )

        base_info = f"""프로젝트: {project_context[:300]}
마케팅 설정: {str(marketing_config.get('key_message', ''))[:300]}

[원본 콘텐츠의 문제를 고쳐서 다시 작성]"""

        retry_response = ""
        with client.messages.stream(
            model=MODEL,
            max_tokens=3000,
            system=retry_system,
            messages=[{"role": "user", "content": base_info}],
            temperature=0.7,
        ) as stream:
            for text in stream.text_stream:
                print(text, end="", flush=True)
                retry_response += text

        print()
        # 재귀 호출
        return _quality_check_and_retry(retry_response, channel, project_context,
                                       marketing_config, client, max_retry - 1)

    return content, score


def _daily_loop_by_channel(
    project_name: str,
    project_context: str,
    marketing_config: dict,
    channels: list,
    client,
) -> str:
    """채널별 맞춤 콘텐츠 생성 + 자기검증 루프."""
    # 트렌드 리서치 (채널 키워드 포함)
    channel_names = " ".join([c["name"] for c in channels])
    research = research_before_task(
        role="콘텐츠 마케터",
        task=project_name,
        queries=[
            f"{project_name} {channel_names} 콘텐츠 트렌드 이번 주",
            f"{project_name} 마케팅 키워드 2026",
        ]
    )

    competitor_patterns = _load_competitor_patterns(max_entries=3)

    base_info = f"""프로젝트: {project_name}
날짜: {datetime.now().strftime('%Y-%m-%d (%A)')}
타겟: {marketing_config.get('target_persona', '')}
핵심 메시지: {marketing_config.get('key_message', '')}

프로젝트 컨텍스트:
{project_context[:800]}

최신 트렌드:
{research[:800]}

{competitor_patterns}"""

    all_responses = []
    quality_scores = []

    for channel in channels:
        channel_name = channel.get("name", "")
        print(f"\n  [{channel_name}] 콘텐츠 생성...")

        channel_prompt = _build_channel_prompt(channel, marketing_config)

        # 인스타그램인 경우 요일별 훅 패턴 주입
        if "인스타" in channel_name:
            hook_pattern = _get_daily_hook_pattern()
            channel_prompt += f"\n\n## 오늘의 훅 패턴: {hook_pattern}\nhook_library.md에서 해당 패턴의 예제를 참고해서 작성해줘."

        system_prompt = inject_context(
            f"""너는 {channel_name} 전문 콘텐츠 크리에이터야.
마케팅 대행사 시니어 수준(8.5/10)으로 만들어.
복붙 가능한 완성본으로 출력해.\n\n{channel_prompt}"""
        )

        # 채널별 max_tokens 조정 (부분 일치)
        max_tokens_map = {
            "인스타": 3000,
            "블로그": 5000,
            "유튜브": 2500,
            "메타광고": 2000,
            "네이버카페": 2500,
            "카카오": 1500,
        }
        max_tokens = 2000
        for key, val in max_tokens_map.items():
            if key in channel_name:
                max_tokens = val
                break

        response = ""
        with client.messages.stream(
            model=MODEL,
            max_tokens=max_tokens,
            system=system_prompt,
            messages=[{"role": "user", "content": base_info}],
            temperature=0.7,
        ) as stream:
            for text in stream.text_stream:
                print(text, end="", flush=True)
                response += text

        print()

        # 품질 검증 + 재생성
        final_content, quality_score = _quality_check_and_retry(
            response, channel_name, project_context, marketing_config, client
        )

        quality_scores.append((channel_name, quality_score))
        all_responses.append(f"### [{channel_name}] (품질: {quality_score:.1f}/10)\n{final_content}")

    # 품질 요약
    avg_score = sum(s[1] for s in quality_scores) / len(quality_scores) if quality_scores else 0
    quality_summary = f"\n\n---\n## 품질 점검 결과\n평균: {avg_score:.1f}/10\n"
    for channel, score in quality_scores:
        quality_summary += f"- {channel}: {score:.1f}/10\n"

    return "\n\n".join(all_responses) + quality_summary


def _daily_loop_generic(project_name: str, project_context: str, client) -> str:
    """범용 콘텐츠 생성 (marketing_config 없는 프로젝트용, 템플릿 기반)."""
    research = research_before_task(
        role="콘텐츠 마케터",
        task=project_name,
        queries=[
            f"{project_name} 인스타그램 마케팅 트렌드 이번 주",
            f"{project_name} 블로그 SEO 키워드 2026",
        ]
    )

    # 범용 템플릿 로드
    generic_prompt, _ = _get_generic_content_prompt()

    user_msg = f"""프로젝트: {project_name}
날짜: {datetime.now().strftime('%Y-%m-%d (%A)')}

프로젝트 컨텍스트:
{project_context[:1500]}

최신 트렌드:
{research[:1500]}

오늘의 콘텐츠를 생성해줘."""

    full_response = ""
    with client.messages.stream(
        model=MODEL,
        max_tokens=2000,
        system=inject_context(generic_prompt),
        messages=[{"role": "user", "content": user_msg}],
        temperature=0.7,
    ) as stream:
        for text in stream.text_stream:
            print(text, end="", flush=True)
            full_response += text

    print()
    return full_response


# ── 매주 루프 ──────────────────────────────────────────────────

WEEKLY_REVIEW_PROMPT = """너는 리안 컴퍼니의 전략 분석가야. 매주 성과를 리뷰하고 다음 주 방향을 제안해.

분석할 것:
1. **이번 주 성과 요약** — 리안이 입력한 숫자 기반
2. **뭐가 잘 됐고 뭐가 안 됐는지** — 구체적으로
3. **다음 주 방향 제안** — 바꿀 것, 유지할 것, 새로 시도할 것
4. **콘텐츠 방향 수정** — 이번 주 반응 기반으로

출력 형식:
## 이번 주 성과
| 지표 | 수치 | 전주 대비 | 판단 |
|------|------|---------|------|

## 잘 된 것 / 안 된 것
- ✅ 잘 된 것: [구체적으로]
- ❌ 안 된 것: [구체적으로 + 원인 추정]

## 다음 주 방향
| 항목 | 액션 | 우선순위 |
|------|------|---------|

## 콘텐츠 방향 수정
[다음 주 인스타/블로그/DM 톤/주제 조정 제안]

숫자 없으면 숫자 없이 정성적으로 분석. 솔직하게."""


def weekly_loop(project_name: str, performance_data: str = ""):
    """매주 성과 리뷰 루프."""
    client = _get_client()
    print(f"\n{'='*60}")
    print(f"📊 매주 운영 루프: {project_name}")
    print(f"{'='*60}")

    project_context = _load_project_context(project_name)

    user_msg = f"""프로젝트: {project_name}
기간: 이번 주

프로젝트 컨텍스트:
{project_context[:1000]}

이번 주 성과 데이터:
{performance_data if performance_data else "(리안이 아직 입력 안 함 — 정성적 분석만)"}

매주 리뷰해줘."""

    full_response = ""
    with client.messages.stream(
        model=MODEL,
        max_tokens=2000,
        system=inject_context(WEEKLY_REVIEW_PROMPT),
        messages=[{"role": "user", "content": user_msg}],
        temperature=0.3,
    ) as stream:
        for text in stream.text_stream:
            print(text, end="", flush=True)
            full_response += text

    print()

    _save_to_report(f"주간 리뷰 ({project_name})", full_response)
    print(f"\n📋 보고사항들.md에 저장 완료")

    # 디스코드 알림
    _send_discord(f"주간 리뷰 — {project_name}", full_response)

    # 자기 점검
    try:
        post_run_review("주간 리뷰", {"project": project_name}, full_response)
    except Exception:
        pass

    return full_response


PIVOT_PROMPT = """너는 사업 전략가야.
팀이 3회 이상 KPI를 달성하지 못했을 때 피벗 방향을 제안해.

규칙:
- "안 됐습니다" 보고 금지. 반드시 "이렇게 바꿀게요" 제안
- 피벗 방향은 반드시 "더 좁히기" 위주 (범용화 절대 금지)
- 예: 전체 소상공인 → 강남 미용실만, 스마트스토어 전체 → 패션 카테고리만
- 피벗 후 기대 수치 반드시 포함

출력:
## 현재 문제 진단
[KPI 미달 원인 3가지]

## 피벗 방향 제안
### 1순위: [더 좁힌 타겟/방향]
- 왜: [이유]
- 기대 효과: [수치]

### 2순위: [다른 접근]
- 왜: [이유]
- 기대 효과: [수치]

## 즉시 실행 액션 (이번 주 안에)
1. [구체적 행동]
2. [구체적 행동]
"""


def pivot_check(project_name: str, kpi_history: list = None, weeks_failing: int = 3) -> str:
    """KPI 미달 감지 시 피벗 방향 자동 제안.

    사용법:
        pivot_check("오프라인 마케팅", weeks_failing=3)
        pivot_check("온라인납품팀", kpi_history=["답장률 15%", "전환율 3%"])
    """
    client = _get_client()

    print(f"\n{'='*60}")
    print(f"🔄 피벗 체크 | {project_name} ({weeks_failing}주 연속 미달)")
    print("="*60)

    kpi_text = "\n".join(kpi_history) if kpi_history else "(KPI 데이터 없음 — 정성적 판단)"

    user_msg = f"""프로젝트: {project_name}
연속 미달 기간: {weeks_failing}주

KPI 데이터:
{kpi_text}

피벗 방향 제안해줘."""

    full_response = ""
    with client.messages.stream(
        model=MODEL,
        max_tokens=1500,
        system=inject_context(PIVOT_PROMPT),
        messages=[{"role": "user", "content": user_msg}],
        temperature=0.3,
    ) as stream:
        for text in stream.text_stream:
            print(text, end="", flush=True)
            full_response += text

    print()
    _save_to_report(f"피벗 제안 ({project_name})", full_response)
    print(f"\n📋 보고사항들.md에 저장 완료")

    # 디스코드 알림
    _send_discord(f"피벗 제안 — {project_name}", full_response)

    return full_response


# ── 모니터링 루프 ───────────────────────────────────────────────

MONITOR_PROMPT = """너는 리안 컴퍼니의 모니터 AI야. 2시간마다 돌면서 이상 신호를 감지해.

분석할 것:
1. **에러/이슈 감지** — 보고사항들.md에서 에러/실패 키워드 스캔
2. **점수 이상** — 팀 실행 결과 중 평점 낮은 것 (7점 이하)
3. **응답 지연** — 에이전트가 30분 이상 응답 없으면 알림
4. **패턴 인식** — 같은 종류의 에러가 반복되면 근본 원인 지적

출력 형식 (간결하게):
## 모니터링 리포트

🟢 정상: [점검 내용]
🟡 주의: [항목] (이유)
🔴 긴급: [항목] (즉시 조치 필요)

[추천 액션 (있으면)]

문제 없으면 "✅ 모니터링: 정상" 한 줄만."""


def monitor(project_name: str = "all"):
    """2시간마다 자동 체크 — 이슈 감지 + 알림."""
    client = _get_client()
    print(f"\n{'='*60}")
    print(f"🔍 모니터링 | {project_name}")
    print(f"{'='*60}")

    # 1. 보고사항들.md 스캔
    report_content = ""
    if os.path.exists(REPORT_PATH):
        with open(REPORT_PATH, encoding="utf-8") as f:
            report_content = f.read()

    # 최근 2시간 분량만 추출 (마지막 1000자)
    recent_report = report_content[-2000:] if len(report_content) > 2000 else report_content

    # 2. 에러 키워드 스캔
    error_keywords = ["에러", "실패", "안 됨", "문제", "timeout", "exception", "failed", "error"]
    issues_found = []

    for kw in error_keywords:
        if kw.lower() in recent_report.lower():
            # 해당 라인 추출
            for line in recent_report.split("\n"):
                if kw.lower() in line.lower() and len(line.strip()) > 5:
                    issues_found.append(line.strip()[:100])

    # 3. 점수 이상 스캔 (점수: X/10 패턴)
    import re
    score_pattern = r'점수[:\s]+(\d+(?:\.\d+)?)\s*/\s*10'
    scores = re.findall(score_pattern, recent_report)
    low_scores = [f"{float(s)}/10" for s in scores if float(s) < 7.0]

    # 4. 모니터링 분석 요청
    user_msg = f"""프로젝트: {project_name}

최근 보고사항 (최근 2시간):
{recent_report}

감지된 이슈:
- 에러 키워드: {', '.join(issues_found) if issues_found else '없음'}
- 낮은 점수: {', '.join(low_scores) if low_scores else '없음'}

모니터링 분석해줘."""

    full_response = ""
    with client.messages.stream(
        model=MODEL,
        max_tokens=600,
        system=inject_context(MONITOR_PROMPT),
        messages=[{"role": "user", "content": user_msg}],
        temperature=0.3,
    ) as stream:
        for text in stream.text_stream:
            print(text, end="", flush=True)
            full_response += text

    print()

    # 5. 보고사항들.md에 기록
    _save_to_report(f"모니터링 체크 ({project_name})", full_response)
    print(f"\n📋 모니터링 결과 저장 완료")

    # 6. 디스코드 알림 (이슈 있으면만)
    if "🔴" in full_response or "🟡" in full_response or issues_found or low_scores:
        _send_discord(f"⚠️ 모니터링 알림 — {project_name}", full_response)

    return full_response


# ── CLI ──────────────────────────────────────────────────────

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("사용법:")
        print('  python -m core.ops_loop daily "프로젝트명" [--auto-publish]')
        print('  python -m core.ops_loop weekly "프로젝트명" ["성과 데이터"]')
        print('  python -m core.ops_loop pivot "프로젝트명" [미달주수]')
        print('  python -m core.ops_loop monitor ["프로젝트명" | "all"]')
        sys.exit(1)

    mode = sys.argv[1]
    project = sys.argv[2] if len(sys.argv) > 2 else "all"

    if mode == "daily":
        auto_publish = "--auto-publish" in sys.argv or "--auto" in sys.argv
        daily_loop(project, auto_publish_mode=auto_publish)
    elif mode == "weekly":
        perf = sys.argv[3] if len(sys.argv) > 3 else ""
        weekly_loop(project, perf)
    elif mode == "pivot":
        weeks = int(sys.argv[3]) if len(sys.argv) > 3 else 3
        pivot_check(project, weeks_failing=weeks)
    elif mode == "monitor":
        monitor(project)
    else:
        print(f"알 수 없는 모드: {mode}. daily / weekly / pivot / monitor 사용.")
