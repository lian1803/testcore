#!/usr/bin/env python3
"""
agent_improver 통합 테스트

실행 방법:
    cd company
    python ../test_agent_improver.py
"""
import sys
import os

# 패스 설정
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "company"))
os.environ['PYTHONIOENCODING'] = 'utf-8'

try:
    from core.agent_improver import (
        _extract_low_quality_agents,
        _get_agent_current_prompt,
        AGENTS_METADATA,
        get_pending_improvements,
    )

    print("=" * 60)
    print("Agent Improver Integration Test")
    print("=" * 60)

    # 1. 등록된 에이전트 확인
    print("\n[1/4] Registered Agents")
    print(f"Total: {len(AGENTS_METADATA)}")
    for agent, meta in AGENTS_METADATA.items():
        print(f"  - {agent}: {meta['name']} ({meta['role'][:40]}...)")

    # 2. 저품질 에이전트 탐지
    print("\n[2/4] Low Quality Agent Detection")
    low_quality = _extract_low_quality_agents()
    if low_quality:
        print(f"Found: {len(low_quality)} agent(s)")
        for item in low_quality:
            agent_name = item['agent']
            score = item['score']
            metadata = item['metadata']
            print(f"  - {agent_name}: {metadata.get('name', '?')} ({score:.1f}/10)")
    else:
        print("No low quality agents detected")

    # 3. 프롬프트 추출 테스트
    print("\n[3/4] Prompt Extraction Test")
    test_agents = ["junhyeok", "sieun", "seoyun", "taeho"]
    for agent in test_agents:
        prompt = _get_agent_current_prompt(agent)
        if prompt:
            first_line = prompt.split('\n')[0]
            print(f"  {agent}: OK ({len(prompt)} chars)")
            print(f"    -> {first_line[:60]}")
        else:
            print(f"  {agent}: FAIL (cannot extract)")

    # 4. 미승인 개선안 확인
    print("\n[4/4] Pending Improvements")
    pending = get_pending_improvements()
    if pending:
        print(f"Found: {len(pending)} improvement(s) awaiting approval")
        for agent, data in pending.items():
            status = data.get('status', 'unknown')
            print(f"  - {agent}: {status}")
    else:
        print("No pending improvements")

    print("\n" + "=" * 60)
    print("Test Complete")
    print("=" * 60)

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
