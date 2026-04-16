#!/usr/bin/env python3
"""
Creative Director — 3개 컨셉 카드 생성

입력: 프로젝트 설명 (string)
출력: 3개 컨셉 JSON (각각 BIG IDEA + 구체적 구현 스펙)

핵심 원칙:
- 추상적 무드 금지 → 실제 파일 경로 + HEX + 폰트명 + 컴포넌트명
- Big Idea가 먼저 → 모든 선택이 Big Idea에서 파생
- 3개 컨셉은 반드시 방향이 다를 것 (같은 색상 팔레트 재활용 금지)
"""

import json
import anthropic

# 사용 가능한 컴포넌트 카탈로그
# (실제 파일 경로: team/디자인팀/components/react-bits/src/content/...)

COMPONENT_CATALOG = """
=== 사용 가능한 컴포넌트 전체 카탈로그 ===

【 BACKGROUNDS (react-bits) 】
경로: team/디자인팀/components/react-bits/src/content/Backgrounds/{Name}/{Name}.jsx

- Aurora          → 부드러운 빛의 흐름. 자연/웰니스/감성 브랜드
- Balatro         → 카드/격자 패턴. 게임/테크 느낌
- Ballpit         → 공들이 떠다님. 재미/플레이풀
- Beams           → 빛 줄기. 스캔/테크/에너지
- ColorBends      → 색상이 구부러짐. 크리에이티브/아트
- DarkVeil        → 어두운 베일 효과. 고급/미스터리
- Dither          → 픽셀 노이즈. 레트로/인디
- DotGrid         → 점 격자. 미니멀/테크
- EvilEye         → 눈 모양. 부적/문화적 컨셉
- FaultyTerminal  → 오류 터미널. 해킹/사이버펑크
- FloatingLines   → 선들이 부유. 아키텍처/구조적
- Galaxy          → 우주/별. SF/비전/미래
- GradientBlinds  → 그라디언트 블라인드. 모던/클린
- Grainient       → 노이즈+그라디언트. 프리미엄/텍스처
- GridDistortion  → 격자 왜곡. 실험적/아트
- GridMotion      → 움직이는 격자. 테크/다이나믹
- GridScan        → 레이더 스캔 격자. 모니터링/테크
- Hyperspeed      → 속도감 있는 빛. SF/드라이빙/속도
- Iridescence     → 무지갯빛 금속. 럭셔리/패션/K뷰티
- LetterGlitch    → 글자 글리치. 해킹/에러/아트
- Lightning       → 번개. 에너지/스포츠/파워
- LightPillar     → 빛의 기둥. 신성/웅장/건축
- LightRays       → 빛 광선. 따뜻함/희망/자연광
- LineWaves       → 선 파도. 음악/오디오/흐름
- LiquidChrome    → 크롬 액체. 럭셔리/금속/미래
- LiquidEther     → 에테르 액체. 신비/감성/부드러움
- Orb             → 발광 구체. AI/에너지/포털
- Particles       → 파티클 필드. 범용 (기본값 — 특별한 이유 없으면 피할 것)
- PixelBlast      → 픽셀 폭발. 게임/레트로/이벤트
- PixelSnow       → 픽셀 눈. 겨울/청량/이벤트
- Plasma          → 플라즈마. 사이언스/에너지/혼돈
- Prism           → 프리즘 광학. 예술/창의/색채
- PrismaticBurst  → 프리즘 폭발. 축제/런칭/임팩트
- Radar           → 레이더. 보안/추적/테크
- RippleGrid      → 파문 격자. 물/서비스/연결
- ShapeGrid       → 도형 격자. 디자인/모던
- Silk            → 실크 파도. 패션/럭셔리/부드러움
- SoftAurora      → 부드러운 오로라. 힐링/명상/스파
- Threads         → 실/섬유. 수공예/텍스타일/연결
- Waves           → 파도. 해변/서핑/리듬

【 TEXT ANIMATIONS (react-bits) 】
경로: team/디자인팀/components/react-bits/src/content/TextAnimations/{Name}/{Name}.jsx

- ASCIIText       → 아스키 아트로 변환
- BlurText        → 블러로 등장
- CircularText    → 원형 텍스트
- CountUp         → 숫자 카운트업 (통계 섹션 필수)
- DecryptedText   → 해독되듯 등장
- FallingText     → 텍스트 낙하
- FuzzyText       → 퍼지 → 선명해짐
- GlitchText      → 글리치 효과
- GradientText    → 그라디언트 색상
- RotatingText    → 회전 등장
- ScrambledText   → 뒤섞임 → 정렬
- ScrollFloat     → 스크롤 시 부유
- ScrollReveal    → 스크롤 시 reveal
- ScrollVelocity  → 스크롤 속도 연동
- ShinyText       → 빛나는 텍스트
- Shuffle         → 셔플 효과
- SplitText       → 글자/라인 단위 등장 (가장 범용적)
- TextCursor      → 커서 깜빡임
- TextPressure    → 마우스 압력 반응

【 CURSOR EFFECTS 】
- BlobCursor      → 블롭 커서 (react-bits/Animations/BlobCursor)
- GhostCursor     → 잔상 커서 (react-bits/Animations/GhostCursor)
- ImageTrail      → 이미지 trail (react-bits/Animations/ImageTrail)
- PixelTrail      → 픽셀 trail (react-bits/Animations/PixelTrail)
- SplashCursor    → 스플래시 (react-bits/Animations/SplashCursor)
- TargetCursor    → 타겟 조준 (react-bits/Animations/TargetCursor)
- MouseFollower   → GSAP 프로덕션급 (team/디자인팀/components/mouse-follower)

【 SCROLL 】
- Lenis           → 스무스 스크롤 (CDN: https://cdn.jsdelivr.net/npm/@studio-freight/lenis)
- AOS             → 스크롤 트리거 애니메이션 (CDN)

【 3D 】
- Three.js        → 직접 3D 구현 (CDN: three.js r128+)
- R3F             → React Three Fiber (next.js 프로젝트용)
- Spline          → 비주얼 3D (CDN: @splinetool/runtime)

【 PARTICLES / EFFECTS 】
- tsparticles     → 파티클 시스템 (CDN)
- vfx-js          → WebGL 효과 한 줄로 (CDN)

【 GENERATIVE 】
- nano-banana     → MCP로 이미지 생성 가능 (프롬프트 텍스트 기반)
"""

