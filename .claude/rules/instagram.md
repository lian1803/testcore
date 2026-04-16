# 인스타그램 접속 규칙

## 단일 URL 접속 (무조건 스크립트로)
```bash
cd "$(git rev-parse --show-toplevel)/company" && ./venv/Scripts/python.exe utils/insta_browse.py "인스타URL"
```
Playwright MCP로 instagram.com 직접 navigate 절대 금지 (로그인 팝업 뜸).

## 배치 분석 (인스타분석팀)
리안이 인스타 링크들을 txt로 가져오면 / "인스타 분석해줘" / "링크 분석":
```bash
cd "$(git rev-parse --show-toplevel)/company" && ./venv/Scripts/python.exe run_인스타분석팀.py "링크파일.txt"
```
- 팀원: 박수집(수집), 김해독(Gemini Vision 분석), 이적용(Claude 인사이트), 정보고(팀장)
- 분석 관점: 게시물 실제 내용 → core-shell 업그레이드에 훔쳐올 것
- 스크린샷: company/utils/insta_screenshots/ 재사용
