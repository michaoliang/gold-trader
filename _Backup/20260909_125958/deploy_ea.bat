@echo off
chcp 65001 >nul
echo ========================================
echo   GoldTrader MTF EA - ????
echo ========================================
echo.

REM ??MT5??
set MT5_PATH=D:\MetaTrader 5 EXNESS
set MT5_EDITOR=D:\MetaTrader 5 EXNESS\MetaEditor64.exe

if not exist "%MT5_EDITOR%" (
    echo [??] MetaEditor????
    echo ???MT5??? D:\MetaTrader 5 EXNESS\
    pause
    exit /b 1
)

echo [1/3] ??EA???...
if not exist "MQL5\Experts\GoldTrader_MTF_EA.mq5" (
    echo [??] EA???????
    pause
    exit /b 1
)
echo      OK: GoldTrader_MTF_EA.mq5

echo.
echo [2/3] ??EA...
start /wait "" "%MT5_EDITOR%" /compile:"MQL5\Experts\GoldTrader_MTF_EA.mq5" /log
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [??] ???????????
    pause
    exit /b 1
)
echo      OK: ????

echo.
echo [3/3] ??????...
if exist "MQL5\Experts\GoldTrader_MTF_EA.ex5" (
    echo      OK: GoldTrader_MTF_EA.ex5 ???
    echo.
    echo [??] ?????????
    echo   1. ??MT5??
    echo   2. ? MQL5\Experts\GoldTrader_MTF_EA.ex5
    echo      ??? %APPDATA%\MetaTrader 5\Profiles\Experts\
    echo   3. ?MT5?????? GoldTrader_MTF_EA
    echo   4. ??XAUUSDc?????
    echo.
) else (
    echo [??] .ex5?????
)

echo.
echo ========================================
echo   ?????
echo ========================================
pause
