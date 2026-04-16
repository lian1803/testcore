"""
ops_planner.py — 운영 전략 자동 수립 + 템플릿 매칭

product_analyzer 결과를 받아서:
1. 사업 유형 판단 (SaaS / E-commerce / Agency / Consulting / Brand)
2. ops_templates/ 에서 적절한 템플릿 자동 매칭
3. ops_config.json에 저장
4. ops_loop에 등록할 설정 생성

사용법:
    from core.ops_planner import plan_operations
    plan = plan_operations(analysis_result, "프로젝트명", client)
"""
import os
import json
import re
import subprocess
from datetime import datetime
import anthropic
from dotenv import load_dotenv
from core.context_loader import inject_context
from core.models import CLAUDE_SONNET

load_dotenv()

MODEL = CLAUDE_SONNET
OPS_CONFIG_PATH = os.path.join(os.path.dirname(__file__), "ops_config.json")
MARKETING_CONFIG_PATH = os.path.join(os.path.dirname(__file__), "marketing_config.json")
TEMPLATES_INDEX_PATH = os.path.join(os.path.dirname(__file__), "..", "knowledge", "ops_templates", "_index.json")
REPORT_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "보고사항들.md")


def _load_ops_config() -> dict:
    """ops_config.json 로드 (없으면 빈 딕셔너리)."""
    if os.path.exists(OPS_CONFIG_PATH):
        try:
            with open(OPS_CONFIG_PATH, encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"projects": {}}


def _save_ops_config(config: dict):
    """ops_config.json 저장."""
    with open(OPS_CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)


def _load_template_index() -> dict:
    """ops_templates/_index.json 로드."""
    if os.path.exists(TEMPLATES_INDEX_PATH):
        try:
            with open(TEMPLATES_INDEX_PATH, encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"templates": [], "metadata": {}}


PLANNER_PROMPT = """너는 운영 전략 총괄이야.
분석 결과를 보고 구체적인 운영 계획을 JSON으로 출력해. 다른 텍스트 없이 JSON만:

{
  "business_type": "saas|ecommerce|agency|consulting|brand",
  "target_persona": "타겟 페르소나 (구체적으로)",
  "key_message": "핵심 메시지 한 줄",
  "tasks": [
    {
      "name": "태스크명",
      "template": "template_path",
      "frequency": "주기",
      "config": {
        "tone": "톤앤매너",
        "hashtags_base": ["#해시태그"],
        "keywords": ["SEO키워드"]
      },
      "priority": 1,
      "reason": "이 태스크를 선택한 이유"
    }
  ],
  "needs_training": ["need_name"],
  "summary": "운영 전략 요약 (3문장)"
}

사업 유형에 맞는 태스크를 현실적으로 최대 5개만. 선택과 집중."""


