@echo off
TITLE PayQuant (PQN) Native Local Node & Miner Launcher v3.0.0
COLOR 0A
CLS

echo ===============================================================================
echo            PAYQUANT (PQN) LOCAL BLOCKCHAIN GUI LAUNCHER
echo ===============================================================================
echo Mode: LOCAL & P2P SYNC
echo Post-Quantum Crypto: ML-DSA-65 (Dilithium NIST FIPS 204)
echo Database: Persistent LevelDB State
echo ===============================================================================
echo.

echo [1/2] Starting PayQuant Native GUI Node...
if exist "dist\payquant-node-gui.exe" (
    start "PayQuantNode" "dist\payquant-node-gui.exe"
) else (
    start "PayQuantNode" python "contrib\node_gui.py"
)

timeout /t 2 /nobreak >nul

echo [2/2] Starting PayQuant Native GUI Miner...
if exist "dist\payquant-miner-gui.exe" (
    start "PayQuantMiner" "dist\payquant-miner-gui.exe"
) else (
    start "PayQuantMiner" python "contrib\miner_gui.py"
)

echo.
echo ===============================================================================
echo PayQuant Local Standalone Desktop GUI Services Active.
echo ===============================================================================
echo.
pause
