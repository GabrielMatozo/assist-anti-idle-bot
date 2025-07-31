import os
import platform
import subprocess
import sys
from pathlib import Path


def print_header(text):
    # Cabeçalho visual para separar etapas no terminal
    print("\n" + "=" * 60)
    print(f" {text} ".center(60, "="))
    print("=" * 60 + "\n")


def print_step(text):
    # Destaca o passo atual do processo
    print(f"[+] {text}")


def print_info(text):
    # Informações complementares para o usuário
    print(f"    → {text}")


def print_warning(text):
    # Aviso importante, mas não bloqueia o processo
    print(f"[!] {text}")


def print_error(text):
    # Erro crítico, precisa de atenção
    print(f"[✗] ERRO: {text}")


def run_command(command, shell=False, check=True, capture_output=True):
    # Executa um comando no terminal e retorna o resultado
    try:
        result = subprocess.run(
            command, shell=shell, check=check, capture_output=capture_output, text=True
        )
        return result
    except subprocess.CalledProcessError as e:
        print_error(f"Erro ao executar comando: {e}")
        if e.output:
            print_info(f"Saída: {e.output}")
        if e.stderr:
            print_info(f"Erro: {e.stderr}")
        return None


def get_python_version():
    # Retorna a versão do Python em uso
    return platform.python_version()


def check_resources():
    # Verifica se a pasta resources e o ícone existem, cria se não tiver
    print_step("Verificando recursos necessários...")

    # Verificar pasta resources
    resources_dir = Path("resources")
    if not resources_dir.exists():
        print_warning("Pasta 'resources' não encontrada. Criando...")
        resources_dir.mkdir(exist_ok=True)

    # Verificar ícone
    icon_path = resources_dir / "app_icon.ico"
    if not icon_path.exists():
        print_warning(
            "Ícone não encontrado. Verificando se o script de download está disponível..."
        )
        download_script = Path("download_icons.py")
        if download_script.exists():
            print_info("Executando script de download de ícones...")
            subprocess.run([sys.executable, str(download_script)], check=False)
            if icon_path.exists():
                print_info("Ícones baixados com sucesso!")
            else:
                print_warning("Não foi possível baixar os ícones automaticamente.")
        else:
            print_warning("Script de download de ícones não encontrado.")
    else:
        print_info(f"Ícone encontrado: {icon_path}")

    return icon_path, None


