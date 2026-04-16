#!/usr/bin/env python3
"""
Gemini 독립 검증 스크립트
UltraProduct /work 완료 후 자동 실행됨.
프로젝트 산출물 전체를 Gemini에게 보내서 독립 검증 받음.
"""
import sys
import os
import io
import glob

# Windows UTF-8
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# company/.env 로드
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)

from dotenv import load_dotenv
load_dotenv(os.path.join(script_dir, ".env"))

from google import genai
from google.genai import types

from core.models import GEMINI_PRO
MODEL = GEMINI_PRO


def collect_files(project_dir: str) -> str:
    """프로젝트 디렉토리에서 검증 대상 파일들을 수집"""
    collected = []

    # 1. Wave 산출물 (md 파일들)
    for pattern in ["wave*.md", "*합의*.md", "*계획*.md"]:
        for f in sorted(glob.glob(os.path.join(project_dir, pattern))):
            name = os.path.basename(f)
            with open(f, "r", encoding="utf-8") as fh:
                content = fh.read()
            collected.append(f"### 파일: {name}\n```\n{content}\n```")

    # 2. QA 결과
    qa_dir = os.path.join(project_dir, "qa")
    if os.path.isdir(qa_dir):
        for f in sorted(glob.glob(os.path.join(qa_dir, "*.md"))):
            name = os.path.basename(f)
            with open(f, "r", encoding="utf-8") as fh:
                content = fh.read()
            collected.append(f"### 파일: qa/{name}\n```\n{content}\n```")

    # 3. 마케팅
    marketing_dir = os.path.join(project_dir, "marketing")
    if os.path.isdir(marketing_dir):
        for f in sorted(glob.glob(os.path.join(marketing_dir, "*.md"))):
            name = os.path.basename(f)
            with open(f, "r", encoding="utf-8") as fh:
                content = fh.read()
            collected.append(f"### 파일: marketing/{name}\n```\n{content}\n```")

    # 4. CLAUDE.md (원본 설계서)
    claude_md = os.path.join(project_dir, "CLAUDE.md")
    if os.path.isfile(claude_md):
        with open(claude_md, "r", encoding="utf-8") as fh:
            content = fh.read()
        collected.append(f"### 파일: CLAUDE.md (원본 설계서)\n```\n{content}\n```")

    # 5. 주요 코드 파일 (schema, route 등 핵심만)
    code_patterns = [
        "**/schema.prisma",
        "**/route.ts",
        "**/page.tsx",
        "**/middleware.ts",
        "**/vercel.json",
        "**/DEPLOY.md",
    ]
    seen = set()
    for pattern in code_patterns:
        for f in sorted(glob.glob(os.path.join(project_dir, pattern), recursive=True)):
            if "node_modules" in f or ".next" in f:
                continue
            rel = os.path.relpath(f, project_dir)
            if rel in seen:
                continue
            seen.add(rel)
            try:
                with open(f, "r", encoding="utf-8") as fh:
                    content = fh.read()
                # 너무 긴 파일은 앞 200줄만
                lines = content.split("\n")
                if len(lines) > 200:
                    content = "\n".join(lines[:200]) + f"\n... (이하 {len(lines)-200}줄 생략)"
                collected.append(f"### 파일: {rel}\n```\n{content}\n```")
            except (UnicodeDecodeError, PermissionError):
                continue

    if not collected:
        return "[산출물 없음]"

    return "\n\n---\n\n".join(collected)


SYSTEM = """너는 독립 검증자야. Gemini로서 Claude가 만든 산출물을 냉정하게 검증해.

네 역할:
1. Wave 1~5 산출물의 일관성 검증 (합의 내용이 코드에 반영됐는가)
2. 비즈니스 로직 공백 발견 (놓친 것)
3. 보안 취약점 확인
4. 엣지케이스 발견 (최소 5개)
5. 배포 실행 가능성 평가

출력 형식:

# 최종 리포트 — [프로젝트명]

## 전체 평가: [준비 완료 / 조건부 준비 / 미준비]

## Wave별 산출물 요약
[테이블]

## 일관성 검증 결과
[Wave 1 제안 → Wave 2 합의 → 코드 반영 대조]

## 발견된 엣지케이스 + 보완 필요
[CRITICAL / HIGH / MEDIUM 분류]

## 비즈니스 로직 검증
[테이블]

## 보안 최종 확인
[테이블]

## 배포 실행 가능성 평가
[테이블]

## 리안(CEO)을 위한 다음 액션 (우선순위 순)
[오늘 / 이번 주 / 출시 전]

## 독립 검증자 종합 의견
[솔직하게. 좋은 점, 나쁜 점, 가장 우선 해결할 것 3가지]

---

규칙:
- Claude가 만들었다고 봐주지 마라. 냉정하게.
- 미확인은 미확인으로 표기. 추측하지 마.
- 코드가 없는 부분은 "코드 미확인"으로 표기.
- 리안은 비개발자. 다음 액션은 쉽게 써."""


def run_verification(project_dir: str) -> str:
    """Gemini로 독립 검증 실행"""
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("❌ GOOGLE_API_KEY가 없어. company/.env 확인해.")
        sys.exit(1)

    gemini = genai.Client(api_key=api_key)

    files_content = collect_files(project_dir)
    project_name = os.path.basename(os.path.abspath(project_dir))

    prompt = f"""다음은 "{project_name}" 프로젝트의 전체 산출물이야.
Claude AI가 Wave 1~5까지 생성한 결과물을 독립 검증해줘.

{files_content}

위 산출물 전체를 검증하고 최종 리포트를 작성해줘."""

    print("=" * 60)
    print("🔬 Gemini 독립 검증 시작")
    print(f"   프로젝트: {project_name}")
    print(f"   모델: {MODEL}")
    print("=" * 60)

    full_response = ""
    try:
        for chunk in gemini.models.generate_content_stream(
            model=MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM,
                max_output_tokens=8192,
            )
        ):
            text = chunk.text or ""
            print(text, end="", flush=True)
            full_response += text
    except Exception as e:
        print(f"\n\n❌ Gemini API 에러: {e}")
        full_response += f"\n\n[검증 중단: {e}]"

    print("\n")
    return full_response


def main():
    if len(sys.argv) < 2:
        print("사용법: python verify_gemini.py <프로젝트 디렉토리>")
        print("예: python verify_gemini.py projects/소상공인_인스타/")
        sys.exit(1)

    project_dir = os.path.abspath(sys.argv[1])
    if not os.path.isdir(project_dir):
        print(f"❌ 디렉토리 없음: {project_dir}")
        sys.exit(1)

    result = run_verification(project_dir)

    # 저장
    output_path = os.path.join(project_dir, "final_report.md")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(result)

    print("=" * 60)
    print(f"✅ 검증 완료! 저장: {output_path}")
    print("=" * 60)


if __name__ == "__main__":
    main()
