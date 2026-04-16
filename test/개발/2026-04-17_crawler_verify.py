"""
네이버 플레이스 크롤러 검증 테스트
- 다양한 업종/지역의 15개 샘플 크롤링
- 21개 필드 검증
- 결과를 마크다운 리포트로 저장
"""
import asyncio
import sys
import json
from pathlib import Path
from datetime import datetime
import time

# 프로젝트 경로 설정
PROJECT_PATH = Path(__file__).parent.parent.parent / "team" / "[진행중] 오프라인 마케팅" / "소상공인_영업툴" / "naver-diagnosis"
sys.path.insert(0, str(PROJECT_PATH))

from services.naver_place_crawler import NaverPlaceCrawler
from playwright.async_api import async_playwright


# 테스트 쿼리: 다양한 업종·지역
TEST_QUERIES = [
    # 미용실
    "강남역 미용실",
    "홍대 입구 미용실",
    # 네일
    "강남 네일샵",
    # 피부관리
    "강남 피부관리숍",
    # 음식점
    "강남역 고깃집",
    "홍대 이태리안",
    "을지로 감자탕",
    # 카페
    "성수동 카페",
    "홍대 카페",
    # 학원
    "목동 수학학원",
    # 헬스장/필라테스
    "강남 필라테스",
    # 병원
    "강남역 피부과",
    # 자유 추가
    "강남 한우",
    "을지로 라면",
]

# 검증할 필드 (21개 기본 필드)
REQUIRED_FIELDS = [
    "photo_count",
    "receipt_review_count",
    "visitor_review_count",
    "blog_review_count",
    "keyword_rating_review_count",
    "bookmark_count",
    "naver_place_rank",
    "has_menu",
    "has_hours",
    "has_price",
    "has_intro",
    "has_directions",
    "has_booking",
    "has_talktalk",
    "has_smartcall",
    "has_coupon",
    "has_news",
    "news_last_days",
    "has_owner_reply",
    "has_instagram",
    "has_kakao",
    # 추가 필드
    "menu_count",
    "has_menu_description",
    "intro_text_length",
    "directions_text_length",
    "keywords",
    "review_texts",
    "photo_urls",
    "owner_reply_rate",
]

# 예상 필드 타입 및 범위
FIELD_SPECS = {
    "photo_count": {"type": int, "min": 0, "max": 10000},
    "receipt_review_count": {"type": int, "min": 0},
    "visitor_review_count": {"type": int, "min": 0},
    "blog_review_count": {"type": int, "min": 0},
    "keyword_rating_review_count": {"type": int, "min": 0},
    "bookmark_count": {"type": int, "min": 0},
    "naver_place_rank": {"type": int, "min": 0},
    "has_menu": {"type": bool},
    "has_hours": {"type": bool},
    "has_price": {"type": bool},
    "has_intro": {"type": bool},
    "has_directions": {"type": bool},
    "has_booking": {"type": bool},
    "has_talktalk": {"type": bool},
    "has_smartcall": {"type": bool},
    "has_coupon": {"type": bool},
    "has_news": {"type": bool},
    "news_last_days": {"type": int, "min": 0},
    "has_owner_reply": {"type": bool},
    "has_instagram": {"type": bool},
    "has_kakao": {"type": bool},
    "menu_count": {"type": int, "min": 0},
    "has_menu_description": {"type": bool},
    "intro_text_length": {"type": int, "min": 0},
    "directions_text_length": {"type": int, "min": 0},
    "keywords": {"type": list},
    "review_texts": {"type": list},
    "photo_urls": {"type": list},
    "owner_reply_rate": {"type": (int, float), "min": 0, "max": 1},
}


