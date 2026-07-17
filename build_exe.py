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

    icon_path = resources_dir / "app_icon.ico"
    if icon_path.exists():
        print_info(f"Ícone encontrado: {icon_path}")
    else:
        print_warning(f"Ícone não encontrado: {icon_path}")

    return icon_path


def install_dependencies():
    # Instala as dependências necessárias para rodar e empacotar o projeto
    print_step("Instalando dependências necessárias...")

    if not os.path.exists("requirements.txt"):
        print_error("requirements.txt não encontrado!")
        return None

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
    print_step("Verificando disponibilidade do PyArmor...")

    result = run_command([sys.executable, "-m", "pip", "show", "pyarmor"], check=False)

    if result and result.returncode == 0:
        print_info("PyArmor encontrado. Pode ser usado para ofuscação.")
    else:
        print_warning("PyArmor não encontrado. Continuando sem ofuscação.")


def build_executable(icon_path):
    print_step("Criando executável com PyInstaller...")

    # Nome do arquivo principal
    main_script = "src/main.py"
    if not os.path.exists(main_script):
        print_error(f"Arquivo principal {main_script} não encontrado!")
        return False

    # Nome do executável de saída
    output_name = "AssistenteAntiIdle"

    # Limpar dist/build antes do build para garantir que o ícone seja atualizado
    for pasta in ["dist", "build"]:
        if os.path.exists(pasta):
            try:
                import shutil

                shutil.rmtree(pasta)
                print_info(f"Pasta '{pasta}' removida antes do build.")
            except Exception as e:
                print_warning(f"Não foi possível remover a pasta '{pasta}': {e}")

    # Separador de path para --add-data: ; no Windows, : no Linux/Mac
    sep = ";" if os.name == "nt" else ":"

    pyinstaller_cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--name",
        output_name,
        "--onefile",
        "--clean",
        f"--icon={icon_path}",
        "--add-data",
        f"resources{sep}resources",
        "--add-data",
        f"src{sep}src",
        main_script,
    ]
    if os.name == "nt":
        pyinstaller_cmd.insert(7, "--windowed")

    print_info(
        "Executando PyInstaller..."
    )
    print_info("Comando gerado:")
    print_info(" ".join(str(arg) for arg in pyinstaller_cmd))

    result = run_command(pyinstaller_cmd, check=False)

    if result and result.returncode == 0:
        dist_dir = os.path.join("dist")
        if os.path.exists(dist_dir):
            ext = ".exe" if os.name == "nt" else ""
            exe_path = os.path.join(dist_dir, f"{output_name}{ext}")
            if os.path.exists(exe_path):
                print_info(f"Executável criado com sucesso: {exe_path}")
                return True

    print_error("Falha ao criar o executável com PyInstaller.")
    return False


def main():
    print_header("CONSTRUÇÃO DO ASSISTENTE ANTI-IDLE")

    # Mostra a versão do Python em uso
    python_version = get_python_version()
    print_step(f"Usando Python versão: {python_version}")
    if python_version.startswith("3.13"):
        print_info("Python 3.13 detectado - pode dar ruim em alguns pacotes.")

    icon_path = check_resources()
    pyinstaller_version = install_dependencies()
    if not pyinstaller_version:
        print_error("Não foi possível instalar as dependências necessárias.")
        return False

    check_pyarmor()
    success = build_executable(icon_path)

    if success:
        print_header("PROCESSO CONCLUÍDO COM SUCESSO")
        print_info("O executável foi criado e tá pronto pra usar.")
        ext = ".exe" if os.name == "nt" else ""
        print_info(f"Localização: dist/AssistenteAntiIdle{ext}")
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

    if os.name == "nt" and not sys.stdout.isatty():
        input("\nPressione ENTER para sair...")
