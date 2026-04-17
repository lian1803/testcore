@echo off
chcp 65001 > nul
cd /d "%~dp0"

set LOG=run_all_log.txt
echo ============================== >> %LOG%
echo 시작: %date% %time% >> %LOG%
echo ============================== >> %LOG%

set REGIONS=수원 용인 안산 안양 부천 시흥 화성 평택 김포 광명 군포 의왕 오산 과천 안성 천안 아산 청주 충주 공주 보령 서산 당진 홍성 세종 대전

for %%R in (%REGIONS%) do (
    echo.
    echo [%%R] 수집 시작 -- %time%
    echo [%%R] 시작: %time% >> %LOG%
    python main_final.py %%R
    echo [%%R] 완료: %time% >> %LOG%
    echo [%%R] 완료 -- %time%
    echo. >> %LOG%
)

echo ============================== >> %LOG%
echo 전체 완료: %date% %time% >> %LOG%
echo ============================== >> %LOG%

echo.
echo 모든 지역 수집 완료!
pause
