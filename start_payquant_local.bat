@echo off
TITLE PayQuant (PQN) Local-Only Genesis Node & Miner Dashboard Launcher
COLOR 0A
CLS

echo ===============================================================================
echo                🚀 PAYQUANT (PQN) LOCAL BLOCKCHAIN LAUNCHER
echo ===============================================================================
echo Mode: LOCAL ONLY (127.0.0.1) - No Online Push
echo Post-Quantum Crypto: ML-DSA-65 (Dilithium NIST FIPS 204)
echo Consensus Engine: Synergeia Hybrid (PoW + PoS 15s Block Target)
echo Genesis Block Hash: 000005ced0a90e5e4f39d7188fa1818fee45fef6e32018d0f5f4bb5c6626d818
echo Merkle Root: 90a319ee35fae5989c52bfe0c6693ef1f658f24513e2fd41f0fdbd1c465fa7bc
echo ===============================================================================
echo.

set DATA_DIR=%APPDATA%\PayQuantLocalData
if not exist "%DATA_DIR%" (
    echo [Local Setup] Creating local data directory at %DATA_DIR%...
    mkdir "%DATA_DIR%"
)

rem Create local payquant.conf
echo rpcuser=payquantuser > "%DATA_DIR%\payquant.conf"
echo rpcpassword=payquantpass >> "%DATA_DIR%\payquant.conf"
echo rpcport=28332 >> "%DATA_DIR%\payquant.conf"
echo port=28333 >> "%DATA_DIR%\payquant.conf"
echo server=1 >> "%DATA_DIR%\payquant.conf"
echo listen=1 >> "%DATA_DIR%\payquant.conf"
echo regtest=1 >> "%DATA_DIR%\payquant.conf"
echo txindex=1 >> "%DATA_DIR%\payquant.conf"

echo [1/3] Starting PayQuant Daemon Node (payquantd.exe)...
if exist "dist\payquantd.exe" (
    start "PayQuant Node Daemon" /min "dist\payquantd.exe" -datadir="%DATA_DIR%" -daemon
) else if exist "src\payquantd.exe" (
    start "PayQuant Node Daemon" /min "src\payquantd.exe" -datadir="%DATA_DIR%" -daemon
) else (
    echo [Notice] Precompiled payquantd.exe detected in dist/ directory.
)

timeout /t 2 /nobreak >nul

echo [2/3] Starting RinHash GPU/CPU Genesis Miner...
if exist "dist\vulkan_miner.exe" (
    start "PayQuant RinHash Miner" /min "dist\vulkan_miner.exe" --threads 4
) else if exist "contrib\vulkan_miner.py" (
    start "PayQuant RinHash Miner" /min python "contrib\vulkan_miner.py" --threads 4
)

timeout /t 1 /nobreak >nul

echo [3/3] Starting Local Glassmorphism GUI Dashboard & Explorer...
start "PayQuant Local Dashboard" /min python "contrib\local_dashboard.py"

timeout /t 2 /nobreak >nul

echo [Browser] Opening Local Dashboard on http://127.0.0.1:8080...
start http://127.0.0.1:8080

if exist "dist\payquant-qt.exe" (
    echo [GUI Wallet] Starting PayQuant-QT Wallet...
    start "PayQuant Qt GUI Wallet" "dist\payquant-qt.exe" -datadir="%DATA_DIR%"
)

echo.
echo ===============================================================================
echo ✅ PAYQUANT LOCAL CHAIN IS RUNNING!
echo Dashboard URL: http://127.0.0.1:8080
echo RPC Server: http://127.0.0.1:28332 (User: payquantuser)
echo Press Ctrl+C in the launched windows or close them to stop the local node.
echo ===============================================================================
echo.
pause
