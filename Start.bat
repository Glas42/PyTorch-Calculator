@echo off
title PyTorch-Calculator Console

echo.
echo PyTorch-Calculator
echo ------------------
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
echo Running App
echo -----------
echo.

python app/main.py %*

:end
pause