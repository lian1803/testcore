# Draftly.space — AI 3D 웹사이트 빌더

> 인스타에서 보이는 감각적인 3D 사이트들의 실제 제작 툴 중 하나.

## 작동 방식
1. 프롬프트 한 줄 입력 ("AI SaaS 랜딩, 다크 미래적, 임팩트 강한 히어로")
2. AI가 이미지 생성 → 8초 영상 제작 → 수백 프레임 추출
3. 프레임을 스크롤 반응 3D 사이트로 자동 조립
4. Tailwind CSS + clean HTML로 export
5. Vercel/Netlify 바로 배포

## 특징
- WebGL 없이 순수 브라우저 스크롤 애니메이션 (호환성 높음)
- 개발자가 편집 가능한 코드로 export
- Gemini/Fal.ai API 키 쓰면 **무료**
- NVIDIA GPU 있으면 로컬 실행 가능

## 사용 방법
- 사이트: https://www.draftly.space/
- 자체 API 키 준비: Gemini API 또는 Fal.ai API
- 프롬프트로 생성 → ZIP 다운로드 → team/ 프로젝트에 적용

## 우리 시스템에서 활용
- 이사팀 GO → 랜딩페이지 히어로 섹션 → Draftly로 3D 기반 생성
- 결과물 HTML을 우리 FE 에이전트가 받아서 통합
- nano-banana 이미지를 Draftly 입력으로 쓰는 것도 가능
