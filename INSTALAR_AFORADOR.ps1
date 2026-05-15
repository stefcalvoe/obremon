# INSTALADOR AFORADOR AMSA v16.15
# Script de instalación automática para Windows

Write-Host "╔═══════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║         INSTALADOR AFORADOR AMSA v16.15                  ║" -ForegroundColor Green
Write-Host "║    Sistema de Conteo de Pasajeros con IA                ║" -ForegroundColor Green
Write-Host "╚═══════════════════════════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""

# Obtener ruta de instalación (Documentos del usuario)
$docsPath = [System.Environment]::GetFolderPath("MyDocuments")
$installPath = "$docsPath\Aforador_AMSA"
$desktopPath = [System.Environment]::GetFolderPath("Desktop")

Write-Host "📁 Ruta de instalación: $installPath" -ForegroundColor Cyan
Write-Host ""

# Crear estructura de carpetas
Write-Host "📂 Creando estructura de carpetas..." -ForegroundColor Yellow
New-Item -Path $installPath -ItemType Directory -Force | Out-Null
New-Item -Path "$installPath\ia_training" -ItemType Directory -Force | Out-Null
New-Item -Path "$installPath\descargas" -ItemType Directory -Force | Out-Null
New-Item -Path "$installPath\videos" -ItemType Directory -Force | Out-Null
Write-Host "✅ Carpetas creadas correctamente" -ForegroundColor Green
Write-Host ""

# Copiar archivo HTML principal
Write-Host "📋 Instalando aplicación..." -ForegroundColor Yellow
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$sourceHTML = "$scriptDir\Aforador_AMSA_v16.15_IA.html"

if (Test-Path $sourceHTML) {
    Copy-Item -Path $sourceHTML -Destination "$installPath\Aforador_AMSA_v16.15_IA.html" -Force
    Write-Host "✅ Aplicación instalada" -ForegroundColor Green
} else {
    Write-Host "⚠️ Archivo HTML no encontrado. Asegúrate que esté en la misma carpeta que este instalador." -ForegroundColor Red
    Read-Host "Presiona Enter para salir"
    exit
}
Write-Host ""

# Crear acceso directo en escritorio
Write-Host "🖥️ Creando acceso directo en el escritorio..." -ForegroundColor Yellow
$shell = New-Object -ComObject WScript.Shell
$shortcut = $shell.CreateShortcut("$desktopPath\Aforador AMSA.lnk")
$shortcut.TargetPath = "C:\Program Files\Google\Chrome\Application\chrome.exe"
$shortcut.Arguments = "file:///$installPath/Aforador_AMSA_v16.15_IA.html"
$shortcut.WorkingDirectory = $installPath
$shortcut.IconLocation = "C:\Program Files\Google\Chrome\Application\chrome.exe,0"
$shortcut.Description = "Aforador de Pasajeros AMSA v16.15"
$shortcut.Save()
Write-Host "✅ Acceso directo creado en el escritorio" -ForegroundColor Green
Write-Host ""

# Crear guía de usuario
Write-Host "📖 Creando guía de usuario..." -ForegroundColor Yellow
$guia = @"
╔═══════════════════════════════════════════════════════════╗
║         GUÍA DE USO - AFORADOR AMSA v16.15               ║
║    Sistema de Conteo de Pasajeros con IA                ║
╚═══════════════════════════════════════════════════════════╝

🎯 OBJETIVO
Contar pasajeros que suben a los autobuses y generar datos
para entrenar un sistema de IA que aprenda automáticamente.

📍 UBICACIÓN DE ARCHIVOS
Instalación: $installPath
- Aforador_AMSA_v16.15_IA.html (aplicación principal)
- ia_training/ (datos de entrenamiento - NO TOCAR)
- descargas/ (Excel exportados aquí)
- videos/ (copiar videos aquí)

🚀 CÓMO USAR

1️⃣ CARGAR VIDEOS
   - Click en "📁 CARGAR VIDEOS"
   - Seleccionar archivos .mov o .mp4
   - Los videos aparecen en el panel IZQUIERDO

2️⃣ CONTAR PASAJEROS
   - Presiona TECLA 1: Efectivo (💵)
   - Presiona TECLA 2: Electrónico (💳)
   - Presiona TECLA 3: Cédula (🪪)
   - O usa los botones con el mouse

3️⃣ LLENAR INFORMACIÓN
   - Conductor: Nombre de quien conduce
   - Aforador: TU nombre (quien cuenta)
   - Observaciones: Notas importantes

4️⃣ SIGUIENTE VIDEO
   - Presiona TECLA 4 o ESPACIO
   - O click en "▶️ SIGUIENTE"

5️⃣ HACER CORTE (Guardar datos)
   - Presiona TECLA + o =
   - O presiona "✂️ HACER CORTE"
   - Los datos se guardan automáticamente

