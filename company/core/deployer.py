import os
import subprocess
import sys
from typing import Optional

CLOUDFLARE_API_TOKEN = os.getenv("CLOUDFLARE_API_TOKEN", "")
CLOUDFLARE_ACCOUNT_ID = os.getenv("CLOUDFLARE_ACCOUNT_ID", "")
CF_PROJECT_NAME = os.getenv("CF_PROJECT_NAME", "")


def deploy(project_dir: str, dry_run: bool = True) -> bool:
    """Cloudflare Pages에 배포

    Args:
        project_dir: 배포할 프로젝트 경로 (CLAUDE.md가 있는 폴더)
        dry_run: True일 때는 실제 배포 안 하고 명령만 출력

    Returns:
        성공 여부
    """
    if not CLOUDFLARE_API_TOKEN:
        print("⚠️  CLOUDFLARE_API_TOKEN 미설정 — 배포 스킵")
        return False

    if not CF_PROJECT_NAME:
        print("⚠️  CF_PROJECT_NAME 미설정 — 배포 스킵")
        return False

    # wrangler.toml 확인
    wrangler_path = os.path.join(project_dir, "wrangler.toml")
    if not os.path.exists(wrangler_path):
        print(f"⚠️  wrangler.toml 없음 — 배포 스킵: {project_dir}")
        return False

    try:
        # wrangler 설치 확인
        result = subprocess.run(
            ["wrangler", "--version"],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode != 0:
            print("⚠️  wrangler CLI 미설치 — 배포 스킵")
            return False

        # 배포 명령 구성
        deploy_cmd = [
            "wrangler",
            "pages",
            "deploy",
            os.path.join(project_dir, "dist"),  # 빌드 결과물 경로
            "--project-name", CF_PROJECT_NAME,
        ]

        if dry_run:
            print(f"🔍 [DRY RUN] 배포 명령: {' '.join(deploy_cmd)}")
            print(f"📁 프로젝트 디렉토리: {project_dir}")
            print(f"📦 배포 대상: {os.path.join(project_dir, 'dist')}")
            return True

        # 실제 배포
        print(f"🚀 Cloudflare Pages 배포 시작...")
        print(f"📦 프로젝트: {CF_PROJECT_NAME}")

        result = subprocess.run(
            deploy_cmd,
            cwd=project_dir,
            timeout=300,
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            print(f"✅ 배포 완료!")
            if result.stdout:
                print(result.stdout)
            return True
        else:
            print(f"❌ 배포 실패:")
            if result.stderr:
                print(result.stderr)
            return False

    except subprocess.TimeoutExpired:
        print("❌ 배포 타임아웃 (5분 초과)")
        return False
    except FileNotFoundError:
        print("❌ wrangler 명령 실행 불가 — PATH 설정 확인")
        return False
    except Exception as e:
        print(f"❌ 배포 중 오류: {e}")
        return False


def build_before_deploy(project_dir: str, build_cmd: str = "npm run build") -> bool:
    """배포 전 빌드

    Args:
        project_dir: 프로젝트 경로
        build_cmd: 빌드 명령 (기본: npm run build)

    Returns:
        성공 여부
    """
    try:
        print(f"🏗️  빌드 시작: {build_cmd}")
        result = subprocess.run(
            build_cmd.split(),
            cwd=project_dir,
            timeout=600,
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            print(f"✅ 빌드 완료")
            return True
        else:
            print(f"❌ 빌드 실패:")
            if result.stderr:
                print(result.stderr)
            return False

    except subprocess.TimeoutExpired:
        print("❌ 빌드 타임아웃 (10분 초과)")
        return False
    except Exception as e:
        print(f"❌ 빌드 중 오류: {e}")
        return False
