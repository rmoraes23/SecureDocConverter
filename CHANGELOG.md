# 📋 Changelog — SecureDoc Converter

Todas as alterações notáveis deste projeto serão documentadas neste arquivo.

O formato segue o padrão [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/)
e este projeto adere ao [Versionamento Semântico](https://semver.org/lang/pt-BR/).

---

## [3.1.0] — 2026-07-12

### ✨ Adicionado
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

### 🔧 Alterado
- Sidebar reorganizada com 8 opções de navegação agrupadas em **Conversão**, **Utilitários PDF** e **Ferramentas**.
- Tela "Sobre" atualizada com a listagem completa de 7 funcionalidades principais e seus ícones.
- Versão do aplicativo atualizada para `3.1.0`.

### 📄 Documentação
- `README.md` atualizado com as duas novas funcionalidades na tabela de features.

---

## [3.0.0] — 2026-07-11

### ✨ Adicionado
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

### 🔧 Alterado
- Sidebar completamente reestruturada com categorias visuais (Conversão, Utilitários PDF, Ferramentas).
- Sistema de threading expandido para suportar todas as novas operações sem travamento da UI.
- Histórico de logs ampliado para registrar cada nova operação com data, hora, tipo e status.

### 🐛 Corrigido
- **Erro de codificação `charmap` no `build.py`**: adicionado `sys.stdout.reconfigure(encoding='utf-8')` para prevenir falhas de impressão no terminal Windows (CMD/PowerShell) ao usar caracteres especiais.
- Emoji de aviso removido dos prints do `build.py` para compatibilidade com consoles legados.

### 📦 Dependências
- Adicionada `pypdf>=4.0.0` ao `requirements.txt`.
- Adicionada `reportlab>=4.1.0` ao `requirements.txt`.

### 📄 Documentação
- `README.md` expandido com tabela completa de funcionalidades da suíte PDF.
- Link do LinkedIn do autor corrigido para `https://www.linkedin.com/in/raonimoraes1/`.

---

## [2.0.0] — 2026-07-11

### ✨ Adicionado
- **Interface gráfica profissional** construída com `CustomTkinter`.
- **Alternância de Tema**: switch dinâmico entre Modo Claro ☀️ e Modo Escuro 🌙 na sidebar.
- **Drag & Drop nativo**: arraste e solte arquivos `.docx` e `.pdf` diretamente na janela do aplicativo (via `tkinterdnd2`).
- **Conversão em Lote**: selecione múltiplos arquivos ou pastas inteiras para conversão simultânea.
- **Barra de progresso em tempo real** com indicação do arquivo atual sendo processado.
- **Botão 🛑 Parar**: cancele operações em andamento a qualquer momento sem travar a interface.
- **Seleção de pasta de destino**: opção de salvar os arquivos convertidos na mesma pasta de origem ou em uma pasta personalizada.
- **Histórico visual de operações**: aba dedicada com tabela interativa mostrando todas as conversões realizadas (data, tipo, arquivo, status).
- **Tratamento de erro do Microsoft Word**: mensagem amigável e descritiva caso o MS Word não esteja instalado (necessário apenas para WORD → PDF).
- **Tela "Sobre"**: informações do aplicativo, versão e créditos do desenvolvedor.

### 📦 Infraestrutura
- Criado `build.py` — script automatizado de compilação via PyInstaller.
- Criado `requirements.txt` com todas as dependências do projeto.
- Criado `.gitignore` com exclusões padrão para projetos Python.
- Criada `LICENSE` (MIT).
- Repositório inicializado e sincronizado com GitHub (`rmoraes23/SecureDocConverter`).

### 📄 Documentação
- `README.md` profissional com:
  - Seção de download direto para usuários leigos.
  - Instruções de instalação para desenvolvedores.
  - Tabela centralizada com screenshots do tema claro e escuro.
  - Badges de privacidade e segurança.

---

## [1.0.0] — 2026-07-11

### ✨ Adicionado
- Versão inicial do conversor WORD → PDF.
- Conversão bidirecional **WORD ↔ PDF** via terminal.
- Processamento 100% offline e local.
- Logging persistente em arquivo `conversor.log`.

---

<div align="center">

**Desenvolvido com ❤️ por [Raoni Moraes](https://www.linkedin.com/in/raonimoraes1/)**

</div>
