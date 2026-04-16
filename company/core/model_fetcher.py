"""
model_fetcher.py — Sketchfab에서 컨셉 키워드 → 3D 모델(.glb) 자동 검색+다운로드

사용법:
    from core.model_fetcher import search_models, download_model

    # 검색
    results = search_models("cave crystal")
    # → [{"uid": "...", "name": "Cave main chamber", "glb_size": 70934208, ...}]

    # 다운로드 (Sketchfab API 토큰 필요)
    path = download_model(results[0]["uid"], output_dir="./models")
"""
import os
import json
import requests
from typing import List, Dict, Optional


SKETCHFAB_API = "https://api.sketchfab.com/v3"


def search_models(
    keyword: str,
    count: int = 5,
    max_face_count: int = 500000,
    downloadable: bool = True,
) -> List[Dict]:
    """Sketchfab에서 키워드로 3D 모델 검색.

    Args:
        keyword: 검색어 (영문 권장)
        count: 결과 수 (최대 24)
        max_face_count: 폴리곤 상한 (웹 성능용)
        downloadable: 다운로드 가능한 것만

    Returns:
        [{"uid", "name", "thumbnail", "glb_size", "face_count", "license", "viewer_url"}]
    """
    params = {
        "type": "models",
        "q": keyword,
        "downloadable": str(downloadable).lower(),
        "count": count,
        "sort_by": "-likeCount",
    }

    try:
        r = requests.get(f"{SKETCHFAB_API}/search", params=params, timeout=10)
        r.raise_for_status()
        data = r.json()
    except Exception as e:
        print(f"Sketchfab 검색 실패: {e}")
        return []

    results = []
    for model in data.get("results", []):
        archives = model.get("archives", {})
        glb = archives.get("glb", {})
        face_count = glb.get("faceCount", 0) or model.get("faceCount", 0)

        # 폴리곤 상한 필터
        if face_count > max_face_count:
            continue

        # 썸네일
        thumbs = model.get("thumbnails", {}).get("images", [])
        thumb_url = thumbs[0]["url"] if thumbs else ""

        # 라이센스
        license_info = model.get("license", {})

        results.append({
            "uid": model["uid"],
            "name": model["name"],
            "thumbnail": thumb_url,
            "glb_size": glb.get("size", 0),
            "face_count": face_count,
            "license": license_info.get("label", "Unknown"),
            "viewer_url": model.get("viewerUrl", ""),
        })

    return results


def download_model(uid: str, output_dir: str = "./models", token: str = None) -> Optional[str]:
    """Sketchfab에서 GLB 모델 다운로드.

    Args:
        uid: 모델 UID
        output_dir: 저장 경로
        token: Sketchfab API 토큰 (다운로드에 필요)

    Returns:
        저장된 파일 경로 또는 None
    """
    if not token:
        token = os.getenv("SKETCHFAB_API_TOKEN")

    if not token:
        print("SKETCHFAB_API_TOKEN 환경변수가 필요합니다.")
        print("https://sketchfab.com/settings/password 에서 API Token 발급")
        return None

    headers = {"Authorization": f"Token {token}"}

    try:
        # 다운로드 URL 요청
        r = requests.get(
            f"{SKETCHFAB_API}/models/{uid}/download",
            headers=headers,
            timeout=10
        )
        r.raise_for_status()
        download_info = r.json()

        glb_url = download_info.get("glb", {}).get("url")
        if not glb_url:
            print("GLB 다운로드 URL을 찾을 수 없습니다.")
            return None

        # 다운로드
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, f"{uid}.glb")

        print(f"다운로드 중: {output_path}")
        dl = requests.get(glb_url, stream=True, timeout=60)
        dl.raise_for_status()

        with open(output_path, "wb") as f:
            for chunk in dl.iter_content(chunk_size=8192):
                f.write(chunk)

        print(f"완료: {output_path} ({os.path.getsize(output_path) / 1024 / 1024:.1f}MB)")
        return output_path

    except Exception as e:
        print(f"다운로드 실패: {e}")
        return None


# 컨셉 → 검색 키워드 매핑
CONCEPT_KEYWORDS = {
    "cave": "cave underground crystal",
    "ocean": "ocean wave water",
    "forest": "forest tree nature",
    "city": "city skyline building",
    "space": "space planet nebula",
    "mountain": "mountain landscape terrain",
    "flower": "flower bloom botanical",
    "bird": "hummingbird bird wing",
    "crystal": "crystal gem mineral",
    "fabric": "silk fabric cloth",
    "machine": "machine gear mechanical",
    "abstract": "abstract sculpture geometric",
}


def search_by_concept(concept: str, count: int = 3) -> List[Dict]:
    """은유 컨셉 → Sketchfab 키워드 변환 → 검색.

    Args:
        concept: director의 Core metaphor (예: "cave", "ocean", "bird")

    Returns:
        검색 결과 리스트
    """
    keyword = CONCEPT_KEYWORDS.get(concept.lower(), concept)
    return search_models(keyword, count=count)
