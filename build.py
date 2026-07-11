"""
Script de empacotamento PyInstaller para o SecureDoc Converter.
Compila todo o projeto em um executável (.exe) autônomo.
"""

import os
import sys
import subprocess
import shutil

def install_pyinstaller():
    print("Verificando se o PyInstaller está instalado...")
    try:
        import PyInstaller
        print("PyInstaller já está instalado.")
    except ImportError:
        print("PyInstaller não encontrado. Instalando via pip...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        print("PyInstaller instalado com sucesso!")

def clean_previous_builds():
    print("Limpando builds antigos...")
    dirs_to_clean = ["build", "dist"]
    for d in dirs_to_clean:
        if os.path.exists(d):
            try:
                shutil.rmtree(d)
                print(f"Diretório '{d}' removido.")
            except PermissionError as pe:
                print(f"\n⚠️  Aviso: Não foi possível remover o diretório '{d}' devido a falta de permissão.")
                print("   Isso geralmente significa que:")
                print("   1. O aplicativo 'SecureDocConverter.exe' ou um processo Python ainda está em execução.")
                print("   2. A pasta está aberta no Windows Explorer ou sendo escaneada pelo antivírus.")
                print("   Por favor, feche a aplicação e tente novamente. Se o erro persistir, tente deletar a pasta manualmente.\n")
                raise pe
            except Exception as e:
                print(f"Erro ao remover '{d}': {e}")
    
    spec_file = "SecureDocConverter.spec"
    if os.path.exists(spec_file):
        try:
            os.remove(spec_file)
            print(f"Arquivo '{spec_file}' removido.")
        except Exception as e:
            print(f"Erro ao remover '{spec_file}': {e}")

def run_build():
    print("Iniciando a compilação do executável...")
    
    # Comando PyInstaller
    # --noconsole: Não abre a janela preta do prompt
    # --onefile: Empacota tudo em um único .exe
    # --name: Nome do arquivo executável final
    # --collect-all tkinterdnd2: Garante a inclusão dos arquivos de drag & drop
    # --collect-all customtkinter: Garante a inclusão das fontes e temas do CTk
    
    command = [
        "pyinstaller",
        "--noconsole",
        "--onefile",
        "--name=SecureDocConverter",
        "--collect-all=tkinterdnd2",
        "--collect-all=customtkinter",
        "main.py"
    ]
    
    print(f"Executando comando: {' '.join(command)}")
    subprocess.check_call(command)
    print("\n" + "="*50)
    print("COMPILAÇÃO CONCLUÍDA COM SUCESSO!")
    print("O executável autônomo está disponível na pasta 'dist/':")
    print(os.path.abspath("dist/SecureDocConverter.exe"))
    print("="*50)

if __name__ == "__main__":
    try:
        install_pyinstaller()
        clean_previous_builds()
        run_build()
    except Exception as e:
        print(f"\nOcorreu um erro durante o empacotamento: {e}")
        sys.exit(1)
