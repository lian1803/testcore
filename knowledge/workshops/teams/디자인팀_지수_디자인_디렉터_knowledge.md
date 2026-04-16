
=== 전문 지식 (세계 최고 수준 자료 기반) ===

### design system INDEX.md parsing strategy for automated design direction routing 2024
### **INDEX.md Parsing Core Strategy**
**Grid-based spatial projection + schema-induced triple extraction** for **design system** docs: Parse INDEX.md as layout-aware grid (preserve hierarchy/tabs), extract triples (Component > Variant > Props), route to **automated design direction** via RAG/SQL hybrid query. 2024-2025 benchmarks: **83.4% precision**, **4,561 triples/doc** uplift[1].

#### **1. Parsing Pipeline (Modular + VLM Hybrid)**
- **Step 1: Layout Grid Projection** (LiteParse[3]/LlamaParse[8] core): Project INDEX.md text to **virtual char grid** (e.g., 100x50 cells). Retains **tabs, headers, merged cells** without Markdown loss.  
  **Code frame**:
  ```
  from llama_index.parse import LiteParse
  parser = LiteParse(grid_res=0.1)  # 0.1px precision
  grid_output = parser.parse("INDEX.md")  # Outputs: {"cells": [...], "bbox": [...]}
  ```
  **Win**: **100% column survival** post-chunking; agents reason on structure, not infer[3].
- **Step 2: Triple Extraction** (Schema-induced[1]): Cluster types (e.g., "Button" → canonical schema), prompt LLM: "Extract <Component, Variant, Direction> triples."  
  **Schema prompt**: "From grid: {grid}, infer triples like (Button.Primary, color:#blue, dir:compact)."  
  **Output**: Neo4j/JSON graph: **10-20% precision/recall gain** vs. flat text[1].
- **Step 3: Chunk + Embed**: **Hierarchical chunks** – grid cells → semantic chunks (512 tokens) → LanceDB vector index. Map to orig bbox[3][4].

| Parser | Strengths | Cost/Metrics | Use Case |
|--------|-----------|--------------|----------|
| **LiteParse Grid** [3] | Layout fidelity, no interp errors | Free/local, 100% struct pres. | INDEX.md tables/tabs |
| **Bedrock FM Parser** [6] | Multimodal (img/code), custom prompt | $0.01/1k tokens | Complex DS visuals |
| **LlamaParse** [8] | Agentic OCR + extract | Enterprise, 95%+ table acc. | Prod DS routing |

#### **2. Automated Design Direction Routing Framework**
**Two-stage agent**: Vector search → SQL/graph fallback. Routes parsed triples to **design actions** (e.g., "Generate Button.Primary compact variant").

- **Retrieval Layer** (LanceDB[3]):
  1. **Text vec search**: Query "compact button direction" → top-5 grid chunks (cosine sim >0.8).
  2. **Image fallback**: If ambiguity, fetch bbox screenshot → VLM verify ("Is this compact?")[3].
  3. **Exhaustive mode**: SQL on triples: `SELECT * FROM components WHERE variant='Primary' AND dir='compact'` → **fixes 100% aggregation fails**[3].
- **Routing Logic** (Claude/Llama agent prompt):
  ```
  Query: {q}
  1. Text chunks sufficient? → Reason + output direction JSON.
  2. Else: Image + SQL → Extract {component, props, direction}.
  3. Route: If "compact" → Figma API gen; else → Tailwind CSS.
  ```
  **Eval wins**: **100% disambig** on dupes (e.g., near-identical variants); **half queries use img** for verify[3].

**Production Metrics** (2024-25 evals):
- **Precision**: 83.4% triples[1]; Layout: 95%+ (LlamaParse)[8].
- **Speed**: Grid parse <1s/page; Retrieval <50ms/query[3].
- **Scale**: 10k+ DS docs → Bedrock KB auto-chunk[5][6].

#### **3. Implementation Stack (2024 Prod-Ready)**
```
INDEX.md → LiteParse grid → Triple extract (Claude3.5) → LanceDB (vec+SQL) → Agent route → Figma/DS gen.
```
- **Open-source**: LlamaIndex LiteParse[3][8] + LanceDB.
- **Cloud**: Bedrock advanced parsing (default/free for .md)[6] + KB query reform[5].
- **Pitfalls + Fixes**: Vector incompleteness → SQL hybrid[3]; Complex layouts → VLM fallback[2].

**Key ROI**: **Upstream grid invest = 2-5x agent accuracy*

### how to analyze 50+ brand design systems and extract reusable visual patterns programmatically
### 50+ 브랜드 디자인 시스템 분석 & 재사용 패턴 추출 프레임워크

**대규모(50+) 브랜드 디자인 시스템을 프로그램으로 분석해 재사용 가능한 시각 패턴(색상, 타이포, 그리드, 아이콘, 컴포넌트)을 추출하는 5단계 실전 워크플로우. 수동 80% → 자동화 90% 전환으로 1인당 주 5개 시스템 처리 가능.**[1][4]

#### 1. **데이터 수집: 50+ 시스템 크롤링 (Python + Scrapy/Selenium, 1-2일)**
   - **대상 선정**: Googl
===

