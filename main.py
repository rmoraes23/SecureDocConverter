"""
SecureDoc Converter - Conversor de Documentos Seguro e Offline
Desenvolvido por Raoni Moraes

Converte documentos entre WORD (.docx) e PDF (.pdf) de forma
100% offline, garantindo a privacidade dos seus dados.
"""

import os
import sys
import glob
import logging
import threading
import datetime
import subprocess
from pathlib import Path

import customtkinter as ctk
from tkinter import filedialog, messagebox

# ─────────────────────────────────────────────────────────────
# Configuração do logging persistente (modo append)
# ─────────────────────────────────────────────────────────────
LOG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "conversor.log")

logging.basicConfig(
    filename=LOG_FILE,
    filemode="a",  # Append — mantém histórico entre execuções
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    level=logging.INFO,
)
logger = logging.getLogger("SecureDoc")


# ─────────────────────────────────────────────────────────────
# Cores e constantes de design
# ─────────────────────────────────────────────────────────────
COLORS = {
    "accent":        "#00B4D8",
    "accent_hover":  "#0096C7",
    "success":       "#2DC653",
    "error":         "#E63946",
    "warning":       "#F4A261",
    "sidebar_dark":  "#0B1622",
    "sidebar_light": "#E8EDF2",
    "bg_dark":       "#0F1F30",
    "bg_light":      "#F0F4F8",
    "card_dark":     "#162A3E",
    "card_light":    "#FFFFFF",
    "text_dark":     "#E2E8F0",
    "text_light":    "#1A202C",
    "muted_dark":    "#64748B",
    "muted_light":   "#94A3B8",
}

APP_NAME = "SecureDoc Converter"
APP_VERSION = "2.1.0"
WINDOW_SIZE = "960x680"
MIN_WIDTH = 850
MIN_HEIGHT = 600


# ─────────────────────────────────────────────────────────────
# Funções utilitárias de conversão
# ─────────────────────────────────────────────────────────────
def convert_docx_to_pdf(input_path: str, output_path: str | None = None) -> str:
    """Converte um arquivo .docx para .pdf usando docx2pdf.

    Args:
        input_path: Caminho do arquivo .docx de entrada.
        output_path: Caminho opcional do .pdf de saída.

    Returns:
        Caminho do arquivo .pdf gerado.
    """
    from docx2pdf import convert
    if output_path is None:
        output_path = str(Path(input_path).with_suffix(".pdf"))
    convert(input_path, output_path)
    return output_path


def convert_pdf_to_docx(input_path: str, output_path: str | None = None) -> str:
    """Converte um arquivo .pdf para .docx usando pdf2docx.

    Args:
        input_path: Caminho do arquivo .pdf de entrada.
        output_path: Caminho opcional do .docx de saída.

    Returns:
        Caminho do arquivo .docx gerado.
    """
    from pdf2docx import Converter
    if output_path is None:
        output_path = str(Path(input_path).with_suffix(".docx"))
    cv = Converter(input_path)
    cv.convert(output_path)
    cv.close()
    return output_path


