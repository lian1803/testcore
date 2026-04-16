# 처음 시작하는 법 (팀원용)

코드 몰라도 됨. 순서대로만 따라하면 돼.

---

## 1단계 — 필수 프로그램 설치

아래 3개 설치되어 있어야 함. 이미 있으면 넘어가.

| 프로그램 | 다운로드 | 확인 방법 |
|---------|---------|---------|
| **Node.js** (v18 이상) | https://nodejs.org → LTS 버전 | 터미널에 `node -v` 입력 → 숫자 나오면 OK |
| **Python** (3.10 이상) | https://python.org/downloads | 터미널에 `python --version` 입력 |
| **Git** | https://git-scm.com | 터미널에 `git --version` 입력 |

---

## 2단계 — 코드 내려받기

터미널(cmd 또는 PowerShell) 열고 아래 붙여넣기:

```bash
git clone https://github.com/core-shell1/core-shell.git
cd core-shell
```

---

## 3단계 — API 키 설정

`company/` 폴더 안에 `.env` 파일 만들기:

```bash
cp company/.env.example company/.env
```

`.env` 파일 열어서 아래 4개만 우선 입력 (나머지는 선택):

```
ANTHROPIC_API_KEY=     ← Claude (필수)
OPENAI_API_KEY=        ← GPT-4o (필수)
GOOGLE_API_KEY=        ← Gemini (필수)
PERPLEXITY_API_KEY=    ← 검색 AI (필수)
```

> 키 모르면 리안한테 물어봐.

---

## 4단계 — Python 패키지 설치

```bash
cd company
python -m venv venv
venv/Scripts/pip install -r requirements.txt
```

---

## 5단계 — Claude Code 설치

```bash
npm install -g @anthropic-ai/claude-code
```

설치 후 프로젝트 폴더에서 `claude` 입력하면 실행됨.

---

## 6단계 — 추가 도구 설정

pull만으로는 안 되고 별도로 설치/로그인해야 하는 것들:

### Cloudflare (사이트 배포용)
```bash
npm install -g wrangler
wrangler login
```
→ 브라우저 열리면 Cloudflare 계정으로 로그인.  
계정 없으면 https://cloudflare.com 에서 무료 가입.

### 이미지 생성 MCP (nano-banana)
`C:/Users/본인계정이름/.claude/` 폴더 안에 `.mcp.json` 파일 만들기:

```json
{
  "mcpServers": {
    "nano-banana": {
      "command": "npx",
      "args": ["nano-banana-mcp"],
      "env": {
        "GEMINI_API_KEY": "여기에_구글_Gemini_키_입력"
      }
    }
  }
}
```
> Gemini 키 = `.env`의 `GOOGLE_API_KEY`와 같음.

### UI 디자인 MCP (Stitch)
위 `.mcp.json` 파일에 stitch 추가:

```json
{
  "mcpServers": {
    "nano-banana": { ... },
    "stitch": {
      "command": "npx",
      "args": ["stitch-mcp"],
      "env": {
        "STITCH_API_KEY": "여기에_Stitch_키_입력"
      }
    }
  }
}
```
> Stitch 키: 리안한테 물어봐 (공유 가능한지 확인 필요).

---

## 선택 사항 (필요할 때만)

| 기능 | 필요한 것 | 설정 위치 |
|------|---------|---------|
| 디스코드 알림 | Discord 웹훅 URL | `.env` → `DISCORD_WEBHOOK_URL` |
| 인스타 자동 발행 | Meta 개발자 계정 | `.env` → `META_ACCESS_TOKEN` |
| 네이버 블로그 | 네이버 개발자 앱 | `.env` → `NAVER_BLOG_*` |
| DB 연결 | Supabase 프로젝트 | `.env` → `SUPABASE_URL` |

---

## 완료 확인

Claude Code 열고 아래 타이핑:
```
안녕
```
답 잘 나오면 성공.

---

## 작업 시작 전 매번 해야 하는 것

```bash
git pull
```

딱 이것만. 안 하면 다른 사람 작업이랑 충돌날 수 있음.