class CrawlerValidator:
    def __init__(self):
        self.results = []
        self.field_stats = {field: {"filled": 0, "empty": 0, "anomalies": []} for field in REQUIRED_FIELDS}
        self.failed_queries = []
        self.start_time = None

    async def run(self):
        """테스트 실행"""
        self.start_time = datetime.now()
        browser = None

        try:
            # Playwright 초기화
            playwright = await async_playwright().start()
            browser = await playwright.chromium.launch(
                headless=True,
                args=[
                    "--no-sandbox",
                    "--disable-setuid-sandbox",
                    "--disable-dev-shm-usage",
                    "--disable-gpu",
                ],
            )
            crawler = NaverPlaceCrawler(browser)

            print(f"\n{'='*60}")
            print(f"크롤러 검증 시작 - {len(TEST_QUERIES)}개 쿼리")
            print(f"{'='*60}\n")

            for idx, query in enumerate(TEST_QUERIES, 1):
                print(f"\n[{idx}/{len(TEST_QUERIES)}] {query}")
                print("-" * 40)

                try:
                    # 크롤링 실행
                    result = await crawler.crawl_from_search(query)

                    # 결과 검증
                    validation = self._validate_result(query, result)
                    self.results.append(validation)

                    # 진행 상황 출력
                    filled_count = sum(1 for f in REQUIRED_FIELDS if result.get(f) is not None and result.get(f) != 0 and result.get(f) != [])
                    print(f"[OK] 필드 채움율: {filled_count}/{len(REQUIRED_FIELDS)} ({filled_count*100//len(REQUIRED_FIELDS)}%)")

                except Exception as e:
                    print(f"[FAIL] 크롤링 실패: {e}")
                    self.failed_queries.append({"query": query, "error": str(e)})

                # 크롤링 간 딜레이 (봇 탐지 방지)
                if idx < len(TEST_QUERIES):
                    wait_time = 3 + (hash(query) % 3)  # 3~5초
                    print(f"대기 중 ({wait_time}초)...")
                    await asyncio.sleep(wait_time)

            # 리포트 생성
            await self._generate_report()

        finally:
            if browser:
                await browser.close()
                await playwright.stop()
                print("\n브라우저 종료")

    def _validate_result(self, query: str, result: dict) -> dict:
        """단일 결과 검증"""
        validation = {
            "query": query,
            "status": "success" if result.get("place_id") else "partial",
            "place_id": result.get("place_id"),
            "fields": {},
            "issues": [],
        }

        for field in REQUIRED_FIELDS:
            value = result.get(field)
            spec = FIELD_SPECS.get(field, {})
            field_validation = {
                "value": value,
                "status": "filled",
                "issue": None,
            }

            # 값 존재 여부
            if value is None or value == "" or value == []:
                field_validation["status"] = "empty"
                self.field_stats[field]["empty"] += 1
            else:
                self.field_stats[field]["filled"] += 1

                # 타입 검증
                expected_type = spec.get("type")
                if expected_type and not isinstance(value, expected_type):
                    field_validation["issue"] = f"타입 오류: {type(value).__name__} (기대: {expected_type})"
                    self.field_stats[field]["anomalies"].append(field_validation["issue"])
                    validation["issues"].append(f"{field}: {field_validation['issue']}")

                # 범위 검증
                if "min" in spec and isinstance(value, (int, float)):
                    if value < spec["min"]:
                        field_validation["issue"] = f"범위 오류: {value} < {spec['min']}"
                        self.field_stats[field]["anomalies"].append(field_validation["issue"])
                        validation["issues"].append(f"{field}: {field_validation['issue']}")

                if "max" in spec and isinstance(value, (int, float)):
                    if value > spec["max"]:
                        field_validation["issue"] = f"범위 오류: {value} > {spec['max']}"
                        self.field_stats[field]["anomalies"].append(field_validation["issue"])
                        validation["issues"].append(f"{field}: {field_validation['issue']}")

            validation["fields"][field] = field_validation

        return validation

    async def _generate_report(self):
        """마크다운 리포트 생성"""
        elapsed = (datetime.now() - self.start_time).total_seconds()
        # UTF-8 인코딩 강제 설정
        import sys
        if hasattr(sys.stdout, 'reconfigure'):
            sys.stdout.reconfigure(encoding='utf-8')

        report_lines = [
            "# 크롤러 검증 리포트 (2026-04-17)",
            "",
            f"**샘플 크롤링**: {len(self.results)}개 성공 / {len(self.failed_queries)}개 실패",
            f"**실행 시간**: {elapsed:.1f}초 ({elapsed/len(TEST_QUERIES):.1f}초/쿼리 평균)",
            f"**생성 시간**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "---",
            "",
            "## 필드별 성공률",
            "",
            "| 필드 | 성공/전체 | 성공률 | 상태 |",
            "|------|-----------|--------|------|",
        ]

        # 필드별 성공률 테이블
        for field in REQUIRED_FIELDS:
            stats = self.field_stats[field]
            filled = stats["filled"]
            total = len(self.results)
            rate = (filled * 100 // total) if total > 0 else 0

            status = "[OK]"
            if rate == 0:
                status = "[MISSING]"
            elif rate < 50:
                status = "[UNSTABLE]"
            elif rate < 90:
                status = "[WARN]"

            report_lines.append(f"| {field} | {filled}/{total} | {rate}% | {status} |")

        report_lines.extend([
            "",
            "---",
            "",
            "## 완전 누락 필드 (성공률 0%)",
            "",
        ])

        missing_fields = [f for f in REQUIRED_FIELDS if self.field_stats[f]["filled"] == 0]
        if missing_fields:
            for field in missing_fields:
                report_lines.append(f"- **{field}**: 0/{len(self.results)}")
        else:
            report_lines.append("없음 [OK]")

        report_lines.extend([
            "",
            "---",
            "",
            "## 불안정 필드 (성공률 50~90%)",
            "",
        ])

        unstable_fields = [
            f for f in REQUIRED_FIELDS
            if 0 < self.field_stats[f]["filled"] < len(self.results) * 0.9
        ]
        if unstable_fields:
            for field in unstable_fields:
                stats = self.field_stats[field]
                rate = stats["filled"] * 100 // len(self.results)
                report_lines.append(f"- **{field}**: {stats['filled']}/{len(self.results)} ({rate}%)")
                if stats["anomalies"]:
                    for anomaly in stats["anomalies"][:3]:  # 최대 3개만
                        report_lines.append(f"  - {anomaly}")
        else:
            report_lines.append("없음 [OK]")

        report_lines.extend([
            "",
            "---",
            "",
            "## 이상값 발견",
            "",
        ])

        anomalies_found = False
        for validation in self.results:
            if validation["issues"]:
                anomalies_found = True
                report_lines.append(f"### {validation['query']}")
                for issue in validation["issues"]:
                    report_lines.append(f"- {issue}")
                report_lines.append("")

        if not anomalies_found:
            report_lines.append("없음 [OK]")
            report_lines.append("")

        report_lines.extend([
            "---",
            "",
            "## 크롤링 실패 업체",
            "",
        ])

        if self.failed_queries:
            for fail in self.failed_queries:
                report_lines.append(f"- **{fail['query']}**: {fail['error']}")
            report_lines.append("")
        else:
            report_lines.append("없음 [OK]")
            report_lines.append("")

        report_lines.extend([
            "---",
            "",
            "## 권고사항",
            "",
        ])

        recommendations = []

        # 권고 1: 완전 누락
        if missing_fields:
            recommendations.append(f"1. **완전 누락 필드 수정 필수**: {', '.join(missing_fields[:5])} 등 {len(missing_fields)}개 필드가 수집되지 않음. CSS 셀렉터/정규식 검증 필요.")

        # 권고 2: 불안정 필드
        if unstable_fields:
            recommendations.append(f"2. **불안정 필드 개선**: {', '.join(unstable_fields[:3])} 등의 수집 안정성 개선 필요 (현재 90% 미만).")

        # 권고 3: 이상값
        anomaly_count = sum(len(v["issues"]) for v in self.results)
        if anomaly_count > 0:
            recommendations.append(f"3. **이상값 검증 강화**: {anomaly_count}개 이상값 발견. 범위/타입 검증 로직 보강 필요.")

        # 권고 4: 실패율
        if self.failed_queries:
            fail_rate = len(self.failed_queries) * 100 / len(TEST_QUERIES)
            recommendations.append(f"4. **크롤링 실패 분석**: {fail_rate:.0f}% 실패율 발생. 네트워크 타임아웃/봇 탐지 리스크 확인 필요.")

        # 권고 5: 성공 평가
        success_rate = len(self.results) * 100 / len(TEST_QUERIES)
        avg_fill_rate = sum(
            self.field_stats[f]["filled"] * 100 / len(self.results)
            for f in REQUIRED_FIELDS
        ) / len(REQUIRED_FIELDS)

        if success_rate >= 90 and avg_fill_rate >= 90:
            recommendations.insert(0, f"**[GO] Phase 2 GO 판정**: 크롤링 성공률 {success_rate:.0f}%, 평균 필드 채움률 {avg_fill_rate:.0f}%. 데이터 신뢰도 높음.")
        elif success_rate >= 80 and avg_fill_rate >= 80:
            recommendations.insert(0, f"**[CONDITIONAL] 조건부 진행**: 크롤링 성공률 {success_rate:.0f}%, 필드 채움률 {avg_fill_rate:.0f}%. 위의 권고 완료 후 재검증.")
        else:
            recommendations.insert(0, f"**[HOLD] Phase 2 HOLD**: 크롤링 성공률 {success_rate:.0f}%, 필드 채움률 {avg_fill_rate:.0f}%. 개선 후 재테스트 필수.")

        report_lines.extend(recommendations)

        report_lines.extend([
            "",
            "---",
            "",
            "## 상세 데이터 (JSON)",
            "",
            "```json",
        ])

        # JSON 첨부 (최상위 레벨만 - 과용량 방지)
        json_data = {
            "metadata": {
                "total_queries": len(TEST_QUERIES),
                "successful": len(self.results),
                "failed": len(self.failed_queries),
                "elapsed_seconds": elapsed,
            },
            "field_stats": {
                field: {
                    "filled": stats["filled"],
                    "empty": stats["empty"],
                    "anomaly_count": len(stats["anomalies"]),
                }
                for field, stats in self.field_stats.items()
            },
        }
        report_lines.append(json.dumps(json_data, indent=2, ensure_ascii=False))

        report_lines.extend([
            "```",
            "",
        ])

        # 파일 저장
        report_path = Path(__file__).parent / "2026-04-17_crawler_report.md"
        report_content = "\n".join(report_lines)
        report_path.write_text(report_content, encoding="utf-8")

        print(f"\n{'='*60}")
        print(f"리포트 저장 완료: {report_path}")
        print(f"{'='*60}\n")
        print(report_content)


async def main():
    """메인 실행"""
    validator = CrawlerValidator()
    await validator.run()


if __name__ == "__main__":
    asyncio.run(main())
