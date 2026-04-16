"""
Instagram 자동 포스터 — Meta Graph API
재원+승현+예진이 만든 콘텐츠를 실제로 올린다.

사전 설정 필요:
1. Meta Business Suite → 앱 만들기 → Instagram Basic Display API
2. Instagram Business 계정 연결
3. .env에 META_ACCESS_TOKEN, INSTAGRAM_BUSINESS_ACCOUNT_ID 입력
"""
import os
import json
import time
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

ACCESS_TOKEN = os.getenv("META_ACCESS_TOKEN")
IG_ACCOUNT_ID = os.getenv("INSTAGRAM_BUSINESS_ACCOUNT_ID")
BASE_URL = "https://graph.facebook.com/v19.0"


def _check_credentials():
    if not ACCESS_TOKEN or ACCESS_TOKEN == "여기에_토큰_입력":
        raise ValueError(
            "META_ACCESS_TOKEN 미설정.\n"
            "Meta Business Suite → 설정 → 앱 → 액세스 토큰 발급 후 .env에 입력"
        )
    if not IG_ACCOUNT_ID or IG_ACCOUNT_ID == "여기에_계정ID_입력":
        raise ValueError(
            "INSTAGRAM_BUSINESS_ACCOUNT_ID 미설정.\n"
            "Meta Business Suite → Instagram 계정 → 계정 ID 확인 후 .env에 입력"
        )


def post_image(image_url: str, caption: str, dry_run: bool = False) -> dict:
    """이미지 + 캡션 포스팅"""
    _check_credentials()

    print(f"\n{'='*50}")
    print(f"Instagram 포스팅")
    print(f"캡션 미리보기: {caption[:80]}...")
    print(f"이미지: {image_url}")
    print(f"{'='*50}")

    if dry_run:
        print("⚠️  DRY RUN — 실제 발행 안 함")
        return {"status": "dry_run", "caption": caption}

    # 1단계: 미디어 컨테이너 생성
    container_resp = requests.post(
        f"{BASE_URL}/{IG_ACCOUNT_ID}/media",
        params={
            "image_url": image_url,
            "caption": caption,
            "access_token": ACCESS_TOKEN,
        }
    )
    container_resp.raise_for_status()
    container_id = container_resp.json()["id"]
    print(f"미디어 컨테이너 생성: {container_id}")

    # 2단계: 컨테이너 처리 대기 (최대 30초)
    for _ in range(6):
        time.sleep(5)
        status_resp = requests.get(
            f"{BASE_URL}/{container_id}",
            params={"fields": "status_code", "access_token": ACCESS_TOKEN}
        )
        status = status_resp.json().get("status_code")
        if status == "FINISHED":
            break
        print(f"  처리중... ({status})")

    # 3단계: 게시
    publish_resp = requests.post(
        f"{BASE_URL}/{IG_ACCOUNT_ID}/media_publish",
        params={
            "creation_id": container_id,
            "access_token": ACCESS_TOKEN,
        }
    )
    publish_resp.raise_for_status()
    post_id = publish_resp.json()["id"]
    print(f"✅ 게시 완료: {post_id}")

    return {"status": "published", "post_id": post_id, "caption": caption}


def post_from_queue(queue_file: str, dry_run: bool = False) -> list:
    """큐 파일에서 읽어서 순서대로 포스팅"""
    if not os.path.exists(queue_file):
        print(f"큐 파일 없음: {queue_file}")
        return []

    with open(queue_file, encoding="utf-8") as f:
        queue = json.load(f)

    results = []
    remaining = []

    for item in queue:
        scheduled_at = item.get("scheduled_at")
        if scheduled_at:
            scheduled_dt = datetime.fromisoformat(scheduled_at)
            if datetime.now() < scheduled_dt:
                remaining.append(item)
                continue

        result = post_image(
            image_url=item["image_url"],
            caption=item["caption"],
            dry_run=dry_run
        )
        result["item"] = item
        results.append(result)

        # 게시 간격 (API rate limit 방지)
        time.sleep(3)

    # 처리된 항목 제거하고 큐 업데이트
    with open(queue_file, "w", encoding="utf-8") as f:
        json.dump(remaining, f, ensure_ascii=False, indent=2)

    print(f"\n✅ {len(results)}건 게시 완료, {len(remaining)}건 대기 중")
    return results


def add_to_queue(queue_file: str, image_url: str, caption: str, scheduled_at: str = None):
    """콘텐츠 큐에 추가 (예진이 생성한 캡션 + nano-banana 이미지)"""
    queue = []
    if os.path.exists(queue_file):
        with open(queue_file, encoding="utf-8") as f:
            queue = json.load(f)

    item = {
        "image_url": image_url,
        "caption": caption,
        "scheduled_at": scheduled_at,
        "added_at": datetime.now().isoformat(),
    }
    queue.append(item)

    os.makedirs(os.path.dirname(queue_file), exist_ok=True)
    with open(queue_file, "w", encoding="utf-8") as f:
        json.dump(queue, f, ensure_ascii=False, indent=2)

    print(f"큐 추가: {caption[:50]}... (예약: {scheduled_at or '즉시'})")


if __name__ == "__main__":
    import sys
    dry_run = "--dry-run" in sys.argv
    queue_file = os.path.join(os.path.dirname(__file__), "content_queue.json")
    post_from_queue(queue_file, dry_run=dry_run)
