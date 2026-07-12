# 📋 Changelog — SecureDoc Converter

All notable changes to this project will be documented in this file.
Todas as alterações notáveis deste projeto serão documentadas neste arquivo.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).
O formato segue o padrão [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/) e este projeto adere ao [Versionamento Semântico](https://semver.org/lang/pt-BR/).

---

## [3.1.0] — 2026-07-12

### 🇺🇸 English

#### Added
- **🔐 Protect PDF (Password Encryption)**
  - New dedicated tab on the sidebar to encrypt PDF documents with an open password.
  - Uses local encryption algorithms from the `pypdf` library — no data is sent to external servers.
  - Password input field with an interactive **"Show Password"** checkbox to toggle between hidden (`***`) and clear text.
  - Batch processing support: protect multiple PDFs at once.
  - Output files are generated with the `_protected.pdf` suffix.

- **✂️ Split PDF (Page Range Extraction)**
  - New dedicated tab on the sidebar to extract specific pages from PDF documents.
  - Intelligent range parser: accepts formats like `1-3, 5, 8-10` and outputs a single PDF containing only selected pages.
  - Automatic page boundary validation (ignores out-of-bounds page requests without throwing exceptions).
  - Reverse range support (e.g., `10-5` is gracefully handled as `5-10`).
  - Output files are generated with the `_split.pdf` suffix.

#### Changed
- Reorganized sidebar layout into 8 navigation options grouped into **Conversion**, **PDF Utilities**, and **Tools**.
- Updated "About" screen layout listing all 7 main features with updated description and icons.
- Updated application version metadata to `3.1.0`.

#### Documentation
- Updated `README.md` features table to reflect the two new tools.

---

### 🇧🇷 Português

#### Adicionado
- **🔐 Proteger PDF (Criptografia com Senha)**
  - Nova aba dedicada na sidebar para criptografar documentos PDF com senha de abertura.
  - Utiliza algoritmos de criptografia local da biblioteca `pypdf` — nenhum dado é enviado para servidores.
  - Campo de senha com checkbox interativo **"Mostrar Senha"** para alternar entre visualização oculta (`***`) e texto claro.
  - Suporte a processamento em lote: proteja múltiplos PDFs de uma só vez.
  - Arquivos de saída recebem o sufixo `_protegido.pdf`.

- **✂️ Dividir PDF (Extração de Páginas por Intervalo)**
  - Nova aba dedicada na sidebar para extrair páginas específicas de documentos PDF.
  - Parser inteligente de intervalos: aceita formatos como `1-3, 5, 8-10` e gera um novo PDF contendo apenas as páginas selecionadas.
  - Validação automática de limites (ignora páginas fora do intervalo total do documento sem gerar erros).
  - Suporte a intervalos invertidos (`10-5` é tratado como `5-10`).
  - Arquivos de saída recebem o sufixo `_dividido.pdf`.

#### Alterado
- Sidebar reorganizada com 8 opções de navegação agrupadas em **Conversão**, **Utilitários PDF** e **Ferramentas**.
- Tela "Sobre" atualizada com a listagem completa de 7 funcionalidades principais e seus ícones.
- Versão do aplicativo atualizada para `3.1.0`.

#### Documentação
- `README.md` atualizado com as duas novas funcionalidades na tabela de features.

---

## [3.0.0] — 2026-07-11

### 🇺🇸 English

#### Added
- **🧩 Merge PDFs (PDF Merger)**
  - Combines multiple PDF files into a single output document.
  - File queue list featuring interactive reordering buttons **▲ (Move Up)** and **▼ (Move Down)** to define the exact merging sequence.
  - Drag & Drop enabled to add PDFs directly into the drop zone frame.

- **📉 Compress PDF (PDF Compressor)**
  - Size optimization of PDF files using the `PyMuPDF` engine.
  - Three distinct compression levels:
    - **Light** — Fast compression with minimal quality impact.
    - **Recommended** — Best balance between output size and visual quality (default).
    - **Extreme** — Maximum size reduction with aggressive metadata and object cleaning.

- **🎨 Custom Watermark (PDF Watermark)**
  - Support for two watermark styles:
    - **Text**: custom text input with color selection (Gray, Black, Red, Blue, Green).
    - **Image**: local `.png` or `.jpg` image file picker.
  - Sliders for precise adjustment of:
    - **Opacity** (10% to 100%)
    - **Rotation** (-90° to +90°)
  - Rendered via `ReportLab` canvas and layered using `pypdf` page merging.

- **🔢 Advanced Page Numbering (PDF Page Numberer)**
  - Flexible positioning with 6 placement configurations:
    - Footer (Left, Center, Right)
    - Header (Left, Center, Right)
  - Two display formats:
    - "Page number only" (`1`)
    - "Page X of Y" (`1 of 10`)
  - Two numbering styles:
    - Traditional Arabic numerals (`1, 2, 3...`)
    - Academic Roman numerals (`I, II, III...`)
  - Three professional standard fonts:
    - Helvetica, Times-Roman, Courier.

#### Changed
- Fully restructured sidebar navigation with dedicated sections (Conversion, PDF Utilities, Tools).
- Expanded multi-threading architecture to process all new utilities asynchronously.
- Log history page updated to register and show status for the newly added operations.

#### Fixed
- **`charmap` encoding crash on `build.py`**: Added `sys.stdout.reconfigure(encoding='utf-8')` to prevent encoding exceptions on Windows terminal environments (CMD/PowerShell) when printing unicode characters.
- Cleaned up emojis in print outputs within `build.py` for legacy console compatibility.

#### Dependencies
- Added `pypdf>=4.0.0` to `requirements.txt`.
- Added `reportlab>=4.1.0` to `requirements.txt`.

#### Documentation
- Expanded `README.md` with complete features table for the new PDF Suite.
- Updated and corrected author's LinkedIn URL to `https://www.linkedin.com/in/raonimoraes1/`.

---

### 🇧🇷 Português

#### Adicionado
- **🧩 Juntar PDFs (PDF Merger)**
  - Mescla múltiplos arquivos PDF em um único documento de saída.
  - Fila de arquivos com botões de reordenação visual **▲ (Subir)** e **▼ (Descer)** para definir a sequência exata de junção.
  - Drag & Drop habilitado para adicionar PDFs diretamente na zona de soltura.

- **📉 Comprimir PDF (PDF Compressor)**
  - Otimização de tamanho de arquivos PDF utilizando a engine `PyMuPDF`.
  - Três níveis de compressão disponíveis:
    - **Leve** — Compressão rápida com mínima perda de qualidade.
    - **Recomendado** — Equilíbrio entre tamanho e qualidade (padrão).
    - **Extremo** — Máxima redução de tamanho com limpeza agressiva de metadados.

- **🎨 Marca D'água Personalizada (PDF Watermark)**
  - Suporte a dois tipos de marca d'água:
    - **Texto**: campo livre com seleção de cor (Cinza, Preto, Vermelho, Azul, Verde).
    - **Imagem**: seleção de arquivo `.png` ou `.jpg` do computador.
  - Controles deslizantes (sliders) para ajuste fino de:
    - **Opacidade** (10% a 100%)
    - **Rotação** (-90° a +90°)
  - Renderização via `ReportLab` com fusão de camadas via `pypdf`.

- **🔢 Numeração Avançada de Páginas (PDF Page Numberer)**
  - Posicionamento flexível com 6 opções:
    - Rodapé (Esquerda, Centro, Direita)
    - Cabeçalho (Esquerda, Centro, Direita)
  - Dois formatos de exibição:
    - "Apenas número" (`1`)
    - "Página X de Y" (`1 de 10`)
  - Dois estilos numéricos:
    - Arábico tradicional (`1, 2, 3...`)
    - Romano acadêmico (`I, II, III...`)
  - Três fontes profissionais:
    - Helvetica, Times-Roman, Courier

#### Alterado
- Sidebar completamente reestruturada com categorias visuais (Conversão, Utilitários PDF, Ferramentas).
- Sistema de threading expandido para suportar todas as novas operações sem travamento da UI.
- Histórico de logs ampliado para registrar cada nova operação com data, hora, tipo e status.

#### Corrigido
- **Erro de codificação `charmap` no `build.py`**: adicionado `sys.stdout.reconfigure(encoding='utf-8')` para prevenir falhas de impressão no terminal Windows (CMD/PowerShell) ao usar caracteres especiais.
- Emoji de aviso removido dos prints do `build.py` para compatibilidade com consoles legados.

#### Dependências
- Adicionada `pypdf>=4.0.0` ao `requirements.txt`.
- Adicionada `reportlab>=4.1.0` ao `requirements.txt`.

#### Documentação
- `README.md` expandido com tabela completa de funcionalidades da suíte PDF.
- Link do LinkedIn do autor corrigido para `https://www.linkedin.com/in/raonimoraes1/`.

---

## [2.0.0] — 2026-07-11

### 🇺🇸 English | 🇧🇷 Português

#### Added | Adicionado
- **GUI (Graphical User Interface)** built with `CustomTkinter` / *Interface gráfica construída com `CustomTkinter`*.
- **Dynamic Theme Toggling**: dynamic switch between Light Mode ☀️ and Dark Mode 🌙 / *Alternância dinâmica de tema claro e escuro na barra lateral*.
- **Native Drag & Drop**: drop `.docx` and `.pdf` files directly onto the app window (via `tkinterdnd2`) / *Arraste e solte nativo de arquivos*.
- **Batch Processing**: select multiple files or entire folders / *Conversão em lote de múltiplos arquivos e pastas*.
- **Real-time Progress Indicator**: progress bar and status updates / *Barra de progresso e informações em tempo real*.
- **🛑 Stop Button**: cancel active operations gracefully without freezing the UI / *Botão Parar para interromper tarefas em execução*.
- **Output Directory Customization**: save outputs to the source folder or select a custom folder / *Salvar na mesma pasta ou em diretório customizado*.
- **Operation History**: dedicated tab displaying logs of past conversions (timestamp, type, filename, status) / *Aba dedicada para histórico local de logs*.
- **Microsoft Word Error Handling**: friendly instructions shown if Microsoft Word is not installed (needed only for DOCX ➔ PDF) / *Aviso amigável caso o Word não esteja instalado*.
- **"About" Screen**: app metadata, version, and developer credits / *Aba sobre com créditos e versão*.

#### Infrastructure | Infraestrutura
- Created `build.py` for PyInstaller packaging / *Criado o script build.py para empacotamento*.
- Created `requirements.txt` with project dependencies / *Criado arquivo de dependências*.
- Created `.gitignore` and `LICENSE` (MIT) / *Criados arquivos .gitignore e Licença*.
- Initialized Git repository and synced with GitHub / *Repositorio inicializado e sincronizado*.

---

## [1.0.0] — 2026-07-11

### Added | Adicionado
- Initial release of the WORD to PDF offline converter / *Lançamento inicial do conversor offline*.
- CLI (Command Line Interface) execution / *Execução via interface de terminal*.
- 100% offline and local file processing / *Processamento local e 100% offline*.
- Logging system writing to `conversor.log` / *Histórico persistente escrito em arquivo de log*.

---

<div align="center">

**Developed with ❤️ by / Desenvolvido com ❤️ por [Raoni Moraes](https://www.linkedin.com/in/raonimoraes1/)**

</div>
