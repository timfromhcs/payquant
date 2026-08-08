@echo off
TITLE PayQuant PQN Real Mainnet Node AND Miner WebUI Controller
COLOR 0A
CLS

echo ===============================================================================
echo            PAYQUANT (PQN) REAL MAINNET NODE AND MINER CONTROLLER
echo ===============================================================================
echo Chain Target: REAL MAINNET (P2P Port 28333, RPC 28332)
echo Post-Quantum Crypto: ML-DSA-65 (Dilithium NIST FIPS 204)
echo Consensus Engine: Synergeia Hybrid (PoW + PoS 15s Block Target)
echo Genesis Block Hash: 000005ced0a90e5e4f39d7188fa1818fee45fef6e32018d0f5f4bb5c6626d818
echo Merkle Root: 90a319ee35fae5989c52bfe0c6693ef1f658f24513e2fd41f0fdbd1c465fa7bc
echo ===============================================================================
echo.

set DATA_DIR=%APPDATA%\PayQuantMainnetData
if not exist "%DATA_DIR%" (
    echo [Mainnet Setup] Creating Mainnet data directory at %DATA_DIR%...
    mkdir "%DATA_DIR%"
)

rem Create mainnet payquant.conf if missing
if not exist "%DATA_DIR%\payquant.conf" (
    echo rpcuser=payquantuser > "%DATA_DIR%\payquant.conf"
    echo rpcpassword=payquantpass >> "%DATA_DIR%\payquant.conf"
    echo rpcport=28332 >> "%DATA_DIR%\payquant.conf"
    echo port=28333 >> "%DATA_DIR%\payquant.conf"
    echo server=1 >> "%DATA_DIR%\payquant.conf"
    echo listen=1 >> "%DATA_DIR%\payquant.conf"
    echo txindex=1 >> "%DATA_DIR%\payquant.conf"
)

echo [1/2] Launching Mainnet WebUI Management Server...
start "PayQuantWebUI" python "contrib\mainnet_webui.py"

timeout /t 2 /nobreak >nul

echo [2/2] Opening WebUI Control Panel on http://127.0.0.1:8080...
start http://127.0.0.1:8080

echo.
echo ===============================================================================
echo PAYQUANT REAL MAINNET CONTROLLER IS ACTIVE!
echo WebUI URL: http://127.0.0.1:8080
echo Features: Real-Time Auto Refresh, Start/Stop Node, Start/Stop Miner
echo ===============================================================================
echo.
pause