SYSTEM_PROMPT = """너는 Creative Director야.

=== 핵심 원칙: 코스요리 방식 ===

"맛있는 재료를 장바구니에 담는 것"이 아니라 "하나의 코스요리를 설계"하는 것이다.

랍스터(비쌈) + 김치찌개(맛있음) + 초콜릿케이크(예쁨) = 각각 좋지만 같이 먹으면 구역질.
프렌치 어니언수프 + 코코뱅 + 크렘브륄레 = 각각도 좋고 같이 먹어도 완성.

차이: 뒤엔 "프렌치"라는 법칙이 있다. 앞엔 없다.

=== 작업 순서 (반드시 이 순서로) ===

STEP 1. Big Idea — 유저가 겪는 '한 순간'
STEP 2. Visual DNA — Big Idea에서 파생되는 3가지 법칙
STEP 3. 컴포넌트 선택 — 법칙에 맞는 것만. 각 선택에 "왜 이것인지" 이유 필수
STEP 4. 금지 목록 — 이 스토리에 안 맞아서 제외한 것

=== Visual DNA가 뭐냐 ===

모든 컴포넌트가 따라야 하는 3가지 법칙:

1. 색상법칙: "이 스토리에서 색은 무엇을 의미하는가"
   예: "어두운 봉오리(#2D1B0E) → 밝은 꽃잎(#F5E6C8)으로 진행. 이 사이만. 파란색/초록색 없음."

2. 모션법칙: "이 스토리에서 움직임의 속도와 방향은?"
   예: "꽃은 천천히 핀다. 모든 등장은 scale 0.95→1.0, 0.8s ease-out. 튀거나 빠른 모션 금지."

3. 형태법칙: "이 스토리에서 형태는 둥근가 날카로운가"
   예: "전부 둥글고 유기적. border-radius 큼. 직선 격자/각진 모서리 금지."

=== 컴포넌트 선택 검증 ===

각 컴포넌트를 고를 때 반드시 물어봐:
"이것이 Visual DNA 3가지 법칙을 전부 충족하는가?"

❌ Silk 배경 + "꽃 피어남" 스토리 → Silk는 파도. 꽃과 파도는 다른 이야기. 색상법칙만 맞고 형태/모션이 안 맞음.
✅ Silk 배경 + "실크 드레스가 바람에 날리는" 스토리 → Silk는 실크. 색상/모션/형태 전부 일치.

"예쁘니까"는 선택 이유가 아니다. "법칙에 맞으니까"가 선택 이유다.

=== 금지 ===
- 추상 단어: "따뜻한", "유기적", "세련된" 금지
- 컴포넌트 쇼핑: 카탈로그에서 예쁜 거 고르는 행위 금지
- 3개 컨셉이 같은 방향이면 금지 (같은 배경, 같은 색상 재활용 금지)
- 카탈로그에 없는 컴포넌트 지어내기 금지

=== 출력 형식 (반드시 JSON만, 설명 텍스트 없이) ===

{
  "business_analysis": {
    "type": "업종/카테고리",
    "positioning": "브랜드가 차지하려는 포지션",
    "target_emotion": "유저가 첫 화면에서 느껴야 하는 감정"
  },
  "concepts": [
    {
      "id": "A",
      "name": "컨셉 이름",
      "big_idea": "이 사이트를 열면 [구체적 경험]이 벌어진다",
      "visual_dna": {
        "story": "Big Idea를 한 문장으로",
        "color_rule": "이 스토리에서 색의 의미와 허용 범위. 금지 색도 명시.",
        "motion_rule": "이 스토리에서 모션의 속도, 방향, 금지 패턴.",
        "shape_rule": "이 스토리에서 형태의 규칙. 둥근가 날카로운가, 금지 형태.",
        "forbidden": ["이 스토리에 안 맞는 요소들 3~5개"]
      },
      "background": {
        "component": "컴포넌트명",
        "why": "이 배경이 Visual DNA 3법칙을 어떻게 충족하는지",
        "colors": ["#HEX1", "#HEX2", "#HEX3"]
      },
      "colors": {
        "bg": "#HEX",
        "primary": "#HEX",
        "accent": "#HEX",
        "secondary": "#HEX"
      },
      "typography": {
        "heading_font": "정확한 폰트명 (Google Fonts)",
        "heading_weight": "100~900",
        "body_font": "정확한 폰트명",
        "body_weight": "100~900"
      },
      "cursor": {
        "component": "커서 컴포넌트명",
        "why": "이 커서가 Visual DNA와 맞는 이유"
      },
      "hero": {
        "approach": "three.js|css-only|nano-banana|video-bg|shader-only",
        "detail": "히어로에서 정확히 무슨 일이 일어나는지",
        "nano_banana_prompt": null
      },
      "text_animation": {
        "component": "텍스트 애니메이션 컴포넌트명",
        "why": "이 텍스트 애니메이션이 모션법칙을 따르는 이유"
      },
      "special": "이 컨셉만의 unique wow factor",
      "sections": ["section1", "section2", "section3", "section4"]
    }
  ]
}

반드시 JSON 형식만 출력. ```json ``` 블록 포함하지 마. 순수 JSON만.
"""


