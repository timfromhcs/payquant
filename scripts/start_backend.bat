@echo off
REM ============================================================
REM PayQuant (PQN) Backend Dashboard Bootstrap (Windows) v6.4.0
REM Starts: node daemon -> miner daemon -> API server -> signaling
REM Order matters: node first, then miner, then API, then WS.
REM ============================================================
setlocal
cd /d "%~dp0.."

set "PYTHON=python"
where python >nul 2>nul
if errorlevel 1 set "PYTHON=py -3"

echo [PayQuant] Starting backend services in the correct order...
%PYTHON% backend\daemon.py start node
%PYTHON% backend\daemon.py start miner
%PYTHON% backend\daemon.py start api
%PYTHON% backend\daemon.py start signaling

echo.
echo [PayQuant] Waiting 4s for all services to stabilize...
timeout /t 4 /nobreak >nul

call scripts\status_backend.bat
echo.
echo [PayQuant] All backend services launched. End = done.