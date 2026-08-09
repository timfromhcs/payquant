@echo off
REM ============================================================
REM PayQuant (PQN) Backend Dashboard Shutdown (Windows) v6.4.0
REM Stops all backend services cleanly, in reverse order.
REM ============================================================
setlocal
cd /d "%~dp0.."

echo [PayQuant] Stopping all backend services...
python backend\daemon.py stop signaling
python backend\daemon.py stop api
python backend\daemon.py stop miner
python backend\daemon.py stop node

echo.
echo [PayQuant] All backend services stopped cleanly.