# /visual-review

Lian Dash 시각 디자인 자동 검수를 실행해라.

## 동작
1. `company/venv/Scripts/python.exe company/auto_visual_review.py` 실행
2. 스크립트가 https://lian-dash.vercel.app 랜딩 + /dashboard 스크린샷을 찍고 Gemini Vision으로 분석함
3. 결과를 보고사항들.md에 저장하고 JSON 요약을 visual_snapshots/에 저장함
4. 분석 완료 후 결과 요약을 리안에게 보고해라

## 설치 안 되어있으면
```bash
company/venv/Scripts/pip install playwright pillow
company/venv/Scripts/playwright install chromium
```