# ─────────────────────────────────────────────────────────────
# Widget personalizado: Zona de Drop
# ─────────────────────────────────────────────────────────────
class DropZone(ctk.CTkFrame):
    """Área visual para drag & drop de arquivos."""

    def __init__(self, master, accepted_extensions: list[str], on_files_dropped, **kwargs):
        super().__init__(master, **kwargs)
        self.accepted_extensions = [ext.lower() for ext in accepted_extensions]
        self.on_files_dropped = on_files_dropped
        self._files: list[str] = []

        # Ícone e textos
        self.icon_label = ctk.CTkLabel(
            self, text="📂", font=ctk.CTkFont(size=40),
        )
        self.icon_label.pack(pady=(20, 5))

        ext_text = " / ".join(self.accepted_extensions)
        self.title_label = ctk.CTkLabel(
            self,
            text="Arraste e solte arquivos aqui",
            font=ctk.CTkFont(size=15, weight="bold"),
        )
        self.title_label.pack(pady=(0, 2))

        self.subtitle_label = ctk.CTkLabel(
            self,
            text=f"Aceita: {ext_text}  •  Ou selecione abaixo",
            font=ctk.CTkFont(size=12),
            text_color=COLORS["muted_dark"],
        )
        self.subtitle_label.pack(pady=(0, 5))

        # Lista de arquivos selecionados
        self.files_frame = ctk.CTkScrollableFrame(self, height=75)
        self.files_frame.pack(fill="x", padx=15, pady=(5, 10))

        self.empty_label = ctk.CTkLabel(
            self.files_frame,
            text="Nenhum arquivo selecionado",
            font=ctk.CTkFont(size=11),
            text_color=COLORS["muted_dark"],
        )
        self.empty_label.pack(pady=10)

        # Tenta registrar drag & drop
        self._setup_dnd()

    def _setup_dnd(self):
        """Configura drag and drop se tkinterdnd2 estiver disponível."""
        try:
            self.after(500, self._register_dnd)
        except Exception:
            pass

    def _register_dnd(self):
        """Registra o handler de drag & drop."""
        try:
            self.drop_target_register("DND_Files")
            self.dnd_bind("<<Drop>>", self._on_drop)
        except Exception:
            pass

    def _on_drop(self, event):
        """Callback quando arquivos são soltos na zona."""
        raw = event.data
        files = []
        if "{" in raw:
            import re
            files = re.findall(r"\{(.+?)\}", raw)
            remaining = re.sub(r"\{.+?\}", "", raw).strip()
            if remaining:
                files.extend(remaining.split())
        else:
            files = raw.split()

        valid_files = [
            f for f in files
            if os.path.isfile(f) and Path(f).suffix.lower() in self.accepted_extensions
        ]

        if valid_files:
            self.add_files(valid_files)

    def add_files(self, file_paths: list[str]):
        """Adiciona arquivos à lista."""
        for fp in file_paths:
            if fp not in self._files:
                self._files.append(fp)
        self._refresh_file_list()
        if self.on_files_dropped:
            self.on_files_dropped(self._files)

    def clear_files(self):
        """Limpa a lista de arquivos."""
        self._files.clear()
        self._refresh_file_list()

    def get_files(self) -> list[str]:
        """Retorna os arquivos selecionados."""
        return self._files.copy()

    def _refresh_file_list(self):
        """Atualiza a exibição da lista de arquivos."""
        for widget in self.files_frame.winfo_children():
            widget.destroy()

        if not self._files:
            self.empty_label = ctk.CTkLabel(
                self.files_frame,
                text="Nenhum arquivo selecionado",
                font=ctk.CTkFont(size=11),
                text_color=COLORS["muted_dark"],
            )
            self.empty_label.pack(pady=10)
            return

        for i, fp in enumerate(self._files):
            row = ctk.CTkFrame(self.files_frame, fg_color="transparent")
            row.pack(fill="x", pady=1)

            name = Path(fp).name
            icon = "📄" if Path(fp).suffix.lower() == ".docx" else "📕"

            ctk.CTkLabel(
                row, text=f"{icon}  {name}",
                font=ctk.CTkFont(size=11),
                anchor="w",
            ).pack(side="left", padx=5)

            remove_btn = ctk.CTkButton(
                row, text="✕", width=24, height=24,
                fg_color="transparent",
                hover_color=COLORS["error"],
                font=ctk.CTkFont(size=12),
                command=lambda idx=i: self._remove_file(idx),
            )
            remove_btn.pack(side="right", padx=5)

    def _remove_file(self, index: int):
        """Remove um arquivo da lista pelo índice."""
        if 0 <= index < len(self._files):
            self._files.pop(index)
            self._refresh_file_list()