6️⃣ EXPORTAR EXCEL
   - Click en "📊 EXPORTAR EXCEL"
   - Se descarga un Excel con todos los datos
   - Guardar en carpeta: descargas/

⚡ ATAJOS DE TECLADO
   Tecla 1 .................... +Efectivo
   Tecla 2 .................... +Electrónico
   Tecla 3 .................... +Cédula
   Tecla 4 o ESPACIO ......... Siguiente video
   ENTER ..................... Siguiente video
   + o = ..................... Hacer CORTE
   Ctrl+P .................... Captura de pantalla

⚙️ IMPORTANTE
- Llena SIEMPRE los campos: Conductor y Aforador
- Agrega observaciones importantes (tráfico, clima, etc.)
- Exporta Excel al terminar cada jornada
- Los datos se guardan automáticamente

📊 DATOS DE ENTRENAMIENTO
- Carpeta: ia_training/
- Archivos: *.json (NO MOVER ni BORRAR)
- Se crean automáticamente al hacer cortes
- Sirven para entrenar la IA

❓ PROBLEMAS COMUNES
- "Sin video": Carga videos primero
- Números no avanzan: Haz click en el video para enfocarlo
- Excel no se descarga: Verifica carpeta Descargas

📞 SOPORTE
Contacta al administrador del sistema si hay problemas.

¡Gracias por usar Aforador AMSA! 🚌
"@

$guia | Out-File -FilePath "$installPath\GUIA_USUARIO.txt" -Encoding UTF8 -Force
Write-Host "✅ Guía de usuario creada" -ForegroundColor Green
Write-Host ""

# Crear script para recopilar datos
Write-Host "🔧 Configurando recopilación de datos..." -ForegroundColor Yellow
$collectScript = @"
@echo off
REM Script para comprimir y respaldar datos de entrenamiento
setlocal enabledelayedexpansion

set "SOURCE=$installPath\ia_training"
set "BACKUP_PATH=%USERPROFILE%\Desktop\BACKUP_IA_TRAINING_%date:~-4%%date:~-10,2%%date:~-7,2%.zip"

if exist "%SOURCE%" (
    echo Respaldando datos de entrenamiento...
    cd /d "%SOURCE%"
    REM Usar PowerShell para comprimir (compatible con Windows 10+)
    powershell -nologo -noprofile -command "Compress-Archive -Path '%SOURCE%\*' -DestinationPath '%BACKUP_PATH%' -Force"
    echo.
    echo ✅ Datos respaldados en: %BACKUP_PATH%
    echo.
    pause
) else (
    echo ⚠️ Carpeta ia_training no encontrada
    pause
)
"@

$collectScript | Out-File -FilePath "$installPath\RESPALDAR_DATOS.bat" -Encoding Default -Force
Write-Host "✅ Script de respaldo creado" -ForegroundColor Green
Write-Host ""

# Crear archivo README
Write-Host "📝 Creando README..." -ForegroundColor Yellow
$readme = @"
# AFORADOR AMSA v16.15

Instalación completada correctamente ✅

## Ubicación
- Aplicación: $installPath\Aforador_AMSA_v16.15_IA.html
- Acceso directo: Escritorio > "Aforador AMSA"

## Primeros pasos
1. Haz double-click en "Aforador AMSA" del escritorio
2. Se abrirá en navegador Chrome
3. Lee la GUIA_USUARIO.txt para aprender a usar

## Carpetas principales
- ia_training/ → Datos de IA (NO MODIFICAR)
- descargas/ → Excel exportados
- videos/ → Coloca videos aquí (opcional)

## Soporte
Si tienes problemas, ejecuta RESPALDAR_DATOS.bat
y envía la carpeta respaldada al administrador.

¡Bienvenido a Aforador AMSA! 🚌
"@

$readme | Out-File -FilePath "$installPath\README.txt" -Encoding UTF8 -Force
Write-Host "✅ README creado" -ForegroundColor Green
Write-Host ""

# Resumen final
Write-Host "╔═══════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║              ✅ INSTALACIÓN COMPLETADA                    ║" -ForegroundColor Green
Write-Host "╚═══════════════════════════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""
Write-Host "📂 Ruta: $installPath" -ForegroundColor Cyan
Write-Host "🖥️ Acceso directo: Escritorio > 'Aforador AMSA'" -ForegroundColor Cyan
Write-Host "📖 Guía: Abre GUIA_USUARIO.txt para aprender" -ForegroundColor Cyan
Write-Host ""
Write-Host "Próximos pasos:" -ForegroundColor Yellow
Write-Host "1. Haz click en el acceso directo del escritorio" -ForegroundColor White
Write-Host "2. Lee la GUIA_USUARIO.txt" -ForegroundColor White
Write-Host "3. Carga tus primeros videos" -ForegroundColor White
Write-Host "4. ¡Comienza a contar!" -ForegroundColor White
Write-Host ""

Read-Host "Presiona Enter para finalizar"
