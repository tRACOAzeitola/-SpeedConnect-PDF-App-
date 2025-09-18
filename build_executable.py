#!/usr/bin/env python3
"""
Build script for creating SpeedConnect PDF Merger executable
v2.2 Minimalist - Interface limpa com drag-and-drop melhorado
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def check_dependencies():
    """Check if all required dependencies are installed."""
    required_packages = ['customtkinter', 'pypdf', 'PIL']
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'PIL':
                __import__('PIL')
            else:
                __import__(package)
        except ImportError:
            if package == 'pypdf':
                try:
                    __import__('PyPDF2')
                except ImportError:
                    missing_packages.append(package)
            else:
                missing_packages.append(package)
    
    # Check PyInstaller separately using the current interpreter
    try:
        subprocess.run([sys.executable, '-m', 'PyInstaller', '--version'], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        missing_packages.append('pyinstaller')
    
    if missing_packages:
        print(f"❌ Pacotes em falta: {', '.join(missing_packages)}")
        print("Execute: pip install -r requirements.txt")
        return False
    
    print("✅ Todas as dependências estão instaladas")
    return True

def create_icon():
    """Create a simple icon if none exists."""
    icon_path = Path("assets/icon.ico")
    
    if icon_path.exists():
        print(f"✅ Ícone encontrado: {icon_path}")
        return str(icon_path)
    
    # Create assets directory
    icon_path.parent.mkdir(exist_ok=True)
    
    try:
        from PIL import Image, ImageDraw, ImageFont
        
        # Create a simple icon
        size = (256, 256)
        img = Image.new('RGBA', size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Draw a simple PDF icon
        # Background
        draw.rectangle([20, 20, 236, 236], fill='#FF3B30', outline='#000000', width=3)
        
        # PDF text
        try:
            font = ImageFont.truetype("Arial", 40)
        except:
            font = ImageFont.load_default()
        
        draw.text((128, 100), "PDF", fill='white', font=font, anchor='mm')
        draw.text((128, 150), "MERGER", fill='white', font=font, anchor='mm')
        
        # Save as ICO
        img.save(icon_path, format='ICO', sizes=[(256, 256), (128, 128), (64, 64), (32, 32), (16, 16)])
        print(f"✅ Ícone criado: {icon_path}")
        return str(icon_path)
        
    except ImportError:
        print("⚠️ Pillow não disponível, usando ícone padrão")
        return None
    except Exception as e:
        print(f"⚠️ Erro ao criar ícone: {e}")
        return None

def get_icon_path():
    """Get the appropriate icon path for the current platform."""
    assets_dir = Path("assets")
    
    if sys.platform == "win32":
        # Windows uses .ico
        icon_path = assets_dir / "SpeedConect.ico"
        if icon_path.exists():
            return str(icon_path)
        icon_path = assets_dir / "icon.ico"
        if icon_path.exists():
            return str(icon_path)
    elif sys.platform == "darwin":
        # macOS uses .icns
        icon_path = assets_dir / "icon.icns"
        if icon_path.exists():
            return str(icon_path)
    
    # Fallback to PNG
    icon_path = assets_dir / "icon.png"
    if icon_path.exists():
        return str(icon_path)
    
    return None

def build_executable():
    """Build the executable using PyInstaller."""
    print("🔨 Iniciando build do executável...")
    
    # Clean previous builds
    for dir_name in ['build', 'dist', '__pycache__']:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"🧹 Limpeza: {dir_name}")
    
    # Detect platform
    platform = sys.platform
    print(f"🖥️ Platform detectada: {platform}")
    
    # Prepare PyInstaller command (use current interpreter for reliability)
    cmd = [
        sys.executable,
        '-m', 'PyInstaller',
        '--onefile',
        '--name=SpeedConnect-PDF-Merger',
        'pdf_merger_improved.py'
    ]
    
    # Add windowed mode for GUI (but not on macOS to avoid .app bundle issues)
    if platform == "win32":
        cmd.append('--windowed')
        cmd.append('--console')  # Keep console for debugging
    
    # Add icon
    icon_path = get_icon_path()
    if icon_path:
        cmd.extend(['--icon', icon_path])
        print(f"🎨 Usando ícone: {icon_path}")
    else:
        print("⚠️ Nenhum ícone encontrado")
    
    # Add data files if they exist
    if os.path.exists('README.md'):
        cmd.extend(['--add-data', f'README.md{os.pathsep}.'])
    if os.path.exists('assets'):
        cmd.extend(['--add-data', f'assets{os.pathsep}assets'])
    
    # Add additional options
    cmd.extend([
        '--hidden-import', 'tkinter',
        '--hidden-import', 'tkinter.ttk',
        '--collect-all', 'customtkinter',
        '--collect-all', 'tkinterdnd2',
        '--distpath', 'dist',
        '--workpath', 'build',
        '--clean',
        '--noconfirm'
    ])
    
    # Add platform-specific options
    if platform == "darwin":
        # macOS specific - simplified to avoid architecture issues
        cmd.extend([
            '--osx-bundle-identifier', 'com.speedconnect.pdfmerger',
            '--target-arch', 'arm64'  # Force arm64 to avoid lipo issues
        ])
    elif platform == "win32":
        # Windows specific - remove version file requirement
        pass  # No additional options needed
    
    print(f"🚀 Executando: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✅ Build concluído com sucesso!")
        print(f"📄 Output: {result.stdout}")
        
        # Show output location
        if platform == "win32":
            exe_path = "dist/SpeedConnect-PDF-Merger.exe"
        else:
            exe_path = "dist/SpeedConnect-PDF-Merger"
        
        if os.path.exists(exe_path):
            file_size = os.path.getsize(exe_path) / (1024 * 1024)  # MB
            print(f"📦 Executável criado: {exe_path} ({file_size:.1f} MB)")
            
            # Make executable on Unix systems
            if platform != "win32":
                os.chmod(exe_path, 0o755)
                print("🔧 Permissões de execução definidas")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro no build:")
        print(f"Stdout: {e.stdout}")
        print(f"Stderr: {e.stderr}")
        return False
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return False

def check_xcode_license():
    """Check if Xcode license is accepted on macOS."""
    if sys.platform == "darwin":
        try:
            result = subprocess.run(['xcodebuild', '-version'], 
                                   capture_output=True, text=True, timeout=10)
            if result.returncode != 0:
                print("⚠️ Xcode license não aceita. Execute: sudo xcodebuild -license")
                print("Ou instale Xcode Command Line Tools: xcode-select --install")
                return False
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
            print("⚠️ Xcode Command Line Tools não encontradas")
            print("Instale com: xcode-select --install")
            return False
    return True

def main():
    """Main build function."""
    print("🔗 SpeedConnect PDF Merger v2.2 Minimalist - Build Script")
    print("✨ Interface limpa • Drag-and-drop melhorado • Defaults inteligentes")
    print("=" * 65)
    
    # Ensure we run from the script directory for reliable relative paths
    try:
        script_dir = Path(__file__).resolve().parent
        os.chdir(script_dir)
    except Exception as e:
        print(f"⚠️ Nao foi possivel mudar para a pasta do script: {e}")
    
    # Check current directory
    if not os.path.exists('pdf_merger_improved.py'):
        print("❌ Arquivo pdf_merger_improved.py não encontrado!")
        print("Execute este script na pasta do projeto.")
        sys.exit(1)
    
    # Check Xcode license on macOS
    if not check_xcode_license():
        sys.exit(1)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Build executable
    if build_executable():
        print("\n🎉 Build concluído com sucesso!")
        print("\nPróximos passos:")
        print("1. Teste o executável na pasta 'dist'")
        print("2. Distribua o arquivo para outros usuários")
        print("3. O executável é independente e não precisa de Python instalado")
    else:
        print("\n❌ Build falhou. Verifique os erros acima.")
        sys.exit(1)

if __name__ == "__main__":
    main()