def run(project_desc: str, client: anthropic.Anthropic) -> dict:
    """
    프로젝트 설명 → 3개 컨셉 JSON 반환
    """
    print("\n🎨 Creative Director 가동...")
    print(f"   프로젝트: {project_desc[:80]}...")

    prompt = f"""프로젝트 설명:
{project_desc}

사용 가능한 컴포넌트:
{COMPONENT_CATALOG}

위 컴포넌트들만 사용해서 3개의 완전히 다른 컨셉 카드를 JSON으로 만들어줘."""

    resp = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=4000,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}]
    )

    raw = resp.content[0].text.strip()

    # JSON 파싱
    try:
        data = json.loads(raw)
        return data
    except json.JSONDecodeError:
        # JSON 블록 추출 시도
        import re
        match = re.search(r'\{[\s\S]+\}', raw)
        if match:
            try:
                return json.loads(match.group())
            except:
                pass

        print(f"⚠️ JSON 파싱 실패. 원본 응답 저장 후 재시도...")
        # 재시도
        resp2 = client.messages.create(
            model="claude-opus-4-5",
            max_tokens=4000,
            system="너는 JSON만 출력하는 봇이야. 아래 텍스트를 올바른 JSON으로 수정해줘. 설명 없이 JSON만.",
            messages=[{"role": "user", "content": raw}]
        )
        raw2 = resp2.content[0].text.strip()
        match2 = re.search(r'\{[\s\S]+\}', raw2)
        if match2:
            return json.loads(match2.group())

        raise ValueError(f"Creative Director JSON 파싱 실패:\n{raw[:500]}")


def display_concepts(concepts_data: dict) -> None:
    """터미널에 컨셉 카드 출력"""
    analysis = concepts_data.get("business_analysis", {})
    print(f"\n{'='*65}")
    print(f"📊 비즈니스 분석")
    print(f"   유형: {analysis.get('type', '?')}")
    print(f"   포지셔닝: {analysis.get('positioning', '?')}")
    print(f"   목표 감정: {analysis.get('target_emotion', '?')}")

    for c in concepts_data.get("concepts", []):
        print(f"\n{'─'*65}")
        print(f"【 컨셉 {c['id']} 】 {c['name']}")
        print(f"\n  💡 BIG IDEA:")
        print(f"     {c['big_idea']}")
        print(f"\n  🎨 배경: {c['background']['component']} | {' '.join(c['background']['colors'])}")
        print(f"  📝 폰트: {c['typography']['heading_font']} {c['typography']['heading_weight']} / {c['typography']['body_font']}")
        print(f"  🖱️  커서: {c['cursor']}")
        print(f"  🦸 히어로: {c['hero']['approach']} — {c['hero']['detail'][:60]}...")
        print(f"  ✨ 스페셜: {c['special']}")
    print(f"\n{'='*65}")
