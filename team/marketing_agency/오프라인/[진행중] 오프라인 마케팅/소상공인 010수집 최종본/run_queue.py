"""
포천 인접 지역 순서대로 자동 실행
"""
import subprocess, sys, datetime

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

QUEUE = ["파주", "고양", "성남", "광주", "이천", "여주"]

for region in QUEUE:
    print(f"\n{'='*50}")
    print(f"  [{datetime.datetime.now().strftime('%H:%M')}] 시작: {region}")
    print(f"{'='*50}")
    subprocess.run([sys.executable, "main_final.py", region], check=False)
    print(f"  [{datetime.datetime.now().strftime('%H:%M')}] 완료: {region}")

print("\n모든 지역 완료!")
