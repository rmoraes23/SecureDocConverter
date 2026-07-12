"""
SecureDoc Converter - Suíte de Documentos Segura e Offline
Desenvolvido por Raoni Moraes

Utilitário desktop completo e 100% offline para conversão e
manipulação de arquivos WORD e PDF com foco total em privacidade.
"""

import os
import sys
import glob
import logging
import threading
import datetime
import tempfile
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
APP_VERSION = "3.1.0"
WINDOW_SIZE = "980x720"
MIN_WIDTH = 900
MIN_HEIGHT = 650


# ─────────────────────────────────────────────────────────────
# Funções utilitárias de conversão e manipulação
# ─────────────────────────────────────────────────────────────
def convert_docx_to_pdf(input_path: str, output_path: str | None = None) -> str:
    """Converte um arquivo .docx para .pdf usando docx2pdf."""
    from docx2pdf import convert
    if output_path is None:
        output_path = str(Path(input_path).with_suffix(".pdf"))
    convert(input_path, output_path)
    return output_path


def convert_pdf_to_docx(input_path: str, output_path: str | None = None) -> str:
    """Converte um arquivo .pdf para .docx usando pdf2docx."""
    from pdf2docx import Converter
    if output_path is None:
        output_path = str(Path(input_path).with_suffix(".docx"))
    cv = Converter(input_path)
    cv.convert(output_path)
    cv.close()
    return output_path


def merge_pdfs(input_paths: list[str], output_path: str) -> str:
    """Mescla vários arquivos PDF em um único PDF de saída."""
    from pypdf import PdfMerger
    merger = PdfMerger()
    for path in input_paths:
        merger.append(path)
    merger.write(output_path)
    merger.close()
    return output_path


def compress_pdf(input_path: str, output_path: str, level: str = "medium") -> str:
    """Comprime um PDF reduzindo e limpando fluxos de dados usando PyMuPDF."""
    import fitz  # PyMuPDF
    doc = fitz.open(input_path)
    
    if level == "extreme":
        doc.save(output_path, garbage=4, deflate=True, clean=True)
    elif level == "medium":
        doc.save(output_path, garbage=3, deflate=True)
    else:  # light
        doc.save(output_path, garbage=1, deflate=True)
        
    doc.close()
    return output_path


def add_watermark(
    input_path: str, output_path: str,
    wm_type: str, text: str = "",
    img_path: str = "", opacity: float = 0.3,
    rotation: float = 45.0, color: str = "#64748B"
) -> str:
    """Aplica marca d'água de texto ou imagem rotacionada e opaca sobre o PDF."""
    from pypdf import PdfReader, PdfWriter
    from reportlab.pdfgen import canvas
    from reportlab.lib.colors import HexColor
    
    reader = PdfReader(input_path)
    writer = PdfWriter()
    total_pages = len(reader.pages)
    
    # Cria PDF temporário para a marca d'água
    fd, temp_pdf = tempfile.mkstemp(suffix=".pdf")
    os.close(fd)
    
    c = canvas.Canvas(temp_pdf)
    
    for page_num in range(total_pages):
        page = reader.pages[page_num]
        width = float(page.mediabox.width)
        height = float(page.mediabox.height)
        c.setPageSize((width, height))
        
        c.saveState()
        c.setFillAlpha(opacity)
        c.setStrokeAlpha(opacity)
        
        if wm_type == "text" and text:
            c.setFillColor(HexColor(color))
            c.setFont("Helvetica-Bold", min(width, height) * 0.08)
            c.translate(width / 2, height / 2)
            c.rotate(rotation)
            c.drawCentredString(0, 0, text)
            
        elif wm_type == "image" and img_path and os.path.exists(img_path):
            img_w = width * 0.5
            img_h = img_w
            c.translate(width / 2, height / 2)
            c.rotate(rotation)
            c.drawImage(img_path, -img_w/2, -img_h/2, width=img_w, height=img_h, mask='auto')
            
        c.restoreState()
        c.showPage()
        
    c.save()
    
    # Junta marca d'água
    wm_reader = PdfReader(temp_pdf)
    for i in range(total_pages):
        orig_page = reader.pages[i]
        wm_page = wm_reader.pages[i]
        orig_page.merge_page(wm_page)
        writer.add_page(orig_page)
        
    with open(output_path, "wb") as f:
        writer.write(f)
        
    try:
        os.remove(temp_pdf)
    except Exception:
        pass
        
    return output_path


def add_page_numbers(
    input_path: str, output_path: str,
    position: str, format_type: str,
    font_name: str, number_style: str
) -> str:
    """Insere numeração romana ou arábica em posições variadas no PDF."""
    from pypdf import PdfReader, PdfWriter
    from reportlab.pdfgen import canvas
    
    def to_roman(n):
        val = [1000, 900, 500, 400, 100, 90, 50, 40, 10, 9, 5, 4, 1]
        syb = ["M", "CM", "D", "CD", "C", "XC", "L", "XL", "X", "IX", "V", "IV", "I"]
        res = ""
        for i in range(len(val)):
            while n >= val[i]:
                res += syb[i]
                n -= val[i]
        return res

    reader = PdfReader(input_path)
    writer = PdfWriter()
    total_pages = len(reader.pages)
    
    fd, temp_pdf = tempfile.mkstemp(suffix=".pdf")
    os.close(fd)
    
    c = canvas.Canvas(temp_pdf)
    
    for page_num in range(1, total_pages + 1):
        page = reader.pages[page_num - 1]
        width = float(page.mediabox.width)
        height = float(page.mediabox.height)
        c.setPageSize((width, height))
        
        c.setFont(font_name, 10)
        
        num_str = to_roman(page_num) if number_style == "Romano (I, II, III)" else str(page_num)
        if format_type == "Página X de Y":
            tot_str = to_roman(total_pages) if number_style == "Romano (I, II, III)" else str(total_pages)
            label = f"{num_str} de {tot_str}"
        else:
            label = num_str
            
        # Posição Y
        y = height - 36 if "Cabeçalho" in position else 36
        
        # Posição X
        if "Esquerda" in position:
            x = 36
            c.drawString(x, y, label)
        elif "Direita" in position:
            x = width - 36
            c.drawRightString(x, y, label)
        else:  # Centro
            x = width / 2
            c.drawCentredString(x, y, label)
            
        c.showPage()
    
    c.save()
    
    # Junta numeração
    num_reader = PdfReader(temp_pdf)
    for i in range(total_pages):
        orig_page = reader.pages[i]
        num_page = num_reader.pages[i]
        orig_page.merge_page(num_page)
        writer.add_page(orig_page)
        
    with open(output_path, "wb") as f:
        writer.write(f)
        
    try:
        os.remove(temp_pdf)
    except Exception:
        pass
        
    return output_path


def encrypt_pdf(input_path: str, output_path: str, password: str) -> str:
    """Criptografa um arquivo PDF com uma senha de abertura usando pypdf."""
    from pypdf import PdfReader, PdfWriter
    reader = PdfReader(input_path)
    writer = PdfWriter()
    
    for page in reader.pages:
        writer.add_page(page)
        
    writer.encrypt(password)
    
    with open(output_path, "wb") as f:
        writer.write(f)
        
    return output_path


def parse_page_ranges(ranges_str: str, max_pages: int) -> list[int]:
    """Converte string '1-3, 5' em lista de indices [0, 1, 2, 4]."""
    pages = set()
    parts = ranges_str.replace(" ", "").split(",")
    for part in parts:
        if not part:
            continue
        if "-" in part:
            subparts = part.split("-")
            if len(subparts) == 2:
                try:
                    start = int(subparts[0])
                    end = int(subparts[1])
                    start = max(1, min(start, max_pages))
                    end = max(1, min(end, max_pages))
                    if start <= end:
                        for p in range(start, end + 1):
                            pages.add(p - 1)
                    else:
                        for p in range(end, start + 1):
                            pages.add(p - 1)
                except ValueError:
                    pass
        else:
            try:
                p = int(part)
                if 1 <= p <= max_pages:
                    pages.add(p - 1)
            except ValueError:
                pass
    return sorted(list(pages))


