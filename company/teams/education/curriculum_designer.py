import anthropic
import json
from core.models import CLAUDE_OPUS, CLAUDE_SONNET
from core.model_loader import get_model

# 모델 설정: config에서 "curriculum" 역할의 모델 로드
# 기본값 Claude Sonnet (커리큘럼 설계는 Sonnet으로 충분, Opus 불필요)
MODEL = get_model("curriculum_designer")

SYSTEM_PROMPT = """너는 리안 컴퍼니의 교육 설계 책임자야.
신설 팀이 들어오면, 그 팀을 세계 최고 수준으로 만들기 위한 교육 커리큘럼을 설계해.

너의 역할:
1. 팀 목표를 분석해서 필요한 에이전트 구성 설계
2. 각 에이전트가 세계적 수준이 되려면 어떤 지식이 필요한지 파악
3. Perplexity가 수집해야 할 구체적 쿼리 목록 생성
4. 각 에이전트의 핵심 행동 원칙 초안 작성
5. 검증자(Validator) 역할이 있다면, 아래 원칙을 반드시 포함시켜:

[검증자 핵심 원칙 — 변경 금지]
검증자는 이 팀의 현재 제약(신설팀, 제한된 자원, 레퍼런스 부족 등)을 먼저 파악한다.
역할: "조건 자체를 바꿔라"는 결론을 절대 내지 말 것. 조건 안에서의 최선을 찾는다.
출력 형식:
- 현재 조건에서 사용 가능한가: YES/조건부YES/NO
- 리스크: (있으면)
- 현재 조건에서 보완할 것: (구체적으로)
이 세 가지가 모든 검증 섹션에 필수로 들어가야 함.

반드시 JSON으로만 출력해. 다른 텍스트 없이.

출력 형식:
{
  "team_name": "팀 이름",
  "team_goal": "팀의 핵심 목표 1줄",
  "lian_wants": "리안이 이 팀에서 원하는 것",
  "agents": [
    {
      "name": "에이전트 이름 (한국 이름)",
      "role": "역할 한 줄",
      "specialty": "전문 분야",
      "knowledge_queries": [
        "Perplexity 수집 쿼리 1",
        "Perplexity 수집 쿼리 2",
        "Perplexity 수집 쿼리 3",
        "Perplexity 수집 쿼리 4",
        "Perplexity 수집 쿼리 5"
      ],
      "core_principles": [
        "이 에이전트가 절대 지켜야 할 원칙 1",
        "원칙 2",
        "원칙 3"
      ],
      "output_format": "이 에이전트가 만들어야 할 결과물"
    }
  ],
  "pipeline_order": ["에이전트1", "에이전트2", "에이전트3"],
  "success_metric": "이 팀이 잘 돌아가는지 판단하는 기준"
}"""


def run(team_name: str, team_purpose: str, client: anthropic.Anthropic) -> dict:
    print("\n" + "="*60)
    print(f"🎓 교육팀 | 커리큘럼 설계 (Claude Opus)")
    print("="*60)
    print(f"신설 팀: {team_name}")
    print(f"목적: {team_purpose}")
    print()

    full_response = ""
    with client.messages.stream(
        model=MODEL,
        max_tokens=16000,
        messages=[{
            "role": "user",
            "content": f"""다음 팀을 신설하려고 해. 세계 최고 수준으로 만들어줘.

팀 이름: {team_name}
팀 목적/해야 할 일: {team_purpose}

이 팀이 최고 수준이 되려면 어떤 에이전트들이 필요하고,
각각 어떤 지식이 필요한지 설계해줘.

JSON만 출력해."""
        }],
        system=SYSTEM_PROMPT,
    ) as stream:
        for text in stream.text_stream:
            print(text, end="", flush=True)
            full_response += text

    print("\n")

    # JSON 파싱
    try:
        # ```json 블록 제거
        clean = full_response.strip()
        if clean.startswith("```"):
            clean = clean.split("```")[1]
            if clean.startswith("json"):
                clean = clean[4:]
        curriculum = json.loads(clean.strip())
    except Exception as e:
        print(f"⚠️ JSON 파싱 실패: {e}")
        curriculum = {"raw": full_response, "agents": []}

    return curriculum
