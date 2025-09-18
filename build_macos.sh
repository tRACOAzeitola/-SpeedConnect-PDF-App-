#!/bin/bash
set -e

echo "🔗 SpeedConnect PDF Merger v2.2 Minimalist - macOS Build Script"
echo "✨ Interface limpa • Drag-and-drop melhorado • Defaults inteligentes"
echo "=================================================================="

# Ensure we run from the script directory
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 não encontrado. Instale Python 3.8+ primeiro."
    exit 1
fi

# Check if pip is available
if ! command -v pip &> /dev/null && ! command -v pip3 &> /dev/null; then
    echo "❌ pip não encontrado. Instale pip primeiro."
    exit 1
fi

# Check Xcode license
if ! xcodebuild -version &> /dev/null; then
    echo "⚠️ Xcode license não aceita ou Command Line Tools não instaladas"
    echo "Execute: sudo xcodebuild -license"
    echo "Ou instale: xcode-select --install"
    exit 1
fi

# Install dependencies
echo "📦 Instalando dependências..."
python3 -m pip install --upgrade pip >/dev/null 2>&1 || true
python3 -m pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "❌ Erro ao instalar dependências"
    exit 1
fi

# Clean previous builds
echo "🧹 Limpando builds anteriores..."
rm -rf build dist *.spec

# Build executable
echo "🔨 Criando executável v2.2 Minimalist para macOS..."

# Build command with conditional data files (use current interpreter)
BUILD_CMD="python3 -m PyInstaller --onefile --name=SpeedConnect-PDF-Merger"

# Add icon if exists
if [ -f "assets/icon.icns" ]; then
    BUILD_CMD="$BUILD_CMD --icon=assets/icon.icns"
fi

# Add data files if they exist
if [ -f "README.md" ]; then
    BUILD_CMD="$BUILD_CMD --add-data=README.md:."
fi
if [ -d "assets" ]; then
    BUILD_CMD="$BUILD_CMD --add-data=assets:assets"
fi

# Add other options
BUILD_CMD="$BUILD_CMD --hidden-import=tkinter --hidden-import=tkinter.ttk --collect-all=customtkinter --collect-all=tkinterdnd2 --osx-bundle-identifier=com.speedconnect.pdfmerger --target-arch=arm64 --clean pdf_merger_improved.py"

# Execute build
eval $BUILD_CMD

if [ $? -ne 0 ]; then
    echo "❌ Erro no build"
    exit 1
fi

echo "✅ Build concluído com sucesso!"

# Check if executable was created
if [ -f "dist/SpeedConnect-PDF-Merger" ]; then
    # Make executable
    chmod +x dist/SpeedConnect-PDF-Merger
    
    # Show file size
    FILE_SIZE=$(ls -lh dist/SpeedConnect-PDF-Merger | awk '{print $5}')
    echo "📦 Executável criado: dist/SpeedConnect-PDF-Merger ($FILE_SIZE)"
    
    echo ""
    echo "🎉 Executável v2.2 Minimalist macOS pronto para distribuição!"
    echo "✨ Novidades: Interface limpa, drag-and-drop melhorado, defaults inteligentes"
    echo "Para testar: ./dist/SpeedConnect-PDF-Merger"
else
    echo "❌ Executável não foi criado"
    exit 1
fi
