import sys
import os
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

from teams.온라인마케팅팀.pipeline import run

if __name__ == "__main__":
    task = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "스마트스토어/쿠팡/인스타 셀러 대상 마케팅 대행 영업 — 구체적 셀러 리드 발굴 → 맞춤 전략 → 콜드메일/DM 전문 작성 → 견적서/계약서까지 바로 실행 가능한 수준으로"
    run(task)
