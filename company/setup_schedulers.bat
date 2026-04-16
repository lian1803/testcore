@echo off
chcp 65001 > nul
echo.
echo ========================================
echo  리안 컴퍼니 스케줄러 설정
echo ========================================
echo.

:: ── 1. 기존 태스크 정리 ──────────────────────────
echo [1] 기존 스케줄러 정리 중...
powershell -Command "Unregister-ScheduledTask -TaskName 'LianCompany_Daily' -Confirm:$false -ErrorAction SilentlyContinue"
powershell -Command "Unregister-ScheduledTask -TaskName 'LianCompany_DailyAuto' -Confirm:$false -ErrorAction SilentlyContinue"
powershell -Command "Unregister-ScheduledTask -TaskName 'LianCompany_Weekly' -Confirm:$false -ErrorAction SilentlyContinue"
powershell -Command "Unregister-ScheduledTask -TaskName 'LianCompany_WeeklyReview' -Confirm:$false -ErrorAction SilentlyContinue"
echo    완료.

:: ── 2. Daily Auto 등록 (매일 오전 8시) ──────────
echo [2] Daily 스케줄러 등록 중...
powershell -Command ^
    "$action = New-ScheduledTaskAction -Execute 'C:\Users\lian1\Documents\Work\core\company\venv\Scripts\python.exe' -Argument 'daily_auto.py' -WorkingDirectory 'C:\Users\lian1\Documents\Work\core\company'; $trigger = New-ScheduledTaskTrigger -Daily -At '08:00AM'; $settings = New-ScheduledTaskSettingsSet -ExecutionTimeLimit (New-TimeSpan -Hours 2) -StartWhenAvailable; Register-ScheduledTask -TaskName 'LianCompany_DailyAuto' -Action $action -Trigger $trigger -Settings $settings -Description '리안 컴퍼니 일일 자동 실행 — 매일 오전 8시' -RunLevel Limited | Out-Null; Write-Host '   Daily 등록 완료'"
echo    완료.

:: ── 3. Weekly Review 등록 (매주 월요일 오전 10시) ──
echo [3] Weekly 스케줄러 등록 중...
powershell -Command ^
    "$action = New-ScheduledTaskAction -Execute 'C:\Users\lian1\Documents\Work\core\company\venv\Scripts\python.exe' -Argument 'weekly_runner.py' -WorkingDirectory 'C:\Users\lian1\Documents\Work\core\company'; $trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Monday -At '10:00AM'; $settings = New-ScheduledTaskSettingsSet -ExecutionTimeLimit (New-TimeSpan -Hours 2) -StartWhenAvailable; Register-ScheduledTask -TaskName 'LianCompany_WeeklyReview' -Action $action -Trigger $trigger -Settings $settings -Description '리안 컴퍼니 주간 리뷰 — 매주 월요일 오전 10시' -RunLevel Limited | Out-Null; Write-Host '   Weekly 등록 완료'"
echo    완료.

:: ── 4. 등록 현황 출력 ───────────────────────────
echo.
echo [4] 등록된 스케줄러 현황:
powershell -Command ^
    "Get-ScheduledTask | Where-Object TaskName -like '*Lian*' | ForEach-Object { $info = $_ | Get-ScheduledTaskInfo; Write-Host \"  $($_.TaskName) | $($_.State) | 다음실행: $($info.NextRunTime)\" }"

echo.
echo ========================================
echo  설정 완료
echo  - Daily: 매일 오전 8시 (daily_auto.py)
echo  - Weekly: 매주 월요일 오전 10시 (weekly_runner.py)
echo ========================================
echo.
pause
