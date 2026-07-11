# 🔒 SecureDoc Converter

<div align="center">

**Conversor de documentos 100% offline e seguro.**
*Seus arquivos nunca saem do seu computador.*

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Windows-0078D6?style=for-the-badge&logo=windows&logoColor=white)](https://www.microsoft.com/windows)

</div>

---

## 🎯 O Problema

Conversores online de documentos exigem que você **faça upload dos seus arquivos** para servidores desconhecidos. Você nunca tem certeza de:
- **Quem tem acesso** aos seus documentos
- **Se eles são armazenados** ou compartilhados
- **O que acontece** com suas informações pessoais

## ✅ A Solução

**SecureDoc Converter** é uma aplicação desktop que converte documentos entre **WORD (.docx)** e **PDF (.pdf)** de forma 100% local. Nenhum dado sai do seu computador.

---

## ⚡ Funcionalidades

| Feature | Descrição |
|---|---|
| 📝 **WORD → PDF** | Converta documentos `.docx` para `.pdf` |
| 📕 **PDF → WORD** | Converta documentos `.pdf` para `.docx` |
| 📂 **Drag & Drop** | Arraste e solte arquivos na janela |
| 📁 **Arquivo ou Pasta** | Converta arquivos individuais ou pastas inteiras |
| 📋 **Histórico Completo** | Log detalhado com data, hora, tipo e status |
| 🔒 **100% Offline** | Seus dados nunca saem do computador |
| 🎨 **Interface Moderna** | Design premium com tema claro/escuro |
| ⚡ **Multi-threading** | Interface fluida mesmo durante conversões |
| 📊 **Barra de Progresso** | Acompanhe o progresso em tempo real |

---

## 🖥️ Screenshots

*Em breve*

---

## 🚀 Instalação

### Pré-requisitos
- **Python 3.10+**
- **Microsoft Word** (necessário para conversão WORD → PDF)

### Passos

```bash
# 1. Clone o repositório
git clone https://github.com/rmoraes23/WORD2PDF_CONVERTER.git
cd WORD2PDF_CONVERTER

# 2. Instale as dependências
pip install -r requirements.txt

# 3. Execute a aplicação
python main.py
```

### 📦 Criando o Executável (.exe)
Se você deseja gerar um executável autônomo para Windows (sem necessidade de ter Python instalado para rodar):

```bash
python build.py
```
O executável `.exe` será gerado automaticamente dentro da pasta `dist/`.

---

## 📦 Dependências

| Pacote | Propósito |
|---|---|
| `customtkinter` | Interface moderna com temas |
| `docx2pdf` | Conversão WORD → PDF |
| `pdf2docx` | Conversão PDF → WORD |
| `Pillow` | Suporte a imagens na UI |
| `tkinterdnd2` | Drag & Drop de arquivos |

---

## 🏗️ Arquitetura

```
SecureDoc Converter/
├── main.py              # Aplicação principal (OOP)
├── build.py             # Script de compilação para executável
├── requirements.txt     # Dependências do projeto
├── conversor.log        # Histórico persistente de conversões
└── README.md            # Documentação
```

### Design Patterns
- **OOP**: Classe `SecureDocApp` encapsula toda a lógica
- **Threading**: Conversões rodam em background sem travar a UI
- **Observer Pattern**: Callbacks de progresso atualizam a interface em tempo real

---

## 🔐 Privacidade e Segurança

- ✅ **Zero upload** — Nenhum arquivo é enviado para servidores externos
- ✅ **Zero tracking** — Sem telemetria ou coleta de dados
- ✅ **Zero dependência de internet** — Funciona 100% offline
- ✅ **Código aberto** — Você pode auditar cada linha de código

---

## 🛠️ Tecnologias Utilizadas

- **Python 3.10+** — Linguagem principal
- **CustomTkinter** — Framework de UI moderna
- **docx2pdf** — Conversão WORD → PDF via COM automation
- **pdf2docx** — Conversão PDF → WORD com parsing local
- **Threading** — Processamento assíncrono

---

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

---

## 👤 Autor

**Raoni Moraes**

- GitHub: [@rmoraes23](https://github.com/rmoraes23)
- LinkedIn: [Raoni Moraes](https://linkedin.com/in/raonimoraes)

---

<div align="center">

*Desenvolvido com ❤️ por Raoni Moraes*

**⭐ Se este projeto te ajudou, considere dar uma estrela!**

</div>
