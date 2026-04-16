#!/bin/bash
# pre_tool_safety.sh — 위험 명령어 차단 hook
# Claude Code PreToolUse hook으로 등록됨
# stdin으로 tool input JSON을 받아서 위험 패턴 감지 시 exit 1

INPUT=$(cat)

# Bash/Shell 명령어 추출 (tool_input.command 필드)
COMMAND=$(echo "$INPUT" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    # tool_input 안의 command 필드
    cmd = data.get('tool_input', {}).get('command', '')
    print(cmd)
except:
    print('')
" 2>/dev/null)

# Write 툴 파일 경로 추출
FILE_PATH=$(echo "$INPUT" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    path = data.get('tool_input', {}).get('file_path', '')
    print(path)
except:
    print('')
" 2>/dev/null)

# ── 패턴 0: archive/company_design/ 보호 ────────────────
# Write/Edit으로 archive/company_design/ 내 파일 수정 차단
if echo "$FILE_PATH" | grep -qE 'archive/company_design'; then
    echo "🚨 [안전 차단] archive/company_design/ 파일 수정 감지" >&2
    echo "   이 폴더는 원본 설계물입니다. 절대 수정/삭제 금지." >&2
    exit 2
fi

# Bash로 archive/company_design/ 삭제/이동 시도 차단
if echo "$COMMAND" | grep -qE 'archive[/\\]company_design'; then
    if echo "$COMMAND" | grep -qiE 'rm\b|del\b|move\b|mv\b|rename\b|ren\b'; then
        echo "🚨 [안전 차단] archive/company_design/ 삭제/이동 시도 감지" >&2
        echo "   이 폴더는 원본 설계물입니다. 절대 수정/삭제 금지." >&2
        exit 2
    fi
fi

# ── 패턴 1: rm -rf ──────────────────────────────────────────
if echo "$COMMAND" | grep -qiE 'rm\s+-rf|rm\s+-r\s+-f|rm\s+--recursive.*--force'; then
    echo "🚨 [안전 차단] 위험 명령어 감지: rm -rf" >&2
    echo "   이 명령어는 파일을 영구 삭제합니다. 리안에게 확인받으세요." >&2
    exit 1
fi

# ── 패턴 2: git push --force ────────────────────────────────
if echo "$COMMAND" | grep -qiE 'git\s+push\s+.*--force|git\s+push\s+.*-f\b'; then
    echo "🚨 [안전 차단] 위험 명령어 감지: git push --force" >&2
    echo "   강제 푸시는 원격 히스토리를 덮어씁니다. 리안에게 확인받으세요." >&2
    exit 1
fi

# ── 패턴 3: DROP TABLE / DELETE FROM (조건 없이) ───────────
if echo "$COMMAND" | grep -qiE 'DROP\s+TABLE|DELETE\s+FROM\s+\w+\s*;|DELETE\s+FROM\s+\w+\s*$'; then
    echo "🚨 [안전 차단] 위험 SQL 감지: DROP TABLE 또는 무조건 DELETE FROM" >&2
    echo "   데이터 전체 삭제 위험. 리안에게 확인받으세요." >&2
    exit 1
fi

# ── 패턴 4: .env 파일 직접 덮어쓰기 ────────────────────────
# Write 툴로 .env를 직접 쓰는 경우 차단
if echo "$FILE_PATH" | grep -qE '(^|/)\.env$'; then
    echo "🚨 [안전 차단] .env 파일 직접 덮어쓰기 감지" >&2
    echo "   API 키/비밀값이 손실될 수 있습니다. 리안에게 확인받으세요." >&2
    exit 1
fi

# Bash 명령어로 .env 덮어쓰는 경우
if echo "$COMMAND" | grep -qE '>\s*\.env\b|>\s*[^/]*\.env\b'; then
    echo "🚨 [안전 차단] .env 파일 덮어쓰기 명령 감지" >&2
    echo "   API 키/비밀값이 손실될 수 있습니다. 리안에게 확인받으세요." >&2
    exit 1
fi

# 통과 — 위험 패턴 없음
exit 0
