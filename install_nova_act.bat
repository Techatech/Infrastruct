@echo off
echo ========================================
echo AWS Infrastruct - Nova-Act Installation
echo ========================================
echo.

echo Checking Python installation...
python --version
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python first: https://python.org
    pause
    exit /b 1
)

echo.
echo Checking pip installation...
python -m pip --version
if errorlevel 1 (
    echo ERROR: pip is not available
    echo Please ensure pip is installed with Python
    pause
    exit /b 1
)

echo.
echo Updating pip to latest version...
python -m pip install --upgrade pip

echo.
echo Installing Nova-Act SDK...
python -m pip install nova-act

if errorlevel 1 (
    echo.
    echo WARNING: Standard installation failed. Trying alternative methods...
    echo.
    
    echo Trying user installation...
    python -m pip install --user nova-act
    
    if errorlevel 1 (
        echo.
        echo ERROR: Installation failed with multiple methods
        echo.
        echo Manual installation steps:
        echo 1. Open Command Prompt as Administrator
        echo 2. Run: python -m pip install --upgrade pip
        echo 3. Run: python -m pip install nova-act
        echo 4. If that fails, try: pip install --user nova-act
        echo.
        echo For build errors on Windows:
        echo - Install Visual Studio Build Tools
        echo - Or install Microsoft C++ Build Tools
        echo.
        pause
        exit /b 1
    )
)

echo.
echo Verifying installation...
python -c "import nova_act; print('✅ Nova-Act SDK installed successfully!')"

if errorlevel 1 (
    echo.
    echo WARNING: Installation completed but verification failed
    echo Please check the installation manually:
    echo python -c "import nova_act; print('Nova-Act is working!')"
) else (
    echo.
    echo ========================================
    echo ✅ INSTALLATION SUCCESSFUL!
    echo ========================================
    echo Nova-Act SDK is ready for use
    echo Enhanced deployment features are now available
    echo Restart your AWS Infrastruct application to use Nova-Act
)

echo.
pause