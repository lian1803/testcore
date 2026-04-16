"""
Gemini Imagen API를 사용한 이미지 자동 생성 모듈.
납품팀 파이프라인에서 콘텐츠 생성 후 호출.
"""

import os
import sys
import json
import base64
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# .env 로드
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)


def generate_image(prompt: str, output_dir: str, filename: str = None) -> str | None:
    """
    Gemini로 이미지 생성. 성공 시 저장 경로 반환, 실패 시 None.

    Args:
        prompt: 이미지 생성 프롬프트 (영어로)
        output_dir: 저장 폴더 경로
        filename: 파일명 (없으면 타임스탐프)

    Returns:
        저장된 이미지 경로 또는 None
    """
    try:
        from google import genai
        from google.genai import types
    except ImportError:
        print("[image_generator] google-genai 미설치. pip install google-genai")
        return None

    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("[image_generator] GOOGLE_API_KEY 없음. 이미지 생성 스킵.")
        return None

    client = genai.Client(api_key=api_key)

    try:
        response = client.models.generate_images(
            model='imagen-3.0-generate-002',
            prompt=prompt,
            config=types.GenerateImagesConfig(
                number_of_images=1,
                aspect_ratio="1:1",  # 인스타그램 기본
                safety_filter_level="block_only_high",
                person_generation="allow_adult"
            )
        )

        if not response.generated_images:
            print("[image_generator] 이미지 생성 실패 (빈 응답)")
            return None

        # 저장
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        if not filename:
            filename = f"img_{datetime.now().strftime('%H%M%S')}.png"

        save_path = Path(output_dir) / filename
        image_bytes = response.generated_images[0].image.image_bytes
        save_path.write_bytes(image_bytes)

        print(f"[image_generator] 저장: {save_path}")
        return str(save_path)

    except Exception as e:
        print(f"[image_generator] 오류: {e}")
        return None


def generate_content_images(content_results: dict, output_dir: str) -> dict:
    """
    납품팀 결과물에서 이미지 프롬프트를 추출하고 생성.

    Args:
        content_results: {
            'instagram': '인스타그램 캡션 텍스트...',
            'blog': '블로그 포스팅 텍스트...',
            'client_name': '업체명',
            'business_type': '업종'
        }
        output_dir: 저장 폴더 경로

    Returns:
        {
            'instagram_image': '파일경로 or None',
            'blog_thumbnail': '파일경로 or None'
        }
    """
    client_name = content_results.get('client_name', '소상공인')
    business_type = content_results.get('business_type', '음식점')

    results = {}

    # 인스타그램 이미지
    instagram_prompt = build_instagram_prompt(
        client_name, business_type,
        content_results.get('instagram', '')
    )
    results['instagram_image'] = generate_image(
        instagram_prompt, output_dir, "instagram.png"
    )

    # 블로그 썸네일
    blog_prompt = build_blog_prompt(
        client_name, business_type,
        content_results.get('blog', '')
    )
    results['blog_thumbnail'] = generate_image(
        blog_prompt, output_dir, "blog_thumbnail.png"
    )

    return results


def build_instagram_prompt(client_name: str, business_type: str, caption: str) -> str:
    """
    인스타그램 피드용 이미지 프롬프트 생성

    Args:
        client_name: 업체명
        business_type: 업종 (예: 카페, 음식점, 뷰티)
        caption: 인스타그램 캡션 텍스트

    Returns:
        Imagen 프롬프트
    """
    return (
        f"Professional Instagram post photo for Korean {business_type} business named {client_name}. "
        f"Clean, modern high-quality photography style. "
        f"Natural lighting, aesthetic composition, Instagram-worthy. "
        f"No text overlay. High quality, vibrant colors. "
        f"Square format (1:1). Professional commercial photography. "
        f"Appealing to Korean audience. Contemporary and trendy."
    )


def build_blog_prompt(client_name: str, business_type: str, blog_text: str) -> str:
    """
    블로그 썸네일용 이미지 프롬프트 생성

    Args:
        client_name: 업체명
        business_type: 업종
        blog_text: 블로그 포스팅 텍스트

    Returns:
        Imagen 프롬프트
    """
    return (
        f"Professional blog thumbnail for Korean {business_type} business named {client_name}. "
        f"Clean white or subtle texture background. "
        f"Eye-catching, professional design. "
        f"No Korean text. Suitable for Naver blog thumbnail. "
        f"Bright, clean, trustworthy and modern aesthetic. "
        f"High quality product or business imagery."
    )
