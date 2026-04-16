"""
gen_hero.py — 실물 비즈니스용 히어로 이미지 + 영상 자동 생성
Imagen 4.0으로 히어로 이미지 생성 후 Veo 2.0으로 image-to-video 변환
"""

import sys
import os
import time
from pathlib import Path

_COMPANY_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(_COMPANY_DIR))
os.chdir(str(_COMPANY_DIR))

from dotenv import load_dotenv
load_dotenv()

import google.genai as genai
from google.genai import types


# 업종별 이미지 프롬프트 템플릿
PROMPT_TEMPLATES = {
    "restaurant": (
        "Fine dining restaurant interior, warm amber candlelight, dark wood tables, "
        "city skyline view, cinematic wide shot, photorealistic, 8K, ultra-detailed"
    ),
    "interior": (
        "Luxurious modern interior design showroom, natural light flooding through large windows, "
        "minimalist furniture, editorial photography style, architectural digest quality"
    ),
    "beauty": (
        "High-end beauty salon interior, soft diffused lighting, marble surfaces, "
        "elegant minimalist aesthetic, editorial photography, vogue magazine style"
    ),
    "cafe": (
        "Specialty coffee shop, warm morning light, exposed brick, wooden furniture, "
        "steam rising from cups, cinematic depth of field, photorealistic"
    ),
    "hotel": (
        "Luxury hotel lobby at twilight, dramatic lighting, marble floors, "
        "floral arrangements, cinematic perspective, ultra-high-end hospitality"
    ),
    "fashion": (
        "High-fashion boutique interior, stark white walls, dramatic spotlights, "
        "glass displays, editorial aesthetic, minimalist luxury, vogue style"
    ),
}

# 업종별 영상 프롬프트 템플릿
VIDEO_PROMPT_TEMPLATES = {
    "restaurant": (
        "Slow cinematic push-in toward the dining table, candles flicker gently, "
        "city lights shimmer through the windows, atmospheric and moody"
    ),
    "interior": (
        "Gentle camera drift slowly revealing the space from left to right, "
        "natural light shifts subtly across surfaces, smooth and cinematic"
    ),
    "beauty": (
        "Slow pan across the marble countertops, soft reflections glimmer, "
        "subtle steam or mist rises, elegant and serene atmosphere"
    ),
    "cafe": (
        "Gentle push toward the coffee cup, steam curls gracefully upward, "
        "warm bokeh lights shimmer in background, slow and dreamy"
    ),
    "hotel": (
        "Slow upward tilt revealing the grand lobby, chandelier sparkles, "
        "guests pass in elegant slow motion, cinematic and majestic"
    ),
    "fashion": (
        "Slow lateral dolly past the glass displays, spotlights create dramatic shadows, "
        "fashion items revealed one by one, editorial and sleek"
    ),
}


