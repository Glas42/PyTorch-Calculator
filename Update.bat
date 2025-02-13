@echo off
setlocal
title PyTorch-Calculator Updater

echo.
echo PyTorch-Calculator Updater
echo --------------------------
echo.

if not exist "%cd%\python" (
    echo PyTorch-Calculator is not installed, use the Installer.bat to install it!
    echo.
    goto :end
)

if not exist cache (
    mkdir cache
)
curl -L https://github.com/OleFranz/PyTorch-Calculator/archive/refs/heads/main.zip -o cache/PyTorch-Calculator-Update.zip >nul 2>&1
powershell -command "$ProgressPreference = 'SilentlyContinue'; Expand-Archive -LiteralPath 'cache\PyTorch-Calculator-Update.zip' -DestinationPath 'cache\UpdateCache' -Force"
for /d %%d in (*) do (
    if not "%%d"=="python" if not "%%d"=="cache" if not "%%d"=="config" if not "%%d"==".vscode" if not "%%d"==".vs" (
        rmdir /s /q "%%d"
    )
)
xcopy /s /y cache\UpdateCache\PyTorch-Calculator-main\* .
rmdir /s /q cache\UpdateCache
del /s /q cache\PyTorch-Calculator-Update.zip

echo.
echo App Updated
echo -----------
echo.

:end
endlocal
pause