def plan_operations(context: dict, project_name: str, client: anthropic.Anthropic) -> dict:
    """마케팅 분석 결과 기반으로 운영 전략 수립.

    Args:
        context: product_analyzer 또는 launch_prep 결과
        project_name: 프로젝트명
        client: Anthropic 클라이언트

    Returns:
        {"config": ops_config, "report": 보고내용}
    """
    print(f"\n{'='*60}")
    print(f"📋 운영 전략 수립: {project_name}")
    print("="*60)

    idea = context.get("clarified", context.get("idea", project_name))
    target = context.get("target_persona", "")
    strategy = context.get("strategy", "")[:800]
    market = context.get("market", "")[:800]

    user_msg = f"""프로젝트명: {project_name}

== 아이디어 ==
{idea[:600]}

== 타겟/마케팅 분석 ==
{target}
{market}

== 전략 ==
{strategy}

이 프로젝트의 운영 전략을 수립해줘."""

    # Claude로 운영 계획 수립
    response = ""
    with client.messages.stream(
        model=MODEL,
        max_tokens=2000,
        system=inject_context(PLANNER_PROMPT),
        messages=[{"role": "user", "content": user_msg}],
        temperature=0.7,
    ) as stream:
        for text in stream.text_stream:
            response += text

    print(response)

    # JSON 파싱
    try:
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if json_match:
            plan = json.loads(json_match.group())
        else:
            print("⚠️ JSON 파싱 실패")
            return {"config": {}, "report": response}
    except json.JSONDecodeError as e:
        print(f"⚠️ JSON 디코딩 에러: {e}")
        return {"config": {}, "report": response}

    # 템플릿 인덱스 로드
    template_index = _load_template_index()
    available_templates = {t["id"]: t for t in template_index.get("templates", [])}

    # ops_config 생성
    ops_config = _load_ops_config()
    project_config = {
        "type": plan.get("business_type", "saas"),
        "target_persona": plan.get("target_persona", ""),
        "key_message": plan.get("key_message", ""),
        "tasks": [],
        "status": "active"
    }

    # 각 태스크 처리
    for task in plan.get("tasks", []):
        task_name = task.get("name", "")
        template_spec = task.get("template", "")

        # 템플릿 찾기
        template_meta = None
        for tmpl in template_index.get("templates", []):
            if template_spec.lower() in tmpl.get("name", "").lower() or \
               template_spec.lower() == tmpl.get("id", "").lower():
                template_meta = tmpl
                break

        if not template_meta:
            # 채널 이름으로 매칭 시도
            for tmpl in template_index.get("templates", []):
                if task_name in tmpl.get("channels", []):
                    template_meta = tmpl
                    break

        if template_meta:
            project_config["tasks"].append({
                "name": task_name,
                "template": template_meta["path"],
                "frequency": task.get("frequency", "주3회"),
                "config": task.get("config", {})
            })
            print(f"  ✓ {task_name}: {template_meta['name']}")
        else:
            print(f"  ⚠️ {task_name}: 템플릿 없음 (훈련 필요)")

    # ops_config.json에 저장
    ops_config["projects"][project_name] = project_config
    ops_config["metadata"]["last_updated"] = datetime.now().isoformat()
    _save_ops_config(ops_config)

    print(f"\n  ✓ ops_config.json 저장 완료")

    report = f"""## 운영 전략 수립 결과

**사업 유형**: {plan.get('business_type')}
**타겟 페르소나**: {plan.get('target_persona')}
**핵심 메시지**: {plan.get('key_message')}

**구성된 태스크**:
{chr(10).join([f"- {t['name']} ({t.get('frequency', '미정')})  → {available_templates.get(t.get('template', ''), {}).get('name', '?')}'" for t in plan.get('tasks', [])])}

**훈련 필요**: {', '.join(plan.get('needs_training', ['없음']))}

**전략 요약**:
{plan.get('summary', '')}
"""

    return {
        "config": project_config,
        "plan": plan,
        "report": report
    }


def activate_teams(project_name: str, plan: dict) -> dict:
    """팀 활성화 (기존 marketing_planner.activate_teams와 동일)."""
    # 현재는 ops_loop에서 자동으로 처리되므로 stub
    return {"status": "activated"}


# 하위호환성: marketing_planner 대체
def plan_marketing(context: dict, project_name: str, client: anthropic.Anthropic) -> dict:
    """(호환성 함수) marketing_planner.plan_marketing 대체."""
    return plan_operations(context, project_name, client)


def plan_from_brief(context: dict, project_name: str, client: anthropic.Anthropic) -> dict:
    """(호환성 함수) marketing_planner.plan_from_brief 대체."""
    return plan_operations(context, project_name, client)


def print_confirmation_prompt(project_name: str, plan: dict) -> str:
    """(호환성 함수) 마케팅 전략 확인 프롬프트."""
    from core.marketing_planner import print_confirmation_prompt as mkt_prompt
    return mkt_prompt(project_name, plan)


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("사용법: python -m core.ops_planner <프로젝트명>")
        sys.exit(1)

    project_name = sys.argv[1]
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    # 테스트용 컨텍스트
    test_context = {
        "idea": "마케팅 데이터 분석 SaaS",
        "target_persona": "스타트업 마케팅 담당자",
        "strategy": "GA4 + 메타 광고 연동으로 ROI 추적",
        "market": "마케팅 자동화 시장"
    }

    result = plan_operations(test_context, project_name, client)
    print("\n" + result["report"])
