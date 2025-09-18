# 🚀 SpeedConnect PDF Merger - Portable Testing Guide

## 📋 Testing Your Standalone Executable

This guide will help you test the SpeedConnect PDF Merger executable on different systems without requiring Python installation.

## 🖥️ macOS Testing

### Current Build Status
- ✅ **Executable Created**: `dist/SpeedConnect-PDF-Merger` (22.3 MB)
- ✅ **App Bundle Created**: `dist/SpeedConnect-PDF-Merger.app`
- ✅ **Architecture**: ARM64 (Apple Silicon)
- ✅ **Dependencies**: All bundled (no Python required)

### Testing on Your Current Mac
```bash
# Test the executable directly
./dist/SpeedConnect-PDF-Merger

# Or use the app bundle
open dist/SpeedConnect-PDF-Merger.app
```

### Testing on Another Mac via USB Drive

#### Step 1: Prepare USB Drive
1. Format USB drive as **ExFAT** (compatible with both Mac and Windows)
2. Create folder: `SpeedConnect-PDF-Merger-Portable`

#### Step 2: Copy Files to USB
```bash
# Copy the app bundle (recommended for Mac)
cp -r dist/SpeedConnect-PDF-Merger.app /Volumes/YOUR_USB/SpeedConnect-PDF-Merger-Portable/

# Copy the executable (alternative)
cp dist/SpeedConnect-PDF-Merger /Volumes/YOUR_USB/SpeedConnect-PDF-Merger-Portable/

# Copy documentation
cp README.md /Volumes/YOUR_USB/SpeedConnect-PDF-Merger-Portable/
cp -r assets /Volumes/YOUR_USB/SpeedConnect-PDF-Merger-Portable/
```

#### Step 3: Test on Target Mac
1. Insert USB drive
2. Navigate to the portable folder
3. Double-click `SpeedConnect-PDF-Merger.app` or run the executable
4. **No Python installation should be required!**

### Expected Behavior
- ✅ App launches immediately
- ✅ Modern GUI appears
- ✅ All features work (folder selection, PDF listing, merging)
- ✅ No error messages about missing Python or libraries

## 🪟 Windows Testing

### Building Windows Executable
Since you tested on Windows and it required Python, we need to rebuild with proper bundling:

```batch
# Use the updated build script
build_windows.bat
```

The updated script includes:
- `--collect-all=customtkinter` - Bundles all CustomTkinter files
- `--collect-all=pypdf` - Bundles all PyPDF files  
- `--collect-all=PIL` - Bundles all Pillow files
- `--hidden-import` flags for critical modules
- `--noconsole` - No command prompt window
- `--clean` - Clean build

### Windows Portable Testing
1. Copy `dist/SpeedConnect-PDF-Merger.exe` to USB drive
2. Test on Windows machine **without Python installed**
3. Should run without any dependencies

## 🔍 Troubleshooting

### If Executable Requires Python Installation

**Problem**: Target system asks for Python installation

**Solution**: Rebuild with better dependency bundling
```bash
# Enhanced build command
pyinstaller --onefile \
    --windowed \
    --icon=assets/icon.icns \
    --name="SpeedConnect-PDF-Merger" \
    --add-data="README.md:." \
    --add-data="assets:assets" \
    --collect-all=customtkinter \
    --collect-all=pypdf \
    --collect-all=PIL \
    --hidden-import=tkinter \
    --hidden-import=tkinter.ttk \
    --hidden-import=tkinter.filedialog \
    --hidden-import=tkinter.messagebox \
    --clean \
    pdf_merger_improved.py
```

### If App Won't Launch on macOS

**Problem**: "App is damaged" or security warning

**Solutions**:
1. **Right-click → Open** (bypass Gatekeeper)
2. **System Preferences → Security → Allow**
3. **Remove quarantine attribute**:
   ```bash
   xattr -dr com.apple.quarantine SpeedConnect-PDF-Merger.app
   ```

### If Missing Libraries Error

**Problem**: ImportError or ModuleNotFoundError

**Solution**: Add missing modules to build:
```bash
--hidden-import=MISSING_MODULE_NAME
```

## 📊 Testing Checklist

### ✅ Pre-Distribution Testing
- [ ] Executable runs on build machine
- [ ] No Python installation required
- [ ] All GUI elements appear correctly
- [ ] Folder selection works
- [ ] PDF detection works
- [ ] PDF merging works
- [ ] Progress bar functions
- [ ] Theme switching works
- [ ] Error handling works

### ✅ Portable Testing
- [ ] Copy to USB drive successful
- [ ] Runs on different Mac (same architecture)
- [ ] Runs on Intel Mac (if applicable)
- [ ] Runs on Windows without Python
- [ ] No additional files needed
- [ ] Performance acceptable

### ✅ Cross-Platform Testing
- [ ] macOS (ARM64) ✅
- [ ] macOS (Intel) - if available
- [ ] Windows 10/11 - needs rebuild
- [ ] Linux - optional

## 🎯 Distribution Best Practices

### For macOS
- Use `.app` bundle for better user experience
- Include both executable and app bundle
- Test on both Intel and Apple Silicon if possible

### For Windows  
- Use `.exe` with proper icon
- Include all DLLs and dependencies
- Test on clean Windows installation

### For All Platforms
- Include README and usage instructions
- Provide sample PDF files for testing
- Create simple folder structure
- Use ExFAT for cross-platform USB compatibility

## 📁 Recommended USB Structure
```
SpeedConnect-PDF-Merger-Portable/
├── macOS/
│   ├── SpeedConnect-PDF-Merger.app
│   └── SpeedConnect-PDF-Merger (executable)
├── Windows/
│   └── SpeedConnect-PDF-Merger.exe
├── README.md
├── USAGE.txt
├── assets/
│   └── icon.png
└── sample-pdfs/
    ├── document1.pdf
    └── document2.pdf
```

## 🚨 Important Notes

1. **Architecture Compatibility**: Current macOS build is ARM64 only
2. **Windows Build**: Needs proper dependency bundling
3. **File Permissions**: Ensure executables have execute permissions
4. **Security**: Users may need to bypass security warnings on first run
5. **Testing**: Always test on clean systems without development tools

## 📞 Support

If executable doesn't work on target system:
1. Check system requirements
2. Verify file permissions
3. Check for security restrictions
4. Try running from terminal for error messages
5. Rebuild with additional dependencies if needed
