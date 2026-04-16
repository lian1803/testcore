
=== 전문 지식 (세계 최고 수준 자료 기반) ===

### Gemini Vision API best prompts for extracting technical information from educational carousel images — prompt engineering guide 2024
# Gemini Vision API로 교육용 캐러셀 이미지에서 기술 정보 추출하기

## 핵심 프롬프트 구조 (검증된 프레임워크)

**5-컴포넌트 공식을 사용하면 일관성 있는 결과를 얻습니다:**[2]

| 컴포넌트 | 포함 내용 | 실제 예시 |
|---------|---------|---------|
| **What** | 구체적인 주제/대상 | "교육용 기술 다이어그램" 아닌 단순 "다이어그램" |
| **Doing What** | 작업 또는 구체적 지시 | "기술 용어 추출 및 정의 분류" |
| **Where** | 맥락/환경 | "캐러셀 슬라이드 형식의 교육 자료" |
| **How It Looks** | 시각적 특성 | "명확한 레이아웃, 고대비 텍스트" |
| **Technical Flavor** | 처리 방식 | "JSON 구조화 출력, 정확한 텍스트 인식" |

**핵심 원칙: 자연어 설명이 키워드 나열보다 효과적입니다.**[2]

## 실전 적용 가능한 프롬프트 템플릿

**약한 프롬프트:**
```
"이 이미지에서 기술 정보를 추출해"
```

**강력한 프롬프트:**
```
"이 교육용 캐러셀 슬라이드에서 다음을 추출하고 JSON으로 구조화해줘:
1. 모든 기술 용어 및 정의
2. 코드 스니펫 또는 수식
3. 계층적 개념 관계
4. 실전 적용 예시

형식: {\"terms\": [], \"code_blocks\": [], \"hierarchy\": {}, \"examples\": []}"
```

## Gemini Vision API의 기술 정보 추출 강점/약점

**우수한 분야:**[2]
- 자연어 이해 (문법적 설명 해석)
- 이미지 내 텍스트 렌더링 (이전보다 개선됨)
- 다단계 지시 따르기
- **정확한 기술 용어 인식** (복잡한 학술 표기법)

**제한사항:**[2]
- 정확한 개수 지정 ("5개 항목"이 4개 또는 6개가 될 수 있음)
- 특정 저작권 자료나 브랜드 재현
- **여러 이미지 간 완벽한 일관성** (캐러셀 시리즈에서 주의 필요)

## 다중 이미지 처리 (캐러셀 전체 분석)

**Python 예시:**[3]
```python
from google import genai
from google.genai import types

client = genai.Client()

# 캐러셀 슬라이드 1 업로드
slide1 = client.files.upload(file="slide1.jpg")

# 슬라이드 2를 인라인 데이터로 준비
with open("slide2.png", 'rb') as f:
    slide2_bytes = f.read()

# 통합 프롬프트
response = client.models.generate_content(

### How to extract AI workflow diagrams, prompt examples, and step-by-step instructions from Instagram card news images using multimodal LLM
제공된 검색 결과에는 Instagram 카드 뉴스 이미지에서 AI 워크플로우 다이어그램, 프롬프트 예제, 단계별 지침을 멀티모달 LLM으로 추출하는 방법에 대한 직접적인 정보가 없습니다.

검색 결과는 주로 다음 두 가지를 다룹니다:

**관련 있는 내용:**
- Instagram 데이터 추출 자동화[1]: 구조화되지 않은 Instagram 페이지 데이터를 JSON/CSV로 변환
- AI를 활용한 Instagram 콘텐츠 생성 워크플로우[2]: 트렌딩 포스트 분석 및 AI 이미지 생성, OpenAI/Replicate API 활용
- Make를 이용한 Instagram 자동화[3]: RSS 피드, OpenAI, Dropbox 등의 모듈 연결

**부족한 부분:**
귀하의 질문에 정확히 답하려면 다음 주제에 대한 정보가 필요합니다:
- 멀티모달 LLM(GPT-4V, Claude Vision 등)을 사용한 이미지 분석 기법
- Instagram 카드/카루셀 포맷의 구조 인식
- OCR + 시각 요소 추출 파이프라인
- 워크플로우 다이어그램 자동 해석 및 구조화

더 정확한 답변을 위해 "multimodal LLM image parsing", "workflow diagram OCR extraction", "Instagram carousel content analysis" 등의 키워드로 재검색이 필요합니다.

### Gemini 1.5 Pro vision vs GPT-4V for dense text extraction from images — accuracy benchmark and cost comparison
**Gemini 1.5 Pro vision outperforms GPT-4V (GPT-4o) in **dense text extraction accuracy** from receipts (factuality 91% vs 84%, Levenshtein 88% vs 85%) and uses 3.5x fewer input tokens, cutting costs ~70% ($7/M input vs $30/M).** GPT-4o edges out in broader vision benchmarks like DocVQA (93% vs implied lower for Gemini).[2][5][6]

### **Accuracy Benchmarks (Dense Text Extraction)**
Receipt extraction eval (image → key-value pairs, n=unspecified, Braintrust 2024):
| Model              | **Factuality** | **Levenshtein** | Notes |
|--------------------|----------------|-----------------|-------|
| **Gemini 1.5 Pro** | **91%**       | **88%**        | Top; 3% variance on reruns [2] |
| Gemini 1.5 Flash  | 88%           | 86%            | Faster (2.2s) [2] |
| **GPT-4o (4V)**   | **84%**       | **85%**        | 13s latency [2] |
| GPT-4o mini       | 81%           | 87%            | 38k tokens/image [2] |

- **Gemini wins on factuality** (LLM-judged via GPT-4o autorater); Levenshtein (edit distance) comparable.[2]
- **TV news OCR fail**: Both hallucinate heavily; GPT-4 > Gemini but neither production-ready vs classical OCR.[1]
- **DocVQA** (doc Q&A): GPT-4o 93%, Gemini 1.5 Pro ~81-89% range (chart-related).[5]
- **General vision**: GPT-4o leads (ChartQA 86%, MathVista 64%); no direct dense text focus.[5]

**실전 프레임워크**: 
1. Test 10-50 images (receipts/docs) on **factuality** (JSON output match) + **Levenshtein**.
2. Threshold: >90% factuality → deploy; else hybrid OCR + LLM.
3. Rerun evals (variance ±3%).[2]

### **Cost Comparison (per 1M Tokens, 
===

