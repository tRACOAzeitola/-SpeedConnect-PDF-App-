#!/usr/bin/env python3
"""
Build script for creating SpeedConnect PDF Merger .app bundle for macOS
v2.2 Minimalist - Interface limpa com drag-and-drop melhorado
"""

import os
import sys
import subprocess
import shutil
import stat
import time
from pathlib import Path

def _on_rm_error(func, path, exc_info):
    """Error handler for shutil.rmtree: make file writable then retry."""
    try:
        os.chmod(path, stat.S_IWRITE)
        func(path)
    except Exception:
        pass


def safe_rmtree(path: str, retries: int = 3, delay: float = 0.2):
    """Remove directory tree robustly, fixing permissions and retrying if needed."""
    if not os.path.exists(path):
        return
    for i in range(retries):
        try:
            shutil.rmtree(path, onerror=_on_rm_error)
            return
        except Exception as e:
            if i == retries - 1:
                raise
            time.sleep(delay)


def build_app_bundle():
    """Build the .app bundle using PyInstaller."""
    print("🔨 Criando .app bundle v2.2 Minimalist para macOS...")
    
    # Clean previous builds
    for dir_name in ['build', 'dist', '__pycache__']:
        if os.path.exists(dir_name):
            try:
                safe_rmtree(dir_name)
                print(f"🧹 Limpeza: {dir_name}")
            except Exception as e:
                print(f"⚠️ Falha ao limpar {dir_name}: {e}. Continuando mesmo assim...")
    
    # Prepare PyInstaller command for .app bundle
    cmd = [
        sys.executable,
        '-m', 'PyInstaller',
        '--windowed',  # This creates .app bundle on macOS
        '--name=SpeedConnect-PDF-Merger',
        'pdf_merger_improved.py'
    ]
    
    # Add icon
    icon_path = "assets/icon.icns"
    if os.path.exists(icon_path):
        cmd.extend(['--icon', icon_path])
        print(f"🎨 Usando ícone: {icon_path}")
    
    # Add data files if they exist
    if os.path.exists('README.md'):
        cmd.extend(['--add-data', f'README.md{os.pathsep}.'])
    if os.path.exists('assets'):
        cmd.extend(['--add-data', f'assets{os.pathsep}assets'])
    
    # Add additional options
    cmd.extend([
        '--distpath', 'dist',
        '--workpath', 'build',
        '--clean',
        '--noconfirm',
        '--osx-bundle-identifier', 'com.speedconnect.pdfmerger',
        '--target-arch', 'arm64',  # Force arm64 to avoid lipo issues
        '--hidden-import', 'tkinter',
        '--hidden-import', 'tkinter.ttk',
        '--collect-all', 'customtkinter',
        '--collect-all', 'tkinterdnd2'
    ])
    
    print(f"🚀 Executando: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✅ Build do .app concluído com sucesso!")
        
        # Check if .app was created
        app_path = "dist/SpeedConnect-PDF-Merger.app"
        if os.path.exists(app_path):
            # Calculate size
            def get_size(start_path):
                total_size = 0
                for dirpath, dirnames, filenames in os.walk(start_path):
                    for f in filenames:
                        fp = os.path.join(dirpath, f)
                        if not os.path.islink(fp):
                            total_size += os.path.getsize(fp)
                return total_size
            
            app_size = get_size(app_path) / (1024 * 1024)  # MB
            print(f"📦 .app bundle criado: {app_path} ({app_size:.1f} MB)")
            print("🎉 Arquivo .app v2.2 Minimalist pronto para uso no macOS!")
            print("✨ Novidades: Interface limpa, drag-and-drop melhorado, defaults inteligentes")
            print(f"Para testar: open '{app_path}'")
        
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
    print("🔗 SpeedConnect PDF Merger v2.2 Minimalist - macOS .app Bundle Builder")
    print("✨ Interface limpa • Drag-and-drop melhorado • Defaults inteligentes")
    print("=" * 70)
    
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
    
    # Check if running on macOS
    if sys.platform != "darwin":
        print("⚠️ Este script é específico para macOS")
        print("Use build_executable.py para outras plataformas")
        sys.exit(1)
    
    # Check Xcode license
    if not check_xcode_license():
        sys.exit(1)
    
    # Build .app bundle
    if build_app_bundle():
        print("\n🎉 .app bundle v2.2 Minimalist criado com sucesso!")
        print("\n✨ Novidades desta versão:")
        print("• Interface minimalista e limpa")
        print("• Drag-and-drop melhorado (funciona em qualquer parte do item)")
        print("• Defaults inteligentes automáticos")
        print("• Feedback visual aprimorado")
        print("\nPróximos passos:")
        print("1. Teste o .app bundle na pasta 'dist'")
        print("2. Arraste para a pasta Applications se desejar")
        print("3. O .app é independente e não precisa de Python instalado")
    else:
        print("\n❌ Build falhou. Verifique os erros acima.")
        sys.exit(1)

if __name__ == "__main__":
    main()
