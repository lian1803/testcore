# -*- coding: utf-8 -*-
"""
경쟁사 자동 모니터링 시스템 - 재원 담당
Databox / Whatagraph / AgencyAnalytics 스크랩 -> 변경 감지 -> 보고사항들.md 알림

실행:
    company/venv/Scripts/python.exe company/auto_competitor_watch.py
"""

import io
import sys
# Windows 콘솔 인코딩 강제 UTF-8
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
if sys.stderr.encoding and sys.stderr.encoding.lower() != 'utf-8':
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import os
import json
import time
import hashlib
import re
from datetime import datetime

import requests
from bs4 import BeautifulSoup

# ── 경로 설정 ────────────────────────────────────────────────────────────────
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SCRIPT_DIR)
SNAPSHOT_PATH = os.path.join(SCRIPT_DIR, "knowledge", "base", "competitor_snapshots.json")
REPORT_PATH = os.path.join(ROOT_DIR, "보고사항들.md")

# ── 모니터링 대상 ────────────────────────────────────────────────────────────
COMPETITORS = [
    {
        "name": "Databox",
        "urls": [
            {"label": "홈", "url": "https://databox.com"},
            {"label": "가격", "url": "https://databox.com/pricing"},
        ],
    },
    {
        "name": "Whatagraph",
        "urls": [
            {"label": "홈", "url": "https://whatagraph.com"},
        ],
    },
    {
        "name": "AgencyAnalytics",
        "urls": [
            {"label": "홈", "url": "https://agencyanalytics.com"},
            {"label": "가격", "url": "https://agencyanalytics.com/pricing"},
        ],
    },
]

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}


# ── 스크래핑 ─────────────────────────────────────────────────────────────────

def _clean_text(text: str) -> str:
    """공백/개행 정규화."""
    return re.sub(r"\s+", " ", text).strip()


def scrape_page(url: str) -> dict:
    """한 페이지에서 핵심 텍스트 추출."""
    try:
        resp = requests.get(url, headers=HEADERS, timeout=20)
        resp.raise_for_status()
    except Exception as e:
        return {"error": str(e), "url": url}

    soup = BeautifulSoup(resp.text, "lxml")

    # 불필요한 태그 제거
    for tag in soup(["script", "style", "noscript", "svg", "img", "iframe", "footer", "nav"]):
        tag.decompose()

    result = {"url": url, "scraped_at": datetime.now().isoformat()}

    # 1. Hero 헤드라인 -h1, 그 다음 h2/h3 순서로
    headline = ""
    for selector in ["h1", "h2", "[class*='hero'] *", "[class*='headline'] *"]:
        el = soup.select_one(selector)
        if el:
            text = _clean_text(el.get_text())
            if len(text) > 10:
                headline = text[:300]
                break
    result["hero_headline"] = headline

    # 2. 서브 헤드라인 (처음 3개 h2)
    h2_texts = []
    for el in soup.find_all("h2")[:5]:
        t = _clean_text(el.get_text())
        if len(t) > 8:
            h2_texts.append(t[:200])
    result["sub_headlines"] = h2_texts

    # 3. 가격 플랜 -price/plan 관련 텍스트 블록
    price_hints = []
    price_patterns = re.compile(
        r"(\$[\d,]+|KRW[\d,]+|EUR[\d,]+|per\s+month|\/mo|\/year|free\s+trial|free\s+plan|starter|pro\s+plan|business|enterprise|growth)",
        re.I,
    )
    for el in soup.find_all(string=price_patterns):
        parent = el.parent
        if parent:
            t = _clean_text(parent.get_text())
            if 5 < len(t) < 300 and t not in price_hints:
                price_hints.append(t)
        if len(price_hints) >= 10:
            break
    result["pricing_hints"] = price_hints

    # 4. 주요 기능 키워드 -모든 h3 + li 텍스트에서 짧은 것들
    feature_keywords = []
    for el in soup.find_all(["h3", "h4"])[:20]:
        t = _clean_text(el.get_text())
        if 5 < len(t) < 120:
            feature_keywords.append(t)
    result["feature_keywords"] = feature_keywords[:20]

    # 5. 전체 텍스트 해시 (변경 감지용)
    body_text = _clean_text(soup.get_text())[:5000]
    result["body_hash"] = hashlib.md5(body_text.encode("utf-8")).hexdigest()
    result["body_preview"] = body_text[:500]

    return result


def scrape_competitor(competitor: dict) -> dict:
    """한 경쟁사의 모든 URL 스크랩."""
    pages = {}
    for entry in competitor["urls"]:
        print(f"  [{competitor['name']} / {entry['label']}] 스크랩 중... {entry['url']}")
        pages[entry["label"]] = scrape_page(entry["url"])
        time.sleep(2)  # 서버 부하 방지
    return pages


# ── 스냅샷 관리 ──────────────────────────────────────────────────────────────

