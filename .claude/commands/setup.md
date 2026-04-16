# /setup — 첫 설치 세팅

새로 clone한 팀원을 위한 초기 세팅 커맨드야.
아래 순서대로 진행해줘. 각 단계마다 결과를 한국어로 설명해줘.

---

## Step 1 — 이름/회사명 확인

사용자에게 아래 두 가지를 물어봐:
1. "이름이 뭐야? (예: 철수)"
2. "회사명이 뭐야? (예: 철수 컴퍼니)"

답변 받은 후 진행해.

---

## Step 2 — .env 파일 생성

`company/.env` 파일이 없으면:
- `company/.env.example`을 복사해서 `company/.env` 생성
- `OWNER_NAME=` 항목을 Step 1에서 받은 이름으로 채워서 저장

`company/.env` 파일이 이미 있으면 이 단계 스킵.

---

## Step 3 — Python 패키지 설치

아래 명령어 실행:
```
cd company && python -m venv venv && venv/Scripts/pip install -r requirements.txt
```

실패하면 `python3 -m venv venv`로 재시도.

---

## Step 4 — 이름 교체

`company/` 하위의 모든 `.py` 파일에서:
- `"리안"` → Step 1에서 받은 **이름** 으로 교체 (예: `"철수"`)
- `"리안 컴퍼니"` → Step 1에서 받은 **회사명** 으로 교체 (예: `"철수 컴퍼니"`)

단, `venv/` 폴더 안은 건드리지 마.

---

## Step 5 — API 키 안내

`company/.env` 파일을 열어서 사용자에게 보여주고:

"아래 키들을 채워야 해. 없는 건 비워도 되는데 해당 에이전트는 작동 안 해:"

| 키 | 용도 | 필수 여부 |
|----|------|---------|
| ANTHROPIC_API_KEY | Claude 에이전트들 (시은, 준혁 등) | 필수 |
| OPENAI_API_KEY | 민수 (전략/수익모델) | 권장 |
| GOOGLE_API_KEY | 하은 (팩트검증), 도윤 (교육팀) | 권장 |
| PERPLEXITY_API_KEY | 서윤 (시장조사) | 권장 |
| DISCORD_WEBHOOK_URL | 디스코드 알림 | 선택 |

---

## Step 6 — MCP 설치

아래 명령어들을 순서대로 실행해:

```
claude mcp add playwright -- npx @playwright/mcp
claude mcp add perplexity -- npx @jschuller/perplexity-mcp
claude mcp add nano-banana -- npx nano-banana-mcp
```

실행 후 `claude mcp list`로 3개 다 Connected 뜨는지 확인해.

그 다음 사용자에게 안내:
"Gmail이랑 Google Calendar MCP는 Claude Code 안에서 /mcp 쳐서 직접 연결해야 해."

---

## Step 7 — Cloudflare 로그인

```
npx wrangler login
```

브라우저가 열리면 Cloudflare 계정으로 로그인.

---

## Step 8 — 완료 안내

```
✅ 세팅 완료!

실행 방법:
cd company
venv/Scripts/python.exe main.py "아이디어를 여기에 입력"
```
