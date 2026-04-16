"""
사용법:
  python input_results.py "미용실 거절, 이유: 비싸다"
  또는:
  python input_results.py  # 입력 프롬프트 나옴

리안이 영업 결과를 팀에게 알려주는 가장 간단한 방법.
결과가 5건 이상 모이면 팀이 자동으로 분석해서 개선한다.
"""

import sys
import os
import io

# Windows 콘솔 인코딩 수정
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 부모 디렉토리를 경로에 추가
sys.path.insert(0, os.path.dirname(__file__))

from teams.offline_marketing import pipeline


def main():
    """
    리안으로부터 결과를 입력받아 ingest_results()에 전달.
    """
    if len(sys.argv) > 1:
        # 명령줄 인자로 전달된 경우
        raw_text = " ".join(sys.argv[1:])
    else:
        # 인터랙티브 입력
        print("\n" + "="*60)
        print("📝 영업 결과 입력")
        print("="*60)
        print("\n리안, 오늘 영업 결과를 입력해줘.")
        print("예시:")
        print("  - 미용실 거절, 이유: 비싸다")
        print("  - 포에트리헤어 계약 성사, 주목패키지")
        print("  - 3건 DM 발송, 1건 답장\n")
        print("리안: ", end="")
        try:
            raw_text = input().strip()
        except EOFError:
            raw_text = ""

    if not raw_text:
        print("입력이 없습니다.")
        return

    # 결과 수집
    print("\n⏳ 결과를 처리 중입니다...")
    status = pipeline.ingest_results(raw_text)

    # 현황 요약 출력
    print(f"\n📊 현재 팀 상태:")
    print(f"  수집 데이터: {status['data_count']}건")
    print(f"  월 계약: {status['kpi']['월계약건수']}건")
    print(f"  현재 버전: {status['current_version']}")

    if status['data_count'] >= 5:
        print(f"\n💡 5건 이상 데이터 수집됨. 다음 실행 시 자동 분석됩니다.")

    print(f"\n✅ 결과가 저장되었습니다.")
    print(f"   파일: {os.path.join(os.path.dirname(__file__), 'teams', 'offline_marketing', 'status.json')}")


if __name__ == "__main__":
    main()
