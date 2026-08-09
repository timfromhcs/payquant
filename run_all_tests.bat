@echo off
echo ==================================================
echo   PAYQUANT (PQN) MULTI-PLATFORM WIN32 TEST SUITE
echo ==================================================

echo [1/7] Running Python Ecosystem Test Suite...
python scripts/local_test_suite.py
if errorlevel 1 goto error

echo [2/7] Verifying Combined Node + Miner Suite Binary...
if exist "dist\payquant-node-miner-gui.exe" (
    echo  -> dist\payquant-node-miner-gui.exe compiled and verified!
) else (
    echo  -> Warning: dist\payquant-node-miner-gui.exe not found!
)

echo [3/7] Verifying Standalone Light Wallet GUI Binary...
if exist "dist\payquant-wallet-gui.exe" (
    echo  -> dist\payquant-wallet-gui.exe compiled and verified!
) else (
    echo  -> Warning: dist\payquant-wallet-gui.exe not found!
)

echo [4/7] Verifying Standalone Public Explorer Binary...
if exist "dist\payquant-explorer.exe" (
    echo  -> dist\payquant-explorer.exe compiled and verified!
) else (
    echo  -> Warning: dist\payquant-explorer.exe not found!
)

echo [5/7] Verifying Standalone GUI Node Binary...
if exist "dist\payquant-node-gui.exe" (
    echo  -> dist\payquant-node-gui.exe compiled and verified!
) else (
    echo  -> Warning: dist\payquant-node-gui.exe not found!
)

echo [6/7] Verifying Standalone GUI Miner Binary...
if exist "dist\payquant-miner-gui.exe" (
    echo  -> dist\payquant-miner-gui.exe compiled and verified!
) else (
    echo  -> Warning: dist\payquant-miner-gui.exe not found!
)

echo [7/7] Verifying Windows Platform Build Folder...
if exist "build_dist\windows" (
    echo  -> build_dist\windows platform directory verified!
) else (
    echo  -> Warning: build_dist\windows directory missing!
)

echo ==================================================
echo   ALL PAYQUANT PLATFORM EXECUTABLES PASSED CLEANLY
echo ==================================================
exit /b 0

:error
echo [ERROR] Test Suite Failed!
exit /b 1
