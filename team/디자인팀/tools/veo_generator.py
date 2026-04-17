#!/usr/bin/env python3
"""
Veo Generator — Imagen 4.0 + Veo 2.0으로 배경 영상 자동 생성
MCP 대용 — Claude가 코드에서 직접 임포트하거나 CLI로 실행

사용법:
  # CLI
  python tools/veo_generator.py "abstract flowing energy, purple cyan magenta" --output bg.mp4

  # Python 임포트
  from tools.veo_generator import generate_hero_video
  path = generate_hero_video("레스토랑 히어로", style="luxury")
"""

import sys, os, time, argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
os.chdir(str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv()

import google.genai as genai
from google.genai import types

# ── 스타일 프리셋 ──────────────────────────────────────────────
STYLE_PRESETS = {
    "abstract_dark": {
        "image_prompt": (
            "Abstract flowing energy streams on pure black background. "
            "Electric purple #8B5CF6, vivid cyan #1ACCE0, hot magenta #EC4899, warm orange #F97316. "
            "Nebula-like swirls, glowing plasma, cinematic composition, 8K, no text."
        ),
        "video_prompt": (
            "Hypnotic flowing energy streams slowly swirling and pulsing. "
            "Colors shift and blend organically. Camera slowly zooms in. "
            "Abstract, atmospheric, no text."
        ),
    },
    "luxury": {
        "image_prompt": (
            "Breathtaking luxury interior at night, warm amber lighting, dark surfaces, "
            "floor-to-ceiling windows, city lights outside, cinematic wide shot, 8K photorealistic."
        ),
        "video_prompt": (
            "Slow cinematic pan through a luxurious interior. "
            "Camera gently drifts forward. Warm golden light reflects. "
            "Atmospheric, elegant, no text."
        ),
    },
    "tech": {
        "image_prompt": (
            "Abstract digital technology background, glowing circuit patterns, "
            "deep navy and electric blue, data visualization aesthetic, 8K, no text."
        ),
        "video_prompt": (
            "Flowing digital data streams, circuit patterns animate and pulse. "
            "Camera slowly orbits. Futuristic, clean, no text."
        ),
    },
    "nature": {
        "image_prompt": (
            "Breathtaking natural landscape at golden hour, sweeping vista, "
            "dramatic light, photorealistic, cinematic 16:9, 8K."
        ),
        "video_prompt": (
            "Slow cinematic drone shot over a beautiful landscape. "
            "Wind moves through grass/water. Golden hour light shifts. No text."
        ),
    },
}

DEFAULT_STYLE = "abstract_dark"


def generate_hero_video(
    description: str = "",
    style: str = DEFAULT_STYLE,
    output_path: str = None,
    duration_seconds: int = 6,
    custom_image_prompt: str = None,
    custom_video_prompt: str = None,
    verbose: bool = True,
) -> str:
    """
    Imagen 4.0으로 이미지 생성 후 Veo 2.0으로 영상 변환.

    Args:
        description: 추가 설명 (프리셋에 덧붙임)
        style: 'abstract_dark' | 'luxury' | 'tech' | 'nature' | 커스텀
        output_path: 저장 경로 (없으면 auto)
        duration_seconds: 영상 길이 (기본 6초)
        custom_image_prompt: 직접 이미지 프롬프트 (style 무시)
        custom_video_prompt: 직접 영상 프롬프트 (style 무시)
        verbose: 진행상황 출력

    Returns:
        생성된 mp4 파일 경로
    """
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise RuntimeError("GOOGLE_API_KEY 없음. .env 확인해.")

    client = genai.Client(api_key=api_key)

    # 프롬프트 결정
    preset = STYLE_PRESETS.get(style, STYLE_PRESETS[DEFAULT_STYLE])
    image_prompt = custom_image_prompt or (
        preset["image_prompt"] + (f" {description}" if description else "")
    )
    video_prompt = custom_video_prompt or (
        preset["video_prompt"] + (f" {description}" if description else "")
    )

    # 출력 경로
    if not output_path:
        ts = int(time.time())
        output_dir = Path(__file__).parent.parent / "tools" / "veo_output"
        output_dir.mkdir(exist_ok=True)
        output_path = str(output_dir / f"hero_{style}_{ts}.mp4")

    if verbose:
        print(f"[Veo Generator] 스타일: {style}")
        print(f"[Step 1/2] Imagen 4.0 이미지 생성 중...")

    # ── Step 1: Imagen으로 이미지 생성 ──
    result = client.models.generate_images(
        model="models/imagen-4.0-generate-001",
        prompt=image_prompt,
        config=types.GenerateImagesConfig(
            number_of_images=1,
            aspect_ratio="16:9",
            output_mime_type="image/jpeg",
        ),
    )
    img_bytes = result.generated_images[0].image.image_bytes

    # 중간 이미지도 저장
    img_path = output_path.replace(".mp4", "_frame.jpg")
    with open(img_path, "wb") as f:
        f.write(img_bytes)
    if verbose:
        print(f"  → 이미지 저장: {img_path} ({len(img_bytes):,} bytes)")
        print(f"[Step 2/2] Veo 2.0 영상 변환 중 (약 2~4분)...")

    # ── Step 2: Veo로 image-to-video ──
    operation = client.models.generate_videos(
        model="models/veo-2.0-generate-001",
        prompt=video_prompt,
        image=types.Image(image_bytes=img_bytes, mime_type="image/jpeg"),
        config=types.GenerateVideosConfig(
            aspect_ratio="16:9",
            duration_seconds=duration_seconds,
            number_of_videos=1,
        ),
    )

    # 폴링
    dots = 0
    while not operation.done:
        time.sleep(10)
        operation = client.operations.get(operation)
        dots += 1
        if verbose:
            print(f"  대기 중{'.' * (dots % 5)}    ", end="\r")

    if verbose:
        print("\n  → 영상 생성 완료!")

    # 다운로드 & 저장
    video = operation.result.generated_videos[0]
    video_data = client.files.download(file=video.video)
    with open(output_path, "wb") as f:
        f.write(video_data)

    size_mb = os.path.getsize(output_path) / 1_000_000
    if verbose:
        print(f"[완료] 저장: {output_path} ({size_mb:.1f} MB)")

    return output_path


# ── CLI ──────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="Veo Generator — Imagen + Veo 영상 생성")
    parser.add_argument("description", nargs="?", default="", help="추가 설명")
    parser.add_argument("--style", default=DEFAULT_STYLE,
                        choices=list(STYLE_PRESETS.keys()),
                        help=f"스타일 프리셋 (기본: {DEFAULT_STYLE})")
    parser.add_argument("--output", default=None, help="출력 파일 경로 (.mp4)")
    parser.add_argument("--duration", type=int, default=6, help="영상 길이 초 (기본: 6)")
    parser.add_argument("--image-prompt", default=None, help="직접 이미지 프롬프트")
    parser.add_argument("--video-prompt", default=None, help="직접 영상 프롬프트")
    parser.add_argument("--list-styles", action="store_true", help="스타일 목록 출력")
    args = parser.parse_args()

    if args.list_styles:
        print("사용 가능한 스타일:")
        for name, preset in STYLE_PRESETS.items():
            print(f"  {name}: {preset['image_prompt'][:60]}...")
        return

    path = generate_hero_video(
        description=args.description,
        style=args.style,
        output_path=args.output,
        duration_seconds=args.duration,
        custom_image_prompt=args.image_prompt,
        custom_video_prompt=args.video_prompt,
    )
    print(f"\n🎬 완료: {path}")


if __name__ == "__main__":
    main()
