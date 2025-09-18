# 📝 Changelog - SpeedConnect PDF Merger

## [v2.2 Minimalist] - 2025-09-17

### 🔧 CORREÇÕES CRÍTICAS
- **CORRIGIDO**: Drag-and-drop para reordenação agora funciona em qualquer parte do item
- **CORRIGIDO**: Propagação de eventos aplicada recursivamente a todos elementos filhos
- **CORRIGIDO**: Detecção precisa de posição usando coordenadas de tela
- **CORRIGIDO**: Feedback visual consistente durante operações de drag

### ✨ NOVAS FUNCIONALIDADES
- **Interface Minimalista**: Design limpo inspirado no iLovePDF
- **Defaults Inteligentes**: Nomes e destinos automáticos com timestamp
- **Auto-Merge Opcional**: Processamento instantâneo após adicionar arquivos
- **Opções Colapsáveis**: Controles avançados ocultos para interface limpa
- **Ajuda Modal**: Tooltip centralizado (F1 ou "?")

### 🎨 MELHORIAS VISUAIS
- **Whitespace Generoso**: 30% mais espaço para respirar
- **Paleta Limitada**: 2-3 cores neutras + Material Blue accent
- **Tipografia Unificada**: Hierarquia visual consistente
- **Feedback Visual**: Azul (arrastando) → Verde (alvo)

### 🛠️ MELHORIAS TÉCNICAS
- **Propagação de Eventos**: `bind_drag_events()` aplicada recursivamente
- **Detecção de Posição**: `find_item_at_position()` usa coordenadas de tela
- **Tratamento de Erros**: Try/catch em operações de posição
- **Debug Logs**: Acompanhamento de movimentação para troubleshooting

### 📦 BUILDS ATUALIZADOS
- **macOS**: .app bundle (49.6 MB) com todas as correções
- **Linux**: Executável (20.9 MB) testado e funcional
- **Windows**: .exe (~22 MB) pronto para distribuição

## [v2.1 Enhanced] - 2025-09-16

### ✨ FUNCIONALIDADES PRINCIPAIS
- **Drag & Drop**: Implementação inicial
- **Seleção Individual**: Múltiplos diretórios
- **Contagem de Páginas**: Análise automática
- **Reordenação**: Botões ↑↓ por item
- **Atalhos de Teclado**: 10+ shortcuts
- **Destino Personalizável**: Escolha onde salvar

### 🎨 INTERFACE
- **Layout Otimizado**: Seções organizadas
- **Controles Inteligentes**: Botões contextuais
- **Feedback Visual**: Indicadores de estado
- **Área de Drop**: Zona visual para arquivos

## [v1.0] - 2025-09-15

### 🚀 LANÇAMENTO INICIAL
- **Funcionalidade Básica**: Junção de PDFs
- **Interface Simples**: Tkinter básico
- **Seleção por Pasta**: Modo tradicional
- **Validação**: Verificação de arquivos PDF
