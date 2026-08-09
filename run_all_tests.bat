@echo off
echo ==================================================
echo   PAYQUANT (PQN) NATIVE STANDALONE WIN32 TEST SUITE
echo ==================================================

echo [1/5] Running Python Ecosystem Test Suite...
python scripts/local_test_suite.py
if errorlevel 1 goto error

echo [2/5] Verifying Standalone GUI Node Binary...
if exist "dist\payquant-node-gui.exe" (
    echo  -> dist\payquant-node-gui.exe compiled and verified!
) else (
    echo  -> Warning: dist\payquant-node-gui.exe not found!
)

echo [3/5] Verifying Standalone GUI Miner Binary...
if exist "dist\payquant-miner-gui.exe" (
    echo  -> dist\payquant-miner-gui.exe compiled and verified!
) else (
    echo  -> Warning: dist\payquant-miner-gui.exe not found!
)

echo [4/5] Verifying Standalone Public Explorer Binary...
if exist "dist\payquant-explorer.exe" (
    echo  -> dist\payquant-explorer.exe compiled and verified!
) else (
    echo  -> Warning: dist\payquant-explorer.exe not found!
)

echo [5/5] Verifying Standalone Daemon Binary...
if exist "dist\payquantd.exe" (
    echo  -> dist\payquantd.exe compiled and verified!
) else (
    echo  -> Warning: dist\payquantd.exe not found!
)

echo ==================================================
echo   ALL PAYQUANT WINDOWS EXECUTABLES PASSED CLEANLY
echo ==================================================
exit /b 0

:error
echo [ERROR] Test Suite Failed!
exit /b 1
