# Effect Library — INDEX

> hero_builder가 이 라이브러리에서 이펙트를 조립한다.
> 전체 레포 클론 금지. 여기서 필요한 것만 가져와서 조합.

---

## 이펙트 목록

| 이펙트 | 용도 | 비용 | 의존성 |
|--------|------|------|--------|
| [crack](crack/) | 균열 벌어짐 + 카메라 관통 히어로 | Medium-High | Three.js, GSAP |
| [emissive-core](emissive-core/) | 발광 유기체 코어 + 촉수 | Medium | Three.js, GSAP |
| [glow-line](glow-line/) | 에너지 빔 / 기둥 / 문 프레임 | Very Low | Three.js |
| [distortion](distortion/) | 이미지 디스플레이스먼트 호버 | Low | Three.js, GSAP |
| [unfold](unfold/) | 오리가미 패널 순차 열림 | Very Low | Three.js, GSAP |
| [bloom-stack](bloom-stack/) | 수동 2패스 블룸 파이프라인 | Low-Medium | Three.js |
| [camera-scroll](camera-scroll/) | 스크롤 연동 카메라 플라이스루 | Low | Three.js, GSAP+ScrollTrigger, Lenis |

---

## hero_builder 조립 규칙

### 1. effect.md 먼저 읽어라
각 이펙트 폴더의 `effect.md`를 읽고 **Anti-Patterns** 섹션을 반드시 확인.
Anti-Pattern을 어기면 구현이 실패한다.

### 2. director 지시서 → 이펙트 매핑

| director가 말하면 | 사용할 이펙트 |
|-----------------|-------------|
| "균열" / "틈" / "벌어짐" | `crack/` |
| "발광체" / "생물" / "코어" / "심장" | `emissive-core/` |
| "문" / "기둥" / "아치" / "에너지 라인" | `glow-line/` |
| "이미지 전환" / "호버 디스토션" | `distortion/` |
| "지도" / "패널" / "열림" / "펼쳐짐" | `unfold/` |
| "글로우" / "블룸" / "빛 번짐" | `bloom-stack/` (다른 이펙트에 추가) |
| "카메라 이동" / "플라이스루" / "스크롤 씬" / "씬 전환" | `camera-scroll/` |

### 3. 조합 패턴

```
히어로 (강렬한 오프닝):
  crack + bloom-stack

문 / 포털:
  glow-line × 2 (좌우 기둥) + glow-line × 1 (아치)

살아있는 중심 오브젝트:
  emissive-core + bloom-stack

지식/데이터 공개:
  unfold + glow-line (패널 테두리)

이미지 포트폴리오:
  distortion (각 카드)
```

### 4. 절대 금지
- `MeshBasicMaterial` flat 색상으로 히어로 구현 금지
- `SphereGeometry` / `BoxGeometry` 그대로 히어로 오브젝트로 쓰기 금지
- 이펙트 없이 `background: #000 + <h1>텍스트</h1>` 만 있는 히어로 금지
- `references/` 폴더의 전체 레포를 import하거나 clone하기 금지

---

## 파일 구조 (각 이펙트 공통)

```
effect-name/
├── effect.md         — 목적, 사용 시기, 의존성, 비용, anti-patterns
├── notes.md          — 기술 결정 사유, 튜닝 파라미터, 색상 프리셋
├── implementation.js — 독립 실행 가능한 JS 함수 (CDN Three.js 기준)
├── shader.frag       — (해당 시) 독립 GLSL fragment shader
└── shader.vert       — (해당 시) 독립 GLSL vertex shader
```

## 신규 이펙트 추가 규칙

1. 위 구조 그대로 새 폴더 생성
2. `effect.md` Anti-Patterns 섹션 필수 작성
3. `implementation.js`는 CDN Three.js r128 기준, zero-dependency
4. 이 INDEX.md 테이블에 한 줄 추가
