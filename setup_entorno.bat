@echo off
echo ============================================================
echo   PASO 1 - INSTALACION DEL ENTORNO - AFORADOR AMSA IA
echo ============================================================
echo.

REM Verificar Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python no encontrado. Instala Python 3.9+ desde https://python.org
    pause
    exit /b 1
)

echo [OK] Python detectado:
python --version
echo.

REM Crear entorno virtual
if not exist "venv" (
    echo Creando entorno virtual...
    python -m venv venv
    echo [OK] Entorno virtual creado
) else (
    echo [OK] Entorno virtual ya existe
)
echo.

REM Activar entorno
echo Activando entorno virtual...
call venv\Scripts\activate.bat

REM Actualizar pip
echo Actualizando pip...
python -m pip install --upgrade pip --quiet

REM Instalar dependencias
echo.
echo Instalando dependencias (puede tardar varios minutos)...
echo.
pip install -r aforador-ia-requirements.txt

if errorlevel 1 (
    echo.
    echo [ERROR] Fallo la instalacion de dependencias
    pause
    exit /b 1
)

echo.
echo ============================================================
echo   [OK] ENTORNO INSTALADO CORRECTAMENTE
echo ============================================================
echo.
echo Para activar el entorno en el futuro:
echo   venv\Scripts\activate.bat
echo.
echo Siguiente paso: python setup_model.py
echo.
pause
