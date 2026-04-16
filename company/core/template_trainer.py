"""
template_trainer.py — 신규 템플릿 자동 생성 (needs_training 태스크용)

ops_planner에서 needs_training에 등재된 태스크를 자동으로 전문가 프롬프트로 변환.

사용법:
    from core.template_trainer import train_new_template
    train_new_template("DM 작성", "카카오톡 고객 지원 DM", "sales", client)
"""
import os
import json
import re
from datetime import datetime
import anthropic
from dotenv import load_dotenv
from core.context_loader import inject_context
from core.research_loop import research_before_task
from core.models import CLAUDE_OPUS, CLAUDE_SONNET

load_dotenv()

TEMPLATES_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "knowledge", "ops_templates")
INDEX_PATH = os.path.join(TEMPLATES_DIR, "_index.json")
REPORT_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "보고사항들.md")


def _load_template_index() -> dict:
    """_index.json 로드."""
    if os.path.exists(INDEX_PATH):
        try:
            with open(INDEX_PATH, encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"templates": [], "metadata": {}}


def _save_template_index(index: dict):
    """_index.json 저장."""
    with open(INDEX_PATH, "w", encoding="utf-8") as f:
        json.dump(index, f, ensure_ascii=False, indent=2)


KNOWLEDGE_RESEARCHER_PROMPT = """너는 마케팅/영업 분야의 세계 최고 전문가야.

다음 태스크에 대해 최신 베스트 프랙티스, 성공 사례, 심리학적 원칙을 수집해줘.

**태스크**: {task_name}
**분야**: {category}
**설명**: {description}

수집할 내용:
1. 이 분야의 최신 트렌드 (2025년)
2. 성공하는 콘텐츠의 공통점 (구체적 숫자/예시)
3. 심리학적 원칙 (AIDA, 사회적 증명, 희소성 등)
4. 자주하는 실수와 해결책
5. 평가 기준 (뭐가 좋은지 안 좋은지)

마크다운 형식으로 정리해줘."""


TEMPLATE_GENERATOR_PROMPT = """너는 마케팅 전문가 프롬프트 엔지니어야.

다음 정보를 바탕으로 전문가 수준의 마케팅 프롬프트를 작성해줘.

**태스크**: {task_name}
**분야**: {category}
**리서치 결과**:
{research_content}

마크다운 형식으로 다음을 포함해야 함:

```markdown
---
name: {template_id}
category: {category}
description: {description}
tags: [태그들]
quality_score: (예상점수 8.0~9.0)
created: {date}
applicable_to: [사업유형들]
---

[전문가 수준 프롬프트 본문 — AIDA/심리학적 원칙 반영]

## 채점 기준

[10점 만점 기준 명시]
[평가 지표]

### 응답 형식:
[점수]/10
[이유]
[피드백]
```

프롬프트는:
- 구체적이고 실행 가능해야 함
- 변수 포함 (tone, format, target_persona 등)
- 실제 마케팅 현장에서 사용 가능할 정도로 상세함
"""


