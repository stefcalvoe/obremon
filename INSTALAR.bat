@echo off
chcp 65001 >nul
title INSTALADOR AFORADOR AMSA v16.15
color 0A

echo.
echo ╔═══════════════════════════════════════════════════════════╗
echo ║         INSTALADOR AFORADOR AMSA v16.15                  ║
echo ║    Sistema de Conteo de Pasajeros con IA                ║
echo ╚═══════════════════════════════════════════════════════════╝
echo.

REM Obtener rutas
for /f "tokens=3" %%A in ('reg query "HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders" /v "Personal" 2^>nul') do set DOCS=%%A
set INSTALL_PATH=%DOCS%\Aforador_AMSA
set DESKTOP=%USERPROFILE%\Desktop

echo 📁 Ruta de instalación: %INSTALL_PATH%
echo.

REM Crear carpetas
echo 📂 Creando estructura de carpetas...
if not exist "%INSTALL_PATH%" mkdir "%INSTALL_PATH%"
if not exist "%INSTALL_PATH%\ia_training" mkdir "%INSTALL_PATH%\ia_training"
if not exist "%INSTALL_PATH%\descargas" mkdir "%INSTALL_PATH%\descargas"
if not exist "%INSTALL_PATH%\videos" mkdir "%INSTALL_PATH%\videos"
echo ✅ Carpetas creadas
echo.

REM Copiar HTML
echo 📋 Instalando aplicación...
if exist "Aforador_AMSA_v16.15_IA.html" (
    copy /Y "Aforador_AMSA_v16.15_IA.html" "%INSTALL_PATH%\Aforador_AMSA_v16.15_IA.html" >nul
    echo ✅ Aplicación instalada
) else (
    echo ❌ ERROR: Aforador_AMSA_v16.15_IA.html no encontrado
    echo.
    pause
    exit /b 1
)
echo.

REM Crear acceso directo en escritorio
echo 🖥️ Creando acceso directo...
powershell -nologo -noprofile -command "^
    $shell = New-Object -ComObject WScript.Shell; ^
    $shortcut = $shell.CreateShortcut('%DESKTOP%\Aforador AMSA.lnk'); ^
    $shortcut.TargetPath = 'C:\Program Files\Google\Chrome\Application\chrome.exe'; ^
    $shortcut.Arguments = 'file:///%INSTALL_PATH%/Aforador_AMSA_v16.15_IA.html'; ^
    $shortcut.WorkingDirectory = '%INSTALL_PATH%'; ^
    $shortcut.IconLocation = 'C:\Program Files\Google\Chrome\Application\chrome.exe,0'; ^
    $shortcut.Description = 'Aforador de Pasajeros AMSA v16.15'; ^
    $shortcut.Save()
"
echo ✅ Acceso directo creado
echo.

REM Crear guía
echo 📖 Creando guía de usuario...
(
echo ╔═══════════════════════════════════════════════════════════╗
echo ║         GUÍA DE USO - AFORADOR AMSA v16.15               ║
echo ║    Sistema de Conteo de Pasajeros con IA                ║
echo ╚═══════════════════════════════════════════════════════════╝
echo.
echo 🎯 OBJETIVO
echo Contar pasajeros y generar datos para entrenar IA
echo.
echo 🚀 CÓMO USAR
echo 1. Haz click en "Aforador AMSA" en el escritorio
echo 2. Se abre el navegador Chrome
echo 3. Carga videos con "📁 CARGAR VIDEOS"
echo 4. Presiona TECLA 1, 2, 3 para contar (o usa botones)
echo 5. Llena Conductor, Aforador, Observaciones
echo 6. Presiona TECLA 4 o ESPACIO para siguiente video
echo 7. Presiona + o = para HACER CORTE
echo 8. Click en "📊 EXPORTAR EXCEL" al terminar
echo.
echo ⚡ ATAJOS DE TECLADO
echo 1 = +Efectivo
echo 2 = +Electrónico
echo 3 = +Cédula
echo 4 o ESPACIO = Siguiente video
echo + o = = Hacer CORTE
echo.
echo 📂 ARCHIVOS IMPORTANTES
echo - Aforador_AMSA_v16.15_IA.html: Aplicación
echo - ia_training/: Datos de IA (NO MODIFICAR)
echo - descargas/: Excel exportados
echo - videos/: Tus videos
echo.
echo ⚙️ IMPORTANTE
echo - Llena SIEMPRE Conductor y Aforador
echo - Agrega observaciones importantes
echo - Exporta Excel cada día
echo - Los datos se guardan automáticamente
echo.
echo ¡Bienvenido a Aforador AMSA! 🚌
) > "%INSTALL_PATH%\GUIA_USUARIO.txt"
echo ✅ Guía creada
echo.

REM Crear script de respaldo
echo 🔧 Configurando respaldo de datos...
(
echo @echo off
echo setlocal enabledelayedexpansion
echo set "SOURCE=%INSTALL_PATH%\ia_training"
echo set "BACKUP_PATH=%DESKTOP%\BACKUP_IA_TRAINING_!date:~-4!!date:~-10,2!!date:~-7,2!.zip"
echo.
echo if exist "!SOURCE!" (
echo     echo Respaldando datos de entrenamiento...
echo     cd /d "!SOURCE!"
echo     powershell -nologo -noprofile -command "Compress-Archive -Path '!SOURCE!\*' -DestinationPath '!BACKUP_PATH!' -Force"
echo     echo ✅ Respaldo completado: !BACKUP_PATH!
echo     pause
echo ) else (
echo     echo ⚠️ Carpeta ia_training no encontrada
echo     pause
echo )
) > "%INSTALL_PATH%\RESPALDAR_DATOS.bat"
echo ✅ Script de respaldo creado
echo.

REM Resumen
echo.
echo ╔═══════════════════════════════════════════════════════════╗
echo ║              ✅ INSTALACIÓN COMPLETADA                    ║
echo ╚═══════════════════════════════════════════════════════════╝
echo.
echo 📂 Ruta: %INSTALL_PATH%
echo 🖥️ Acceso directo: Escritorio ^> "Aforador AMSA"
echo 📖 Guía: %INSTALL_PATH%\GUIA_USUARIO.txt
echo.
echo 🚀 PRÓXIMOS PASOS:
echo 1. Haz doble-click en "Aforador AMSA" del escritorio
echo 2. Lee GUIA_USUARIO.txt
echo 3. ¡Comienza a contar pasajeros!
echo.
echo.
pause
