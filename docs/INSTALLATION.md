# ⚙️ Instalação - SpeedConnect PDF Merger v2.2

## 📥 Executáveis (Recomendado)

### 🍎 macOS
```bash
# Download do .app bundle
# Arraste para Applications
# Duplo clique para executar
```

### 🐧 Linux/Unix
```bash
# Download do executável
chmod +x SpeedConnect-PDF-Merger
./SpeedConnect-PDF-Merger
```

### 🪟 Windows
```batch
# Download do .exe
# Duplo clique para executar
# Ou execute via linha de comando
SpeedConnect-PDF-Merger.exe
```

## 🛠️ Instalação do Código Fonte

### Pré-requisitos
- Python 3.8 ou superior
- pip (gerenciador de pacotes Python)

### Instalação Rápida
```bash
# Clone o repositório
git clone https://github.com/speedconnect/pdf-merger.git
cd pdf-merger

# Crie ambiente virtual (opcional)
python -m venv venv
source venv/bin/activate  # Linux/macOS
# ou
venv\Scripts\activate     # Windows

# Instale dependências
pip install -r requirements.txt

# Execute a aplicação
python pdf_merger_improved.py
```

### Dependências
```
customtkinter>=5.2.0    # Interface gráfica moderna
pypdf>=3.0.0           # Manipulação de PDFs
tkinterdnd2>=0.4.0     # Drag & Drop funcional
Pillow>=10.0.0         # Processamento de imagens
pyinstaller>=5.13.0    # Criação de executáveis
```

## 🔨 Criar Executável

### macOS - App Bundle
```bash
python build_app_bundle.py
# Resultado: dist/SpeedConnect-PDF-Merger.app
```

### Linux/Unix - Executável Único
```bash
python build_executable.py
# Resultado: dist/SpeedConnect-PDF-Merger
```

### Windows
```batch
build_windows.bat
# Resultado: dist/SpeedConnect-PDF-Merger.exe
```

## ⚠️ Solução de Problemas

### Drag & Drop não funciona
```bash
# Instale tkinterdnd2
pip install tkinterdnd2
```

### Erro de importação PIL
```bash
# Instale Pillow
pip install Pillow
```

### Erro PyPDF
```bash
# Instale pypdf
pip install pypdf
```