def train_new_template(
    task_name: str,
    description: str,
    category: str,
    client: anthropic.Anthropic,
    business_types: list = None
) -> dict:
    """신규 템플릿 자동 생성.

    Args:
        task_name: 태스크명 (예: "카카오톡 DM")
        description: 태스크 설명
        category: 카테고리 (marketing/sales/general)
        client: Anthropic 클라이언트
        business_types: 적용 가능한 사업 유형

    Returns:
        {"status": "success|failed", "template_path": "...", "report": "..."}
    """
    if business_types is None:
        business_types = ["saas", "ecommerce", "agency"]

    print(f"\n{'='*60}")
    print(f"🎓 신규 템플릿 훈련: {task_name}")
    print("="*60)

    # 1. Perplexity로 최신 지식 수집
    print("\n  📚 Step 1: 최신 지식 수집 중...")
    research = research_before_task(
        role="마케팅 전문가",
        task=task_name,
        queries=[
            f"{task_name} 2025년 베스트 프랙티스",
            f"{task_name} 심리학적 원칙 및 성공 패턴",
            f"{category} 마케팅 최신 트렌드"
        ]
    )
    print(f"  ✓ 수집 완료 ({len(research)} 자)")

    # 2. Claude Opus로 프롬프트 설계
    print("  🔧 Step 2: 전문가 프롬프트 설계 중...")

    template_id = re.sub(r'[^가-힣a-zA-Z0-9]', '_', task_name)
    date_str = datetime.now().strftime("%Y-%m-%d")

    generation_prompt = TEMPLATE_GENERATOR_PROMPT.format(
        task_name=task_name,
        category=category,
        description=description,
        research_content=research[:2000],
        template_id=template_id,
        date=date_str
    )

    template_content = ""
    with client.messages.stream(
        model=CLAUDE_OPUS,
        max_tokens=3000,
        messages=[{"role": "user", "content": generation_prompt}],
        temperature=0.7,
    ) as stream:
        for text in stream.text_stream:
            template_content += text
            print(text, end="", flush=True)

    print()

    # 3. 템플릿 파일 저장
    print("  💾 Step 3: 템플릿 파일 저장 중...")

    template_path = os.path.join(TEMPLATES_DIR, category, f"{task_name}.md")
    os.makedirs(os.path.dirname(template_path), exist_ok=True)

    with open(template_path, "w", encoding="utf-8") as f:
        f.write(template_content)

    print(f"  ✓ 저장: {template_path}")

    # 4. 인덱스 업데이트
    print("  🔍 Step 4: 인덱스 업데이트 중...")

    index = _load_template_index()
    new_template = {
        "id": template_id,
        "name": task_name,
        "category": category,
        "path": f"{category}/{task_name}.md",
        "description": description,
        "quality_score": 7.5,  # 훈련으로 생성된 것은 낮은 초기 점수
        "tags": [category, task_name.split()[0].lower()],
        "applicable_to": business_types,
        "channels": [task_name],
        "created": date_str,
        "training_generated": True
    }

    index["templates"].append(new_template)
    index["metadata"]["last_updated"] = datetime.now().isoformat()
    _save_template_index(index)

    print(f"  ✓ 인덱스 업데이트 완료")

    # 5. 보고사항 작성
    report = f"""## 신규 템플릿 훈련 완료

**템플릿명**: {task_name}
**카테고리**: {category}
**설명**: {description}

**파일 위치**: {template_path}
**적용 가능**: {', '.join(business_types)}

**초기 품질 점수**: 7.5/10 (훈련 생성)
**다음 단계**: 실제 콘텐츠 생성으로 테스트 후 점수 상향 조정

**프롬프트 미리보기**:
{template_content[:500]}...
"""

    return {
        "status": "success",
        "template_path": template_path,
        "template_id": template_id,
        "report": report
    }


def evaluate_and_improve(template_path: str, test_content: str, score: float, client: anthropic.Anthropic) -> dict:
    """생성된 콘텐츠 품질로 템플릿 평가 및 개선.

    Args:
        template_path: 템플릿 파일 경로
        test_content: 이 템플릿으로 생성한 콘텐츠
        score: 해당 콘텐츠 점수 (0~10)
        client: Anthropic 클라이언트

    Returns:
        {"status": "improved|maintained", "new_score": 8.0}
    """
    # 점수 >= 7.5면 유지, 낮으면 개선
    if score >= 7.5:
        return {"status": "maintained", "new_score": score}

    print(f"\n  ⚠️ 템플릿 점수 낮음 ({score}/10) — 개선 중...")

    # 현재 템플릿 로드
    with open(template_path, encoding="utf-8") as f:
        current_template = f.read()

    # Claude Opus로 개선안 생성
    improvement_prompt = f"""이 템플릿으로 생성한 콘텐츠 점수가 {score}/10이야.

**현재 템플릿**:
{current_template[:1500]}

**생성된 콘텐츠**:
{test_content[:1000]}

어떤 부분을 개선해야 점수가 올라갈까? 구체적 수정안을 제시해줘."""

    improvement = ""
    with client.messages.stream(
        model=CLAUDE_OPUS,
        max_tokens=2000,
        messages=[{"role": "user", "content": improvement_prompt}],
        temperature=0.7,
    ) as stream:
        for text in stream.text_stream:
            improvement += text

    print(f"  개선안:\n{improvement[:500]}")

    return {
        "status": "flagged_for_review",
        "score": score,
        "improvement_suggestion": improvement
    }


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 3:
        print("사용법: python -m core.template_trainer <태스크명> <카테고리>")
        print("예: python -m core.template_trainer '틱톡 쇼츠' marketing")
        sys.exit(1)

    task_name = sys.argv[1]
    category = sys.argv[2]
    description = sys.argv[3] if len(sys.argv) > 3 else task_name

    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    result = train_new_template(task_name, description, category, client)
    print("\n" + result["report"])
