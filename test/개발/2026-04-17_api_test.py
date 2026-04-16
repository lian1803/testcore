#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""네이버 API 테스트"""
import asyncio
import httpx
import re
import json
from dotenv import load_dotenv
import os
from pathlib import Path

# naver-diagnosis 디렉토리의 .env 로드
load_dotenv(Path(__file__).parent.parent.parent / "team" / "[진행중] 오프라인 마케팅" / "소상공인_영업툴" / "naver-diagnosis" / ".env")

NAVER_CLIENT_ID = os.getenv("NAVER_CLIENT_ID")
NAVER_CLIENT_SECRET = os.getenv("NAVER_CLIENT_SECRET")

async def test_api():
    """네이버 API 테스트"""
    if not NAVER_CLIENT_ID or not NAVER_CLIENT_SECRET:
        print("[ERROR] NAVER_CLIENT_ID/SECRET 없음")
        return

    api_url = "https://openapi.naver.com/v1/search/local.json"
    headers = {
        "X-Naver-Client-Id": NAVER_CLIENT_ID,
        "X-Naver-Client-Secret": NAVER_CLIENT_SECRET,
    }
    params = {"query": "강남역 미용실", "display": 5}

    print(f"[TEST] {params['query']} 검색")

    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(api_url, headers=headers, params=params)
            print(f"Status: {resp.status_code}")

            if resp.status_code == 200:
                data = resp.json()
                print(f"\n[API Response]")
                print(json.dumps(data, ensure_ascii=False, indent=2)[:1000])

                # place_id 추출 테스트
                for idx, item in enumerate(data.get("items", [])[:3]):
                    title = re.sub(r"<[^>]+>", "", item.get("title", ""))
                    link = item.get("link", "")
                    print(f"\n[Item {idx+1}]")
                    print(f"  Title: {title}")
                    print(f"  Link: {link}")

                    # place_id 추출
                    place_id = None
                    if link:
                        match = re.search(r'/place/(\d+)', link)
                        if match:
                            place_id = match.group(1)
                        elif not match:
                            match = re.search(r'/(\w+)/(\d+)', link)
                            if match and len(match.group(2)) >= 6:
                                place_id = match.group(2)

                    print(f"  Extracted place_id: {place_id}")
            else:
                print(f"Error: {resp.text}")

    except Exception as e:
        print(f"[ERROR] {e}")

if __name__ == "__main__":
    asyncio.run(test_api())
