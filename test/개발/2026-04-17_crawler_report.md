# 크롤러 검증 리포트 (2026-04-17)

**샘플 크롤링**: 14개 성공 / 0개 실패
**실행 시간**: 332.8초 (23.8초/쿼리 평균)
**생성 시간**: 2026-04-17 06:12:04

---

## 필드별 성공률

| 필드 | 성공/전체 | 성공률 | 상태 |
|------|-----------|--------|------|
| photo_count | 14/14 | 100% | [OK] |
| receipt_review_count | 14/14 | 100% | [OK] |
| visitor_review_count | 14/14 | 100% | [OK] |
| blog_review_count | 14/14 | 100% | [OK] |
| keyword_rating_review_count | 14/14 | 100% | [OK] |
| bookmark_count | 14/14 | 100% | [OK] |
| naver_place_rank | 14/14 | 100% | [OK] |
| has_menu | 14/14 | 100% | [OK] |
| has_hours | 14/14 | 100% | [OK] |
| has_price | 14/14 | 100% | [OK] |
| has_intro | 14/14 | 100% | [OK] |
| has_directions | 14/14 | 100% | [OK] |
| has_booking | 14/14 | 100% | [OK] |
| has_talktalk | 14/14 | 100% | [OK] |
| has_smartcall | 14/14 | 100% | [OK] |
| has_coupon | 14/14 | 100% | [OK] |
| has_news | 14/14 | 100% | [OK] |
| news_last_days | 14/14 | 100% | [OK] |
| has_owner_reply | 14/14 | 100% | [OK] |
| has_instagram | 14/14 | 100% | [OK] |
| has_kakao | 14/14 | 100% | [OK] |
| menu_count | 14/14 | 100% | [OK] |
| has_menu_description | 14/14 | 100% | [OK] |
| intro_text_length | 14/14 | 100% | [OK] |
| directions_text_length | 14/14 | 100% | [OK] |
| keywords | 11/14 | 78% | [WARN] |
| review_texts | 11/14 | 78% | [WARN] |
| photo_urls | 12/14 | 85% | [WARN] |
| owner_reply_rate | 12/14 | 85% | [WARN] |

---

## 완전 누락 필드 (성공률 0%)

없음 [OK]

---

## 불안정 필드 (성공률 50~90%)

- **keywords**: 11/14 (78%)
- **review_texts**: 11/14 (78%)
- **photo_urls**: 12/14 (85%)
- **owner_reply_rate**: 12/14 (85%)

---

## 이상값 발견

### 강남역 고깃집
- photo_count: 범위 오류: 57978 > 10000

### 을지로 감자탕
- photo_count: 범위 오류: 16790 > 10000

### 성수동 카페
- photo_count: 범위 오류: 12652 > 10000

### 강남 한우
- photo_count: 범위 오류: 34424 > 10000

---

## 크롤링 실패 업체

없음 [OK]

---

## 권고사항

**[GO] Phase 2 GO 판정**: 크롤링 성공률 100%, 평균 필드 채움률 98%. 데이터 신뢰도 높음.
2. **불안정 필드 개선**: keywords, review_texts, photo_urls 등의 수집 안정성 개선 필요 (현재 90% 미만).
3. **이상값 검증 강화**: 4개 이상값 발견. 범위/타입 검증 로직 보강 필요.

---

## 상세 데이터 (JSON)

```json
{
  "metadata": {
    "total_queries": 14,
    "successful": 14,
    "failed": 0,
    "elapsed_seconds": 332.813271
  },
  "field_stats": {
    "photo_count": {
      "filled": 14,
      "empty": 0,
      "anomaly_count": 4
    },
    "receipt_review_count": {
      "filled": 14,
      "empty": 0,
      "anomaly_count": 0
    },
    "visitor_review_count": {
      "filled": 14,
      "empty": 0,
      "anomaly_count": 0
    },
    "blog_review_count": {
      "filled": 14,
      "empty": 0,
      "anomaly_count": 0
    },
    "keyword_rating_review_count": {
      "filled": 14,
      "empty": 0,
      "anomaly_count": 0
    },
    "bookmark_count": {
      "filled": 14,
      "empty": 0,
      "anomaly_count": 0
    },
    "naver_place_rank": {
      "filled": 14,
      "empty": 0,
      "anomaly_count": 0
    },
    "has_menu": {
      "filled": 14,
      "empty": 0,
      "anomaly_count": 0
    },
    "has_hours": {
      "filled": 14,
      "empty": 0,
      "anomaly_count": 0
    },
    "has_price": {
      "filled": 14,
      "empty": 0,
      "anomaly_count": 0
    },
    "has_intro": {
      "filled": 14,
      "empty": 0,
      "anomaly_count": 0
    },
    "has_directions": {
      "filled": 14,
      "empty": 0,
      "anomaly_count": 0
    },
    "has_booking": {
      "filled": 14,
      "empty": 0,
      "anomaly_count": 0
    },
    "has_talktalk": {
      "filled": 14,
      "empty": 0,
      "anomaly_count": 0
    },
    "has_smartcall": {
      "filled": 14,
      "empty": 0,
      "anomaly_count": 0
    },
    "has_coupon": {
      "filled": 14,
      "empty": 0,
      "anomaly_count": 0
    },
    "has_news": {
      "filled": 14,
      "empty": 0,
      "anomaly_count": 0
    },
    "news_last_days": {
      "filled": 14,
      "empty": 0,
      "anomaly_count": 0
    },
    "has_owner_reply": {
      "filled": 14,
      "empty": 0,
      "anomaly_count": 0
    },
    "has_instagram": {
      "filled": 14,
      "empty": 0,
      "anomaly_count": 0
    },
    "has_kakao": {
      "filled": 14,
      "empty": 0,
      "anomaly_count": 0
    },
    "menu_count": {
      "filled": 14,
      "empty": 0,
      "anomaly_count": 0
    },
    "has_menu_description": {
      "filled": 14,
      "empty": 0,
      "anomaly_count": 0
    },
    "intro_text_length": {
      "filled": 14,
      "empty": 0,
      "anomaly_count": 0
    },
    "directions_text_length": {
      "filled": 14,
      "empty": 0,
      "anomaly_count": 0
    },
    "keywords": {
      "filled": 11,
      "empty": 3,
      "anomaly_count": 0
    },
    "review_texts": {
      "filled": 11,
      "empty": 3,
      "anomaly_count": 0
    },
    "photo_urls": {
      "filled": 12,
      "empty": 2,
      "anomaly_count": 0
    },
    "owner_reply_rate": {
      "filled": 12,
      "empty": 2,
      "anomaly_count": 0
    }
  }
}
```
