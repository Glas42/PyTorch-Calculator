@echo off
title PyTorch-Calculator Updater

echo.
echo PyTorch-Calculator Updater
echo --------------------------
echo.

cd %~dp0
if not exist venv (
    echo Creating venv...
    python -m venv venv
    call venv/Scripts/activate
    python.exe -m pip install --upgrade pip >nul 2>&1
) else (
    call venv/Scripts/activate
)

if not exist config/requirements.txt (
    echo requirements.txt not found.
    goto end
)

echo Checking required packages...
set MISSING_PACKAGES=0
for /f "tokens=*" %%a in ('pip list --format=freeze  2^>nul') do (
    for /f "tokens=1 delims==" %%b in ("%%a") do (
        set "INSTALLED_PACKAGES[%%b]=1"
    )
)

for /f "tokens=*" %%a in (config/requirements.txt) do (
    for /f "tokens=1 delims==" %%b in ("%%a") do (
        if not defined INSTALLED_PACKAGES[%%b] (
            echo ^> Installing %%b...
            set MISSING_PACKAGES=1
        )
    )
)

if %MISSING_PACKAGES% equ 1 (
    echo Installing all required packages...
    pip install -r config/requirements.txt -q --force-reinstall >nul 2>&1
)
echo All required packages installed.

echo.
echo Updating App
echo ------------
echo.

if not exist cache (
    mkdir cache
)
curl -L https://github.com/Glas42/PyTorch-Calculator/archive/refs/heads/main.zip -o cache/PyTorch-Calculator-Update.zip >nul 2>&1
powershell -command "$ProgressPreference = 'SilentlyContinue'; Expand-Archive -LiteralPath 'cache\PyTorch-Calculator-Update.zip' -DestinationPath 'cache\UpdateCache' -Force"
for /d %%d in (*) do (
    if not "%%d"=="venv" if not "%%d"=="cache" if not "%%d"=="config" if not "%%d"==".vs" if not "%%d"==".vscode" (
        rmdir /s /q "%%d"
    )
)
xcopy /s /y cache\UpdateCache\PyTorch-Calculator-main\* .
rmdir /s /q cache\UpdateCache
rmdir /s /q cache\PyTorch-Calculator-Update.zip

echo.
echo App Updated
echo -----------
echo.

:end
pause