def install_dependencies():
    # Instala as dependências necessárias para rodar e empacotar o projeto
    print_step("Instalando dependências necessárias...")

    # Criar arquivo requirements.txt com versões compatíveis com Python 3.13
    with open("requirements.txt", "w") as f:
        f.write("pyautogui\n")
        f.write("pillow\n")
        f.write("pyinstaller\n")

    # Instalar dependências
    run_command(
        [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=False
    )

    # Verificar se PyInstaller foi instalado
    pyinstaller_check = run_command(
        [sys.executable, "-m", "pip", "show", "pyinstaller"], check=False
    )

    if pyinstaller_check and pyinstaller_check.returncode == 0:
        # Extrair versão do PyInstaller
        for line in pyinstaller_check.stdout.splitlines():
            if line.startswith("Version: "):
                pyinstaller_version = line.split("Version: ")[1].strip()
                print_info(f"PyInstaller versão {pyinstaller_version} instalado.")
                return pyinstaller_version
    else:
        print_error("PyInstaller não foi instalado corretamente.")
        return None


def check_pyarmor():
    # Verifica se o PyArmor está instalado, oferece para instalar se não estiver
    print_step("Verificando disponibilidade do PyArmor...")

    result = run_command([sys.executable, "-m", "pip", "show", "pyarmor"], check=False)

    if result and result.returncode == 0:
        print_info("PyArmor encontrado. Pode ser usado para ofuscação.")
        return True
    else:
        print_warning("PyArmor não encontrado. Ofuscação não será aplicada.")
        install_pyarmor = input("Deseja instalar o PyArmor agora? (s/n): ").lower()
        if install_pyarmor == "s":
            print_info("Instalando PyArmor...")
            result = run_command(
                [sys.executable, "-m", "pip", "install", "pyarmor"], check=False
            )
            if result and result.returncode == 0:
                print_info("PyArmor instalado com sucesso!")
                return True
            else:
                print_warning(
                    "Não foi possível instalar o PyArmor. Continuando sem ofuscação."
                )
        return False


def build_executable(icon_path, cleanup_path, use_pyarmor=False):
    # Gera o executável .exe usando PyInstaller, limpando builds antigos para garantir atualização do ícone
    print_step("Criando executável com PyInstaller...")

    # Nome do arquivo principal
    main_script = "assistente_produtividade.py"
    if not os.path.exists(main_script):
        print_error(f"Arquivo principal {main_script} não encontrado!")
        return False

    # Nome do executável de saída
    output_name = "AssistenteProducao"

    # Limpar dist/build antes do build para garantir que o ícone seja atualizado
    for pasta in ["dist", "build"]:
        if os.path.exists(pasta):
            try:
                import shutil

                shutil.rmtree(pasta)
                print_info(f"Pasta '{pasta}' removida antes do build.")
            except Exception as e:
                print_warning(f"Não foi possível remover a pasta '{pasta}': {e}")

    # Preparar comando PyInstaller
    pyinstaller_cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--name",
        output_name,
        "--onefile",
        "--windowed",
        "--clean",
        f"--icon={icon_path}",
        "--add-data",
        "resources;resources",
        main_script,
    ]

    print_info(
        "Executando comando PyInstaller para gerar o .exe com ícone personalizado..."
    )
    print_info("Comando gerado:")
    print_info(" ".join(str(arg) for arg in pyinstaller_cmd))

    result = run_command(pyinstaller_cmd, check=False)

    if result and result.returncode == 0:
        dist_dir = os.path.join("dist")
        if os.path.exists(dist_dir):
            exe_path = os.path.join(dist_dir, f"{output_name}.exe")
            if os.path.exists(exe_path):
                print_info(f"Executável criado com sucesso: {exe_path}")
                print_info(
                    "Se o ícone do .exe não aparecer, pressione F5 no Explorer ou reinicie o Explorer."
                )
                return True

    print_error("Falha ao criar o executável com PyInstaller.")
    return False


def main():
    print_header("CONSTRUÇÃO DO ASSISTENTE DE PRODUTIVIDADE")

    # Mostra a versão do Python em uso
    python_version = get_python_version()
    print_step(f"Usando Python versão: {python_version}")
    if python_version.startswith("3.13"):
        print_info("Python 3.13 detectado - pode dar ruim em alguns pacotes.")

    # Verifica se os recursos necessários estão presentes
    icon_path, cleanup_path = check_resources()

    # Instala as dependências do projeto
    pyinstaller_version = install_dependencies()
    if not pyinstaller_version:
        print_error("Não foi possível instalar as dependências necessárias.")
        return False

    # PyArmor é opcional, só instala se desejar ofuscação
    use_pyarmor = check_pyarmor()

    # Gera o executável final
    success = build_executable(icon_path, cleanup_path, use_pyarmor)

    if success:
        print_header("PROCESSO CONCLUÍDO COM SUCESSO")
        print_info("O executável foi criado e tá pronto pra usar.")
        print_info("Localização: dist/AssistenteProducao.exe")
    else:
        print_header("PROCESSO CONCLUÍDO COM ERROS")
        print_warning("Revise os erros acima e tenta de novo.")

    return success


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nOperação cancelada pelo usuário.")
    except Exception as e:
        print_error(f"Erro inesperado: {e}")

    # Mantém a janela do CMD aberta após execução para leitura das mensagens
    if not sys.stdout.isatty():
        input("\nPressione ENTER para sair...")
