#!/usr/bin/env python3
"""
PDF Merger Application Enhanced
===============================
A modern GUI application for merging PDF files with advanced features.

Features:
- Select and merge multiple PDF files from different directories
- Individual file selection with management controls
- Flexible output directory selection
- Search PDFs in subfolders (folder mode)
- Progress bar during merging
- Theme customization
- Input validation
- Detailed error messages
- Company branding

Author: SpeedConnect Team
Version: 2.1 Enhanced
"""

import os
import re
import threading
import time
import json
from pathlib import Path
from typing import List, Tuple, Optional
import customtkinter as ctk
from tkinter import filedialog, messagebox, Menu
import sys
try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
    DRAG_DROP_AVAILABLE = True
except ImportError:
    DRAG_DROP_AVAILABLE = False
    print("⚠️ tkinterdnd2 não disponível - drag-and-drop desabilitado")
try:
    from pypdf import PdfWriter as PdfMerger
except ImportError:
    try:
        from PyPDF2 import PdfMerger
    except ImportError:
        from pypdf import PdfMerger


class PDFMergerApp:
    """Main application class for PDF Merger."""
    
    # Constants
    MAX_FILENAME_LENGTH = 200
    INVALID_CHARS = r'[<>:"/\\|?*]'
    APPEARANCE_MODES = ["System", "Dark", "Light"]
    
    def __init__(self):
        """Initialize the application."""
        self.setup_theme()
        self.create_main_window()
        self.create_variables()
        self.load_preferences()  # Carregar preferências antes de criar widgets
        self.create_widgets()
        self.setup_layout()
        self.update_ui_from_preferences()  # Atualizar UI com preferências carregadas
        self.update_smart_defaults()  # Atualizar defaults inteligentes
        
    def setup_keyboard_shortcuts(self):
        """Setup keyboard shortcuts for common operations."""
        # Ctrl+O - Open/Add files
        self.root.bind('<Control-o>', lambda e: self.selecionar_arquivos_individuais())
        self.root.bind('<Command-o>', lambda e: self.selecionar_arquivos_individuais())  # macOS
        
        # Ctrl+Shift+O - Open folder
        self.root.bind('<Control-Shift-O>', lambda e: self.selecionar_pasta())
        self.root.bind('<Command-Shift-O>', lambda e: self.selecionar_pasta())  # macOS
        
        # Ctrl+A - Select all
        self.root.bind('<Control-a>', lambda e: self.selecionar_todos())
        self.root.bind('<Command-a>', lambda e: self.selecionar_todos())  # macOS
        
        # Ctrl+D - Deselect all
        self.root.bind('<Control-d>', lambda e: self.desmarcar_todos())
        self.root.bind('<Command-d>', lambda e: self.desmarcar_todos())  # macOS
        
        # Ctrl+L - Clear list
        self.root.bind('<Control-l>', lambda e: self.limpar_lista_arquivos())
        self.root.bind('<Command-l>', lambda e: self.limpar_lista_arquivos())  # macOS
        
        # Ctrl+M - Merge PDFs
        self.root.bind('<Control-m>', lambda e: self.juntar_pdfs_threaded() if not self.is_merging else None)
        self.root.bind('<Command-m>', lambda e: self.juntar_pdfs_threaded() if not self.is_merging else None)  # macOS
        
        # Ctrl+S - Save to (choose output directory)
        self.root.bind('<Control-s>', lambda e: self.selecionar_pasta_destino())
        self.root.bind('<Command-s>', lambda e: self.selecionar_pasta_destino())  # macOS
        
        # F1 - Show help
        self.root.bind('<F1>', lambda e: self.mostrar_ajuda())
        
        # Focus on filename entry when typing
        self.root.bind('<Control-n>', lambda e: self.entrada_nome.focus())
        self.root.bind('<Command-n>', lambda e: self.entrada_nome.focus())  # macOS
        
    def setup_theme(self):
        """Configure the initial theme."""
        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")
        
    def create_main_window(self):
        """Create and configure the main window."""
        if DRAG_DROP_AVAILABLE:
            # Use TkinterDnD root for drag-and-drop support
            self.root = TkinterDnD.Tk()
        else:
            self.root = ctk.CTk()
            
        self.root.title("SpeedConnect - PDF Merger v2.2 Minimalist")
        self.root.geometry("550x600")  # Tamanho inicial ultra-compacto
        self.root.resizable(True, True)  # Totalmente redimensionável
        
        # Set minimum size - ultra-flexibilidade
        self.root.minsize(400, 450)  # Mínimo ultra-flexível
        
        # Bind keyboard shortcuts
        self.setup_keyboard_shortcuts()
        
        # Configure window closing protocol
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # App-level container to ensure proper light/dark background (avoids dark gaps)
        self.app_container = ctk.CTkFrame(
            self.root,
            corner_radius=0,
            fg_color=("gray95", "gray15")
        )
        self.app_container.pack(fill="both", expand=True)
        
        # Create main responsive scrollable frame inside container
        self.main_scroll = ctk.CTkScrollableFrame(
            self.app_container,
            corner_radius=0,
            fg_color=("gray95", "gray15")
        )
        self.main_scroll.pack(fill="both", expand=True, padx=2, pady=2)  # Padding ultra-mínimo
        
        # Bind resize event for responsive behavior
        self.root.bind("<Configure>", self.on_window_resize)
        
        # Store initial window size for responsive calculations
        self.initial_width = 600
        self.initial_height = 700
        
    def on_closing(self):
        """Handle window close event: persist preferences and close safely."""
        try:
            # Tentar salvar preferências antes de sair
            if hasattr(self, 'save_preferences'):
                self.save_preferences()
        except Exception as e:
            print(f"Aviso: falha ao salvar preferências no fechamento: {e}")
        
        # Se estiver em processo de merge, confirmar com o usuário
        try:
            if getattr(self, 'is_merging', False):
                if messagebox.askokcancel("Sair", "Uma operação está em andamento. Deseja sair mesmo assim?"):
                    self.root.destroy()
                return
        except Exception:
            # Se messagebox falhar por qualquer motivo, fechar direto
            pass
        
        # Fechar a janela
        try:
            self.root.destroy()
        except Exception:
            pass

    def create_variables(self):
        """Initialize application variables."""
        self.pasta_var = ctk.StringVar()
        self.nome_var = ctk.StringVar(value=self.generate_default_filename())
        self.appearance_var = ctk.StringVar(value="System")
        self.output_dir_var = ctk.StringVar(value=self.get_smart_default_output())
        self.auto_merge_var = ctk.BooleanVar(value=False)  # Auto-merge opcional
        self.auto_open_var = ctk.BooleanVar(value=True)   # Auto-abrir por padrão
        self.show_feedback_var = ctk.BooleanVar(value=False)  # Feedback visual desabilitado por padrão
        self.checkboxes = []  # Manter para compatibilidade
        self.individual_files = []  # Lista para arquivos selecionados individualmente
        self.file_items = []  # Lista para widgets dos itens drag-sortable
        self.is_merging = False
        
    def create_widgets(self):
        """Create all GUI widgets."""
        self.create_header()
        self.create_folder_selection()
        self.create_pdf_list()
        self.create_selection_buttons_minimal()  # Versão minimalista
        self.create_info_section()
        self.create_filename_input()
        self.create_output_selection()
        self.create_progress_section()
        self.create_action_buttons()
        
    def create_header(self):
        """Create minimal application header with file stats."""
        self.header_frame = ctk.CTkFrame(self.main_scroll, fg_color="transparent")
        
        # Título principal - ultra minimalista
        self.title_label = ctk.CTkLabel(
            self.header_frame, 
            text="PDF Merger",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=("gray10", "gray90")
        )
        self.title_label.pack(pady=(4, 0))  # Sem padding inferior
        
        # Subtítulo com estatísticas dos arquivos
        self.subtitle_label = ctk.CTkLabel(
            self.header_frame,
            text="",  # Inicialmente vazio
            font=ctk.CTkFont(size=12),
            text_color=("gray40", "gray70")
        )
        self.subtitle_label.pack(pady=(0, 0))  # Sem padding
        
    def create_folder_selection(self):
        """Create minimalist drag & drop section."""
        self.folder_frame = ctk.CTkFrame(self.main_scroll, corner_radius=15)
        
        # Área central de drag & drop - ultra minimalista
        self.drop_frame = ctk.CTkFrame(
            self.folder_frame, 
            height=120,  # Altura ainda menor
            corner_radius=10,  # Corner radius menor
            border_width=1,  # Borda mais fina
            border_color=("gray70", "gray30")
        )
        self.drop_frame.pack(pady=2, padx=4, fill="both", expand=True)  # Padding ultra-mínimo
        
        # Container central para o conteúdo
        self.drop_content = ctk.CTkFrame(self.drop_frame, fg_color="transparent")
        self.drop_content.pack(expand=True, fill="both")
        
        # Ícone ultra minimalista
        self.drop_icon = ctk.CTkLabel(
            self.drop_content,
            text="📄",
            font=ctk.CTkFont(size=36)  # Ainda menor
        )
        self.drop_icon.pack(pady=(15, 4))  # Padding ultra-mínimo
        
        # Texto principal
        if DRAG_DROP_AVAILABLE:
            main_text = "Arraste arquivos PDF aqui"
            sub_text = "ou clique para selecionar"
        else:
            main_text = "Clique para selecionar"
            sub_text = "arquivos PDF"
        
        self.drop_label_main = ctk.CTkLabel(
            self.drop_content,
            text=main_text,
            font=ctk.CTkFont(size=14, weight="bold"),  # Ainda menor
            text_color=("gray20", "gray80")
        )
        self.drop_label_main.pack(pady=(0, 1))  # Padding ultra-mínimo
        
        self.drop_label_sub = ctk.CTkLabel(
            self.drop_content,
            text=sub_text,
            font=ctk.CTkFont(size=10),  # Ainda menor
            text_color="gray"
        )
        self.drop_label_sub.pack(pady=(0, 4))  # Padding ultra-mínimo
        
        # Botão "Adicionar Mais" - mais compacto
        self.btn_add_more = ctk.CTkButton(
            self.drop_content,
            text="➕ Adicionar Mais Arquivos",
            command=self.selecionar_arquivos_individuais,
            height=36,  # Reduzido de 45 para 36
            font=ctk.CTkFont(size=12, weight="bold"),  # Reduzido fonte
            corner_radius=8
        )
        # Não fazer pack() ainda - será mostrado condicionalmente
        
        # Fazer toda a área clicável
        self.drop_frame.bind("<Button-1>", lambda e: self.selecionar_arquivos_individuais())
        self.drop_content.bind("<Button-1>", lambda e: self.selecionar_arquivos_individuais())
        self.drop_icon.bind("<Button-1>", lambda e: self.selecionar_arquivos_individuais())
        self.drop_label_main.bind("<Button-1>", lambda e: self.selecionar_arquivos_individuais())
        self.drop_label_sub.bind("<Button-1>", lambda e: self.selecionar_arquivos_individuais())
        
        # Configurar drag-and-drop se disponível
        if DRAG_DROP_AVAILABLE:
            self.setup_drag_and_drop()
        
        # Label de status - inicialmente oculto
        self.pasta_label = ctk.CTkLabel(
            self.folder_frame,
            text="",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=("green", "lightgreen")
        )
        # Não fazer pack() ainda - será mostrado quando houver arquivos
        
    def setup_drag_and_drop(self):
        """Configure drag-and-drop functionality."""
        try:
            # Register drop target for all drop area elements
            elements_to_register = [
                self.drop_frame,
                self.drop_content,
                self.drop_icon,
                self.drop_label_main,
                self.drop_label_sub
            ]
            
            for element in elements_to_register:
                element.drop_target_register(DND_FILES)
                element.dnd_bind('<<Drop>>', self.on_drop)
                element.dnd_bind('<<DragEnter>>', self.on_drag_enter)
                element.dnd_bind('<<DragLeave>>', self.on_drag_leave)
            
        except Exception as e:
            print(f"Erro ao configurar drag-and-drop: {e}")
            
    def on_drag_enter(self, event):
        """Handle drag enter event."""
        self.drop_frame.configure(
            fg_color=("lightblue", "darkblue"),
            border_color=("blue", "lightblue")
        )
        self.drop_icon.configure(text="📥")
        self.drop_label_main.configure(text="Solte os arquivos aqui!", text_color="blue")
        self.drop_label_sub.configure(text="Arquivos PDF serão adicionados automaticamente", text_color="blue")
        
    def on_drag_leave(self, event):
        """Handle drag leave event."""
        self.drop_frame.configure(
            fg_color=("gray90", "gray13"),
            border_color=("gray70", "gray30")
        )
        self.drop_icon.configure(text="📄")
        
        if DRAG_DROP_AVAILABLE:
            self.drop_label_main.configure(text="Arraste arquivos PDF aqui", text_color=("gray20", "gray80"))
            self.drop_label_sub.configure(text="ou clique para selecionar", text_color="gray")
        else:
            self.drop_label_main.configure(text="Clique para selecionar", text_color=("gray20", "gray80"))
            self.drop_label_sub.configure(text="arquivos PDF", text_color="gray")
            
    def on_drop(self, event):
        """Handle file drop event."""
        try:
            # Reset visual feedback
            self.on_drag_leave(event)
            
            # Get dropped files
            files = self.root.tk.splitlist(event.data)
            pdf_files = []
            
            # Filter for PDF files
            for file_path in files:
                if file_path.lower().endswith('.pdf'):
                    pdf_files.append(file_path)
                    
            if pdf_files:
                # Process dropped PDF files
                self.processar_arquivos_arrastados(pdf_files)
            else:
                messagebox.showwarning(
                    "Arquivos Inválidos",
                    "Apenas arquivos PDF são aceitos.\nArquivos suportados: .pdf"
                )
                
        except Exception as e:
            print(f"Erro ao processar arquivos arrastados: {e}")
            messagebox.showerror("Erro", f"Erro ao processar arquivos: {str(e)}")
            
    def processar_arquivos_arrastados(self, pdf_files):
        """Process dropped PDF files with auto-selection."""
        # Limpar seleção de pasta quando arrastar arquivos
        self.pasta_var.set("")
        
        # Validar e adicionar arquivos
        arquivos_validos = 0
        arquivos_invalidos = []
        
        for arquivo in pdf_files:
            if arquivo not in [f[0] for f in self.individual_files]:
                # Validar arquivo PDF
                is_valid, error_msg, page_count = self.validate_pdf_file(arquivo)
                
                if is_valid:
                    filename = os.path.basename(arquivo)
                    # Auto-selecionar arquivo (True no final)
                    self.individual_files.append((arquivo, filename, page_count, True))
                    arquivos_validos += 1
                else:
                    arquivos_invalidos.append((os.path.basename(arquivo), error_msg))
        
        # Mostrar resultado apenas se houver erros
        if arquivos_invalidos:
            invalid_list = "\n".join([f"• {name}: {error}" for name, error in arquivos_invalidos])
            messagebox.showwarning(
                "Alguns Arquivos Inválidos",
                f"Os seguintes arquivos não puderam ser adicionados:\n\n{invalid_list}"
            )
        
        if arquivos_validos > 0:
            self.atualizar_interface_com_arquivos()
            self.atualizar_info_section()
            self.listar_arquivos_individuais()
            
            # Feedback visual sutil apenas se habilitado
            if self.show_feedback_var.get():
                self.mostrar_feedback_sucesso(arquivos_validos)
        elif not arquivos_invalidos:
            # Feedback sutil para arquivos duplicados apenas se habilitado
            if self.show_feedback_var.get():
                self.mostrar_feedback_duplicados()
        
    def create_pdf_list(self):
        """Create clean, minimal PDF list."""
        # Sem label - lista fala por si
        self.frame_scroll = ctk.CTkScrollableFrame(
            self.main_scroll, 
            corner_radius=12,
            height=200,  # Mais compacto
            fg_color=("gray98", "gray12")
        )
        self.frame_pdfs = self.frame_scroll
        
    def create_selection_buttons_minimal(self):
        """Create minimal selection control buttons - removed for cleaner interface."""
        # Removido - interface auto-seleciona tudo, sem necessidade de botões extras
        self.selection_frame = ctk.CTkFrame(self.main_scroll, fg_color="transparent")
    
    def create_minimal_controls(self):
        """Create minimal controls for file list."""
        # Apenas instrução sutil
        instruction_label = ctk.CTkLabel(
            self.frame_pdfs,
            text="Arraste para reordenar • Clique direito para opções",
            font=ctk.CTkFont(size=11),
            text_color=("gray50", "gray60")
        )
        instruction_label.pack(pady=(15, 20))  # Mais whitespace
        
    def create_info_section(self):
        """Create minimal stats display integrated with drop area."""
        # Integrado na área de drop - sem frame separado
        self.info_frame = ctk.CTkFrame(self.main_scroll, fg_color="transparent")
        
        # Stats simples e discretos
        self.info_text = ctk.CTkLabel(
            self.info_frame,
            text="",
            font=ctk.CTkFont(size=12),  # Fonte menor
            text_color=("gray40", "gray70")
        )
        self.info_text.pack(pady=(0, 15))  # Menos whitespace
        
    def atualizar_info_section(self):
        """Update the subtitle with file statistics."""
        if not self.individual_files:
            self.subtitle_label.configure(text="")
            return
            
        total_files = len(self.individual_files)
        total_pages = sum(file_info[2] if len(file_info) >= 3 else 0 for file_info in self.individual_files)
        
        # Atualizar subtítulo no header
        if total_pages > 0:
            subtitle_text = f"{total_files} arquivos • {total_pages} páginas"
        else:
            subtitle_text = f"{total_files} arquivos"
            
        self.subtitle_label.configure(text=subtitle_text)
        
        # Limpar o texto verde antigo (se ainda existir)
        self.info_text.configure(text="")
        
    def create_filename_input(self):
        """Create minimal smart defaults section."""
        self.defaults_frame = ctk.CTkFrame(self.main_scroll, fg_color="transparent")
        
        # Container ultra-compacto para defaults
        self.defaults_container = ctk.CTkFrame(
            self.defaults_frame, 
            corner_radius=6,  # Corner radius menor
            fg_color=("gray95", "gray15")
        )
        self.defaults_container.pack(fill="x", padx=4, pady=(0, 3))  # Padding ultra-mínimo
        
        # Labels editáveis em linha horizontal - ultra-compacto
        self.labels_row = ctk.CTkFrame(self.defaults_container, fg_color="transparent")
        self.labels_row.pack(fill="x", padx=6, pady=4)  # Padding ultra-mínimo
        
        # Nome do arquivo - responsivo
        self.filename_label = ctk.CTkLabel(
            self.labels_row,
            text=self.nome_var.get(),
            font=ctk.CTkFont(size=11),
            cursor="hand2",
            text_color=("#2196F3", "#64B5F6")
        )
        self.filename_label.pack(side="left", padx=(0, 8))  # Espaço responsivo
        self.filename_label.bind("<Button-1>", self.edit_filename)
        
        # Separador visual - responsivo
        self.separator = ctk.CTkLabel(
            self.labels_row,
            text="•",
            font=ctk.CTkFont(size=10),
            text_color=("gray50", "gray60")
        )
        self.separator.pack(side="left", padx=(0, 8))  # Espaço responsivo
        
        # Destino - responsivo
        self.output_label_smart = ctk.CTkLabel(
            self.labels_row,
            text=self.get_display_output_path(),
            font=ctk.CTkFont(size=11),
            cursor="hand2",
            text_color=("#2196F3", "#64B5F6")
        )
        self.output_label_smart.pack(side="left")
        self.output_label_smart.bind("<Button-1>", self.edit_output_path)
        
        # Opções avançadas colapsáveis
        self.create_advanced_options()
    
    def on_window_resize(self, event):
        """Handle window resize events for responsive behavior."""
        # Only handle root window resize events
        if event.widget != self.root:
            return
            
        current_width = self.root.winfo_width()
        current_height = self.root.winfo_height()
        
        # Adjust drop area height based on window size - ultra-minimal
        if hasattr(self, 'drop_frame'):
            if current_height < 500:
                # Ultra small window - ultra minimal drop area
                new_height = 80
                icon_size = 24
                main_font = 12
                sub_font = 8
            elif current_height < 600:
                # Very small window - minimal drop area
                new_height = 100
                icon_size = 30
                main_font = 13
                sub_font = 9
            elif current_height < 700:
                # Small window - compact drop area
                new_height = 120
                icon_size = 36
                main_font = 14
                sub_font = 10
            else:
                # Normal/large window - standard drop area
                new_height = 120
                icon_size = 36
                main_font = 14
                sub_font = 10
            
            # Update drop frame height
            self.drop_frame.configure(height=new_height)
            
            # Update icon and text sizes
            if hasattr(self, 'drop_icon'):
                self.drop_icon.configure(font=ctk.CTkFont(size=icon_size))
            if hasattr(self, 'drop_label_main'):
                self.drop_label_main.configure(font=ctk.CTkFont(size=main_font, weight="bold"))
            if hasattr(self, 'drop_label_sub'):
                self.drop_label_sub.configure(font=ctk.CTkFont(size=sub_font))
        
        # Adjust title size based on window width - ultra-minimal
        if hasattr(self, 'title_label'):
            if current_width < 450:
                title_size = 14
            elif current_width < 550:
                title_size = 15
            else:
                title_size = 16
            self.title_label.configure(font=ctk.CTkFont(size=title_size, weight="bold"))
        
        # Adjust padding based on window size - ultra-minimal
        if current_width < 450:
            # Ultra narrow - ultra minimal padding
            padding = 1
        elif current_width < 550:
            # Very narrow - minimal padding
            padding = 2
        else:
            # Normal/wide - compact padding
            padding = 3
        
        # Update layout padding dynamically
        try:
            self.folder_frame.pack_configure(padx=padding)
            if hasattr(self, 'defaults_container'):
                self.defaults_container.pack_configure(padx=padding)
        except:
            pass  # Ignore if widgets don't exist yet
        
        # Update file list items for responsive text truncation
        self.root.after_idle(lambda: self.update_file_list_responsive(current_width))
    
    def create_advanced_options(self):
        """Create collapsible advanced options section."""
        self.advanced_frame = ctk.CTkFrame(self.main_scroll, fg_color="transparent")
        
        # Botão para expandir/colapsar
        self.advanced_toggle = ctk.CTkButton(
            self.advanced_frame,
            text="⚙️ Opções Avançadas",
            command=self.toggle_advanced_options,
            height=32,
            font=ctk.CTkFont(size=11),
            fg_color="transparent",
            text_color=("gray50", "gray60"),
            hover_color=("gray90", "gray20")
        )
        self.advanced_toggle.pack(pady=(20, 10))
        
        # Container para opções (inicialmente oculto)
        self.advanced_content = ctk.CTkFrame(
            self.advanced_frame,
            corner_radius=8,
            fg_color=("gray92", "gray18")
        )
        self.advanced_expanded = False
        
        # Conteúdo das opções avançadas
        options_row = ctk.CTkFrame(self.advanced_content, fg_color="transparent")
        options_row.pack(fill="x", padx=15, pady=12)
        
        # Auto-merge checkbox
        self.auto_merge_checkbox = ctk.CTkCheckBox(
            options_row,
            text="Auto-Juntar",
            variable=self.auto_merge_var,
            font=ctk.CTkFont(size=11),
            command=self.on_auto_merge_changed
        )
        self.auto_merge_checkbox.pack(side="left", padx=(0, 20))
        
        # Auto-open checkbox
        self.auto_open_checkbox = ctk.CTkCheckBox(
            options_row,
            text="Auto-Abrir",
            variable=self.auto_open_var,
            font=ctk.CTkFont(size=11)
        )
        self.auto_open_checkbox.pack(side="left", padx=(0, 20))
        
        # Show feedback checkbox
        self.show_feedback_checkbox = ctk.CTkCheckBox(
            options_row,
            text="Mostrar Feedback",
            variable=self.show_feedback_var,
            font=ctk.CTkFont(size=11)
        )
        self.show_feedback_checkbox.pack(side="left", padx=(0, 20))
        
        # Seletor de tema
        theme_label = ctk.CTkLabel(
            options_row,
            text="Tema:",
            font=ctk.CTkFont(size=11),
            text_color=("gray50", "gray60")
        )
        theme_label.pack(side="left", padx=(0, 5))
        
        self.appearance_menu = ctk.CTkOptionMenu(
            options_row,
            variable=self.appearance_var,
            values=self.APPEARANCE_MODES,
            command=self.change_appearance,
            width=80,
            height=24,
            font=ctk.CTkFont(size=10)
        )
        self.appearance_menu.pack(side="left", padx=(0, 20))
        
        # Botão de ajuda
        help_btn = ctk.CTkButton(
            options_row,
            text="?",
            command=self.show_help_tooltip,
            width=24,
            height=24,
            font=ctk.CTkFont(size=11),
            corner_radius=12
        )
        help_btn.pack(side="right")
    
    def toggle_advanced_options(self):
        """Toggle advanced options visibility."""
        if self.advanced_expanded:
            self.advanced_content.pack_forget()
            self.advanced_toggle.configure(text="⚙️ Opções Avançadas")
            self.advanced_expanded = False
        else:
            self.advanced_content.pack(fill="x", pady=(0, 10))
            self.advanced_toggle.configure(text="⚙️ Opções Avançadas ▲")
            self.advanced_expanded = True
    
    def show_help_tooltip(self):
        """Show help as modal tooltip."""
        # Criar tooltip modal
        help_modal = ctk.CTkToplevel(self.root)
        help_modal.title("Ajuda - PDF Merger")
        help_modal.geometry("400x300")
        help_modal.resizable(False, False)
        help_modal.transient(self.root)
        help_modal.grab_set()
        
        # Centralizar na tela
        help_modal.update_idletasks()
        x = (help_modal.winfo_screenwidth() // 2) - (400 // 2)
        y = (help_modal.winfo_screenheight() // 2) - (300 // 2)
        help_modal.geometry(f"400x300+{x}+{y}")
        
        # Conteúdo da ajuda
        help_text = ctk.CTkTextbox(
            help_modal,
            font=ctk.CTkFont(size=12),
            wrap="word"
        )
        help_text.pack(fill="both", expand=True, padx=20, pady=20)
        
        help_content = """PDF Merger - Ajuda Rápida

🎯 COMO USAR:
1. Arraste arquivos PDF para a área central
2. Reordene arrastando itens na lista
3. Clique em "Juntar PDFs" ou use auto-merge

⌨️ ATALHOS:
• Ctrl+O: Adicionar arquivos
• Ctrl+M: Juntar PDFs
• F1: Esta ajuda

🖱️ DICAS:
• Clique direito nos itens para opções
• Clique nos textos azuis para editar
• Use auto-merge para fluxo instantâneo

✨ RECURSOS:
• Drag & drop para reordenar
• Defaults inteligentes automáticos
• Validação de PDFs em tempo real
• Contagem automática de páginas"""
        
        help_text.insert("0.0", help_content)
        help_text.configure(state="disabled")
        
        # Botão fechar
        close_btn = ctk.CTkButton(
            help_modal,
            text="Fechar",
            command=help_modal.destroy,
            width=100
        )
        close_btn.pack(pady=(0, 20))
        
    def create_output_selection(self):
        """Legacy method - now integrated into smart defaults."""
        # Método mantido para compatibilidade, mas funcionalidade movida para create_filename_input
        pass
        
    def create_progress_section(self):
        """Create minimal progress section."""
        self.progress_frame = ctk.CTkFrame(self.main_scroll, fg_color="transparent")
        
        # Progress bar minimalista
        self.progress_bar = ctk.CTkProgressBar(
            self.progress_frame,
            height=4,  # Mais fino
            corner_radius=2,
            progress_color=("#2196F3", "#1976D2")  # Accent color
        )
        self.progress_bar.pack(fill="x", padx=40)
        self.progress_bar.set(0)
        
        # Label de status discreto
        self.progress_label = ctk.CTkLabel(
            self.progress_frame,
            text="",
            font=ctk.CTkFont(size=11),
            text_color=("gray50", "gray60")
        )
        self.progress_label.pack(pady=(8, 0))
        
    def create_action_buttons(self):
        """Create main action button - clean and prominent."""
        self.action_frame = ctk.CTkFrame(self.main_scroll, fg_color="transparent")
        
        # Botão principal - ultra minimalista
        self.btn_juntar = ctk.CTkButton(
            self.action_frame,
            text="🚀 Juntar PDFs",
            command=self.juntar_pdfs_threaded,
            height=40,  # Ainda menor
            font=ctk.CTkFont(size=14, weight="bold"),  # Fonte menor
            corner_radius=20,
            fg_color=("#2196F3", "#1976D2"),
            hover_color=("#1976D2", "#1565C0")
        )
        self.btn_juntar.pack(pady=(4, 6), padx=20)  # Padding ultra-mínimo
        
        
    def setup_layout(self):
        """Setup ultra-minimal layout with zero wasted space."""
        # TOPO: Header ultra-compacto - sem espaço inferior
        self.header_frame.pack(fill="x", padx=2)
        
        # TOPO: Drop zone + Stats integrados - colado ao header
        self.folder_frame.pack(pady=(0, 2), padx=3, fill="both", expand=True)
        self.info_frame.pack(fill="x", padx=2)
        
        # MEIO: Lista ultra-compacta
        self.frame_scroll.pack(pady=(0, 1), padx=3, fill="x")
        
        # FUNDO: Defaults + Botão + Progress - ultra-compacto
        self.defaults_frame.pack(pady=(0, 1), padx=3, fill="x")
        self.progress_frame.pack(pady=(0, 1), padx=3, fill="x")
        self.action_frame.pack(pady=(0, 1), padx=3, fill="x")
        
        # Opções avançadas (colapsável) - sem espaço final
        if hasattr(self, 'advanced_frame'):
            self.advanced_frame.pack(pady=(0, 0), padx=3, fill="x")  # Zero padding final
        
    def validate_filename(self, filename: str) -> Tuple[bool, str]:
        """
        Validate the filename for invalid characters and length.
        
        Args:
            filename: The filename to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not filename.strip():
            return False, "O nome do arquivo não pode estar vazio."
            
        if len(filename) > self.MAX_FILENAME_LENGTH:
            return False, f"O nome do arquivo é muito longo (máximo {self.MAX_FILENAME_LENGTH} caracteres)."
            
        if re.search(self.INVALID_CHARS, filename):
            return False, "O nome contém caracteres inválidos: < > : \" / \\ | ? *"
            
        return True, ""
        
    def validate_pdf_file(self, pdf_path: str) -> Tuple[bool, str, int]:
        """
        Validate if file is a proper PDF and get page count.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Tuple of (is_valid, error_message, page_count)
        """
        try:
            from pypdf import PdfReader
            reader = PdfReader(pdf_path)
            page_count = len(reader.pages)
            return True, "", page_count
        except Exception as e:
            return False, str(e), 0
    
    def get_pdf_files(self, directory: str, include_subfolders: bool = False) -> List[str]:
        """
        Get all PDF files from directory and optionally subfolders.
        
        Args:
            directory: Directory path to search
            include_subfolders: Whether to include subfolders
            
        Returns:
            List of PDF file paths
        """
        pdf_files = []
        
        try:
            if include_subfolders:
                print(f"Buscando PDFs em subpastas de: {directory}")
                for root, dirs, files in os.walk(directory):
                    for file in files:
                        if file.lower().endswith('.pdf'):
                            full_path = os.path.join(root, file)
                            pdf_files.append(full_path)
                            print(f"PDF encontrado: {full_path}")
            else:
                print(f"Buscando PDFs em: {directory}")
                if os.path.exists(directory) and os.path.isdir(directory):
                    for file in os.listdir(directory):
                        if file.lower().endswith('.pdf'):
                            full_path = os.path.join(directory, file)
                            pdf_files.append(full_path)
                            print(f"PDF encontrado: {full_path}")
                else:
                    print(f"Diretório não existe ou não é válido: {directory}")
                        
            print(f"Total de PDFs encontrados: {len(pdf_files)}")
            return sorted(pdf_files)
            
        except Exception as e:
            print(f"Erro ao buscar PDFs: {e}")
            messagebox.showerror(
                "Erro de Acesso",
                f"Erro ao acessar a pasta:\n{str(e)}\n\nVerifique se você tem permissão para acessar esta pasta."
            )
            return []
            
    def selecionar_pasta(self):
        """Handle folder selection."""
        pasta = filedialog.askdirectory(title="Escolha a pasta com PDFs")
        if pasta:
            # Limpar arquivos individuais quando selecionar pasta
            self.individual_files.clear()
            self.pasta_var.set(pasta)
            self.pasta_label.configure(text=f"Pasta: {pasta}")
            self.listar_pdfs()
            
    def selecionar_arquivos_individuais(self):
        """Handle individual file selection with improved UX."""
        arquivos = filedialog.askopenfilenames(
            title="Selecione arquivos PDF",
            filetypes=[("Arquivos PDF", "*.pdf"), ("Todos os arquivos", "*.*")]
        )
        if arquivos:
            # Limpar seleção de pasta quando selecionar arquivos individuais
            self.pasta_var.set("")
            
            # Validar e adicionar novos arquivos à lista
            arquivos_validos = 0
            arquivos_invalidos = []
            
            for arquivo in arquivos:
                if arquivo not in [f[0] for f in self.individual_files]:
                    # Validar arquivo PDF
                    is_valid, error_msg, page_count = self.validate_pdf_file(arquivo)
                    
                    if is_valid:
                        filename = os.path.basename(arquivo)
                        # Auto-selecionar arquivo (True no final)
                        self.individual_files.append((arquivo, filename, page_count, True))
                        arquivos_validos += 1
                    else:
                        arquivos_invalidos.append((os.path.basename(arquivo), error_msg))
            
            # Mostrar resultado da validação apenas se houver erros
            if arquivos_invalidos:
                invalid_list = "\n".join([f"• {name}: {error}" for name, error in arquivos_invalidos])
                messagebox.showwarning(
                    "Arquivos Inválidos",
                    f"Os seguintes arquivos não puderam ser adicionados:\n\n{invalid_list}"
                )
            
            if arquivos_validos > 0:
                self.atualizar_interface_com_arquivos()
                self.atualizar_info_section()
                self.listar_arquivos_individuais()
                
                # Feedback sutil apenas se habilitado nas opções
                if self.show_feedback_var.get():
                    self.mostrar_feedback_sucesso(arquivos_validos)
            elif not arquivos_invalidos:
                # Feedback sutil para arquivos duplicados apenas se habilitado
                if self.show_feedback_var.get():
                    self.mostrar_feedback_duplicados()
            
    def selecionar_pasta_destino(self):
        """Handle output directory selection."""
        pasta_destino = filedialog.askdirectory(title="Escolha a pasta de destino")
        if pasta_destino:
            self.output_dir_var.set(pasta_destino)
            if hasattr(self, 'output_label_smart'):
                self.output_label_smart.configure(text=self.get_display_output_path())
        else:
            # Se cancelar, manter o padrão
            self.output_dir_var.set("")
            if hasattr(self, 'output_label_smart'):
                self.output_label_smart.configure(text=self.get_display_output_path())
            
    def atualizar_interface_com_arquivos(self):
        """Update interface when files are added - no green text."""
        if self.individual_files:
            count = len(self.individual_files)
            total_pages = sum(file_info[2] if len(file_info) >= 3 else 0 for file_info in self.individual_files)
            
            # Não mostrar mais o texto verde - removido conforme solicitado
            # self.pasta_label.configure(text="")  # Limpar qualquer texto
            if hasattr(self, 'pasta_label'):
                self.pasta_label.pack_forget()  # Esconder completamente
            
            # Mostrar botão "Adicionar Mais" se houver arquivos
            self.btn_add_more.pack(pady=(10, 20))
            
            # Atualizar área de drop para modo compacto
            self.drop_frame.configure(height=200)  # Reduzir altura
            self.drop_icon.configure(text="📁", font=ctk.CTkFont(size=40))  # Ícone menor
            self.drop_icon.pack_configure(pady=(30, 10))  # Menos padding
            self.drop_label_main.configure(text="Arquivos adicionados", font=ctk.CTkFont(size=18, weight="bold"))
            self.drop_label_sub.configure(text="Use o botão abaixo para adicionar mais")
            
            # Atualizar defaults inteligentes
            self.update_smart_defaults()
            
            # Auto-merge se habilitado
            if self.auto_merge_var.get() and not self.is_merging:
                self.root.after(500, self.juntar_pdfs_threaded)  # Delay para UX
        else:
            # Voltar ao estado inicial
            self.pasta_label.pack_forget()
            self.btn_add_more.pack_forget()
            self.drop_frame.configure(height=400)
            self.drop_icon.configure(text="📄", font=ctk.CTkFont(size=80))
            self.drop_icon.pack_configure(pady=(80, 20))
            
            if DRAG_DROP_AVAILABLE:
                self.drop_label_main.configure(text="Arraste arquivos PDF aqui", font=ctk.CTkFont(size=24, weight="bold"))
                self.drop_label_sub.configure(text="ou clique para selecionar")
            else:
                self.drop_label_main.configure(text="Clique para selecionar", font=ctk.CTkFont(size=24, weight="bold"))
                self.drop_label_sub.configure(text="arquivos PDF")
    
    def mostrar_feedback_sucesso(self, count):
        """Show subtle success feedback."""
        # Animação sutil do ícone
        original_text = self.drop_icon.cget("text")
        self.drop_icon.configure(text="✅")
        self.root.after(1500, lambda: self.drop_icon.configure(text=original_text))
        
        # Atualizar texto temporariamente
        self.drop_label_main.configure(text=f"{count} arquivo(s) adicionado(s)!", text_color="green")
        self.root.after(2000, lambda: self.drop_label_main.configure(
            text="Arquivos adicionados", 
            text_color=("gray20", "gray80")
        ))
    
    def mostrar_feedback_duplicados(self):
        """Show feedback for duplicate files."""
        self.drop_label_sub.configure(text="Arquivos já estão na lista", text_color="orange")
        self.root.after(2000, lambda: self.drop_label_sub.configure(
            text="Use o botão abaixo para adicionar mais", 
            text_color="gray"
        ))
    
    def atualizar_label_arquivos(self):
        """Update the file selection label (legacy compatibility)."""
        self.atualizar_interface_com_arquivos()
    
    # Smart Defaults Functions
    def generate_default_filename(self):
        """Generate intelligent default filename with date."""
        from datetime import datetime
        date_str = datetime.now().strftime("%Y%m%d")
        return f"merged_pdf_{date_str}.pdf"
    
    def get_smart_default_output(self):
        """Get intelligent default output directory."""
        try:
            # Tentar Desktop primeiro
            desktop_path = os.path.expanduser("~/Desktop")
            if os.path.exists(desktop_path):
                return desktop_path
            
            # Fallback para Documentos
            return self.get_default_output_directory()
        except:
            return os.path.expanduser("~")
    
    def get_display_output_path(self):
        """Get display-friendly output path."""
        path = self.output_dir_var.get()
        if not path:
            path = self.get_smart_default_output()
            self.output_dir_var.set(path)
        
        # Mostrar apenas o nome da pasta para economizar espaço
        return f"Destino: {os.path.basename(path)}"
    
    def update_smart_defaults(self):
        """Update smart defaults based on current files."""
        if self.individual_files:
            # Atualizar destino baseado no primeiro arquivo
            first_file_dir = os.path.dirname(self.individual_files[0][0])
            if os.path.exists(first_file_dir):
                self.output_dir_var.set(first_file_dir)
            
            # Atualizar nome baseado no conteúdo
            count = len(self.individual_files)
            if count > 1:
                from datetime import datetime
                date_str = datetime.now().strftime("%Y%m%d_%H%M")
                new_name = f"merged_{count}files_{date_str}.pdf"
                self.nome_var.set(new_name)
        
        # Atualizar labels visuais
        if hasattr(self, 'filename_label'):
            self.filename_label.configure(text=self.nome_var.get())
        if hasattr(self, 'output_label_smart'):
            self.output_label_smart.configure(text=self.get_display_output_path())
    
    def edit_filename(self, event=None):
        """Edit filename via dialog."""
        from tkinter import simpledialog
        
        new_name = simpledialog.askstring(
            "Editar Nome do Arquivo",
            "Digite o novo nome do arquivo:",
            initialvalue=self.nome_var.get().replace('.pdf', '')
        )
        
        if new_name:
            if not new_name.endswith('.pdf'):
                new_name += '.pdf'
            
            # Validar nome
            is_valid, error_msg = self.validate_filename(new_name)
            if is_valid:
                self.nome_var.set(new_name)
                self.filename_label.configure(text=new_name)
            else:
                messagebox.showwarning("Nome Inválido", error_msg)
    
    def edit_output_path(self, event=None):
        """Edit output path via dialog."""
        new_path = filedialog.askdirectory(
            title="Escolher Pasta de Destino",
            initialdir=self.output_dir_var.get()
        )
        
        if new_path:
            self.output_dir_var.set(new_path)
            self.output_label_smart.configure(text=self.get_display_output_path())
    
    def on_auto_merge_changed(self):
        """Handle auto-merge checkbox change."""
        if self.auto_merge_var.get():
            # Feedback sutil
            self.progress_label.configure(
                text="Auto-merge ativado",
                text_color=("#2196F3", "#64B5F6")
            )
        else:
            self.progress_label.configure(
                text="",
                text_color=("gray50", "gray60")
            )
            
    def get_default_output_directory(self):
        """Get the default output directory (user's Documents folder)."""
        try:
            # Tentar obter a pasta Documentos do usuário
            if os.name == 'nt':  # Windows
                import winreg
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                                   r"Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders")
                documents_path = winreg.QueryValueEx(key, "Personal")[0]
                winreg.CloseKey(key)
                return documents_path
            else:  # macOS/Linux
                return os.path.expanduser("~/Documents")
        except:
            # Fallback para home directory
            return os.path.expanduser("~")
            
    def get_config_file_path(self):
        """Get the path to the configuration file."""
        config_dir = os.path.expanduser("~/.speedconnect")
        os.makedirs(config_dir, exist_ok=True)
        return os.path.join(config_dir, "pdf_merger_config.json")
        
    def save_preferences(self):
        """Save user preferences to config file."""
        try:
            preferences = {
                "appearance_mode": self.appearance_var.get(),
                "default_output_dir": self.output_dir_var.get(),
                "window_geometry": self.root.geometry(),
                "auto_merge": self.auto_merge_var.get(),
                "auto_open": self.auto_open_var.get()
            }
            
            config_path = self.get_config_file_path()
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(preferences, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"Erro ao salvar preferências: {e}")
            
    def load_preferences(self):
        """Load user preferences from config file."""
        try:
            config_path = self.get_config_file_path()
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    preferences = json.load(f)
            
                # Aplicar preferências carregadas
                if "appearance_mode" in preferences:
                    self.appearance_var.set(preferences["appearance_mode"])
                    ctk.set_appearance_mode(preferences["appearance_mode"])
                    
                if "default_output_dir" in preferences and preferences["default_output_dir"]:
                    self.output_dir_var.set(preferences["default_output_dir"])
                    
                # Não carregar filename das preferências - usar defaults inteligentes
                # if "default_filename" in preferences and preferences["default_filename"]:
                #     self.nome_var.set(preferences["default_filename"])
                    
                if "window_geometry" in preferences:
                    self.root.geometry(preferences["window_geometry"])
                    
                if "auto_merge" in preferences:
                    self.auto_merge_var.set(preferences["auto_merge"])
                    
                if "auto_open" in preferences:
                    self.auto_open_var.set(preferences["auto_open"])
                    
                self.update_ui_from_preferences()
        except Exception as e:
            print(f"Erro ao carregar preferências: {e}")

    def update_ui_from_preferences(self):
        """Update UI elements based on loaded preferences (theme, paths, controls)."""
        try:
            # Atualizar label do diretório de saída, se existir
            if hasattr(self, 'output_label_smart'):
                self.output_label_smart.configure(text=self.get_display_output_path())
            
            # Atualizar menu de aparência, se existir
            if hasattr(self, 'appearance_menu') and hasattr(self, 'appearance_var'):
                try:
                    self.appearance_menu.set(self.appearance_var.get())
                except Exception:
                    pass
            
            # Reaplicar tema aos widgets/cartões para refletir imediatamente
            if hasattr(self, 'apply_theme_to_widgets'):
                self.apply_theme_to_widgets()
        except Exception as e:
            print(f"Erro ao atualizar UI: {e}")
            
    def listar_pdfs(self):
        """List all PDF files in the selected folder."""
        print("=== INICIANDO LISTAGEM DE PDFs ===")
        
        # Clear existing checkboxes safely
        try:
            for widget in self.frame_pdfs.winfo_children():
                widget.destroy()
        except Exception as e:
            print(f"Erro ao limpar widgets: {e}")
        
        self.checkboxes.clear()
        
        # Force update to ensure widgets are cleared
        self.frame_pdfs.update_idletasks()
        
        if not self.pasta_var.get():
            print("Nenhuma pasta selecionada")
            return
            
        # Get PDF files (sem subpastas por padrão na nova interface minimalista)
        include_subfolders = False  # Simplificado para interface minimalista
        print(f"Pasta selecionada: {self.pasta_var.get()}")
        print(f"Incluir subpastas: {include_subfolders}")
        
        pdf_files = self.get_pdf_files(self.pasta_var.get(), include_subfolders)
        
        if not pdf_files:
            print("Nenhum PDF encontrado - exibindo mensagem")
            no_pdfs_label = ctk.CTkLabel(
                self.frame_pdfs,
                text="❌ Nenhum PDF encontrado nesta pasta.",
                font=ctk.CTkFont(size=14),
                text_color="red"
            )
            no_pdfs_label.pack(pady=20)
            
            # Debug info
            debug_label = ctk.CTkLabel(
                self.frame_pdfs,
                text=f"📁 Pasta verificada: {self.pasta_var.get()}",
                font=ctk.CTkFont(size=10),
                text_color="gray"
            )
            debug_label.pack(pady=5)
            return
            
        print(f"Criando checkboxes para {len(pdf_files)} PDFs")
        
        # Create checkboxes for each PDF
        for i, pdf_path in enumerate(pdf_files):
            var = ctk.BooleanVar(value=False)
            
            # Display relative path if in subfolder
            if include_subfolders:
                try:
                    display_name = os.path.relpath(pdf_path, self.pasta_var.get())
                except ValueError:
                    display_name = pdf_path  # Fallback to full path
            else:
                display_name = os.path.basename(pdf_path)
            
            print(f"Criando checkbox {i+1}: {display_name}")
                
            chk = ctk.CTkCheckBox(
                self.frame_pdfs,
                text=display_name,
                variable=var,
                font=ctk.CTkFont(size=12)
            )
            chk.pack(anchor="w", padx=10, pady=3, fill="x")
            self.checkboxes.append((pdf_path, var, display_name))
            
        print(f"=== LISTAGEM COMPLETA: {len(self.checkboxes)} PDFs ===")
        
        # Update the frame to ensure it's visible
        self.frame_pdfs.update_idletasks()
        
    def listar_arquivos_individuais(self):
        """List individually selected PDF files with drag-sortable interface."""
        print("=== INICIANDO LISTAGEM DE ARQUIVOS INDIVIDUAIS ===")
        
        # Clear existing widgets safely
        try:
            for widget in self.frame_pdfs.winfo_children():
                widget.destroy()
        except Exception as e:
            print(f"Erro ao limpar widgets: {e}")
        
        self.file_items = []  # Lista para armazenar widgets dos arquivos
        
        # Force update to ensure widgets are cleared
        self.frame_pdfs.update_idletasks()
        
        if not self.individual_files:
            print("Nenhum arquivo individual selecionado")
            # Ocultar botões de seleção quando não há arquivos
            self.selection_frame.pack_forget()
            
            no_files_label = ctk.CTkLabel(
                self.frame_pdfs,
                text="📄 Use a área de drag & drop acima para adicionar PDFs",
                font=ctk.CTkFont(size=14),
                text_color="gray"
            )
            no_files_label.pack(pady=20)
            return
        
        # Mostrar apenas botão de limpar (versão minimalista)
        self.create_minimal_controls()
            
        print(f"Criando lista drag-sortable para {len(self.individual_files)} arquivos")
        
        # Create drag-sortable list items
        for i, file_info in enumerate(self.individual_files):
            # Compatibilidade com formato antigo e novo
            if len(file_info) == 2:
                pdf_path, display_name = file_info
                page_count = 0
                is_valid = True
            else:
                pdf_path, display_name, page_count, is_valid = file_info
            
            # Criar item da lista minimalista
            file_item = self.create_file_item(i, pdf_path, display_name, page_count)
            self.file_items.append(file_item)
                
        print(f"=== LISTAGEM DRAG-SORTABLE COMPLETA: {len(self.file_items)} PDFs ===")
        
        # Update the frame to ensure it's visible
        self.frame_pdfs.update_idletasks()
    
    def create_file_item(self, index, pdf_path, display_name, page_count):
        """Create a clean, minimal file item."""
        # Frame principal - ainda mais compacto
        item_frame = ctk.CTkFrame(
            self.frame_pdfs, 
            corner_radius=6,
            height=36,  # Mais compacto ainda
            fg_color=("gray97", "gray13"),
            border_width=1,
            border_color=("gray85", "gray25")
        )
        item_frame.pack(fill="x", padx=8, pady=1)  # Padding mínimo
        item_frame.pack_propagate(False)
        
        # Container interno - mais compacto
        content_frame = ctk.CTkFrame(item_frame, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=12, pady=6)  # Padding reduzido
        
        # Nome do arquivo com contagem de páginas - responsivo
        if page_count > 0:
            file_text = f"{display_name} ({page_count} página{'s' if page_count != 1 else ''})"
        else:
            file_text = display_name
            
        name_label = ctk.CTkLabel(
            content_frame,
            text=file_text,
            font=ctk.CTkFont(size=11),
            anchor="w",
            text_color=("gray20", "gray80"),
            wraplength=0  # Disable text wrapping to prevent horizontal scroll
        )
        name_label.pack(side="left", fill="x", expand=True)
        
        # Store original text for responsive truncation
        name_label.original_text = file_text
        name_label.display_name = display_name
        name_label.page_count = page_count
        
        # Force immediate responsive update
        self.root.after_idle(lambda: self.update_single_item_responsive(name_label))
        
        # Ícone de drag sutil
        drag_icon = ctk.CTkLabel(
            content_frame,
            text="⋮⋮",
            font=ctk.CTkFont(size=10),
            text_color=("gray60", "gray50"),
            width=15
        )
        drag_icon.pack(side="right")
        
        # Configurações de interação
        if DRAG_DROP_AVAILABLE:
            self.setup_item_drag_drop(item_frame, index)
        
        self.setup_context_menu(item_frame, pdf_path, display_name, index)
        
        # Hover tooltip shows full filename and path for truncated items
        tooltip_text = f"{display_name}"
        if page_count > 0:
            tooltip_text += f"\n{page_count} página{'s' if page_count != 1 else ''}"
        tooltip_text += f"\nCaminho: {pdf_path}"
        self.setup_hover_tooltip(item_frame, tooltip_text)
        
        # Referências
        item_frame.pdf_path = pdf_path
        item_frame.index = index
        item_frame.display_name = display_name
        item_frame.name_label = name_label  # Reference for responsive updates
        
        return item_frame
    
    def update_single_item_responsive(self, name_label):
        """Update a single item for responsive display immediately."""
        try:
            window_width = self.root.winfo_width()
            if window_width <= 1:
                return
                
            original_text = getattr(name_label, 'original_text', '')
            display_name = getattr(name_label, 'display_name', '')
            page_count = getattr(name_label, 'page_count', 0)
            
            if not original_text or not display_name:
                return
            
            # Calculate available width more precisely
            available_width = window_width - 100
            max_chars = max(12, available_width // 6)
            
            # Aggressive truncation for responsiveness
            if window_width < 500:
                if page_count > 0:
                    truncated_text = f"{display_name[:8]}...({page_count}p)"
                else:
                    truncated_text = f"{display_name[:12]}..."
            elif window_width < 650:
                if page_count > 0:
                    truncated_text = f"{display_name[:15]}...({page_count}p)"
                else:
                    truncated_text = f"{display_name[:18]}..."
            else:
                if len(original_text) <= max_chars:
                    truncated_text = original_text
                else:
                    if page_count > 0:
                        page_text = f" ({page_count} página{'s' if page_count != 1 else ''})"
                        max_name_chars = max_chars - len(page_text) - 3
                        truncated_text = f"{display_name[:max_name_chars]}...{page_text}"
                    else:
                        truncated_text = f"{display_name[:max_chars-3]}..."
            
            name_label.configure(text=truncated_text)
            
        except Exception as e:
            print(f"Erro ao atualizar item: {e}")
    
    def update_file_list_responsive(self, window_width):
        """Update file list items for responsive text display - REAL responsiveness."""
        if not hasattr(self, 'file_items') or not self.file_items:
            return
        
        # Get actual available width more accurately
        try:
            # Get the actual width of the scrollable frame
            frame_width = self.main_scroll.winfo_width()
            if frame_width <= 1:  # Not yet rendered
                frame_width = window_width - 20
            
            # Account for padding, margins, drag icon, scrollbar
            available_width = frame_width - 80  # More conservative
            
            # Calculate max characters based on actual font metrics
            # Font size 11 with average character width ~6px
            max_chars = max(15, available_width // 6)
            
            for item_frame in self.file_items:
                if hasattr(item_frame, 'name_label'):
                    name_label = item_frame.name_label
                    original_text = getattr(name_label, 'original_text', '')
                    display_name = getattr(name_label, 'display_name', '')
                    page_count = getattr(name_label, 'page_count', 0)
                    
                    if not original_text or not display_name:
                        continue
                    
                    # Always truncate aggressively for small windows
                    if window_width < 500:
                        # Very small window - ultra compact
                        if page_count > 0:
                            max_name_chars = max(8, max_chars - 6)  # Reserve space for (Xp)
                            truncated_text = f"{display_name[:max_name_chars]}...({page_count}p)"
                        else:
                            truncated_text = f"{display_name[:max_chars-3]}..."
                    elif window_width < 650:
                        # Medium window - moderate truncation
                        if page_count > 0:
                            page_text = f" ({page_count}p)"
                            max_name_chars = max(10, max_chars - len(page_text) - 3)
                            truncated_text = f"{display_name[:max_name_chars]}...{page_text}"
                        else:
                            truncated_text = f"{display_name[:max_chars-3]}..."
                    else:
                        # Large window - try to show more
                        if len(original_text) <= max_chars:
                            truncated_text = original_text
                        else:
                            if page_count > 0:
                                page_text = f" ({page_count} página{'s' if page_count != 1 else ''})"
                                max_name_chars = max(15, max_chars - len(page_text) - 3)
                                truncated_text = f"{display_name[:max_name_chars]}...{page_text}"
                            else:
                                truncated_text = f"{display_name[:max_chars-3]}..."
                    
                    name_label.configure(text=truncated_text)
                    
        except Exception as e:
            print(f"Erro na responsividade: {e}")
            # Fallback - truncate everything aggressively
            for item_frame in self.file_items:
                if hasattr(item_frame, 'name_label'):
                    name_label = item_frame.name_label
                    display_name = getattr(name_label, 'display_name', '')
                    page_count = getattr(name_label, 'page_count', 0)
                    if display_name:
                        if page_count > 0:
                            truncated_text = f"{display_name[:12]}...({page_count}p)"
                        else:
                            truncated_text = f"{display_name[:15]}..."
                        name_label.configure(text=truncated_text)
    
    def setup_item_drag_drop(self, item_frame, index):
        """Setup drag and drop for list item reordering."""
        try:
            # Função para aplicar eventos a um widget e seus filhos
            def bind_drag_events(widget):
                widget.bind("<Button-1>", lambda e: self.start_drag(e, item_frame, index))
                widget.bind("<B1-Motion>", lambda e: self.on_drag_motion(e, item_frame))
                widget.bind("<ButtonRelease-1>", lambda e: self.end_drag(e, item_frame))
                widget.bind("<Enter>", lambda e: self.on_drag_enter_item(e, item_frame))
                widget.bind("<Leave>", lambda e: self.on_drag_leave_item(e, item_frame))
            
            # Aplicar eventos ao frame principal
            bind_drag_events(item_frame)
            
            # Aplicar eventos a todos os elementos filhos recursivamente
            def bind_children(parent):
                for child in parent.winfo_children():
                    bind_drag_events(child)
                    # Recursivamente para netos
                    bind_children(child)
            
            bind_children(item_frame)
            
        except Exception as e:
            print(f"Erro ao configurar drag-drop do item: {e}")
    
    def setup_context_menu(self, widget, pdf_path, display_name, index):
        """Setup right-click context menu for file operations with native Tk Menu (better on Windows)."""
        def show_context_menu(event):
            # Usar menu nativo do Tk para máxima compatibilidade (especialmente no Windows)
            menu = Menu(self.root, tearoff=0)
            menu.add_command(label="❌ Remover", command=lambda: self.context_remove_file(None, pdf_path))
            menu.add_separator()
            menu.add_command(label="⬆️ Mover para Topo", command=lambda: self.context_move_to_top(None, index))
            menu.add_command(label="⬇️ Mover para Fim", command=lambda: self.context_move_to_bottom(None, index))
            try:
                menu.tk_popup(event.x_root, event.y_root)
            finally:
                try:
                    menu.grab_release()
                except Exception:
                    pass

        # Bind right-click para todos os elementos do item (cross-platform)
        # Windows/Linux: Button-3. macOS: Button-2 (alguns trackpads) e Control-Button-1
        bindings = ["<Button-3>"]
        if sys.platform == "darwin":
            bindings.extend(["<Button-2>", "<Control-Button-1>"])

        for sequence in bindings:
            widget.bind(sequence, show_context_menu)

        # Bind para elementos filhos também
        for child in widget.winfo_children():
            for sequence in bindings:
                child.bind(sequence, show_context_menu)
            for grandchild in child.winfo_children():
                for sequence in bindings:
                    grandchild.bind(sequence, show_context_menu)
    
    def setup_hover_tooltip(self, widget, tooltip_text):
        """Setup hover tooltip to show file details."""
        def show_tooltip(event):
            # Criar tooltip
            self.tooltip = ctk.CTkToplevel()
            self.tooltip.withdraw()
            self.tooltip.overrideredirect(True)
            self.tooltip.configure(fg_color=("lightyellow", "gray25"))
            
            tooltip_label = ctk.CTkLabel(
                self.tooltip,
                text=tooltip_text,
                font=ctk.CTkFont(size=10),
                text_color=("black", "white")
            )
            tooltip_label.pack(padx=8, pady=4)
            
            # Posição do tooltip
            x = event.x_root + 10
            y = event.y_root - 10
            self.tooltip.geometry(f"+{x}+{y}")
            self.tooltip.deiconify()
        
        def hide_tooltip(event):
            if hasattr(self, 'tooltip'):
                self.tooltip.destroy()
                delattr(self, 'tooltip')
        
        widget.bind("<Enter>", show_tooltip)
        widget.bind("<Leave>", hide_tooltip)
        
    def remover_arquivo_individual(self, pdf_path):
        """Remove an individual file from the list."""
        self.individual_files = [file_info for file_info in self.individual_files if file_info[0] != pdf_path]
        self.atualizar_interface_com_arquivos()
        self.atualizar_info_section()
        self.listar_arquivos_individuais()
    
    # Context menu actions
    def context_remove_file(self, menu=None, pdf_path=None):
        """Remove file via context menu."""
        try:
            if menu is not None:
                menu.destroy()
        except Exception:
            pass
        if pdf_path:
            self.remover_arquivo_individual(pdf_path)
    
    def context_move_to_top(self, menu=None, index=None):
        """Move file to top via context menu."""
        try:
            if menu is not None:
                menu.destroy()
        except Exception:
            pass
        if index is not None and index > 0:
            file_info = self.individual_files.pop(index)
            self.individual_files.insert(0, file_info)
            self.listar_arquivos_individuais()
    
    def context_move_to_bottom(self, menu=None, index=None):
        """Move file to bottom via context menu."""
        try:
            if menu is not None:
                menu.destroy()
        except Exception:
            pass
        if index is not None and index < len(self.individual_files) - 1:
            file_info = self.individual_files.pop(index)
            self.individual_files.append(file_info)
            self.listar_arquivos_individuais()
    
    # Drag and drop for reordering (improved implementation)
    def start_drag(self, event, item_frame, index):
        """Start dragging an item."""
        self.drag_data = {
            'item': item_frame,
            'index': index,
            'start_y': event.y_root,
            'original_color': item_frame.cget("fg_color")
        }
        # Visual feedback - item sendo arrastado
        item_frame.configure(
            fg_color=("lightblue", "darkblue"),
            border_color=("blue", "lightblue")
        )
        print(f"Iniciando drag do item {index}: {item_frame.display_name}")
    
    def on_drag_motion(self, event, item_frame):
        """Handle drag motion with better target detection."""
        if hasattr(self, 'drag_data'):
            # Encontrar o item sobre o qual estamos arrastando
            target_item = self.find_item_at_position(event.x_root, event.y_root)
            
            # Resetar cores de todos os itens (exceto o que está sendo arrastado)
            for file_item in self.file_items:
                if file_item != self.drag_data['item']:
                    file_item.configure(
                        fg_color=("gray97", "gray13"),
                        border_color=("gray85", "gray25")
                    )
            
            # Destacar o item alvo
            if target_item and target_item != self.drag_data['item']:
                target_item.configure(
                    fg_color=("lightgreen", "darkgreen"),
                    border_color=("green", "lightgreen")
                )
    
    def find_item_at_position(self, x, y):
        """Find which item is at the given screen coordinates."""
        for file_item in self.file_items:
            try:
                # Obter posição do item na tela
                item_x = file_item.winfo_rootx()
                item_y = file_item.winfo_rooty()
                item_width = file_item.winfo_width()
                item_height = file_item.winfo_height()
                
                # Verificar se o mouse está sobre este item
                if (item_x <= x <= item_x + item_width and 
                    item_y <= y <= item_y + item_height):
                    return file_item
            except:
                continue
        return None
    
    def end_drag(self, event, item_frame):
        """End dragging and reorder if needed."""
        if hasattr(self, 'drag_data'):
            # Restaurar cor original do item arrastado
            item_frame.configure(
                fg_color=self.drag_data['original_color'],
                border_color=("gray85", "gray25")
            )
            
            # Encontrar item alvo
            target_item = self.find_item_at_position(event.x_root, event.y_root)
            
            if target_item and target_item != self.drag_data['item']:
                # Encontrar índices
                old_index = self.drag_data['index']
                new_index = None
                
                for i, file_item in enumerate(self.file_items):
                    if file_item == target_item:
                        new_index = i
                        break
                
                if new_index is not None and new_index != old_index:
                    print(f"Movendo item de {old_index} para {new_index}")
                    # Reordenar na lista de dados
                    file_info = self.individual_files.pop(old_index)
                    self.individual_files.insert(new_index, file_info)
                    # Atualizar interface
                    self.listar_arquivos_individuais()
            
            # Resetar cores de todos os itens
            for file_item in self.file_items:
                file_item.configure(
                    fg_color=("gray97", "gray13"),
                    border_color=("gray85", "gray25")
                )
            
            delattr(self, 'drag_data')
    
    def on_drag_enter_item(self, event, item_frame):
        """Visual feedback when dragging over an item."""
        # Feedback já é tratado em on_drag_motion
        pass
    
    def on_drag_leave_item(self, event, item_frame):
        """Remove visual feedback when leaving an item."""
        # Feedback já é tratado em on_drag_motion
        pass
        
    def mover_arquivo_cima(self, index):
        """Move file up in the list."""
        if index > 0 and index < len(self.individual_files):
            # Trocar posições
            self.individual_files[index], self.individual_files[index-1] = \
                self.individual_files[index-1], self.individual_files[index]
            self.listar_arquivos_individuais()
            
    def mover_arquivo_baixo(self, index):
        """Move file down in the list."""
        if index >= 0 and index < len(self.individual_files) - 1:
            # Trocar posições
            self.individual_files[index], self.individual_files[index+1] = \
                self.individual_files[index+1], self.individual_files[index]
            self.listar_arquivos_individuais()
            
    def selecionar_todos(self):
        """Select all PDF files (legacy compatibility)."""
        # Todos já estão selecionados por padrão na nova interface
        pass
            
    def desmarcar_todos(self):
        """Deselect all PDF files (legacy compatibility)."""
        # Não aplicável na nova interface minimalista
        pass
            
    def limpar_lista_arquivos(self):
        """Clear all individual files and folder selection."""
        if messagebox.askyesno("Confirmar", "Deseja limpar toda a lista de arquivos?"):
            self.individual_files.clear()
            self.pasta_var.set("")
            self.checkboxes.clear()
            
            # Limpar widgets da lista
            try:
                for widget in self.frame_pdfs.winfo_children():
                    widget.destroy()
            except Exception as e:
                print(f"Erro ao limpar widgets: {e}")
            
            # Voltar ao estado inicial da interface
            self.atualizar_interface_com_arquivos()
            self.atualizar_info_section()
            
            # Mostrar mensagem informativa
            info_label = ctk.CTkLabel(
                self.frame_pdfs,
                text="📄 Selecione uma pasta ou adicione arquivos para começar",
                font=ctk.CTkFont(size=14),
                text_color="gray"
            )
            info_label.pack(pady=20)
            
    def update_progress(self, current: int, total: int, message: str = ""):
        """Update progress bar and label."""
        progress = current / total if total > 0 else 0
        self.progress_bar.set(progress)
        
        if message:
            self.progress_label.configure(text=message)
        else:
            self.progress_label.configure(text=f"Processando: {current}/{total} PDFs")
            
        self.root.update_idletasks()
        
    def juntar_pdfs_threaded(self):
        """Start PDF merging in a separate thread."""
        if self.is_merging:
            return
            
        thread = threading.Thread(target=self.juntar_pdfs, daemon=True)
        thread.start()
        
    def juntar_pdfs(self):
        """Merge selected PDF files with progress tracking."""
        try:
            self.is_merging = True
            self.btn_juntar.configure(state="disabled", text="🔄 Juntando PDFs...")
            
            # Na nova interface, todos os arquivos estão selecionados por padrão
            if hasattr(self, 'checkboxes') and self.checkboxes:
                # Modo legado com checkboxes
                selecionados = [(pdf_path, display_name) for pdf_path, var, display_name in self.checkboxes if var.get()]
            else:
                # Novo modo minimalista - todos os arquivos
                selecionados = [(file_info[0], file_info[1]) for file_info in self.individual_files]
            
            if not selecionados:
                messagebox.showwarning("Aviso", "Nenhum PDF para juntar.")
                return
                
            # Calcular total de páginas (se disponível)
            total_pages = 0
            for pdf_path, _ in selecionados:
                # Procurar nas informações dos arquivos individuais
                for file_info in self.individual_files:
                    if len(file_info) >= 3 and file_info[0] == pdf_path:
                        total_pages += file_info[2]  # page_count
                        break
                
            # Validate filename
            nome_final = self.nome_var.get().strip()
            is_valid, error_msg = self.validate_filename(nome_final)
            
            if not is_valid:
                messagebox.showwarning("Nome Inválido", error_msg)
                return
                
            if not nome_final.endswith(".pdf"):
                nome_final += ".pdf"
                
            # Create output file path
            output_dir = self.output_dir_var.get() or self.get_default_output_directory()
            ficheiro_saida = os.path.join(output_dir, nome_final)
            
            # Check if file already exists
            if os.path.exists(ficheiro_saida):
                if not messagebox.askyesno(
                    "Arquivo Existe",
                    f"O arquivo '{nome_final}' já existe.\nDeseja substituí-lo?"
                ):
                    return
                    
            # Initialize progress
            total_pdfs = len(selecionados)
            self.update_progress(0, total_pdfs, "Iniciando junção de PDFs...")
            
            # Merge PDFs
            try:
                from pypdf import PdfReader, PdfWriter
                merger = PdfWriter()
                
                for i, (pdf_path, display_name) in enumerate(selecionados):
                    try:
                        self.update_progress(i, total_pdfs, f"Adicionando: {display_name}")
                        reader = PdfReader(pdf_path)
                        for page in reader.pages:
                            merger.add_page(page)
                        time.sleep(0.1)  # Small delay for visual feedback
                        
                    except Exception as e:
                        messagebox.showerror(
                            "Erro no PDF",
                            f"Erro ao processar '{display_name}':\n{str(e)}\n\nO PDF pode estar corrompido ou protegido por senha."
                        )
                        return
                        
                # Write final file
                self.update_progress(total_pdfs, total_pdfs, "Salvando arquivo final...")
                with open(ficheiro_saida, 'wb') as output_file:
                    merger.write(output_file)
                    
            except ImportError:
                # Fallback to older PyPDF2 or pypdf versions
                merger = PdfMerger()
                
                for i, (pdf_path, display_name) in enumerate(selecionados):
                    try:
                        self.update_progress(i, total_pdfs, f"Adicionando: {display_name}")
                        merger.append(pdf_path)
                        time.sleep(0.1)  # Small delay for visual feedback
                        
                    except Exception as e:
                        messagebox.showerror(
                            "Erro no PDF",
                            f"Erro ao processar '{display_name}':\n{str(e)}\n\nO PDF pode estar corrompido ou protegido por senha."
                        )
                        merger.close()
                        return
                        
                # Write final file
                self.update_progress(total_pdfs, total_pdfs, "Salvando arquivo final...")
                merger.write(ficheiro_saida)
                merger.close()
            
            # Success
            self.progress_bar.set(1.0)
            self.progress_label.configure(text="✅ PDFs unidos com sucesso!")
            
            # Mensagem de sucesso com informações detalhadas
            success_msg = f"PDF criado com sucesso!\n\n📁 Local: {ficheiro_saida}\n📊 {total_pdfs} PDFs unidos"
            if total_pages > 0:
                success_msg += f"\n📄 Total de páginas: {total_pages}"
            
            # Auto-abrir se habilitado, senão perguntar (apenas se feedback habilitado)
            if self.auto_merge_var.get():
                # No modo auto-merge, sempre abrir automaticamente
                self.abrir_arquivo(ficheiro_saida)
                if self.show_feedback_var.get():
                    messagebox.showinfo("Auto-Merge Concluído", success_msg + "\n\n🚀 Arquivo aberto automaticamente!")
            elif self.auto_open_var.get():
                self.abrir_arquivo(ficheiro_saida)
                if self.show_feedback_var.get():
                    messagebox.showinfo("Sucesso", success_msg + "\n\n🚀 Arquivo aberto automaticamente!")
            else:
                # Sem popup por padrão - apenas se feedback habilitado
                if self.show_feedback_var.get():
                    if messagebox.askyesno(
                        "Sucesso", 
                        success_msg + "\n\nDeseja abrir o arquivo agora?",
                        icon="question"
                    ):
                        self.abrir_arquivo(ficheiro_saida)
                # Se feedback desabilitado, não mostrar popup nem abrir arquivo
            
        finally:
            self.is_merging = False
            self.btn_juntar.configure(state="normal", text="🚀 Juntar PDFs")
            self.progress_bar.set(0)
            self.progress_label.configure(text="Pronto para juntar PDFs")
            
        
    def mostrar_ajuda(self):
        """Legacy help method - now redirects to modal tooltip."""
        self.show_help_tooltip()
        
    def abrir_arquivo(self, caminho_arquivo: str):
        """Open the created PDF file with the default application."""
        try:
            import subprocess
            import platform
            
            system = platform.system()
            if system == "Darwin":  # macOS
                subprocess.run(["open", caminho_arquivo])
            elif system == "Windows":  # Windows
                subprocess.run(["start", caminho_arquivo], shell=True)
            else:  # Linux
                subprocess.run(["xdg-open", caminho_arquivo])
                
        except Exception as e:
            messagebox.showerror(
                "Erro ao Abrir Arquivo",
                f"Não foi possível abrir o arquivo:\n{str(e)}\n\nVocê pode encontrá-lo em:\n{caminho_arquivo}"
            )
        
    def change_appearance(self, appearance: str):
        """Change appearance mode (Dark/Light/System)."""
        ctk.set_appearance_mode(appearance)
        # Persist preference and force-refresh themed widgets/cards so colors update immediately
        try:
            self.appearance_var.set(appearance)
            self.apply_theme_to_widgets()
            self.save_preferences()
        except Exception as e:
            print(f"Erro ao aplicar tema: {e}")

    def apply_theme_to_widgets(self):
        """Re-apply themed colors to key widgets so cards respect light/dark mode immediately."""
        try:
            # Determine current appearance
            current_mode = None
            try:
                current_mode = self.appearance_var.get()
            except Exception:
                pass

            # Update root background (especially when using TkinterDnD.Tk)
            try:
                if current_mode == "Light":
                    self.root.configure(bg="#F2F2F2")  # near system light background
                elif current_mode == "Dark":
                    self.root.configure(bg="#1A1A1A")
                else:
                    # System: leave as-is, or a neutral
                    self.root.configure(bg="#F2F2F2")
            except Exception:
                pass

            # App container background
            if hasattr(self, 'app_container'):
                self.app_container.configure(fg_color=("gray95", "gray15"))

            # Drop area card
            if hasattr(self, 'drop_frame'):
                self.drop_frame.configure(
                    fg_color=("gray90", "gray13"),
                    border_color=("gray70", "gray30")
                )
            if hasattr(self, 'drop_content'):
                self.drop_content.configure(fg_color="transparent")
            if hasattr(self, 'folder_frame'):
                # Container of drop zone
                self.folder_frame.configure(fg_color=None)  # use default
        
            # Info + header
            if hasattr(self, 'header_frame'):
                self.header_frame.configure(fg_color="transparent")
            if hasattr(self, 'info_frame'):
                self.info_frame.configure(fg_color="transparent")
        
            # Defaults container (smart defaults card)
            if hasattr(self, 'defaults_container'):
                self.defaults_container.configure(fg_color=("gray95", "gray15"))
            if hasattr(self, 'labels_row'):
                self.labels_row.configure(fg_color="transparent")
        
            # Advanced options container
            if hasattr(self, 'advanced_frame'):
                self.advanced_frame.configure(fg_color="transparent")
            if hasattr(self, 'advanced_content'):
                self.advanced_content.configure(fg_color=("gray92", "gray18"))
        
            # Progress and action frames
            if hasattr(self, 'progress_frame'):
                self.progress_frame.configure(fg_color="transparent")
            if hasattr(self, 'action_frame'):
                self.action_frame.configure(fg_color="transparent")
        
            # Scrollable list background (list card)
            if hasattr(self, 'frame_scroll'):
                self.frame_scroll.configure(fg_color=("gray98", "gray12"))
            # Main scroll container background
            if hasattr(self, 'main_scroll'):
                self.main_scroll.configure(fg_color=("gray95", "gray15"))
        
            # Re-apply styling to each file item card
            if hasattr(self, 'file_items'):
                for item in self.file_items:
                    try:
                        item.configure(
                            fg_color=("gray97", "gray13"),
                            border_color=("gray85", "gray25")
                        )
                    except Exception:
                        pass
        except Exception as e:
            print(f"Erro ao atualizar widgets com novo tema: {e}")
        
    def run(self):
        """Start the application."""
        self.root.mainloop()


def main():
    """Main function to run the application."""
    try:
        app = PDFMergerApp()
        app.run()
    except Exception as e:
        messagebox.showerror(
            "Erro Fatal",
            f"Erro ao iniciar a aplicação:\n{str(e)}\n\nVerifique se todas as dependências estão instaladas."
        )


if __name__ == "__main__":
    main()
