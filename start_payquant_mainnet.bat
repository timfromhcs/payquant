@echo off
TITLE PayQuant (PQN) Native Mainnet Launcher v3.0.0
COLOR 0A
CLS

echo ===============================================================================
echo            PAYQUANT (PQN) MAINNET STANDALONE GUI LAUNCHER
echo ===============================================================================
echo Mode: REAL MAINNET (P2P Port 28333)
echo Post-Quantum Crypto: ML-DSA-65 (Dilithium NIST FIPS 204)
echo Consensus Engine: Synergeia Hybrid (PoW + PoS 15s Target)
echo Database: Persistent LevelDB / ChainDB State
echo ===============================================================================
echo.

set DATA_DIR=%APPDATA%\PayQuantMainnetData
if not exist "%DATA_DIR%" (
    echo [Mainnet Setup] Creating Mainnet data directory at %DATA_DIR%...
    mkdir "%DATA_DIR%"
)

echo [1/2] Launching Standalone GUI Node...
if exist "dist\payquant-node-gui.exe" (
    start "PayQuantNode" "dist\payquant-node-gui.exe"
) else (
    start "PayQuantNode" python "contrib\node_gui.py"
)

timeout /t 2 /nobreak >nul

echo [2/2] Launching Standalone GUI Miner...
if exist "dist\payquant-miner-gui.exe" (
    start "PayQuantMiner" "dist\payquant-miner-gui.exe"
) else (
    start "PayQuantMiner" python "contrib\miner_gui.py"
)

echo.
echo ===============================================================================
echo PAYQUANT STANDALONE MAINNET ECOSYSTEM ACTIVE!
echo Node GUI & Miner GUI running natively on desktop.
echo ===============================================================================
echo.
pause