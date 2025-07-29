import os
import sys
import subprocess
import platform
import shutil
import time
from pathlib import Path

def print_header(text):
    """Imprime um cabeçalho formatado."""
    print("\n" + "=" * 60)
    print(f" {text} ".center(60, "="))
    print("=" * 60 + "\n")

def print_step(text):
    """Imprime um passo do processo."""
    print(f"[+] {text}")

def print_info(text):
    """Imprime uma informação."""
    print(f"    → {text}")

def print_warning(text):
    """Imprime um aviso."""
    print(f"[!] {text}")

def print_error(text):
    """Imprime um erro."""
    print(f"[✗] ERRO: {text}")

def run_command(command, shell=False, check=True, capture_output=True):
    """Executa um comando e retorna o resultado."""
    try:
        result = subprocess.run(
            command, 
            shell=shell, 
            check=check, 
            capture_output=capture_output, 
            text=True
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
    """Retorna a versão do Python."""
    return platform.python_version()

def check_resources():
    """Verifica se os recursos necessários estão disponíveis."""
    print_step("Verificando recursos necessários...")
    
    # Verificar pasta resources
    resources_dir = Path("resources")
    if not resources_dir.exists():
        print_warning("Pasta 'resources' não encontrada. Criando...")
        resources_dir.mkdir(exist_ok=True)
    
    # Verificar ícone
    icon_path = resources_dir / "app_icon.ico"
    if not icon_path.exists():
        print_warning("Ícone não encontrado. Verificando se o script de download está disponível...")
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
    """Instala as dependências necessárias."""
    print_step("Instalando dependências necessárias...")
    
    # Criar arquivo requirements.txt com versões compatíveis com Python 3.13
    with open("requirements.txt", "w") as f:
        f.write("pyautogui\n")
        f.write("pillow\n")
        f.write("pyinstaller\n")

    # Instalar dependências
    result = run_command([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=False)
    
    # Verificar se PyInstaller foi instalado
    pyinstaller_check = run_command([sys.executable, "-m", "pip", "show", "pyinstaller"], check=False)
    
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
    """Verifica se o PyArmor está disponível."""
    print_step("Verificando disponibilidade do PyArmor...")
    
    result = run_command([sys.executable, "-m", "pip", "show", "pyarmor"], check=False)
    
    if result and result.returncode == 0:
        print_info("PyArmor encontrado. Pode ser usado para ofuscação.")
        return True
    else:
        print_warning("PyArmor não encontrado. Ofuscação não será aplicada.")
        install_pyarmor = input("Deseja instalar o PyArmor agora? (s/n): ").lower()
        if install_pyarmor == 's':
            print_info("Instalando PyArmor...")
            result = run_command([sys.executable, "-m", "pip", "install", "pyarmor"], check=False)
            if result and result.returncode == 0:
                print_info("PyArmor instalado com sucesso!")
                return True
            else:
                print_warning("Não foi possível instalar o PyArmor. Continuando sem ofuscação.")
        return False

def build_executable(icon_path, cleanup_path, use_pyarmor=False):
    """Cria o executável usando PyInstaller."""
    print_step("Criando executável com PyInstaller...")
    
    # Nome do arquivo principal
    main_script = "assistente_produtividade.py"
    if not os.path.exists(main_script):
        print_error(f"Arquivo principal {main_script} não encontrado!")
        return False
    
    # Nome do executável de saída
    output_name = "AssistenteProducao"
    
    # Preparar comando PyInstaller
    pyinstaller_cmd = [
        sys.executable, 
        "-m", 
        "PyInstaller",
        "--name", output_name,
        "--onefile",
        "--windowed",
        "--clean",
        f"--icon={icon_path}",
        "--add-data", f"resources;resources"
    ]
    
    # Adicionar arquivo principal
    pyinstaller_cmd.append(main_script)
    
    # Executar PyInstaller
    print_info(f"Executando comando PyInstaller...")
    for i, arg in enumerate(pyinstaller_cmd):
        if i > 2:  # Pular python -m PyInstaller
            print_info(f"  {arg}")
    
    result = run_command(pyinstaller_cmd, check=False)
    
    if result and result.returncode == 0:
        dist_dir = os.path.join("dist")
        if os.path.exists(dist_dir):
            exe_path = os.path.join(dist_dir, f"{output_name}.exe")
            if os.path.exists(exe_path):
                print_info(f"Executável criado com sucesso: {exe_path}")
                return True
    
    print_error("Falha ao criar o executável com PyInstaller.")
    return False

def main():
    print_header("CONSTRUÇÃO DO ASSISTENTE DE PRODUTIVIDADE")
    
    # Verificar versão do Python
    python_version = get_python_version()
    print_step(f"Usando Python versão: {python_version}")
    
    if python_version.startswith('3.13'):
        print_info("Python 3.13 detectado - alguns pacotes podem ter compatibilidade limitada.")
    
    # Verificar recursos
    icon_path, cleanup_path = check_resources()
    
    # Instalar dependências
    pyinstaller_version = install_dependencies()
    if not pyinstaller_version:
        print_error("Não foi possível instalar as dependências necessárias.")
        return False
    
    # Verificar PyArmor (opcional)
    use_pyarmor = check_pyarmor()
    
    # Criar executável
    success = build_executable(icon_path, cleanup_path, use_pyarmor)
    
    if success:
        print_header("PROCESSO CONCLUÍDO COM SUCESSO")
        print_info("O executável foi criado e está pronto para distribuição.")
        print_info("Localização: dist/AssistenteProducao.exe")
    else:
        print_header("PROCESSO CONCLUÍDO COM ERROS")
        print_warning("Revise os erros acima e tente novamente.")
    
    return success

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nOperação cancelada pelo usuário.")
    except Exception as e:
        print_error(f"Erro inesperado: {e}")
    
    # Manter a janela aberta
    if not sys.stdout.isatty():  # Se estiver em uma janela CMD
        input("\nPressione ENTER para sair...")
