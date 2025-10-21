import argparse
import logging
import tkinter as tk
from tkinter import filedialog, ttk
from docx2pdf import convert

# Configura o módulo logging para registrar as mensagens de status e erro
logging.basicConfig(
    filename="conversor.log",  # Nome do arquivo de log
    filemode="w",  # Modo de escrita (sobrescreve o arquivo a cada execução)
    format="%(asctime)s - %(levelname)s - %(message)s",  # Formato das mensagens
    level=logging.INFO  # Nível de detalhe das mensagens (INFO ou DEBUG)
)

# Define uma função para converter os arquivos da pasta selecionada
def converter_pasta(caminho_pasta):
    """Converte todos os arquivos .docx da pasta em arquivos .pdf.

    Parâmetros:
        caminho_pasta (str): O caminho absoluto ou relativo da pasta.

    Retorna:
        None

    Lança:
        ValueError: Se o caminho da pasta for inválido ou vazio.
        Exception: Se ocorrer algum erro durante a conversão dos arquivos.
    """
    # Verifica se o caminho da pasta é válido
    if not caminho_pasta:
        raise ValueError("Nenhum diretório selecionado.")
    
    # Atualiza o label de status com uma mensagem de conversão
    label_status["text"] = "Convertendo arquivos..."
    janela.update()  # Atualiza a janela para exibir a mensagem de status
    
    # Registra uma mensagem de início da conversão no arquivo de log
    logging.info(f"Iniciando a conversão dos arquivos da pasta {caminho_pasta}")
    
    try:
        # Usa o módulo docx2pdf para converter os arquivos da pasta
        convert(caminho_pasta)
        
        # Atualiza o label de status com uma mensagem de sucesso
        label_status["text"] = "Conversão concluída com sucesso!"
        
        # Registra uma mensagem de fim da conversão no arquivo de log
        logging.info(f"Conversão concluída com sucesso.")
    
    except Exception as e:
        # Atualiza o label de status com uma mensagem de erro
        label_status["text"] = f"Ocorreu um erro: {e}"
        
        # Registra uma mensagem de erro no arquivo de log
        logging.error(f"Ocorreu um erro: {e}")


# Define uma função para selecionar a pasta usando o filedialog
def selecionar_pasta():
    """Abre uma caixa de diálogo para selecionar uma pasta e chama a função de conversão.

    Parâmetros:
        None

    Retorna:
        None
    """
    # Usa o filedialog para obter o caminho da pasta
    caminho_pasta = filedialog.askdirectory()
    
    try:
        # Chama a função de conversão passando o caminho da pasta
        converter_pasta(caminho_pasta)
    
    except ValueError as e:
        # Atualiza o label de status com uma mensagem de erro
        label_status["text"] = f"Ocorreu um erro: {e}"
        
        # Registra uma mensagem de erro no arquivo de log
        logging.error(f"Ocorreu um erro: {e}")


# Cria um parser para os argumentos da linha de comando
parser = argparse.ArgumentParser(description="Converte todos os arquivos .docx de uma pasta em arquivos .pdf.")

# Adiciona um argumento opcional para o caminho da pasta
parser.add_argument("-p", "--pasta", type=str, help="O caminho da pasta que contém os arquivos .docx.")

# Adiciona um argumento opcional para a opacidade da janela
parser.add_argument("-o", "--opacidade", type=float, default=1.0, help="A opacidade da janela (entre 0 e 1).")

# Adiciona um argumento opcional para o tamanho da janela
parser.add_argument("-t", "--tamanho", type=str, default="600x400", help="O tamanho da janela (largura x altura em pixels).")

# Analisa os argumentos da linha de comando e armazena em uma variável
args = parser.parse_args()

# Cria a janela principal
janela = tk.Tk()

# Define o título da janela
janela.title("Conversor de .docx para .pdf - Desenvolvido por Raoni Moraes")

# Define a opacidade da janela de acordo com o argumento passado
janela.attributes("-alpha", args.opacidade)

# Cria um canvas para desenhar a cor de fundo e configura sua cor e posição
canvas = tk.Canvas(janela, bg="#06221a")  # Escolha a cor que você quiser
canvas.pack(fill="both", expand=True)

# Obtém as dimensões da janela de acordo com o argumento passado
largura_janela, altura_janela = map(int, args.tamanho.split("x"))  # Extrai a largura e altura do argumento

# Redimensiona a janela de acordo com as dimensões obtidas
janela.geometry(f"{largura_janela}x{altura_janela}")

# Cria um frame para conter os widgets principais e configura sua cor e posição
frame_principal = tk.Frame(canvas, bg="#124f53")
frame_principal.place(relx=0.5, rely=0.5, anchor="center")

# Cria um label com o texto do conversor e configura sua cor, fonte e posição
label_texto = tk.Label(frame_principal, text="Conversor de .docx para .pdf", bg="#124f53", fg="#e8e8c5", font=("Arial", 18))
label_texto.grid(row=0, column=0, sticky="w", padx=10)

# Cria um separador horizontal para dividir os widgets e configura sua cor e posição
separador = ttk.Separator(frame_principal, orient="horizontal")
separador.grid(row=1, column=0, sticky="ew", pady=10)

# Cria um botão para selecionar a pasta e configura sua cor, comando e posição
botao_selecionar = tk.Button(frame_principal, text="Selecionar Pasta", command=selecionar_pasta, bg="#124f53", fg="#e8e8c5", width=40)
botao_selecionar.grid(row=2, column=0)

# Cria um label para exibir o status da conversão e configura sua cor, fonte e posição
label_status = tk.Label(frame_principal, text="", bg="#124f53", fg="#e8e8c5", font=("Arial", 12))
label_status.grid(row=3, column=0, pady=10)

# Cria um label com a mensagem "Desenvolvido por Raoni Moraes" no canto inferior esquerdo do frame_principal
label_creditos = tk.Label(frame_principal, text="Desenvolvido por Raoni Moraes", bg="#124f53", fg="#e8e8c5", font=("Arial", 8))
label_creditos.grid(row=4, column=0, sticky="sw", padx=10, pady=10)

# Inicia o loop principal da interface gráfica
janela.mainloop()

# Verifica se o argumento da pasta foi passado pela linha de comando
if args.pasta:
    # Chama a função de conversão passando o argumento da pasta
    converter_pasta(args.pasta)
