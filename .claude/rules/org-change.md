---
paths:
  - "회사 조직도.md"
  - "zip/**"
---
# 조직도 변경 시 (팀 신설/해체/인원/모델 변경)

두 파일 반드시 동시 업데이트:
1. `회사 조직도.md` — 팀/인원 정보, 변경 이력
2. `zip/src/App.tsx` — 해당 팀 배열 수정 (ai: '모델명')

수정 후 빌드 + 배포:
```bash
cd zip && npm run build && npx wrangler pages deploy dist/
```
