#!/usr/bin/env python3
"""
Create truly standalone executables for SpeedConnect PDF Merger
This script ensures all dependencies are properly bundled
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def create_spec_file():
    """Create a custom .spec file for better control over the build process."""
    spec_content = '''
# -*- mode: python ; coding: utf-8 -*-
import sys

block_cipher = None

a = Analysis(
    ['pdf_merger_improved.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('README.md', '.'),
        ('assets', 'assets'),
    ],
    hiddenimports=[
        'PIL',
        'PIL._tkinter_finder',
        'PIL.Image',
        'PIL.ImageTk',
        'tkinter',
        'tkinter.ttk',
        'tkinter.filedialog',
        'tkinter.messagebox',
        'customtkinter',
        'pypdf',
        'pypdf.generic',
        'threading',
        'queue',
        'darkdetect',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# Collect all customtkinter files
from PyInstaller.utils.hooks import collect_all
datas, binaries, hiddenimports = collect_all('customtkinter')
a.datas += datas
a.binaries += binaries
a.hiddenimports += hiddenimports

# Collect all pypdf files
datas, binaries, hiddenimports = collect_all('pypdf')
a.datas += datas
a.binaries += binaries
a.hiddenimports += hiddenimports

# Collect all PIL files
datas, binaries, hiddenimports = collect_all('PIL')
a.datas += datas
a.binaries += binaries
a.hiddenimports += hiddenimports

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='SpeedConnect-PDF-Merger',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/icon.icns' if sys.platform == 'darwin' else 'assets/SpeedConect.ico',
)
'''
    
    with open('SpeedConnect-PDF-Merger.spec', 'w') as f:
        f.write(spec_content.strip())
    
    print("✅ Custom .spec file created")

def build_standalone():
    """Build truly standalone executable."""
    print("🔨 Building standalone executable...")
    
    # Clean previous builds
    for dir_name in ['build', 'dist']:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"🧹 Cleaned {dir_name}")
    
    # Remove old spec files
    for spec_file in Path('.').glob('*.spec'):
        spec_file.unlink()
    
    # Create custom spec file
    create_spec_file()
    
    # Build using spec file
    cmd = ['pyinstaller', '--clean', 'SpeedConnect-PDF-Merger.spec']
    
    print(f"🚀 Running: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✅ Build completed successfully!")
        
        # Check executable
        if sys.platform == "win32":
            exe_path = "dist/SpeedConnect-PDF-Merger.exe"
        else:
            exe_path = "dist/SpeedConnect-PDF-Merger"
        
        if os.path.exists(exe_path):
            file_size = os.path.getsize(exe_path) / (1024 * 1024)
            print(f"📦 Executable created: {exe_path} ({file_size:.1f} MB)")
            
            # Make executable on Unix systems
            if sys.platform != "win32":
                os.chmod(exe_path, 0o755)
                print("🔧 Execute permissions set")
            
            return True
        else:
            print("❌ Executable not found")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Build failed:")
        print(f"stdout: {e.stdout}")
        print(f"stderr: {e.stderr}")
        return False

def test_executable():
    """Test if executable runs without Python."""
    print("🧪 Testing executable...")
    
    exe_path = "dist/SpeedConnect-PDF-Merger.exe" if sys.platform == "win32" else "dist/SpeedConnect-PDF-Merger"
    
    if not os.path.exists(exe_path):
        print("❌ Executable not found")
        return False
    
    # Test basic execution (should start GUI)
    try:
        # Just check if it starts without immediate crash
        process = subprocess.Popen([exe_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait a bit to see if it crashes immediately
        import time
        time.sleep(2)
        
        if process.poll() is None:
            # Still running, kill it
            process.terminate()
            print("✅ Executable starts successfully")
            return True
        else:
            # Process ended, check why
            stdout, stderr = process.communicate()
            print(f"❌ Executable failed to start:")
            print(f"stdout: {stdout.decode()}")
            print(f"stderr: {stderr.decode()}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing executable: {e}")
        return False

def create_portable_package():
    """Create a portable package for distribution."""
    print("📦 Creating portable package...")
    
    exe_path = "dist/SpeedConnect-PDF-Merger.exe" if sys.platform == "win32" else "dist/SpeedConnect-PDF-Merger"
    
    if not os.path.exists(exe_path):
        print("❌ Executable not found")
        return False
    
    # Create portable directory
    portable_dir = "SpeedConnect-PDF-Merger-Portable"
    if os.path.exists(portable_dir):
        shutil.rmtree(portable_dir)
    
    os.makedirs(portable_dir)
    
    # Copy executable
    shutil.copy2(exe_path, portable_dir)
    
    # Copy documentation
    if os.path.exists("README.md"):
        shutil.copy2("README.md", portable_dir)
    
    # Copy assets
    if os.path.exists("assets"):
        shutil.copytree("assets", os.path.join(portable_dir, "assets"))
    
    # Create usage instructions
    instructions = """
# SpeedConnect PDF Merger - Portable Version

## How to Use:
1. Double-click SpeedConnect-PDF-Merger to run
2. No Python installation required!
3. Works on any compatible system

## System Requirements:
- Windows 10+ / macOS 10.14+ / Linux (modern distro)
- No additional software needed

## Features:
- Merge multiple PDF files
- Modern GUI interface
- Progress tracking
- Theme customization
- Subfolder support

For more information, see README.md
"""
    
    with open(os.path.join(portable_dir, "USAGE.txt"), "w") as f:
        f.write(instructions.strip())
    
    print(f"✅ Portable package created: {portable_dir}/")
    return True

def main():
    """Main function."""
    print("🔗 SpeedConnect PDF Merger - Standalone Builder")
    print("=" * 50)
    
    # Check if we have the source file
    if not os.path.exists('pdf_merger_improved.py'):
        print("❌ pdf_merger_improved.py not found!")
        return False
    
    # Build standalone executable
    if not build_standalone():
        return False
    
    # Test executable
    if not test_executable():
        print("⚠️ Executable test failed, but build completed")
    
    # Create portable package
    create_portable_package()
    
    print("\n🎉 Standalone executable ready!")
    print("📁 Check the 'SpeedConnect-PDF-Merger-Portable' folder")
    print("💾 Copy this folder to USB drive for distribution")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