def generate_hero(business_type: str, description: str, output_dir: str) -> dict:
    """
    실물 비즈니스용 히어로 이미지 + 영상 자동 생성

    Args:
        business_type: "restaurant" | "interior" | "beauty" | "cafe" | "hotel" | "fashion"
        description: 사업 설명 (한국어 가능)
        output_dir: 저장 경로 (절대경로)

    Returns:
        {
            "image_path": "...",
            "video_path": "...",
            "success": True,
            "error": "..." (실패 시)
        }
    """
    result = {
        "image_path": None,
        "video_path": None,
        "success": False,
    }

    # API 키 확인
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        result["error"] = "GOOGLE_API_KEY가 설정되지 않았습니다. .env 파일을 확인하세요."
        return result

    client = genai.Client(api_key=api_key)

    # 출력 폴더 생성
    os.makedirs(output_dir, exist_ok=True)

    # ─── Step 1: 이미지 프롬프트 구성 ───────────────────────────────────────
    base_prompt = PROMPT_TEMPLATES.get(business_type.lower())

    if base_prompt is None:
        # 알 수 없는 업종 → description 기반 프롬프트 자동 생성
        base_prompt = (
            f"Professional commercial photography, high-end business environment, "
            f"cinematic lighting, editorial quality, photorealistic, 8K"
        )

    # description이 있으면 프롬프트에 추가로 구체화
    if description and description.strip():
        image_prompt = f"{base_prompt}, {description.strip()}"
    else:
        image_prompt = base_prompt

    # ─── Step 2: Imagen 4.0으로 이미지 생성 ─────────────────────────────────
    img_bytes = None
    image_path = os.path.join(output_dir, "hero.jpg")

    try:
        print(f"[gen_hero] Imagen 4.0 이미지 생성 중...")
        print(f"[gen_hero] 업종: {business_type}")
        print(f"[gen_hero] 프롬프트: {image_prompt[:100]}...")

        imagen_result = client.models.generate_images(
            model="models/imagen-4.0-generate-001",
            prompt=image_prompt,
            config=types.GenerateImagesConfig(
                number_of_images=1,
                aspect_ratio="16:9",
                output_mime_type="image/jpeg",
            ),
        )

        img_bytes = imagen_result.generated_images[0].image.image_bytes

        with open(image_path, "wb") as f:
            f.write(img_bytes)

        result["image_path"] = image_path
        print(f"[gen_hero] 이미지 저장 완료: {image_path}")

    except Exception as e:
        result["error"] = f"이미지 생성 실패: {str(e)}"
        print(f"[gen_hero] 이미지 생성 실패: {e}")
        return result

    # ─── Step 3: Veo 2.0으로 image-to-video 생성 ────────────────────────────
    video_prompt = VIDEO_PROMPT_TEMPLATES.get(
        business_type.lower(),
        "Slow cinematic camera movement, atmospheric and elegant, smooth motion"
    )

    if description and description.strip():
        video_prompt = f"{video_prompt}, {description.strip()}"

    video_path = os.path.join(output_dir, "hero.mp4")

    try:
        print(f"[gen_hero] Veo 2.0 영상 생성 중 (6초)...")
        print(f"[gen_hero] 영상 프롬프트: {video_prompt[:100]}...")

        operation = client.models.generate_videos(
            model="models/veo-2.0-generate-001",
            prompt=video_prompt,
            image=types.Image(image_bytes=img_bytes, mime_type="image/jpeg"),
            config=types.GenerateVideosConfig(
                aspect_ratio="16:9",
                duration_seconds=6,
                number_of_videos=1,
            ),
        )

        # 완료 대기
        wait_count = 0
        while not operation.done:
            time.sleep(10)
            operation = client.operations.get(operation)
            wait_count += 1
            print(f"[gen_hero] 영상 생성 대기 중... ({wait_count * 10}초 경과)")

        video_data = client.files.download(
            file=operation.result.generated_videos[0].video
        )

        with open(video_path, "wb") as f:
            f.write(bytes(video_data))

        result["video_path"] = video_path
        result["success"] = True
        print(f"[gen_hero] 영상 저장 완료: {video_path}")

    except Exception as e:
        # 영상 생성 실패해도 이미지는 반환
        result["error"] = f"영상 생성 실패 (이미지는 정상): {str(e)}"
        result["success"] = True  # 이미지는 성공했으므로 partial success
        print(f"[gen_hero] 영상 생성 실패 (이미지는 정상 저장됨): {e}")

    return result


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="실물 비즈니스용 히어로 이미지+영상 생성")
    parser.add_argument("business_type", help="업종 (restaurant/interior/beauty/cafe/hotel/fashion)")
    parser.add_argument("--description", "-d", default="", help="사업 설명 (선택)")
    parser.add_argument("--output", "-o", default="./output/hero", help="저장 경로")
    args = parser.parse_args()

    result = generate_hero(
        business_type=args.business_type,
        description=args.description,
        output_dir=os.path.abspath(args.output),
    )

    print("\n" + "=" * 50)
    print("생성 결과:")
    for k, v in result.items():
        print(f"  {k}: {v}")
