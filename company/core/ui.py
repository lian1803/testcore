"""터미널 UI 유틸리티 — 진행률, 에러 메시지, 저장 피드백"""

TOTAL_STEPS = 9  # 1.taeho + 2.seoyun + 3.minsu + 4.haeun + 5.junhyeok + 6.jihun + 7.jongbum + 8.sua (시은은 별도)


def print_step(step: int, name: str, role: str) -> None:
    """진행률 헤더 출력. 예: [2/9] 서윤 — 시장조사"""
    print(f"\n{'='*60}")
    print(f"[{step}/{TOTAL_STEPS}] {name} | {role}")
    print(f"{'='*60}")


def print_save_ok(filepath: str) -> None:
    """파일 저장 완료 피드백"""
    filename = filepath.split("\\")[-1].split("/")[-1]
    print(f"  [저장] {filename}")


def print_error(context: str, detail: str, hint: str = "") -> None:
    """에러 메시지 — 원인 + 해결책 포함"""
    print(f"\n[오류] {context}")
    print(f"  원인: {detail}")
    if hint:
        print(f"  해결: {hint}")


def print_api_key_error(key_name: str) -> None:
    print_error(
        f"{key_name} 없음",
        f".env 파일에 {key_name}가 없거나 비어 있어.",
        ".env 파일을 열고 키를 확인해봐. .env.example 참고."
    )


def print_section(title: str) -> None:
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")