# ─────────────────────────────────────────────────────────────
# Aplicação principal
# ─────────────────────────────────────────────────────────────
class SecureDocApp(ctk.CTk):
    """Aplicação principal do SecureDoc Converter."""

    def __init__(self):
        super().__init__()

        self.title(APP_NAME)
        self.geometry(WINDOW_SIZE)
        self.minsize(MIN_WIDTH, MIN_HEIGHT)
        self._center_window()

        # Estado
        self._current_page = "word2pdf"
        self._is_converting = False
        self._cancel_requested = False
        self._log_entries: list[dict] = []
        self._nav_buttons: dict[str, ctk.CTkButton] = {}
        self._last_output_dir = None

        # Tema inicial
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Carrega log existente
        self._load_existing_log()

        # Constrói a interface
        self._build_ui()

        # Protocolo de fechamento
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _center_window(self):
        """Centraliza a janela na tela."""
        self.update_idletasks()
        w, h = map(int, WINDOW_SIZE.split("x"))
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        x = (sw - w) // 2
        y = (sh - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")

    # ─────────────── UI PRINCIPAL ───────────────

    def _build_ui(self):
        """Constrói toda a interface da aplicação."""
        # Grid principal: sidebar + conteúdo
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._build_sidebar()
        self._build_content_area()

        # Mostra a página inicial
        self._show_page("word2pdf")

    def _build_sidebar(self):
        """Constrói a sidebar de navegação."""
        self.sidebar = ctk.CTkFrame(self, width=220, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)

        # Logo / Título
        logo_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        logo_frame.pack(fill="x", padx=15, pady=(25, 5))

        ctk.CTkLabel(
            logo_frame,
            text="🔒",
            font=ctk.CTkFont(size=28),
        ).pack(anchor="w")

        ctk.CTkLabel(
            logo_frame,
            text="SecureDoc",
            font=ctk.CTkFont(size=22, weight="bold"),
        ).pack(anchor="w", pady=(2, 0))

        ctk.CTkLabel(
            logo_frame,
            text="Converter",
            font=ctk.CTkFont(size=14),
            text_color=COLORS["accent"],
        ).pack(anchor="w")

        ctk.CTkLabel(
            logo_frame,
            text=f"v{APP_VERSION}",
            font=ctk.CTkFont(size=10),
            text_color=COLORS["muted_dark"],
        ).pack(anchor="w", pady=(0, 5))

        # Separador
        sep = ctk.CTkFrame(self.sidebar, height=1, fg_color=COLORS["muted_dark"])
        sep.pack(fill="x", padx=15, pady=(5, 15))

        # Navegação label
        ctk.CTkLabel(
            self.sidebar,
            text="CONVERSÃO",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color=COLORS["muted_dark"],
        ).pack(anchor="w", padx=20, pady=(0, 5))

        # Botões de navegação
        nav_items = [
            ("word2pdf", "📝  WORD → PDF", "Converter documentos Word para PDF"),
            ("pdf2word", "📕  PDF → WORD", "Converter documentos PDF para Word"),
        ]

        for page_id, label, tooltip in nav_items:
            btn = ctk.CTkButton(
                self.sidebar,
                text=label,
                anchor="w",
                height=38,
                corner_radius=8,
                fg_color="transparent",
                text_color=COLORS["text_dark"],
                hover_color=COLORS["accent_hover"],
                font=ctk.CTkFont(size=13),
                command=lambda pid=page_id: self._show_page(pid),
            )
            btn.pack(fill="x", padx=10, pady=2)
            self._nav_buttons[page_id] = btn

        # Separador e seção de ferramentas
        ctk.CTkLabel(
            self.sidebar,
            text="FERRAMENTAS",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color=COLORS["muted_dark"],
        ).pack(anchor="w", padx=20, pady=(20, 5))

        tool_items = [
            ("log", "📋  Histórico", "Ver log de conversões"),
            ("about", "ℹ️  Sobre", "Informações do aplicativo"),
        ]

        for page_id, label, tooltip in tool_items:
            btn = ctk.CTkButton(
                self.sidebar,
                text=label,
                anchor="w",
                height=38,
                corner_radius=8,
                fg_color="transparent",
                text_color=COLORS["text_dark"],
                hover_color=COLORS["accent_hover"],
                font=ctk.CTkFont(size=13),
                command=lambda pid=page_id: self._show_page(pid),
            )
            btn.pack(fill="x", padx=10, pady=2)
            self._nav_buttons[page_id] = btn

        # Toggle de tema (embaixo)
        theme_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        theme_frame.pack(side="bottom", fill="x", padx=15, pady=15)

        ctk.CTkLabel(
            theme_frame,
            text="Tema",
            font=ctk.CTkFont(size=11),
            text_color=COLORS["muted_dark"],
        ).pack(anchor="w")

        self.theme_switch = ctk.CTkSwitch(
            theme_frame,
            text="Modo Claro",
            command=self._toggle_theme,
            onvalue="light",
            offvalue="dark",
            font=ctk.CTkFont(size=12),
        )
        self.theme_switch.pack(anchor="w", pady=(5, 0))

        # Créditos
        ctk.CTkLabel(
            theme_frame,
            text="Por Raoni Moraes",
            font=ctk.CTkFont(size=9),
            text_color=COLORS["muted_dark"],
        ).pack(anchor="w", pady=(10, 0))

    def _build_content_area(self):
        """Constrói a área principal de conteúdo."""
        self.content_area = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.content_area.grid(row=0, column=1, sticky="nsew", padx=0, pady=0)
        self.content_area.grid_columnconfigure(0, weight=1)
        self.content_area.grid_rowconfigure(0, weight=1)

        # Frames de cada página (criados sob demanda)
        self._pages: dict[str, ctk.CTkFrame] = {}

    def _show_page(self, page_id: str):
        """Navega para uma página específica."""
        self._current_page = page_id

        # Atualiza botões da sidebar
        for pid, btn in self._nav_buttons.items():
            if pid == page_id:
                btn.configure(fg_color=COLORS["accent"], text_color="#FFFFFF")
            else:
                btn.configure(fg_color="transparent", text_color=COLORS["text_dark"])

        # Esconde todas as páginas
        for frame in self._pages.values():
            frame.grid_remove()

        # Cria a página se não existir
        if page_id not in self._pages:
            if page_id == "word2pdf":
                self._pages[page_id] = self._create_converter_page(
                    direction="word2pdf",
                    title="WORD → PDF",
                    subtitle="Converta documentos .docx para .pdf de forma segura e offline",
                    accepted_ext=[".docx"],
                    icon="📝",
                )
            elif page_id == "pdf2word":
                self._pages[page_id] = self._create_converter_page(
                    direction="pdf2word",
                    title="PDF → WORD",
                    subtitle="Converta documentos .pdf para .docx de forma segura e offline",
                    accepted_ext=[".pdf"],
                    icon="📕",
                )
            elif page_id == "log":
                self._pages[page_id] = self._create_log_page()
            elif page_id == "about":
                self._pages[page_id] = self._create_about_page()

        # Mostra a página
        self._pages[page_id].grid(row=0, column=0, sticky="nsew")

    # ─────────────── PÁGINA DE CONVERSÃO ───────────────

    def _create_converter_page(
        self, direction: str, title: str, subtitle: str,
        accepted_ext: list[str], icon: str,
    ) -> ctk.CTkFrame:
        """Cria uma página de conversão genérica (WORD→PDF ou PDF→WORD)."""
        page = ctk.CTkFrame(self.content_area, fg_color="transparent")
        page.grid_columnconfigure(0, weight=1)

        # Header
        header = ctk.CTkFrame(page, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=30, pady=(20, 5))

        ctk.CTkLabel(
            header,
            text=f"{icon}  {title}",
            font=ctk.CTkFont(size=24, weight="bold"),
        ).pack(anchor="w")

        ctk.CTkLabel(
            header,
            text=subtitle,
            font=ctk.CTkFont(size=13),
            text_color=COLORS["muted_dark"],
        ).pack(anchor="w", pady=(2, 0))

        # Badge de segurança
        security_badge = ctk.CTkFrame(header, fg_color=COLORS["success"], corner_radius=12, height=26)
        security_badge.pack(anchor="w", pady=(8, 0))
        ctk.CTkLabel(
            security_badge,
            text="  🔒 100% Offline — Seus dados nunca saem do computador  ",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="#FFFFFF",
        ).pack(padx=8, pady=3)

        # Drop Zone
        drop = DropZone(
            page,
            accepted_extensions=accepted_ext,
            on_files_dropped=None,
            corner_radius=12,
            border_width=2,
            border_color=COLORS["accent"],
        )
        drop.grid(row=1, column=0, sticky="ew", padx=30, pady=(10, 10))

        drop_zone_ref = drop

        # Configuração de Destino
        dest_frame = ctk.CTkFrame(page, fg_color="transparent")
        dest_frame.grid(row=2, column=0, sticky="ew", padx=30, pady=(0, 10))

        ctk.CTkLabel(
            dest_frame,
            text="Salvar em:",
            font=ctk.CTkFont(size=12, weight="bold"),
        ).pack(side="left", padx=(0, 10))

        dest_var = ctk.StringVar(value="same")
        page._dest_var = dest_var

        def toggle_dest():
            if dest_var.get() == "same":
                btn_choose_dest.configure(state="disabled")
                label_dest_path.configure(text_color=COLORS["muted_dark"])
            else:
                btn_choose_dest.configure(state="normal")
                label_dest_path.configure(text_color=COLORS["text_dark"])

        r_same = ctk.CTkRadioButton(
            dest_frame,
            text="Mesma pasta do arquivo",
            variable=dest_var,
            value="same",
            command=toggle_dest,
            font=ctk.CTkFont(size=12),
        )
        r_same.pack(side="left", padx=(0, 15))

        r_custom = ctk.CTkRadioButton(
            dest_frame,
            text="Pasta personalizada:",
            variable=dest_var,
            value="custom",
            command=toggle_dest,
            font=ctk.CTkFont(size=12),
        )
        r_custom.pack(side="left", padx=(0, 10))

        page._custom_dest_path = ""

        def choose_dest():
            folder = filedialog.askdirectory(title="Selecione a pasta de destino")
            if folder:
                page._custom_dest_path = folder
                label_dest_path.configure(text=os.path.basename(folder))
                tooltip_label.configure(text=f"Caminho completo: {folder}")

        btn_choose_dest = ctk.CTkButton(
            dest_frame,
            text="Selecionar...",
            width=90,
            height=26,
            state="disabled",
            fg_color="transparent",
            border_width=1,
            border_color=COLORS["accent"],
            hover_color=COLORS["accent_hover"],
            font=ctk.CTkFont(size=11),
            command=choose_dest,
        )
        btn_choose_dest.pack(side="left", padx=(0, 10))

        label_dest_path = ctk.CTkLabel(
            dest_frame,
            text="Nenhuma selecionada",
            font=ctk.CTkFont(size=11, slant="italic"),
            text_color=COLORS["muted_dark"],
        )
        label_dest_path.pack(side="left")

        # Botões de seleção de origem
        action_btn_frame = ctk.CTkFrame(page, fg_color="transparent")
        action_btn_frame.grid(row=3, column=0, sticky="ew", padx=30, pady=(0, 10))

        btn_select_files = ctk.CTkButton(
            action_btn_frame,
            text=f"📁  Selecionar Arquivo(s) {'/'.join(accepted_ext)}",
            height=40,
            corner_radius=10,
            fg_color=COLORS["accent"],
            hover_color=COLORS["accent_hover"],
            font=ctk.CTkFont(size=13, weight="bold"),
            command=lambda: self._select_files(drop_zone_ref, accepted_ext),
        )
        btn_select_files.pack(side="left", padx=(0, 10))

        btn_select_folder = ctk.CTkButton(
            action_btn_frame,
            text="📂  Selecionar Pasta",
            height=40,
            corner_radius=10,
            fg_color="transparent",
            border_width=2,
            border_color=COLORS["accent"],
            hover_color=COLORS["accent_hover"],
            font=ctk.CTkFont(size=13),
            command=lambda: self._select_folder(drop_zone_ref, accepted_ext),
        )
        btn_select_folder.pack(side="left", padx=(0, 10))

        btn_clear = ctk.CTkButton(
            action_btn_frame,
            text="🗑️  Limpar",
            height=40,
            width=90,
            corner_radius=10,
            fg_color="transparent",
            border_width=1,
            border_color=COLORS["muted_dark"],
            text_color=COLORS["muted_dark"],
            hover_color=COLORS["error"],
            font=ctk.CTkFont(size=12),
            command=lambda: drop_zone_ref.clear_files(),
        )
        btn_clear.pack(side="left")

        # Barra de progresso e informações
        progress_frame = ctk.CTkFrame(page, fg_color="transparent")
        progress_frame.grid(row=4, column=0, sticky="ew", padx=30, pady=(5, 5))

        progress_bar = ctk.CTkProgressBar(
            progress_frame,
            height=8,
            corner_radius=4,
            progress_color=COLORS["accent"],
        )
        progress_bar.pack(fill="x")
        progress_bar.set(0)

        progress_info_row = ctk.CTkFrame(progress_frame, fg_color="transparent")
        progress_info_row.pack(fill="x", pady=(4, 0))

        progress_label = ctk.CTkLabel(
            progress_info_row,
            text="",
            font=ctk.CTkFont(size=11),
            text_color=COLORS["muted_dark"],
        )
        progress_label.pack(side="left")

        # Botão para abrir pasta pós-conclusão
        btn_open_folder = ctk.CTkButton(
            progress_info_row,
            text="📂 Abrir pasta de destino",
            height=22,
            width=150,
            fg_color=COLORS["success"],
            hover_color="#24A148",
            font=ctk.CTkFont(size=10, weight="bold"),
            command=self._open_last_output_dir,
        )
        # Escondido por padrão, será exibido no finish()
        page._btn_open_folder = btn_open_folder

        # Caminho completo do destino selecionado
        tooltip_label = ctk.CTkLabel(
            page,
            text="",
            font=ctk.CTkFont(size=10),
            text_color=COLORS["muted_dark"],
        )
        tooltip_label.grid(row=5, column=0, sticky="w", padx=35, pady=0)

        # Frame do Botão Converter / Parar
        run_frame = ctk.CTkFrame(page, fg_color="transparent")
        run_frame.grid(row=6, column=0, sticky="ew", padx=30, pady=(10, 5))
        run_frame.grid_columnconfigure(0, weight=1)

        convert_btn = ctk.CTkButton(
            run_frame,
            text=f"⚡  Converter {title}",
            height=46,
            corner_radius=12,
            fg_color=COLORS["accent"],
            hover_color=COLORS["accent_hover"],
            font=ctk.CTkFont(size=15, weight="bold"),
            command=lambda: self._start_conversion(
                direction, drop_zone_ref, progress_bar, progress_label, convert_btn, page,
            ),
        )
        convert_btn.grid(row=0, column=0, sticky="ew")

        # Botão Cancelar (escondido inicialmente)
        cancel_btn = ctk.CTkButton(
            run_frame,
            text="🛑  Parar",
            height=46,
            width=100,
            corner_radius=12,
            fg_color=COLORS["error"],
            hover_color="#C1121F",
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self._cancel_conversion,
        )
        # cancel_btn.grid não é chamado ainda, só na conversão

        # Status do processo
        status_label = ctk.CTkLabel(
            page,
            text="",
            font=ctk.CTkFont(size=12),
        )
        status_label.grid(row=7, column=0, sticky="ew", padx=30, pady=(0, 10))
        page._drop_zone = drop_zone_ref
        page._progress_bar = progress_bar
        page._progress_label = progress_label
        page._convert_btn = convert_btn
        page._cancel_btn = cancel_btn
        page._status_label = status_label
        page._tooltip_label = tooltip_label

        return page

    # ─────────────── LÓGICA DE CONVERSÃO ───────────────

    def _cancel_conversion(self):
        """Solicita o cancelamento da conversão em andamento."""
        if self._is_converting:
            self._cancel_requested = True
            # Procura a página atual e desabilita o botão de cancelar
            page = self._pages.get(self._current_page)
            if page and hasattr(page, "_cancel_btn"):
                page._cancel_btn.configure(state="disabled", text="⏳ Parando...")

    def _select_files(self, drop_zone: DropZone, extensions: list[str]):
        """Abre diálogo para selecionar arquivos."""
        filetypes = []
        for ext in extensions:
            if ext == ".docx":
                filetypes.append(("Documentos Word", "*.docx"))
            elif ext == ".pdf":
                filetypes.append(("Documentos PDF", "*.pdf"))
        filetypes.append(("Todos os arquivos", "*.*"))

        files = filedialog.askopenfilenames(
            title="Selecione os arquivos",
            filetypes=filetypes,
        )
        if files:
            drop_zone.add_files(list(files))

    def _select_folder(self, drop_zone: DropZone, extensions: list[str]):
        """Abre diálogo para selecionar pasta e encontra arquivos compatíveis."""
        folder = filedialog.askdirectory(title="Selecione a pasta")
        if folder:
            found = []
            for ext in extensions:
                pattern = os.path.join(folder, f"*{ext}")
                found.extend(glob.glob(pattern))
            if found:
                drop_zone.add_files(found)
            else:
                messagebox.showinfo(
                    "Nenhum arquivo encontrado",
                    f"Nenhum arquivo {', '.join(extensions)} foi encontrado na pasta selecionada.",
                )

    def _start_conversion(
        self, direction: str, drop_zone: DropZone,
        progress_bar: ctk.CTkProgressBar, progress_label: ctk.CTkLabel,
        convert_btn: ctk.CTkButton, page: ctk.CTkFrame,
    ):
        """Inicia a conversão em uma thread separada."""
        files = drop_zone.get_files()
        if not files:
            messagebox.showwarning(
                "Nenhum arquivo",
                "Selecione pelo menos um arquivo ou pasta para converter.",
            )
            return

        if self._is_converting:
            messagebox.showinfo("Aguarde", "Uma conversão já está em andamento.")
            return

        # Limpa o estado anterior do botão de abrir pasta
        page._btn_open_folder.pack_forget()

        self._is_converting = True
        self._cancel_requested = False
        
        # Exibe o botão de parar e ajusta o botão converter
        convert_btn.configure(state="disabled", text="⏳ Convertendo...")
        convert_btn.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        page._cancel_btn.configure(state="normal", text="🛑  Parar")
        page._cancel_btn.grid(row=0, column=1, sticky="e")
        
        progress_bar.set(0)
        progress_label.configure(text="Iniciando conversão...", text_color=COLORS["muted_dark"])

        thread = threading.Thread(
            target=self._conversion_worker,
            args=(direction, files, progress_bar, progress_label, convert_btn, drop_zone, page),
            daemon=True,
        )
        thread.start()

    def _conversion_worker(
        self, direction: str, files: list[str],
        progress_bar: ctk.CTkProgressBar, progress_label: ctk.CTkLabel,
        convert_btn: ctk.CTkButton, drop_zone: DropZone, page: ctk.CTkFrame,
    ):
        """Worker que executa as conversões em background."""
        total = len(files)
        success_count = 0
        error_count = 0
        cancelled = False

        # Identifica o diretório de destino
        dest_mode = page._dest_var.get()
        custom_dest = page._custom_dest_path
        
        last_success_dir = None

        for i, file_path in enumerate(files):
            # Verifica cancelamento
            if self._cancel_requested:
                cancelled = True
                break

            file_name = Path(file_path).name
            progress = (i + 1) / total

            self.after(0, lambda p=progress: progress_bar.set(p))
            self.after(
                0,
                lambda fn=file_name, idx=i: progress_label.configure(
                    text=f"Convertendo {idx + 1}/{total}: {fn}"
                ),
            )

            # Define o path de saída completo
            if dest_mode == "custom" and custom_dest:
                out_dir = custom_dest
            else:
                out_dir = str(Path(file_path).parent)

            last_success_dir = out_dir
            suffix = ".pdf" if direction == "word2pdf" else ".docx"
            output_file = str(Path(out_dir) / Path(file_path).with_suffix(suffix).name)

            try:
                if direction == "word2pdf":
                    try:
                        output = convert_docx_to_pdf(file_path, output_file)
                    except Exception as e:
                        err_str = str(e)
                        # Identifica falha COM ou Word Application não encontrado
                        if "Word.Application" in err_str or "com_error" in err_str or "pywintypes" in err_str.lower():
                            raise Exception("Necessita do Microsoft Word instalado no Windows para converter WORD -> PDF.")
                        raise e
                    conv_type = "WORD → PDF"
                else:
                    output = convert_pdf_to_docx(file_path, output_file)
                    conv_type = "PDF → WORD"

                success_count += 1
                self._add_log_entry(conv_type, file_name, "✅ Sucesso", Path(output).name)
                logger.info(f"{conv_type} | {file_name} → {Path(output).name} | Sucesso")

            except Exception as e:
                error_count += 1
                error_msg = str(e)
                # Formata erro simplificado para o log visual
                short_err = error_msg if "Microsoft Word" in error_msg else error_msg[:60]
                self._add_log_entry(
                    "WORD → PDF" if direction == "word2pdf" else "PDF → WORD",
                    file_name,
                    f"❌ Erro: {short_err}",
                )
                logger.error(f"{direction.upper()} | {file_name} | Erro: {error_msg}")

        # Finalização na thread principal
        def finish():
            self._is_converting = False
            title = "WORD → PDF" if direction == "word2pdf" else "PDF → WORD"
            
            # Restaura botões
            page._cancel_btn.grid_forget()
            convert_btn.grid(row=0, column=0, sticky="ew", padx=0)
            convert_btn.configure(
                state="normal",
                text=f"⚡  Converter {title}",
            )

            if error_count == 0:
                progress_label.configure(
                    text=f"✅ Concluído! {success_count} arquivo(s) convertido(s) com sucesso.",
                    text_color=COLORS["success"],
                )
                # Salva o último diretório de saída com sucesso para permitir abrir
                if last_success_dir and os.path.exists(last_success_dir):
                    self._last_output_dir = last_success_dir
                    page._btn_open_folder.pack(side="right", padx=5)
            else:
                progress_label.configure(
                    text=f"⚠️ Concluído: {success_count} sucesso, {error_count} erro(s). Veja o Histórico.",
                    text_color=COLORS["warning"],
                )
                if success_count > 0 and last_success_dir and os.path.exists(last_success_dir):
                    self._last_output_dir = last_success_dir
                    page._btn_open_folder.pack(side="right", padx=5)

            # Atualiza a página de log se estiver visível
            if "log" in self._pages:
                self._refresh_log_page()

        self.after(0, finish)

    def _open_last_output_dir(self):
        """Abre o último diretório de saída no Windows Explorer."""
        if self._last_output_dir and os.path.exists(self._last_output_dir):
            try:
                os.startfile(self._last_output_dir)
            except Exception as e:
                messagebox.showerror("Erro ao abrir pasta", f"Não foi possível abrir a pasta:\n{e}")

    # ─────────────── SISTEMA DE LOG ───────────────

    def _add_log_entry(self, conv_type: str, file_name: str, status: str, output_name: str = ""):
        """Adiciona uma entrada ao log em memória."""
        entry = {
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "type": conv_type,
            "file": file_name,
            "output": output_name,
            "status": status,
        }
        self._log_entries.append(entry)

    def _load_existing_log(self):
        """Carrega entradas do arquivo de log existente."""
        if os.path.exists(LOG_FILE):
            try:
                with open(LOG_FILE, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if not line:
                            continue
                        parts = line.split(" | ", 2)
                        if len(parts) >= 3:
                            timestamp = parts[0].strip()
                            level = parts[1].strip()
                            message = parts[2].strip()
                            self._log_entries.append({
                                "timestamp": timestamp,
                                "type": "Histórico",
                                "file": message,
                                "output": "",
                                "status": "ℹ️ " + level,
                            })
            except Exception:
                pass

    def _create_log_page(self) -> ctk.CTkFrame:
        """Cria a página de histórico de log."""
        page = ctk.CTkFrame(self.content_area, fg_color="transparent")
        page.grid_columnconfigure(0, weight=1)
        page.grid_rowconfigure(1, weight=1)

        # Header
        header = ctk.CTkFrame(page, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=30, pady=(25, 10))

        title_row = ctk.CTkFrame(header, fg_color="transparent")
        title_row.pack(fill="x")

        ctk.CTkLabel(
            title_row,
            text="📋  Histórico de Conversões",
            font=ctk.CTkFont(size=24, weight="bold"),
        ).pack(side="left")

        btn_clear_log = ctk.CTkButton(
            title_row,
            text="🗑️  Limpar Histórico",
            width=140,
            height=32,
            corner_radius=8,
            fg_color="transparent",
            border_width=1,
            border_color=COLORS["error"],
            text_color=COLORS["error"],
            hover_color=COLORS["error"],
            font=ctk.CTkFont(size=12),
            command=self._clear_log,
        )
        btn_clear_log.pack(side="right")

        ctk.CTkLabel(
            header,
            text="Todas as conversões realizadas são registradas aqui com data, hora e status.",
            font=ctk.CTkFont(size=13),
            text_color=COLORS["muted_dark"],
        ).pack(anchor="w", pady=(2, 0))

        # Tabela de log
        log_container = ctk.CTkScrollableFrame(page, corner_radius=12)
        log_container.grid(row=1, column=0, sticky="nsew", padx=30, pady=(0, 20))
        log_container.grid_columnconfigure(0, weight=1)

        page._log_container = log_container
        self._refresh_log_page()

        return page

    def _refresh_log_page(self):
        """Atualiza o conteúdo da página de log."""
        if "log" not in self._pages:
            return

        container = self._pages["log"]._log_container

        for widget in container.winfo_children():
            widget.destroy()

        if not self._log_entries:
            ctk.CTkLabel(
                container,
                text="Nenhuma conversão registrada ainda.\nConverta alguns arquivos para ver o histórico aqui.",
                font=ctk.CTkFont(size=13),
                text_color=COLORS["muted_dark"],
                justify="center",
            ).pack(pady=40)
            return

        # Header da tabela
        header_row = ctk.CTkFrame(container, fg_color=COLORS["accent"], corner_radius=8, height=36)
        header_row.pack(fill="x", pady=(0, 5))
        header_row.grid_columnconfigure((0, 1, 2, 3), weight=1)

        headers = ["Data/Hora", "Tipo", "Arquivo", "Status"]
        for col, text in enumerate(headers):
            ctk.CTkLabel(
                header_row,
                text=text,
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color="#FFFFFF",
            ).grid(row=0, column=col, padx=10, pady=6, sticky="w")

        # Entradas (ordem reversa — mais recentes primeiro)
        for i, entry in enumerate(reversed(self._log_entries)):
            row_color = COLORS["card_dark"] if i % 2 == 0 else "transparent"
            row = ctk.CTkFrame(container, fg_color=row_color, corner_radius=6, height=32)
            row.pack(fill="x", pady=1)
            row.grid_columnconfigure((0, 1, 2, 3), weight=1)

            values = [
                entry.get("timestamp", ""),
                entry.get("type", ""),
                entry.get("file", ""),
                entry.get("status", ""),
            ]

            for col, text in enumerate(values):
                color = COLORS["text_dark"]
                if "Sucesso" in text:
                    color = COLORS["success"]
                elif "Erro" in text:
                    color = COLORS["error"]

                ctk.CTkLabel(
                    row,
                    text=text,
                    font=ctk.CTkFont(size=11),
                    text_color=color,
                    anchor="w",
                ).grid(row=0, column=col, padx=10, pady=5, sticky="w")

    def _clear_log(self):
        """Limpa o histórico de log."""
        if messagebox.askyesno("Confirmar", "Tem certeza que deseja limpar todo o histórico?"):
            self._log_entries.clear()
            try:
                with open(LOG_FILE, "w", encoding="utf-8") as f:
                    f.write("")
            except Exception:
                pass
            self._refresh_log_page()

    # ─────────────── PÁGINA SOBRE ───────────────

    def _create_about_page(self) -> ctk.CTkFrame:
        """Cria a página Sobre com informações do aplicativo."""
        page = ctk.CTkFrame(self.content_area, fg_color="transparent")
        page.grid_columnconfigure(0, weight=1)

        # Card principal
        card = ctk.CTkFrame(page, corner_radius=16)
        card.grid(row=0, column=0, padx=60, pady=40, sticky="ew")

        # Logo
        ctk.CTkLabel(
            card,
            text="🔒",
            font=ctk.CTkFont(size=48),
        ).pack(pady=(25, 5))

        ctk.CTkLabel(
            card,
            text=APP_NAME,
            font=ctk.CTkFont(size=28, weight="bold"),
        ).pack()

        ctk.CTkLabel(
            card,
            text=f"Versão {APP_VERSION}",
            font=ctk.CTkFont(size=13),
            text_color=COLORS["accent"],
        ).pack(pady=(2, 12))

        # Descrição
        desc = (
            "Conversor de documentos 100% offline e seguro.\n"
            "Seus arquivos nunca saem do seu computador.\n"
            "Sem upload, sem nuvem, sem rastreamento."
        )
        ctk.CTkLabel(
            card,
            text=desc,
            font=ctk.CTkFont(size=13),
            text_color=COLORS["muted_dark"],
            justify="center",
        ).pack(padx=30)

        # Separador
        sep = ctk.CTkFrame(card, height=1, fg_color=COLORS["muted_dark"])
        sep.pack(fill="x", padx=30, pady=15)

        # Features
        features = [
            ("📝", "WORD → PDF", "Converta documentos .docx para .pdf"),
            ("📕", "PDF → WORD", "Converta documentos .pdf para .docx"),
            ("📋", "Histórico Completo", "Log detalhado de todas as conversões"),
            ("🔒", "100% Offline", "Seus dados nunca saem do computador"),
            ("🎨", "Interface Moderna", "Design premium com tema claro/escuro"),
            ("📂", "Drag & Drop", "Arraste e solte arquivos para converter"),
        ]

        features_frame = ctk.CTkFrame(card, fg_color="transparent")
        features_frame.pack(padx=30, pady=(0, 10))

        for i, (icon, title, desc) in enumerate(features):
            row = i // 2
            col = i % 2

            feature_card = ctk.CTkFrame(features_frame, fg_color="transparent")
            feature_card.grid(row=row, column=col, padx=15, pady=8, sticky="w")

            ctk.CTkLabel(
                feature_card,
                text=f"{icon}  {title}",
                font=ctk.CTkFont(size=13, weight="bold"),
            ).pack(anchor="w")

            ctk.CTkLabel(
                feature_card,
                text=desc,
                font=ctk.CTkFont(size=11),
                text_color=COLORS["muted_dark"],
            ).pack(anchor="w")

        # Créditos
        sep2 = ctk.CTkFrame(card, height=1, fg_color=COLORS["muted_dark"])
        sep2.pack(fill="x", padx=30, pady=(10, 15))

        ctk.CTkLabel(
            card,
            text="Desenvolvido com ❤️ por Raoni Moraes",
            font=ctk.CTkFont(size=13, weight="bold"),
        ).pack()

        ctk.CTkLabel(
            card,
            text="github.com/rmoraes23",
            font=ctk.CTkFont(size=11),
            text_color=COLORS["accent"],
        ).pack(pady=(2, 20))

        return page

    # ─────────────── TEMA ───────────────

    def _toggle_theme(self):
        """Alterna entre tema claro e escuro."""
        current = ctk.get_appearance_mode()
        if current == "Dark":
            ctk.set_appearance_mode("light")
            self.theme_switch.configure(text="Modo Claro")
        else:
            ctk.set_appearance_mode("dark")
            self.theme_switch.configure(text="Modo Escuro")

    # ─────────────── ENCERRAMENTO ───────────────

    def _on_close(self):
        """Encerra a aplicação de forma segura."""
        if self._is_converting:
            if not messagebox.askyesno(
                "Conversão em andamento",
                "Uma conversão está em andamento. Deseja realmente sair?",
            ):
                return
        self.destroy()


# ─────────────────────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app = SecureDocApp()
    app.mainloop()
