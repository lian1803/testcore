import os
from openai import OpenAI
from concurrent.futures import ThreadPoolExecutor, as_completed
from core.models import SONAR_PRO

MODEL = SONAR_PRO


def _query(perplexity: OpenAI, query: str) -> tuple[str, str]:
    try:
        resp = perplexity.chat.completions.create(
            model=MODEL,
            messages=[
                {
                    "role": "system",
                    "content": "세계 최고 수준의 전문가 지식을 압축해서 전달해. 이론 최소화, 실전 적용 가능한 핵심만. 수치/사례/프레임워크 위주로."
                },
                {
                    "role": "user",
                    "content": f"다음 주제의 세계 최고 수준 지식을 수집해줘:\n\n{query}"
                }
            ],
            max_tokens=1000,
        )
        return query, resp.choices[0].message.content
    except Exception as e:
        return query, f"수집 실패: {e}"


def run(curriculum: dict) -> dict:
    print("\n" + "="*60)
    print("📚 교육팀 | 전문 지식 수집 (Perplexity)")
    print("="*60)

    perplexity = OpenAI(
        api_key=os.getenv("PERPLEXITY_API_KEY"),
        base_url="https://api.perplexity.ai",
        timeout=120.0,
    )

    # 모든 에이전트의 쿼리 수집
    all_queries = []
    query_to_agent = {}

    for agent in curriculum.get("agents", []):
        for q in agent.get("knowledge_queries", []):
            all_queries.append(q)
            query_to_agent[q] = agent["name"]

    print(f"총 {len(all_queries)}개 쿼리 병렬 수집...")

    knowledge_map = {}
    with ThreadPoolExecutor(max_workers=6) as executor:
        futures = {executor.submit(_query, perplexity, q): q for q in all_queries}
        for i, future in enumerate(as_completed(futures), 1):
            q, result = future.result()
            knowledge_map[q] = result
            agent_name = query_to_agent.get(q, "")
            print(f"  [{i}/{len(all_queries)}] {agent_name} — {q[:40]}...")

    # 에이전트별로 지식 정리
    agent_knowledge = {}
    for agent in curriculum.get("agents", []):
        name = agent["name"]
        agent_knowledge[name] = ""
        for q in agent.get("knowledge_queries", []):
            agent_knowledge[name] += f"\n### {q}\n{knowledge_map.get(q, '')}\n"

    print(f"\n✅ 지식 수집 완료 ({len(all_queries)}개)")
    return agent_knowledge
