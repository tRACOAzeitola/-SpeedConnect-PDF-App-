@echo off
setlocal ENABLEDELAYEDEXPANSION

REM ==================================================================
echo 🔗 SpeedConnect PDF Merger v2.2 Minimalist - Windows Build Script
echo ✨ Interface limpa • Drag-and-drop melhorado • Defaults inteligentes
echo ==================================================================

REM Garantir que o script roda a partir da sua própria pasta
pushd "%~dp0"

REM Verificar Python (launcher) instalado
py -3 --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python (launcher) nao encontrado. Instale Python 3.8+ e tente novamente.
    echo Dica: https://www.python.org/downloads/windows/
    pause
    exit /b 1
)

REM Instalar dependencias com o launcher para evitar conflitos de ambiente
echo 📦 Instalando dependencias...
py -3 -m pip install --upgrade pip >nul 2>&1
py -3 -m pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ Erro ao instalar dependencias
    pause
    exit /b 1
)

REM Limpar builds anteriores
echo 🧹 Limpando builds anteriores...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist *.spec del /q *.spec

REM Construir executavel
echo 🔨 Criando executavel v2.2 Minimalist para Windows...

set "BUILD_CMD=py -3 -m PyInstaller --onefile --windowed --name=SpeedConnect-PDF-Merger"

REM Adicionar icone se existir
if exist "assets\SpeedConect.ico" (
    set "BUILD_CMD=!BUILD_CMD! --icon=assets\SpeedConect.ico"
) else if exist "assets\icon.ico" (
    set "BUILD_CMD=!BUILD_CMD! --icon=assets\icon.ico"
)

REM Adicionar arquivos de dados se existirem
if exist "README.md" (
    set "BUILD_CMD=!BUILD_CMD! --add-data=README.md;."
)
if exist "assets" (
    set "BUILD_CMD=!BUILD_CMD! --add-data=assets;assets"
)

REM Outras opcoes: coletar pacotes que precisam de recursos
set "BUILD_CMD=!BUILD_CMD! --hidden-import=tkinter --hidden-import=tkinter.ttk --collect-all=customtkinter --collect-all=tkinterdnd2 --noconsole --clean pdf_merger_improved.py"

REM Executar build
echo Comando: !BUILD_CMD!
!BUILD_CMD!
if errorlevel 1 (
    echo ❌ Erro no build
    popd
    pause
    exit /b 1
)

echo ✅ Build concluido com sucesso!
echo 📦 Executavel criado em: dist\SpeedConnect-PDF-Merger.exe

REM Mostrar tamanho do arquivo
for %%I in ("dist\SpeedConnect-PDF-Merger.exe") do echo 📊 Tamanho: %%~zI bytes

echo.
echo 🎉 Executavel v2.2 Minimalist Windows pronto para distribuicao!
echo ✨ Novidades: Interface limpa, drag-and-drop melhorado, defaults inteligentes
echo Para testar: dist\SpeedConnect-PDF-Merger.exe

popd
endlocal
pause