def load_snapshots() -> dict:
    if os.path.exists(SNAPSHOT_PATH):
        try:
            with open(SNAPSHOT_PATH, encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def save_snapshots(snapshots: dict):
    os.makedirs(os.path.dirname(SNAPSHOT_PATH), exist_ok=True)
    with open(SNAPSHOT_PATH, "w", encoding="utf-8") as f:
        json.dump(snapshots, f, ensure_ascii=False, indent=2)
    print(f"[스냅샷] 저장 완료: {SNAPSHOT_PATH}")


# ── 변경 감지 ────────────────────────────────────────────────────────────────

def detect_changes(old: dict, new: dict) -> list[str]:
    """두 스냅샷을 비교해 변경사항 목록 반환."""
    changes = []

    for label, new_page in new.items():
        if "error" in new_page:
            continue
        old_page = old.get(label, {})

        # Hero 헤드라인 변경
        if new_page.get("hero_headline") and new_page["hero_headline"] != old_page.get("hero_headline"):
            changes.append(
                f"**Hero 헤드라인 변경** [{label}]\n"
                f"  이전: {old_page.get('hero_headline', '(없음)')}\n"
                f"  현재: {new_page['hero_headline']}"
            )

        # body 해시 변경 (전반적 내용 변경)
        if new_page.get("body_hash") and new_page["body_hash"] != old_page.get("body_hash"):
            # 사소한 변경일 수도 있으니 헤드라인 변경이 없어도 기록
            if not any("헤드라인" in c and f"[{label}]" in c for c in changes):
                changes.append(
                    f"**페이지 내용 변경 감지** [{label}]\n"
                    f"  (세부 내용 확인 필요 -직접 방문 권장)"
                )

        # 가격 힌트 변경
        old_prices = set(old_page.get("pricing_hints", []))
        new_prices = set(new_page.get("pricing_hints", []))
        added_prices = new_prices - old_prices
        removed_prices = old_prices - new_prices
        if added_prices:
            for p in list(added_prices)[:3]:
                changes.append(f"**가격 정보 추가** [{label}]: {p[:150]}")
        if removed_prices:
            for p in list(removed_prices)[:3]:
                changes.append(f"**가격 정보 삭제** [{label}]: {p[:150]}")

        # 기능 키워드 변경
        old_features = set(old_page.get("feature_keywords", []))
        new_features = set(new_page.get("feature_keywords", []))
        added_features = new_features - old_features
        removed_features = old_features - new_features
        if added_features:
            for f_kw in list(added_features)[:3]:
                changes.append(f"**새 기능 키워드** [{label}]: {f_kw[:100]}")
        if removed_features:
            for f_kw in list(removed_features)[:3]:
                changes.append(f"**기능 키워드 삭제** [{label}]: {f_kw[:100]}")

    return changes


# ── 보고 ────────────────────────────────────────────────────────────────────

def write_report(changes_by_company: dict[str, list[str]]):
    """변경사항을 보고사항들.md에 추가."""
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    total = sum(len(v) for v in changes_by_company.values())

    lines = [
        f"\n\n## [재원] 경쟁사 변동 감지 -{now_str}\n",
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n",
        f"총 **{total}건** 변경 감지됨\n",
    ]

    for company, changes in changes_by_company.items():
        if not changes:
            continue
        lines.append(f"\n### {company} ({len(changes)}건)\n")
        for i, ch in enumerate(changes, 1):
            lines.append(f"{i}. {ch}\n")

    lines.append(f"\n스냅샷 저장 위치: `company/knowledge/base/competitor_snapshots.json`\n")
    lines.append(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")

    report_text = "".join(lines)

    # 파일에 추가
    os.makedirs(os.path.dirname(REPORT_PATH), exist_ok=True)
    with open(REPORT_PATH, "a", encoding="utf-8") as f:
        f.write(report_text)

    print(f"\n[보고] 보고사항들.md에 추가 완료 ({total}건)")
    print(report_text)


def write_initial_report(snapshot: dict):
    """최초 스냅샷 저장 시 보고."""
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    lines = [
        f"\n\n## [재원] 경쟁사 모니터링 초기화 완료 -{now_str}\n",
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n",
        f"초기 스냅샷 저장 완료. 다음 실행 시부터 변경 감지 시작.\n\n",
    ]

    for company_name, pages in snapshot.items():
        lines.append(f"**{company_name}**\n")
        for label, page in pages.items():
            if "error" in page:
                lines.append(f"  - [{label}] 스크랩 실패: {page['error']}\n")
            else:
                headline = page.get("hero_headline", "(없음)")
                lines.append(f"  - [{label}] Hero: {headline[:100]}\n")
        lines.append("\n")

    lines.append(f"스냅샷: `company/knowledge/base/competitor_snapshots.json`\n")
    lines.append(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")

    report_text = "".join(lines)
    with open(REPORT_PATH, "a", encoding="utf-8") as f:
        f.write(report_text)

    print(report_text)


# ── 메인 ─────────────────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("[재원] 경쟁사 모니터링 시작")
    print("=" * 60)

    old_snapshots = load_snapshots()
    is_initial = len(old_snapshots) == 0

    new_snapshots = {}
    for competitor in COMPETITORS:
        print(f"\n[{competitor['name']}] 스크랩 시작")
        pages = scrape_competitor(competitor)
        new_snapshots[competitor["name"]] = pages

    if is_initial:
        print("\n[초기화] 첫 실행 -스냅샷 저장 후 종료")
        save_snapshots(new_snapshots)
        write_initial_report(new_snapshots)
        return

    # 변경 감지
    changes_by_company = {}
    for competitor in COMPETITORS:
        name = competitor["name"]
        old_pages = old_snapshots.get(name, {})
        new_pages = new_snapshots.get(name, {})
        changes = detect_changes(old_pages, new_pages)
        changes_by_company[name] = changes
        if changes:
            print(f"  [{name}] {len(changes)}건 변경 감지!")
        else:
            print(f"  [{name}] 변경 없음")

    total_changes = sum(len(v) for v in changes_by_company.values())

    # 스냅샷 업데이트
    save_snapshots(new_snapshots)

    if total_changes > 0:
        write_report(changes_by_company)
    else:
        print("\n변경사항 없음 -보고사항들.md 업데이트 생략")

    print("\n[재원] 모니터링 완료")


if __name__ == "__main__":
    main()