def split_pdf(input_path: str, output_path: str, page_ranges_str: str) -> str:
    """Gera um novo PDF apenas com as páginas especificadas na string de intervalos."""
    from pypdf import PdfReader, PdfWriter
    reader = PdfReader(input_path)
    writer = PdfWriter()
    max_pages = len(reader.pages)
    
    indices = parse_page_ranges(page_ranges_str, max_pages)
    if not indices:
        raise Exception("Nenhuma página válida especificada no intervalo.")
        
    for idx in indices:
        writer.add_page(reader.pages[idx])
        
    with open(output_path, "wb") as f:
        writer.write(f)
        
    return output_path


# ─────────────────────────────────────────────────────────────
# Widget personalizado: Zona de Drop com Reordenação Opcional
# ─────────────────────────────────────────────────────────────
class DropZone(ctk.CTkFrame):
    """Área visual para drag & drop de arquivos com suporte a reordenação."""

    def __init__(self, master, accepted_extensions: list[str], show_ordering: bool = False, **kwargs):
        super().__init__(master, **kwargs)
        self.accepted_extensions = [ext.lower() for ext in accepted_extensions]
        self.show_ordering = show_ordering
        self._files: list[str] = []

        # Ícone e textos
        self.icon_label = ctk.CTkLabel(self, text="📂", font=ctk.CTkFont(size=36))
        self.icon_label.pack(pady=(15, 2))

        ext_text = " / ".join(self.accepted_extensions)
        self.title_label = ctk.CTkLabel(
            self, text="Arraste e solte arquivos aqui",
            font=ctk.CTkFont(size=14, weight="bold"),
        )
        self.title_label.pack(pady=0)

        self.subtitle_label = ctk.CTkLabel(
            self, text=f"Aceita: {ext_text}  •  Ou selecione abaixo",
            font=ctk.CTkFont(size=11),
            text_color=COLORS["muted_dark"],
        )
        self.subtitle_label.pack(pady=(0, 5))

        # Lista de arquivos selecionados
        self.files_frame = ctk.CTkScrollableFrame(self, height=75)
        self.files_frame.pack(fill="x", padx=15, pady=(5, 10))

        self.empty_label = ctk.CTkLabel(
            self.files_frame, text="Nenhum arquivo selecionado",
            font=ctk.CTkFont(size=11),
            text_color=COLORS["muted_dark"],
        )
        self.empty_label.pack(pady=10)

        self._setup_dnd()

    def _setup_dnd(self):
        try:
            self.after(500, self._register_dnd)
        except Exception:
            pass

    def _register_dnd(self):
        try:
            self.drop_target_register("DND_Files")
            self.dnd_bind("<<Drop>>", self._on_drop)
        except Exception:
            pass

    def _on_drop(self, event):
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
        for fp in file_paths:
            if fp not in self._files:
                self._files.append(fp)
        self._refresh_file_list()

    def clear_files(self):
        self._files.clear()
        self._refresh_file_list()

    def get_files(self) -> list[str]:
        return self._files.copy()

    def _refresh_file_list(self):
        for widget in self.files_frame.winfo_children():
            widget.destroy()

        if not self._files:
            self.empty_label = ctk.CTkLabel(
                self.files_frame, text="Nenhum arquivo selecionado",
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

            # Botão de remover no canto direito
            remove_btn = ctk.CTkButton(
                row, text="✕", width=22, height=22,
                fg_color="transparent",
                hover_color=COLORS["error"],
                font=ctk.CTkFont(size=11),
                command=lambda idx=i: self._remove_file(idx),
            )
            remove_btn.pack(side="right", padx=2)

            # Botões de ordenação se necessário
            if self.show_ordering and len(self._files) > 1:
                if i < len(self._files) - 1:
                    down_btn = ctk.CTkButton(
                        row, text="▼", width=22, height=22,
                        fg_color="transparent",
                        hover_color=COLORS["accent_hover"],
                        font=ctk.CTkFont(size=9),
                        command=lambda idx=i: self._move_file_down(idx),
                    )
                    down_btn.pack(side="right", padx=1)

                if i > 0:
                    up_btn = ctk.CTkButton(
                        row, text="▲", width=22, height=22,
                        fg_color="transparent",
                        hover_color=COLORS["accent_hover"],
                        font=ctk.CTkFont(size=9),
                        command=lambda idx=i: self._move_file_up(idx),
                    )
                    up_btn.pack(side="right", padx=1)

    def _remove_file(self, index: int):
        if 0 <= index < len(self._files):
            self._files.pop(index)
            self._refresh_file_list()

    def _move_file_up(self, index: int):
        if index > 0:
            self._files[index], self._files[index - 1] = self._files[index - 1], self._files[index]
            self._refresh_file_list()

    def _move_file_down(self, index: int):
        if index < len(self._files) - 1:
            self._files[index], self._files[index + 1] = self._files[index + 1], self._files[index]
            self._refresh_file_list()


# ─────────────────────────────────────────────────────────────
# Aplicação Principal
# ─────────────────────────────────────────────────────────────
class SecureDocApp(ctk.CTk):
    """Suíte Desktop de utilitários WORD e PDF offline."""

    def __init__(self):
        super().__init__()

        self.title(APP_NAME)
        self.geometry(WINDOW_SIZE)
        self.minsize(MIN_WIDTH, MIN_HEIGHT)
        self._center_window()

        # Estado geral
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

        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _center_window(self):
        self.update_idletasks()
        w, h = map(int, WINDOW_SIZE.split("x"))
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        x = (sw - w) // 2
        y = (sh - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")

    # ─────────────── UI PRINCIPAL ───────────────

    def _build_ui(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._build_sidebar()
        self._build_content_area()
        self._show_page("word2pdf")

    def _build_sidebar(self):
        self.sidebar = ctk.CTkFrame(self, width=220, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)

        # Header logo
        logo_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        logo_frame.pack(fill="x", padx=15, pady=(20, 5))

        ctk.CTkLabel(logo_frame, text="🔒", font=ctk.CTkFont(size=28)).pack(anchor="w")
        ctk.CTkLabel(logo_frame, text="SecureDoc", font=ctk.CTkFont(size=20, weight="bold")).pack(anchor="w", pady=(2, 0))
        ctk.CTkLabel(logo_frame, text="PDF Suite", font=ctk.CTkFont(size=14), text_color=COLORS["accent"]).pack(anchor="w")
        ctk.CTkLabel(logo_frame, text=f"v{APP_VERSION}", font=ctk.CTkFont(size=10), text_color=COLORS["muted_dark"]).pack(anchor="w", pady=(0, 5))

        sep = ctk.CTkFrame(self.sidebar, height=1, fg_color=COLORS["muted_dark"])
        sep.pack(fill="x", padx=15, pady=(5, 10))

        # Navegação: Conversão
        ctk.CTkLabel(self.sidebar, text="CONVERSÃO", font=ctk.CTkFont(size=10, weight="bold"), text_color=COLORS["muted_dark"]).pack(anchor="w", padx=20, pady=(5, 2))

        conv_items = [
            ("word2pdf", "📝  WORD → PDF"),
            ("pdf2word", "📕  PDF → WORD"),
        ]
        for page_id, label in conv_items:
            self._create_nav_button(page_id, label)

        # Navegação: Utilitários PDF
        ctk.CTkLabel(self.sidebar, text="UTILITÁRIOS PDF", font=ctk.CTkFont(size=10, weight="bold"), text_color=COLORS["muted_dark"]).pack(anchor="w", padx=20, pady=(15, 2))

        pdf_items = [
            ("pdfmerge", "🧩  Juntar PDFs"),
            ("pdfcompress", "📉  Comprimir PDF"),
            ("pdfsplit", "✂️  Dividir PDF"),
            ("pdfwatermark", "🎨  Marca D'água"),
            ("pdfnumber", "🔢  Numerar Páginas"),
            ("pdfprotect", "🔐  Proteger PDF"),
        ]
        for page_id, label in pdf_items:
            self._create_nav_button(page_id, label)

        # Navegação: Ferramentas
        ctk.CTkLabel(self.sidebar, text="FERRAMENTAS", font=ctk.CTkFont(size=10, weight="bold"), text_color=COLORS["muted_dark"]).pack(anchor="w", padx=20, pady=(15, 2))

        tool_items = [
            ("log", "📋  Histórico"),
            ("about", "ℹ️  Sobre"),
        ]
        for page_id, label in tool_items:
            self._create_nav_button(page_id, label)

        # Switch de tema
        theme_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        theme_frame.pack(side="bottom", fill="x", padx=15, pady=15)

        self.theme_switch = ctk.CTkSwitch(
            theme_frame, text="Modo Claro",
            command=self._toggle_theme,
            onvalue="light", offvalue="dark",
            font=ctk.CTkFont(size=12),
        )
        self.theme_switch.pack(anchor="w")

        ctk.CTkLabel(theme_frame, text="Por Raoni Moraes", font=ctk.CTkFont(size=9), text_color=COLORS["muted_dark"]).pack(anchor="w", pady=(5, 0))

    def _create_nav_button(self, page_id: str, label: str):
        btn = ctk.CTkButton(
            self.sidebar, text=label, anchor="w", height=34, corner_radius=8,
            fg_color="transparent", text_color=COLORS["text_dark"],
            hover_color=COLORS["accent_hover"], font=ctk.CTkFont(size=12),
            command=lambda: self._show_page(page_id),
        )
        btn.pack(fill="x", padx=10, pady=1)
        self._nav_buttons[page_id] = btn

    def _build_content_area(self):
        self.content_area = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.content_area.grid(row=0, column=1, sticky="nsew")
        self.content_area.grid_columnconfigure(0, weight=1)
        self.content_area.grid_rowconfigure(0, weight=1)
        self._pages: dict[str, ctk.CTkFrame] = {}

    def _show_page(self, page_id: str):
        self._current_page = page_id

        # Sidebar highlights
        for pid, btn in self._nav_buttons.items():
            if pid == page_id:
                btn.configure(fg_color=COLORS["accent"], text_color="#FFFFFF")
            else:
                btn.configure(fg_color="transparent", text_color=COLORS["text_dark"])

        for frame in self._pages.values():
            frame.grid_remove()

        if page_id not in self._pages:
            if page_id == "word2pdf":
                self._pages[page_id] = self._create_converter_page(
                    "word2pdf", "WORD → PDF", "Converta documentos .docx para .pdf de forma offline", [".docx"], "📝"
                )
            elif page_id == "pdf2word":
                self._pages[page_id] = self._create_converter_page(
                    "pdf2word", "PDF → WORD", "Converta documentos .pdf para .docx de forma offline", [".pdf"], "📕"
                )
            elif page_id == "pdfmerge":
                self._pages[page_id] = self._create_merge_page()
            elif page_id == "pdfcompress":
                self._pages[page_id] = self._create_compress_page()
            elif page_id == "pdfsplit":
                self._pages[page_id] = self._create_split_page()
            elif page_id == "pdfwatermark":
                self._pages[page_id] = self._create_watermark_page()
            elif page_id == "pdfnumber":
                self._pages[page_id] = self._create_numbering_page()
            elif page_id == "pdfprotect":
                self._pages[page_id] = self._create_protect_page()
            elif page_id == "log":
                self._pages[page_id] = self._create_log_page()
            elif page_id == "about":
                self._pages[page_id] = self._create_about_page()

        self._pages[page_id].grid(row=0, column=0, sticky="nsew")

    # ─────────────── BASE DA UI DE CONVERSÃO / UTILS ───────────────

    def _create_base_layout(self, title: str, subtitle: str, icon: str) -> tuple[ctk.CTkFrame, ctk.CTkFrame]:
        """Cria estrutura de cabeçalho padrão para as abas."""
        page = ctk.CTkFrame(self.content_area, fg_color="transparent")
        page.grid_columnconfigure(0, weight=1)

        # Header
        header = ctk.CTkFrame(page, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=30, pady=(20, 5))

        ctk.CTkLabel(header, text=f"{icon}  {title}", font=ctk.CTkFont(size=24, weight="bold")).pack(anchor="w")
        ctk.CTkLabel(header, text=subtitle, font=ctk.CTkFont(size=12), text_color=COLORS["muted_dark"]).pack(anchor="w", pady=(2, 0))

        security_badge = ctk.CTkFrame(header, fg_color=COLORS["success"], corner_radius=12, height=24)
        security_badge.pack(anchor="w", pady=(6, 0))
        ctk.CTkLabel(
            security_badge, text="  🔒 100% Offline — Seus dados não saem do computador  ",
            font=ctk.CTkFont(size=10, weight="bold"), text_color="#FFFFFF"
        ).pack(padx=8, pady=3)

        return page, header

    def _add_dest_selection(self, page: ctk.CTkFrame, row: int) -> ctk.StringVar:
        """Insere widget de seleção de pasta de destino."""
        dest_frame = ctk.CTkFrame(page, fg_color="transparent")
        dest_frame.grid(row=row, column=0, sticky="ew", padx=30, pady=(0, 10))

        ctk.CTkLabel(dest_frame, text="Salvar em:", font=ctk.CTkFont(size=12, weight="bold")).pack(side="left", padx=(0, 10))

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
            dest_frame, text="Mesma pasta", variable=dest_var, value="same",
            command=toggle_dest, font=ctk.CTkFont(size=12)
        )
        r_same.pack(side="left", padx=(0, 15))

        r_custom = ctk.CTkRadioButton(
            dest_frame, text="Personalizada:", variable=dest_var, value="custom",
            command=toggle_dest, font=ctk.CTkFont(size=12)
        )
        r_custom.pack(side="left", padx=(0, 10))

        page._custom_dest_path = ""

        def choose_dest():
            folder = filedialog.askdirectory(title="Selecione a pasta de destino")
            if folder:
                page._custom_dest_path = folder
                label_dest_path.configure(text=os.path.basename(folder))

        btn_choose_dest = ctk.CTkButton(
            dest_frame, text="Selecionar...", width=80, height=24, state="disabled",
            fg_color="transparent", border_width=1, border_color=COLORS["accent"],
            hover_color=COLORS["accent_hover"], font=ctk.CTkFont(size=11), command=choose_dest
        )
        btn_choose_dest.pack(side="left", padx=(0, 10))

        label_dest_path = ctk.CTkLabel(
            dest_frame, text="Nenhuma selecionada",
            font=ctk.CTkFont(size=11, slant="italic"), text_color=COLORS["muted_dark"]
        )
        label_dest_path.pack(side="left")

        return dest_var

    def _add_progress_elements(self, page: ctk.CTkFrame, row: int, convert_command) -> tuple[ctk.CTkProgressBar, ctk.CTkLabel, ctk.CTkButton]:
        """Adiciona barra de progresso, labels e botões de execução."""
        progress_frame = ctk.CTkFrame(page, fg_color="transparent")
        progress_frame.grid(row=row, column=0, sticky="ew", padx=30, pady=(5, 5))

        progress_bar = ctk.CTkProgressBar(progress_frame, height=8, corner_radius=4, progress_color=COLORS["accent"])
        progress_bar.pack(fill="x")
        progress_bar.set(0)

        progress_info_row = ctk.CTkFrame(progress_frame, fg_color="transparent")
        progress_info_row.pack(fill="x", pady=(4, 0))

        progress_label = ctk.CTkLabel(progress_info_row, text="", font=ctk.CTkFont(size=11), text_color=COLORS["muted_dark"])
        progress_label.pack(side="left")

        btn_open_folder = ctk.CTkButton(
            progress_info_row, text="📂 Abrir pasta de destino", height=22, width=150,
            fg_color=COLORS["success"], hover_color="#24A148",
            font=ctk.CTkFont(size=10, weight="bold"), command=self._open_last_output_dir
        )
        page._btn_open_folder = btn_open_folder

        run_frame = ctk.CTkFrame(page, fg_color="transparent")
        run_frame.grid(row=row + 1, column=0, sticky="ew", padx=30, pady=(10, 5))
        run_frame.grid_columnconfigure(0, weight=1)

        convert_btn = ctk.CTkButton(
            run_frame, text="⚡ Executar Operação", height=42, corner_radius=12,
            fg_color=COLORS["accent"], hover_color=COLORS["accent_hover"],
            font=ctk.CTkFont(size=14, weight="bold"), command=convert_command
        )
        convert_btn.grid(row=0, column=0, sticky="ew")

        cancel_btn = ctk.CTkButton(
            run_frame, text="🛑  Parar", height=42, width=90, corner_radius=12,
            fg_color=COLORS["error"], hover_color="#C1121F",
            font=ctk.CTkFont(size=13, weight="bold"), command=self._cancel_conversion
        )
        page._cancel_btn = cancel_btn

        return progress_bar, progress_label, convert_btn

    # ─────────────── PÁGINA: WORD ↔ PDF ───────────────

    def _create_converter_page(
        self, direction: str, title: str, subtitle: str, accepted_ext: list[str], icon: str
    ) -> ctk.CTkFrame:
        page, _ = self._create_base_layout(title, subtitle, icon)

        drop = DropZone(page, accepted_extensions=accepted_ext, show_ordering=False, corner_radius=12, border_width=2, border_color=COLORS["accent"])
        drop.grid(row=1, column=0, sticky="ew", padx=30, pady=(10, 10))

        self._add_dest_selection(page, 2)

        # Botões de Origem
        action_btn_frame = ctk.CTkFrame(page, fg_color="transparent")
        action_btn_frame.grid(row=3, column=0, sticky="ew", padx=30, pady=(0, 10))

        ctk.CTkButton(
            action_btn_frame, text=f"📁  Selecionar Arquivo(s) {'/'.join(accepted_ext)}", height=38, corner_radius=10,
            fg_color=COLORS["accent"], hover_color=COLORS["accent_hover"], font=ctk.CTkFont(size=12, weight="bold"),
            command=lambda: self._select_files(drop, accepted_ext)
        ).pack(side="left", padx=(0, 10))

        ctk.CTkButton(
            action_btn_frame, text="📂  Selecionar Pasta", height=38, corner_radius=10,
            fg_color="transparent", border_width=2, border_color=COLORS["accent"],
            hover_color=COLORS["accent_hover"], font=ctk.CTkFont(size=12),
            command=lambda: self._select_folder(drop, accepted_ext)
        ).pack(side="left", padx=(0, 10))

        ctk.CTkButton(
            action_btn_frame, text="🗑️  Limpar", height=38, width=80, corner_radius=10,
            fg_color="transparent", border_width=1, border_color=COLORS["muted_dark"],
            text_color=COLORS["muted_dark"], hover_color=COLORS["error"], font=ctk.CTkFont(size=12),
            command=drop.clear_files
        ).pack(side="left")

        # Progresso e Execução
        def run_action():
            self._start_conversion(direction, drop, pbar, plabel, pbtn, page)

        pbar, plabel, pbtn = self._add_progress_elements(page, 4, run_action)
        pbtn.configure(text=f"⚡  Converter {title}")

        page._drop_zone = drop
        page._progress_bar = pbar
        page._progress_label = plabel
        page._convert_btn = pbtn

        return page

    # ─────────────── PÁGINA: JUNTAR PDFS ───────────────

    def _create_merge_page(self) -> ctk.CTkFrame:
        page, _ = self._create_base_layout("Juntar PDFs", "Mescle múltiplos documentos PDF em um único arquivo", [".pdf"])

        drop = DropZone(page, accepted_extensions=[".pdf"], show_ordering=True, corner_radius=12, border_width=2, border_color=COLORS["accent"])
        drop.grid(row=1, column=0, sticky="ew", padx=30, pady=(10, 10))

        self._add_dest_selection(page, 2)

        # Botões de Origem
        action_btn_frame = ctk.CTkFrame(page, fg_color="transparent")
        action_btn_frame.grid(row=3, column=0, sticky="ew", padx=30, pady=(0, 10))

        ctk.CTkButton(
            action_btn_frame, text="📁  Adicionar PDF(s)", height=38, corner_radius=10,
            fg_color=COLORS["accent"], hover_color=COLORS["accent_hover"], font=ctk.CTkFont(size=12, weight="bold"),
            command=lambda: self._select_files(drop, [".pdf"])
        ).pack(side="left", padx=(0, 10))

        ctk.CTkButton(
            action_btn_frame, text="🗑️  Limpar Tudo", height=38, width=100, corner_radius=10,
            fg_color="transparent", border_width=1, border_color=COLORS["muted_dark"],
            text_color=COLORS["muted_dark"], hover_color=COLORS["error"], font=ctk.CTkFont(size=12),
            command=drop.clear_files
        ).pack(side="left")

        # Progresso e Execução
        def run_action():
            self._start_conversion("merge", drop, pbar, plabel, pbtn, page)

        pbar, plabel, pbtn = self._add_progress_elements(page, 4, run_action)
        pbtn.configure(text="⚡  Juntar PDFs")

        page._drop_zone = drop
        page._progress_bar = pbar
        page._progress_label = plabel
        page._convert_btn = pbtn

        return page

    # ─────────────── PÁGINA: COMPRIMIR PDF ───────────────

    def _create_compress_page(self) -> ctk.CTkFrame:
        page, _ = self._create_base_layout("Comprimir PDF", "Reduza o tamanho de documentos PDF mantendo a legibilidade", [".pdf"])

        drop = DropZone(page, accepted_extensions=[".pdf"], show_ordering=False, corner_radius=12, border_width=2, border_color=COLORS["accent"])
        drop.grid(row=1, column=0, sticky="ew", padx=30, pady=(10, 10))

        # Nível de compressão
        options_frame = ctk.CTkFrame(page, fg_color="transparent")
        options_frame.grid(row=2, column=0, sticky="ew", padx=30, pady=(0, 10))

        ctk.CTkLabel(options_frame, text="Nível:", font=ctk.CTkFont(size=12, weight="bold")).pack(side="left", padx=(0, 15))

        compress_level = ctk.StringVar(value="medium")
        page._compress_level = compress_level

        r_light = ctk.CTkRadioButton(options_frame, text="Leve (Compressão rápida)", variable=compress_level, value="light", font=ctk.CTkFont(size=12))
        r_light.pack(side="left", padx=(0, 15))

        r_med = ctk.CTkRadioButton(options_frame, text="Recomendado", variable=compress_level, value="medium", font=ctk.CTkFont(size=12))
        r_med.pack(side="left", padx=(0, 15))

        r_ext = ctk.CTkRadioButton(options_frame, text="Extremo (Máxima redução)", variable=compress_level, value="extreme", font=ctk.CTkFont(size=12))
        r_ext.pack(side="left")

        self._add_dest_selection(page, 3)

        action_btn_frame = ctk.CTkFrame(page, fg_color="transparent")
        action_btn_frame.grid(row=4, column=0, sticky="ew", padx=30, pady=(0, 10))

        ctk.CTkButton(
            action_btn_frame, text="📁  Selecionar PDF(s)", height=38, corner_radius=10,
            fg_color=COLORS["accent"], hover_color=COLORS["accent_hover"], font=ctk.CTkFont(size=12, weight="bold"),
            command=lambda: self._select_files(drop, [".pdf"])
        ).pack(side="left", padx=(0, 10))

        ctk.CTkButton(
            action_btn_frame, text="🗑️  Limpar", height=38, width=80, corner_radius=10,
            fg_color="transparent", border_width=1, border_color=COLORS["muted_dark"],
            text_color=COLORS["muted_dark"], hover_color=COLORS["error"], font=ctk.CTkFont(size=12),
            command=drop.clear_files
        ).pack(side="left")

        def run_action():
            self._start_conversion("compress", drop, pbar, plabel, pbtn, page)

        pbar, plabel, pbtn = self._add_progress_elements(page, 5, run_action)
        pbtn.configure(text="⚡  Comprimir PDF(s)")

        page._drop_zone = drop
        page._progress_bar = pbar
        page._progress_label = plabel
        page._convert_btn = pbtn

        return page

    # ─────────────── PÁGINA: DIVIDIR PDF ───────────────

    def _create_split_page(self) -> ctk.CTkFrame:
        page, _ = self._create_base_layout("Dividir PDF", "Extraia ou remova páginas de arquivos PDF localmente", [".pdf"])

        drop = DropZone(page, accepted_extensions=[".pdf"], show_ordering=False, corner_radius=12, border_width=2, border_color=COLORS["accent"])
        drop.grid(row=1, column=0, sticky="ew", padx=30, pady=(10, 10))

        # Painel de Intervalos
        panel = ctk.CTkFrame(page, corner_radius=10)
        panel.grid(row=2, column=0, sticky="ew", padx=30, pady=(0, 10))
        
        ctk.CTkLabel(panel, text="Intervalo de Páginas:", font=ctk.CTkFont(size=12, weight="bold")).pack(side="left", padx=(15, 10), pady=10)
        
        range_input = ctk.CTkEntry(panel, placeholder_text="Ex: 1-3, 5, 8-10", height=28, width=220)
        range_input.pack(side="left", padx=(0, 15), pady=10)
        page._split_ranges = range_input
        
        ctk.CTkLabel(
            panel, text="Use vírgula para páginas soltas e hífen para intervalos.",
            font=ctk.CTkFont(size=11, slant="italic"), text_color=COLORS["muted_dark"]
        ).pack(side="left", padx=(0, 15))

        self._add_dest_selection(page, 3)

        action_btn_frame = ctk.CTkFrame(page, fg_color="transparent")
        action_btn_frame.grid(row=4, column=0, sticky="ew", padx=30, pady=(0, 10))

        ctk.CTkButton(
            action_btn_frame, text="📁  Selecionar PDF(s)", height=38, corner_radius=10,
            fg_color=COLORS["accent"], hover_color=COLORS["accent_hover"], font=ctk.CTkFont(size=12, weight="bold"),
            command=lambda: self._select_files(drop, [".pdf"])
        ).pack(side="left", padx=(0, 10))

        ctk.CTkButton(
            action_btn_frame, text="🗑️  Limpar", height=38, width=80, corner_radius=10,
            fg_color="transparent", border_width=1, border_color=COLORS["muted_dark"],
            text_color=COLORS["muted_dark"], hover_color=COLORS["error"], font=ctk.CTkFont(size=12),
            command=drop.clear_files
        ).pack(side="left")

        def run_action():
            self._start_conversion("split", drop, pbar, plabel, pbtn, page)

        pbar, plabel, pbtn = self._add_progress_elements(page, 5, run_action)
        pbtn.configure(text="⚡  Dividir PDF(s)")

        page._drop_zone = drop
        page._progress_bar = pbar
        page._progress_label = plabel
        page._convert_btn = pbtn

        return page

    # ─────────────── PÁGINA: MARCA D'ÁGUA ───────────────

    def _create_watermark_page(self) -> ctk.CTkFrame:
        page, _ = self._create_base_layout("Marca D'água", "Insira texto ou imagens como marcas d'água no PDF", [".pdf"])

        drop = DropZone(page, accepted_extensions=[".pdf"], show_ordering=False, corner_radius=12, border_width=2, border_color=COLORS["accent"])
        drop.grid(row=1, column=0, sticky="ew", padx=30, pady=(10, 5))

        # Painel de Opções da Marca D'água
        options_panel = ctk.CTkFrame(page, corner_radius=10)
        options_panel.grid(row=2, column=0, sticky="ew", padx=30, pady=(5, 10))
        options_panel.grid_columnconfigure((0, 1, 2, 3), weight=1)

        wm_type_var = ctk.StringVar(value="text")
        page._wm_type = wm_type_var

        # Tipo da marca d'água
        type_frame = ctk.CTkFrame(options_panel, fg_color="transparent")
        type_frame.grid(row=0, column=0, columnspan=4, sticky="w", padx=15, pady=8)
        ctk.CTkLabel(type_frame, text="Tipo:", font=ctk.CTkFont(size=12, weight="bold")).pack(side="left", padx=(0, 15))

        def on_type_change():
            if wm_type_var.get() == "text":
                text_input.configure(state="normal")
                color_combo.configure(state="normal")
                btn_img.configure(state="disabled")
            else:
                text_input.configure(state="disabled")
                color_combo.configure(state="disabled")
                btn_img.configure(state="normal")

        ctk.CTkRadioButton(type_frame, text="Texto", variable=wm_type_var, value="text", command=on_type_change, font=ctk.CTkFont(size=12)).pack(side="left", padx=(0, 15))
        ctk.CTkRadioButton(type_frame, text="Imagem", variable=wm_type_var, value="image", command=on_type_change, font=ctk.CTkFont(size=12)).pack(side="left")

        # Parâmetro de Texto
        ctk.CTkLabel(options_panel, text="Texto:", font=ctk.CTkFont(size=12, weight="bold")).grid(row=1, column=0, sticky="w", padx=15, pady=5)
        text_input = ctk.CTkEntry(options_panel, placeholder_text="Marca D'água Exemplo", height=28)
        text_input.grid(row=1, column=1, columnspan=2, sticky="ew", padx=(0, 15), pady=5)
        page._wm_text = text_input

        # Cor do Texto
        color_combo = ctk.CTkComboBox(options_panel, values=["Cinza", "Preto", "Vermelho", "Azul", "Verde"], height=28)
        color_combo.grid(row=1, column=3, sticky="ew", padx=(0, 15), pady=5)
        page._wm_color = color_combo

        # Parâmetro de Imagem
        ctk.CTkLabel(options_panel, text="Imagem:", font=ctk.CTkFont(size=12, weight="bold")).grid(row=2, column=0, sticky="w", padx=15, pady=5)
        
        page._wm_image_path = ""
        label_img_name = ctk.CTkLabel(options_panel, text="Nenhuma imagem", font=ctk.CTkFont(size=11, slant="italic"), text_color=COLORS["muted_dark"])
        label_img_name.grid(row=2, column=2, sticky="w", pady=5)

        def select_image():
            path = filedialog.askopenfilename(title="Selecione a Imagem", filetypes=[("Imagens", "*.png;*.jpg;*.jpeg")])
            if path:
                page._wm_image_path = path
                label_img_name.configure(text=os.path.basename(path), text_color=COLORS["text_dark"])

        btn_img = ctk.CTkButton(
            options_panel, text="Escolher...", height=28, state="disabled",
            fg_color="transparent", border_width=1, border_color=COLORS["accent"], command=select_image
        )
        btn_img.grid(row=2, column=1, sticky="ew", padx=(0, 15), pady=5)

        # Rotação e Opacidade
        ctrl_frame = ctk.CTkFrame(options_panel, fg_color="transparent")
        ctrl_frame.grid(row=3, column=0, columnspan=4, sticky="ew", padx=15, pady=8)
        ctrl_frame.grid_columnconfigure((1, 3), weight=1)

        # Opacidade
        ctk.CTkLabel(ctrl_frame, text="Opacidade:", font=ctk.CTkFont(size=11, weight="bold")).grid(row=0, column=0, sticky="w", padx=(0, 10))
        opac_slider = ctk.CTkSlider(ctrl_frame, from_=0.1, to=1.0, number_of_steps=9)
        opac_slider.set(0.3)
        opac_slider.grid(row=0, column=1, sticky="ew", padx=(0, 20))
        page._wm_opacity = opac_slider

        # Rotação
        ctk.CTkLabel(ctrl_frame, text="Rotação (Graus):", font=ctk.CTkFont(size=11, weight="bold")).grid(row=0, column=2, sticky="w", padx=(0, 10))
        rot_slider = ctk.CTkSlider(ctrl_frame, from_=-90, to=90, number_of_steps=180)
        rot_slider.set(45)
        rot_slider.grid(row=0, column=3, sticky="ew")
        page._wm_rotation = rot_slider

        self._add_dest_selection(page, 3)

        # Botões de Origem
        action_btn_frame = ctk.CTkFrame(page, fg_color="transparent")
        action_btn_frame.grid(row=4, column=0, sticky="ew", padx=30, pady=(0, 10))

        ctk.CTkButton(
            action_btn_frame, text="📁  Selecionar PDF(s)", height=38, corner_radius=10,
            fg_color=COLORS["accent"], hover_color=COLORS["accent_hover"], font=ctk.CTkFont(size=12, weight="bold"),
            command=lambda: self._select_files(drop, [".pdf"])
        ).pack(side="left", padx=(0, 10))

        ctk.CTkButton(
            action_btn_frame, text="🗑️  Limpar", height=38, width=80, corner_radius=10,
            fg_color="transparent", border_width=1, border_color=COLORS["muted_dark"],
            text_color=COLORS["muted_dark"], hover_color=COLORS["error"], font=ctk.CTkFont(size=12),
            command=drop.clear_files
        ).pack(side="left")

        def run_action():
            self._start_conversion("watermark", drop, pbar, plabel, pbtn, page)

        pbar, plabel, pbtn = self._add_progress_elements(page, 5, run_action)
        pbtn.configure(text="⚡  Aplicar Marca D'água")

        page._drop_zone = drop
        page._progress_bar = pbar
        page._progress_label = plabel
        page._convert_btn = pbtn

        return page

    # ─────────────── PÁGINA: NUMERAÇÃO DE PÁGINAS ───────────────

    def _create_numbering_page(self) -> ctk.CTkFrame:
        page, _ = self._create_base_layout("Numerar Páginas", "Adicione paginação avançada no cabeçalho ou rodapé do PDF", [".pdf"])

        drop = DropZone(page, accepted_extensions=[".pdf"], show_ordering=False, corner_radius=12, border_width=2, border_color=COLORS["accent"])
        drop.grid(row=1, column=0, sticky="ew", padx=30, pady=(10, 5))

        # Painel de Opções
        panel = ctk.CTkFrame(page, corner_radius=10)
        panel.grid(row=2, column=0, sticky="ew", padx=30, pady=(5, 10))
        panel.grid_columnconfigure((0, 1, 2, 3), weight=1)

        # Posição
        ctk.CTkLabel(panel, text="Posição:", font=ctk.CTkFont(size=12, weight="bold")).grid(row=0, column=0, sticky="w", padx=15, pady=8)
        pos_combo = ctk.CTkComboBox(
            panel, height=28,
            values=[
                "Rodapé - Centro", "Rodapé - Direita", "Rodapé - Esquerda",
                "Cabeçalho - Centro", "Cabeçalho - Direita", "Cabeçalho - Esquerda"
            ]
        )
        pos_combo.grid(row=0, column=1, sticky="ew", padx=(0, 15), pady=8)
        page._num_position = pos_combo

        # Formato
        ctk.CTkLabel(panel, text="Formato:", font=ctk.CTkFont(size=12, weight="bold")).grid(row=0, column=2, sticky="w", padx=15, pady=8)
        fmt_combo = ctk.CTkComboBox(panel, values=["Apenas número (1)", "Página X de Y"], height=28)
        fmt_combo.grid(row=0, column=3, sticky="ew", padx=(0, 15), pady=8)
        page._num_format = fmt_combo

        # Estilo do Número
        ctk.CTkLabel(panel, text="Estilo:", font=ctk.CTkFont(size=12, weight="bold")).grid(row=1, column=0, sticky="w", padx=15, pady=8)
        style_combo = ctk.CTkComboBox(panel, values=["Arábico (1, 2, 3)", "Romano (I, II, III)"], height=28)
        style_combo.grid(row=1, column=1, sticky="ew", padx=(0, 15), pady=8)
        page._num_style = style_combo

        # Fonte
        ctk.CTkLabel(panel, text="Fonte:", font=ctk.CTkFont(size=12, weight="bold")).grid(row=1, column=2, sticky="w", padx=15, pady=8)
        font_combo = ctk.CTkComboBox(panel, values=["Helvetica", "Times-Roman", "Courier"], height=28)
        font_combo.grid(row=1, column=3, sticky="ew", padx=(0, 15), pady=8)
        page._num_font = font_combo

        self._add_dest_selection(page, 3)

        # Botões de Origem
        action_btn_frame = ctk.CTkFrame(page, fg_color="transparent")
        action_btn_frame.grid(row=4, column=0, sticky="ew", padx=30, pady=(0, 10))

        ctk.CTkButton(
            action_btn_frame, text="📁  Selecionar PDF(s)", height=38, corner_radius=10,
            fg_color=COLORS["accent"], hover_color=COLORS["accent_hover"], font=ctk.CTkFont(size=12, weight="bold"),
            command=lambda: self._select_files(drop, [".pdf"])
        ).pack(side="left", padx=(0, 10))

        ctk.CTkButton(
            action_btn_frame, text="🗑️  Limpar", height=38, width=80, corner_radius=10,
            fg_color="transparent", border_width=1, border_color=COLORS["muted_dark"],
            text_color=COLORS["muted_dark"], hover_color=COLORS["error"], font=ctk.CTkFont(size=12),
            command=drop.clear_files
        ).pack(side="left")

        def run_action():
            self._start_conversion("number", drop, pbar, plabel, pbtn, page)

        pbar, plabel, pbtn = self._add_progress_elements(page, 5, run_action)
        pbtn.configure(text="⚡  Numerar Páginas")

        page._drop_zone = drop
        page._progress_bar = pbar
        page._progress_label = plabel
        page._convert_btn = pbtn

        return page

    # ─────────────── PÁGINA: PROTEGER PDF ───────────────

    def _create_protect_page(self) -> ctk.CTkFrame:
        page, _ = self._create_base_layout("Proteger PDF", "Adicione criptografia e senha de leitura aos seus arquivos PDF", [".pdf"])

        drop = DropZone(page, accepted_extensions=[".pdf"], show_ordering=False, corner_radius=12, border_width=2, border_color=COLORS["accent"])
        drop.grid(row=1, column=0, sticky="ew", padx=30, pady=(10, 10))

        # Painel de Senha
        panel = ctk.CTkFrame(page, corner_radius=10)
        panel.grid(row=2, column=0, sticky="ew", padx=30, pady=(0, 10))
        
        ctk.CTkLabel(panel, text="Senha de Abertura:", font=ctk.CTkFont(size=12, weight="bold")).pack(side="left", padx=(15, 10), pady=10)
        
        pwd_input = ctk.CTkEntry(panel, placeholder_text="Senha para abrir o PDF", height=28, width=220, show="*")
        pwd_input.pack(side="left", padx=(0, 15), pady=10)
        page._protect_pwd = pwd_input
        
        def toggle_password_visibility():
            if show_pwd_var.get():
                pwd_input.configure(show="")
            else:
                pwd_input.configure(show="*")
                
        show_pwd_var = ctk.BooleanVar(value=False)
        chk_show = ctk.CTkCheckBox(
            panel, text="Mostrar Senha", variable=show_pwd_var,
            command=toggle_password_visibility, font=ctk.CTkFont(size=11)
        )
        chk_show.pack(side="left", padx=(0, 15), pady=10)

        self._add_dest_selection(page, 3)

        action_btn_frame = ctk.CTkFrame(page, fg_color="transparent")
        action_btn_frame.grid(row=4, column=0, sticky="ew", padx=30, pady=(0, 10))

        ctk.CTkButton(
            action_btn_frame, text="📁  Selecionar PDF(s)", height=38, corner_radius=10,
            fg_color=COLORS["accent"], hover_color=COLORS["accent_hover"], font=ctk.CTkFont(size=12, weight="bold"),
            command=lambda: self._select_files(drop, [".pdf"])
        ).pack(side="left", padx=(0, 10))

        ctk.CTkButton(
            action_btn_frame, text="🗑️  Limpar", height=38, width=80, corner_radius=10,
            fg_color="transparent", border_width=1, border_color=COLORS["muted_dark"],
            text_color=COLORS["muted_dark"], hover_color=COLORS["error"], font=ctk.CTkFont(size=12),
            command=drop.clear_files
        ).pack(side="left")

        def run_action():
            self._start_conversion("protect", drop, pbar, plabel, pbtn, page)

        pbar, plabel, pbtn = self._add_progress_elements(page, 5, run_action)
        pbtn.configure(text="⚡  Criptografar PDF(s)")

        page._drop_zone = drop
        page._progress_bar = pbar
        page._progress_label = plabel
        page._convert_btn = pbtn

        return page

    # ─────────────── SISTEMA DE NAVEGAÇÃO DOS DIRETÓRIOS ───────────────

    def _select_files(self, drop_zone: DropZone, extensions: list[str]):
        filetypes = []
        for ext in extensions:
            if ext == ".docx":
                filetypes.append(("Documentos Word", "*.docx"))
            elif ext == ".pdf":
                filetypes.append(("Documentos PDF", "*.pdf"))
        filetypes.append(("Todos os arquivos", "*.*"))

        files = filedialog.askopenfilenames(title="Selecione os arquivos", filetypes=filetypes)
        if files:
            drop_zone.add_files(list(files))

    def _select_folder(self, drop_zone: DropZone, extensions: list[str]):
        folder = filedialog.askdirectory(title="Selecione a pasta")
        if folder:
            found = []
            for ext in extensions:
                pattern = os.path.join(folder, f"*{ext}")
                found.extend(glob.glob(pattern))
            if found:
                drop_zone.add_files(found)
            else:
                messagebox.showinfo("Nenhum arquivo", f"Nenhum arquivo {', '.join(extensions)} foi encontrado.")

    # ─────────────── SISTEMA DE CONVERSÃO / THREADING ───────────────

    def _cancel_conversion(self):
        if self._is_converting:
            self._cancel_requested = True
            page = self._pages.get(self._current_page)
            if page and hasattr(page, "_cancel_btn"):
                page._cancel_btn.configure(state="disabled", text="⏳ Parando...")

    def _start_conversion(
        self, op_type: str, drop_zone: DropZone,
        progress_bar: ctk.CTkProgressBar, progress_label: ctk.CTkLabel,
        convert_btn: ctk.CTkButton, page: ctk.CTkFrame,
    ):
        files = drop_zone.get_files()
        if not files:
            messagebox.showwarning("Nenhum arquivo", "Adicione pelo menos um arquivo na lista.")
            return

        if self._is_converting:
            messagebox.showinfo("Aguarde", "Uma operação já está em andamento.")
            return

        page._btn_open_folder.pack_forget()

        self._is_converting = True
        self._cancel_requested = False

        convert_btn.configure(state="disabled", text="⏳ Processando...")
        convert_btn.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        page._cancel_btn.configure(state="normal", text="🛑  Parar")
        page._cancel_btn.grid(row=0, column=1, sticky="e")

        progress_bar.set(0)
        progress_label.configure(text="Iniciando...", text_color=COLORS["muted_dark"])

        thread = threading.Thread(
            target=self._conversion_worker,
            args=(op_type, files, progress_bar, progress_label, convert_btn, page),
            daemon=True
        )
        thread.start()

    def _conversion_worker(
        self, op_type: str, files: list[str],
        progress_bar: ctk.CTkProgressBar, progress_label: ctk.CTkLabel,
        convert_btn: ctk.CTkButton, page: ctk.CTkFrame
    ):
        success_count = 0
        error_count = 0
        cancelled = False
        last_success_dir = None

        dest_mode = page._dest_var.get()
        custom_dest = page._custom_dest_path

        # 1. Trata operação de Merge (junção) -> Gera apenas um único arquivo final
        if op_type == "merge":
            if dest_mode == "custom" and custom_dest:
                out_dir = custom_dest
            else:
                out_dir = str(Path(files[0]).parent)
            
            output_file = str(Path(out_dir) / f"Mesclado_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf")
            last_success_dir = out_dir

            self.after(0, lambda: progress_bar.set(0.5))
            self.after(0, lambda: progress_label.configure(text="Juntando arquivos PDF..."))

            try:
                merge_pdfs(files, output_file)
                success_count = len(files)
                self._add_log_entry("Juntar PDFs", f"{len(files)} arquivos", "✅ Sucesso", Path(output_file).name)
                logger.info(f"Merge PDF | {len(files)} arquivos mesclados em {Path(output_file).name}")
            except Exception as e:
                error_count = len(files)
                self._add_log_entry("Juntar PDFs", "Fila PDF", f"❌ Erro: {str(e)[:60]}")
                logger.error(f"Merge PDF | Erro: {e}")

        # 2. Operações em fila (múltiplos arquivos independentes)
        else:
            total = len(files)
            for i, file_path in enumerate(files):
                if self._cancel_requested:
                    cancelled = True
                    break

                file_name = Path(file_path).name
                progress = (i + 1) / total

                self.after(0, lambda p=progress: progress_bar.set(p))
                self.after(0, lambda fn=file_name, idx=i: progress_label.configure(text=f"Processando {idx + 1}/{total}: {fn}"))

                if dest_mode == "custom" and custom_dest:
                    out_dir = custom_dest
                else:
                    out_dir = str(Path(file_path).parent)

                last_success_dir = out_dir

                try:
                    # WORD -> PDF
                    if op_type == "word2pdf":
                        suffix = ".pdf"
                        output_file = str(Path(out_dir) / Path(file_path).with_suffix(suffix).name)
                        try:
                            output = convert_docx_to_pdf(file_path, output_file)
                        except Exception as e:
                            err_str = str(e)
                            if "Word.Application" in err_str or "com_error" in err_str or "pywintypes" in err_str.lower():
                                raise Exception("Necessita do Microsoft Word instalado no Windows para converter WORD -> PDF.")
                            raise e
                        log_type = "WORD → PDF"

                    # PDF -> WORD
                    elif op_type == "pdf2word":
                        suffix = ".docx"
                        output_file = str(Path(out_dir) / Path(file_path).with_suffix(suffix).name)
                        output = convert_pdf_to_docx(file_path, output_file)
                        log_type = "PDF → WORD"

                    # Comprimir PDF
                    elif op_type == "compress":
                        suffix = "_comprimido.pdf"
                        output_file = str(Path(out_dir) / (Path(file_path).stem + suffix))
                        level = page._compress_level.get()
                        output = compress_pdf(file_path, output_file, level)
                        log_type = "Comprimir PDF"

                    # Dividir PDF
                    elif op_type == "split":
                        suffix = "_dividido.pdf"
                        output_file = str(Path(out_dir) / (Path(file_path).stem + suffix))
                        ranges = page._split_ranges.get()
                        if not ranges:
                            raise Exception("Digite os intervalos de pagina (ex: 1-3, 5).")
                        output = split_pdf(file_path, output_file, ranges)
                        log_type = "Dividir PDF"

                    # Marca D'água
                    elif op_type == "watermark":
                        suffix = "_marca.pdf"
                        output_file = str(Path(out_dir) / (Path(file_path).stem + suffix))
                        
                        wm_type = page._wm_type.get()
                        text = page._wm_text.get()
                        img = page._wm_image_path
                        opacity = page._wm_opacity.get()
                        rotation = page._wm_rotation.get()
                        
                        color_name = page._wm_color.get()
                        color_map = {
                            "Cinza": "#64748B", "Preto": "#000000", "Vermelho": "#E63946",
                            "Azul": "#00B4D8", "Verde": "#2DC653"
                        }
                        color_hex = color_map.get(color_name, "#64748B")

                        output = add_watermark(file_path, output_file, wm_type, text, img, opacity, rotation, color_hex)
                        log_type = "Marca D'água"

                    # Numeração de Páginas
                    elif op_type == "number":
                        suffix = "_numerado.pdf"
                        output_file = str(Path(out_dir) / (Path(file_path).stem + suffix))
                        
                        pos = page._num_position.get()
                        fmt = page._num_format.get()
                        style = page._num_style.get()
                        font = page._num_font.get()

                        output = add_page_numbers(file_path, output_file, pos, fmt, font, style)
                        log_type = "Numerar PDF"

                    # Proteger PDF
                    elif op_type == "protect":
                        suffix = "_protegido.pdf"
                        output_file = str(Path(out_dir) / (Path(file_path).stem + suffix))
                        pwd = page._protect_pwd.get()
                        if not pwd:
                            raise Exception("Digite a senha de abertura desejada.")
                        output = encrypt_pdf(file_path, output_file, pwd)
                        log_type = "Proteger PDF"

                    success_count += 1
                    self._add_log_entry(log_type, file_name, "✅ Sucesso", Path(output).name)
                    logger.info(f"{log_type} | {file_name} → {Path(output).name} | Sucesso")

                except Exception as e:
                    error_count += 1
                    error_msg = str(e)
                    short_err = error_msg if "Microsoft Word" in error_msg else error_msg[:60]
                    self._add_log_entry(
                        op_type.upper(), file_name, f"❌ Erro: {short_err}"
                    )
                    logger.error(f"{op_type.upper()} | {file_name} | Erro: {error_msg}")

        # Finalização da UI
        def finish():
            self._is_converting = False
            
            page._cancel_btn.grid_forget()
            convert_btn.grid(row=0, column=0, sticky="ew", padx=0)
            
            titles_map = {
                "word2pdf": "Converter WORD → PDF", "pdf2word": "Converter PDF → WORD",
                "merge": "Juntar PDFs", "compress": "Comprimir PDF(s)",
                "split": "Dividir PDF(s)", "watermark": "Aplicar Marca D'água",
                "number": "Numerar Páginas", "protect": "Criptografar PDF(s)"
            }
            convert_btn.configure(state="normal", text=f"⚡  {titles_map.get(op_type, 'Executar')}")
            progress_bar.set(1)

            if cancelled:
                progress_label.configure(
                    text=f"🛑 Operação interrompida! {success_count} concluído(s).",
                    text_color=COLORS["warning"]
                )
                self._add_log_entry(op_type.upper(), "Vários", "🛑 Operação parada pelo usuário")
            elif error_count == 0:
                progress_label.configure(
                    text="✅ Concluído com sucesso!", text_color=COLORS["success"]
                )
                if last_success_dir and os.path.exists(last_success_dir):
                    self._last_output_dir = last_success_dir
                    page._btn_open_folder.pack(side="right", padx=5)
            else:
                progress_label.configure(
                    text=f"⚠️ Concluído com {error_count} erro(s). Veja o Histórico.",
                    text_color=COLORS["warning"]
                )
                if success_count > 0 and last_success_dir and os.path.exists(last_success_dir):
                    self._last_output_dir = last_success_dir
                    page._btn_open_folder.pack(side="right", padx=5)

            if "log" in self._pages:
                self._refresh_log_page()

        self.after(0, finish)

    def _open_last_output_dir(self):
        if self._last_output_dir and os.path.exists(self._last_output_dir):
            try:
                os.startfile(self._last_output_dir)
            except Exception as e:
                messagebox.showerror("Erro ao abrir pasta", f"Não foi possível abrir a pasta:\n{e}")

    # ─────────────── SISTEMA DE HISTÓRICO / LOGS ───────────────

    def _add_log_entry(self, conv_type: str, file_name: str, status: str, output_name: str = ""):
        entry = {
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "type": conv_type,
            "file": file_name,
            "output": output_name,
            "status": status,
        }
        self._log_entries.append(entry)

    def _load_existing_log(self):
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
        page = ctk.CTkFrame(self.content_area, fg_color="transparent")
        page.grid_columnconfigure(0, weight=1)
        page.grid_rowconfigure(1, weight=1)

        # Header
        header = ctk.CTkFrame(page, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=30, pady=(25, 10))

        title_row = ctk.CTkFrame(header, fg_color="transparent")
        title_row.pack(fill="x")

        ctk.CTkLabel(title_row, text="📋  Histórico de Operações", font=ctk.CTkFont(size=24, weight="bold")).pack(side="left")

        ctk.CTkButton(
            title_row, text="🗑️  Limpar Histórico", width=140, height=32, corner_radius=8,
            fg_color="transparent", border_width=1, border_color=COLORS["error"],
            text_color=COLORS["error"], hover_color=COLORS["error"], font=ctk.CTkFont(size=12),
            command=self._clear_log
        ).pack(side="right")

        ctk.CTkLabel(
            header, text="Todas as operações e conversões realizadas são registradas localmente aqui.",
            font=ctk.CTkFont(size=12), text_color=COLORS["muted_dark"]
        ).pack(anchor="w", pady=(2, 0))

        log_container = ctk.CTkScrollableFrame(page, corner_radius=12)
        log_container.grid(row=1, column=0, sticky="nsew", padx=30, pady=(0, 20))
        log_container.grid_columnconfigure(0, weight=1)

        page._log_container = log_container
        self._refresh_log_page()

        return page

    def _refresh_log_page(self):
        if "log" not in self._pages:
            return

        container = self._pages["log"]._log_container

        for widget in container.winfo_children():
            widget.destroy()

        if not self._log_entries:
            ctk.CTkLabel(
                container, text="Nenhum histórico registrado.\nExecute algumas tarefas para ver o log.",
                font=ctk.CTkFont(size=12), text_color=COLORS["muted_dark"], justify="center"
            ).pack(pady=40)
            return

        header_row = ctk.CTkFrame(container, fg_color=COLORS["accent"], corner_radius=8, height=36)
        header_row.pack(fill="x", pady=(0, 5))
        header_row.grid_columnconfigure((0, 1, 2, 3), weight=1)

        headers = ["Data/Hora", "Operação", "Arquivo", "Status"]
        for col, text in enumerate(headers):
            ctk.CTkLabel(header_row, text=text, font=ctk.CTkFont(size=11, weight="bold"), text_color="#FFFFFF").grid(row=0, column=col, padx=10, pady=6, sticky="w")

        for i, entry in enumerate(reversed(self._log_entries)):
            row_color = COLORS["card_dark"] if i % 2 == 0 else "transparent"
            row = ctk.CTkFrame(container, fg_color=row_color, corner_radius=6, height=32)
            row.pack(fill="x", pady=1)
            row.grid_columnconfigure((0, 1, 2, 3), weight=1)

            values = [entry.get("timestamp", ""), entry.get("type", ""), entry.get("file", ""), entry.get("status", "")]

            for col, text in enumerate(values):
                color = COLORS["text_dark"]
                if "Sucesso" in text:
                    color = COLORS["success"]
                elif "Erro" in text:
                    color = COLORS["error"]

                ctk.CTkLabel(row, text=text, font=ctk.CTkFont(size=10), text_color=color, anchor="w").grid(row=0, column=col, padx=10, pady=5, sticky="w")

    def _clear_log(self):
        if messagebox.askyesno("Confirmar", "Deseja realmente limpar todo o histórico?"):
            self._log_entries.clear()
            try:
                with open(LOG_FILE, "w", encoding="utf-8") as f:
                    f.write("")
            except Exception:
                pass
            self._refresh_log_page()

    # ─────────────── PÁGINA: SOBRE ───────────────

    def _create_about_page(self) -> ctk.CTkFrame:
        page = ctk.CTkFrame(self.content_area, fg_color="transparent")
        page.grid_columnconfigure(0, weight=1)

        card = ctk.CTkFrame(page, corner_radius=16)
        card.grid(row=0, column=0, padx=50, pady=25, sticky="ew")

        ctk.CTkLabel(card, text="🔒", font=ctk.CTkFont(size=44)).pack(pady=(20, 2))
        ctk.CTkLabel(card, text=APP_NAME, font=ctk.CTkFont(size=24, weight="bold")).pack()
        ctk.CTkLabel(card, text=f"Versão {APP_VERSION} (PDF Suite)", font=ctk.CTkFont(size=12), text_color=COLORS["accent"]).pack(pady=(2, 10))

        desc = (
            "Sua suíte completa e segura para tratamento de PDFs e WORD.\n"
            "Todos os processos de junção, compressão, paginação, marcas d'água\n"
            "e conversões rodam de maneira 100% offline localmente."
        )
        ctk.CTkLabel(card, text=desc, font=ctk.CTkFont(size=12), text_color=COLORS["muted_dark"], justify="center").pack(padx=25)

        sep = ctk.CTkFrame(card, height=1, fg_color=COLORS["muted_dark"])
        sep.pack(fill="x", padx=30, pady=12)

        features = [
            ("📝", "WORD ↔ PDF", "Converte docx ↔ pdf"),
            ("🧩", "Juntar PDFs", "Une vários arquivos PDF"),
            ("📉", "Comprimir PDF", "Reduz o tamanho com PyMuPDF"),
            ("✂️", "Dividir PDF", "Extrai intervalos de páginas"),
            ("🎨", "Marca D'água", "Adiciona texto/imagem opacos"),
            ("🔢", "Numerar Páginas", "Cabeçalho/rodapé romano ou arábico"),
            ("🔐", "Proteger PDF", "Criptografa com senha local"),
        ]

        features_frame = ctk.CTkFrame(card, fg_color="transparent")
        features_frame.pack(padx=25, pady=(0, 5))
        features_frame.grid_columnconfigure((0, 1), weight=1)

        for i, (icon, title, f_desc) in enumerate(features):
            row = i // 2
            col = i % 2

            f_card = ctk.CTkFrame(features_frame, fg_color="transparent")
            f_card.grid(row=row, column=col, padx=15, pady=6, sticky="w")

            ctk.CTkLabel(f_card, text=f"{icon}  {title}", font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w")
            ctk.CTkLabel(f_card, text=f_desc, font=ctk.CTkFont(size=10), text_color=COLORS["muted_dark"]).pack(anchor="w")

        sep2 = ctk.CTkFrame(card, height=1, fg_color=COLORS["muted_dark"])
        sep2.pack(fill="x", padx=30, pady=(10, 10))

        ctk.CTkLabel(card, text="Desenvolvido com ❤️ por Raoni Moraes", font=ctk.CTkFont(size=12, weight="bold")).pack()
        ctk.CTkLabel(card, text="github.com/rmoraes23", font=ctk.CTkFont(size=11), text_color=COLORS["accent"]).pack(pady=(2, 20))

        return page

    # ─────────────── TEMA ───────────────

    def _toggle_theme(self):
        current = ctk.get_appearance_mode()
        if current == "Dark":
            ctk.set_appearance_mode("light")
            self.theme_switch.configure(text="Modo Claro")
        else:
            ctk.set_appearance_mode("dark")
            self.theme_switch.configure(text="Modo Escuro")

    # ─────────────── ENCERRAMENTO ───────────────

    def _on_close(self):
        if self._is_converting:
            if not messagebox.askyesno("Execução ativa", "Uma operação está ativa. Deseja cancelar e sair?"):
                return
        self.destroy()


# ─────────────────────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app = SecureDocApp()
    app.mainloop()
