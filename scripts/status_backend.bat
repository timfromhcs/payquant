@echo off
REM ============================================================
REM PayQuant (PQN) Backend Service Status (Windows) v6.4.0
REM ============================================================
setlocal
cd /d "%~dp0.."

python backend\daemon.py status

echo.
echo [PayQuant] API health check:
powershell -NoProfile -Command "try { $r = Invoke-WebRequest -Uri 'http://127.0.0.1:28377/api/health' -UseBasicParsing -TimeoutSec 4; Write-Output ('API: ' + $r.StatusCode + ' - ' + $r.Content) } catch { Write-Output 'API: unreachable (is api daemon running?)' }"