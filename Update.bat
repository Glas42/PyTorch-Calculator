@echo off
setlocal
title PyTorch-Calculator Updater

echo.
echo PyTorch-Calculator Updater
echo --------------------------
echo.

set "PATH=%cd%\python\Scripts;%cd%\python"

if not exist "%cd%\python" (
    echo PyTorch-Calculator is not installed, use the Installer.bat to install it!
    echo.
    goto :end
)

echo Updating App...

python  -c "import subprocess; import time; time.sleep(0.5); subprocess.Popen(['python', 'app/update.py'])"

echo.
echo App Updated
echo -----------
echo.

:end
endlocal
pause