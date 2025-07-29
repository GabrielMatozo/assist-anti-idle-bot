import tkinter as tk
from tkinter import ttk, messagebox
import time
import threading
import pyautogui
import random
import subprocess
import os
import sys
import shutil  # Adicionando importação do módulo shutil
from PIL import Image, ImageTk

class AssistenteDigital:
    def __init__(self, root):
        self.root = root
        self.root.title("Assistente de Produtividade Digital")
        self.root.geometry("550x650")  # Reduzido de 750 para 650 pixels na altura
        self.root.resizable(True, True)  # Permitir redimensionamento
        
        # Definir cores do tema (tema escuro)
        self.colors = {
            "primary": "#1e88e5",            # Azul principal
            "secondary": "#0d47a1",          # Azul mais escuro
            "background": "#121212",         # Fundo escuro
            "card_bg": "#1e1e1e",            # Fundo dos cards
            "text": "#ffffff",               # Texto principal
            "text_secondary": "#b0b0b0",     # Texto secundário
            "success": "#00c853",            # Verde sucesso
            "error": "#ff5252",              # Vermelho erro
            "border": "#333333"              # Bordas
        }

        # Aplicar estilos personalizados
        self.apply_custom_styles()
        
        # Carregar ícone da aplicação
        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                              "resources", "app_icon.ico")
        if os.path.exists(icon_path):
            try:
                self.root.iconbitmap(icon_path)
            except tk.TclError:
                pass

        # Configurar a janela principal
        self.root.configure(background=self.colors["background"])
        
        # Carregar ícones
        self.icons = {}
        self.load_icons()
        
        self.running = False
        self.thread = None
        self.last_activity_time = 0
        
        # Interface principal - usar diretamente um frame na janela principal
        self.main_frame = ttk.Frame(self.root, style='TFrame')
        self.main_frame.pack(pady=15, padx=15, fill=tk.BOTH, expand=True)
        
        # Título e Status
        header_frame = ttk.Frame(self.main_frame, style='TFrame')
        header_frame.pack(fill=tk.X, pady=(0, 15))
        
        title_label = ttk.Label(header_frame, text="Assistente de Produtividade", 
                              font=("Arial", 14, "bold"), 
                              foreground=self.colors["primary"],
                              style='TLabel')
        title_label.pack(anchor="w")
        
        self.status_frame = ttk.Frame(header_frame, style='TFrame')
        self.status_frame.pack(fill=tk.X, pady=(5, 0))
        
        status_text = ttk.Label(self.status_frame, text="Status:", font=("Arial", 10), 
                              style='TLabel')
        status_text.pack(side=tk.LEFT)
        
        self.status_label = ttk.Label(self.status_frame, text="Inativo", 
                                    font=("Arial", 10, "bold"), 
                                    foreground=self.colors["error"], style='TLabel')
        self.status_label.pack(side=tk.LEFT, padx=(5, 0))
        
        # Frame para botões
        button_frame = ttk.Frame(self.main_frame, style='TFrame')
        button_frame.pack(fill=tk.X, pady=10)
        
        self.start_button = ttk.Button(button_frame, text=" Iniciar Assistente", 
                                     command=self.start_activity, width=18, style='TButton')
        self.start_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.stop_button = ttk.Button(button_frame, text=" Pausar Assistente", 
                                    command=self.stop_activity, width=18, style='TButton', 
                                    state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT)
        
        # Aplicar ícones aos botões
        if 'start' in self.icons:
            self.start_button.image = self.icons['start']
            self.start_button.configure(image=self.icons['start'], compound=tk.LEFT)
        
        if 'stop' in self.icons:
            self.stop_button.image = self.icons['stop']
            self.stop_button.configure(image=self.icons['stop'], compound=tk.LEFT)
        
        # Frame para configurações
        config_frame = ttk.LabelFrame(self.main_frame, text=" Configurações ", padding=(15, 10))
        config_frame.pack(fill=tk.X, pady=10)
        
        # Intervalo
        interval_frame = ttk.Frame(config_frame, style='Card.TFrame')
        interval_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(interval_frame, text="Intervalo entre atividades:", 
                style='Card.TLabel').pack(side=tk.LEFT)
        
        # Corrigindo estilo da entrada para melhor visibilidade
        vcmd = (self.root.register(self.validate_numeric_input), '%P')
        self.interval_entry = tk.Entry(interval_frame, width=8, font=("Arial", 10),
                                     foreground=self.colors["text"], 
                                     background=self.colors["card_bg"],
                                     insertbackground=self.colors["text"],  # Cursor visível
                                     validate="key", validatecommand=vcmd,
                                     relief=tk.FLAT, bd=2,
                                     highlightbackground=self.colors["border"],
                                     highlightcolor=self.colors["primary"],
                                     highlightthickness=1)
        self.interval_entry.insert(0, "60")
        self.interval_entry.pack(side=tk.LEFT, padx=10)
        
        ttk.Label(interval_frame, text="segundos", style='Card.TLabel').pack(side=tk.LEFT)
        
        # Opções de atividade
        activity_label = ttk.Label(config_frame, text="Ações a realizar:", 
                                 font=("Arial", 10, "bold"), style='Card.TLabel')
        activity_label.pack(fill=tk.X, pady=(15, 5), anchor="w")
        
        self.use_caps_var = tk.BooleanVar(value=True)
        self.use_keys_var = tk.BooleanVar(value=True)
        
        ttk.Checkbutton(config_frame, text="Alternar Caps Lock", 
                       variable=self.use_caps_var, style='TCheckbutton').pack(anchor="w", pady=3)
        ttk.Checkbutton(config_frame, text="Simular pressionamento de teclas", 
                       variable=self.use_keys_var, style='TCheckbutton').pack(anchor="w", pady=3)
        
        # NOVA SEÇÃO: Configurações de Teclas
        keys_config_frame = ttk.LabelFrame(self.main_frame, text=" Configurações de Teclas ", 
                                         padding=(15, 10))
        keys_config_frame.pack(fill=tk.X, pady=10)
        
        # Opções de teclas para simular
        keys_option_frame = ttk.Frame(keys_config_frame, style='Card.TFrame')
        keys_option_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(keys_option_frame, text="Selecione as teclas a simular:", 
                style='Card.TLabel').pack(anchor=tk.W, pady=3)
        
        # Checkboxes para teclas
        self.use_f15_var = tk.BooleanVar(value=True)
        self.use_shift_var = tk.BooleanVar(value=True)
        self.use_alt_var = tk.BooleanVar(value=True)
        self.use_ctrl_var = tk.BooleanVar(value=False)
        
        ttk.Checkbutton(keys_option_frame, text="Tecla F15", 
                       variable=self.use_f15_var, style='TCheckbutton').pack(anchor=tk.W, padx=20, pady=3)
        ttk.Checkbutton(keys_option_frame, text="Tecla Shift", 
                       variable=self.use_shift_var, style='TCheckbutton').pack(anchor=tk.W, padx=20, pady=3)
        ttk.Checkbutton(keys_option_frame, text="Tecla Alt", 
                       variable=self.use_alt_var, style='TCheckbutton').pack(anchor=tk.W, padx=20, pady=3)
        ttk.Checkbutton(keys_option_frame, text="Tecla Ctrl", 
                       variable=self.use_ctrl_var, style='TCheckbutton').pack(anchor=tk.W, padx=20, pady=3)
        
        # Tempo de segurar tecla
        key_hold_frame = ttk.Frame(keys_config_frame, style='Card.TFrame')
        key_hold_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(key_hold_frame, text="Tempo segurando a tecla (segundos):", 
                style='Card.TLabel').pack(side=tk.LEFT)
        
        # Definir validação para entrada de duração
        vcmd_duration = (self.root.register(self.validate_duration_input), '%P')
        
        self.key_hold_entry = tk.Entry(key_hold_frame, width=5, font=("Arial", 10),
                                     foreground=self.colors["text"], 
                                     background=self.colors["card_bg"],
                                     insertbackground=self.colors["text"],
                                     validate="key", validatecommand=vcmd_duration,
                                     relief=tk.FLAT, bd=2,
                                     highlightbackground=self.colors["border"],
                                     highlightcolor=self.colors["primary"],
                                     highlightthickness=1)
        self.key_hold_entry.insert(0, "0.1")
        self.key_hold_entry.pack(side=tk.LEFT, padx=10)
        
        # Informações de rodapé
        footer_frame = ttk.Frame(self.main_frame, style='TFrame')
        footer_frame.pack(fill=tk.X, pady=(15, 0))
        
        info_label = ttk.Label(footer_frame, 
                             text="Dica: Ajuste as configurações conforme a necessidade do seu ambiente.",
                             font=("Arial", 9), style='Secondary.TLabel')
        info_label.pack(side=tk.LEFT)
        
        # Encerrar a thread quando a janela for fechada
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        
        # Adicionar verificação periódica para garantir que o thread está rodando
        self.check_thread_interval = 5000  # 5 segundos
        self.check_thread_id = None
    
    def apply_custom_styles(self):
        """Aplica estilos personalizados a elementos nativos do tkinter"""
        # Configurar cores padrão para widgets tk (não-ttk)
        self.root.option_add("*Text.background", self.colors["card_bg"])
        self.root.option_add("*Text.foreground", self.colors["text"])
        self.root.option_add("*Text.selectBackground", self.colors["primary"])
        self.root.option_add("*Text.selectForeground", self.colors["text"])
        self.root.option_add("*Entry.background", self.colors["card_bg"])
        self.root.option_add("*Entry.foreground", self.colors["text"])
        self.root.option_add("*Entry.selectBackground", self.colors["primary"])
        self.root.option_add("*Entry.selectForeground", self.colors["text"])
        
        # Configurar estilo ttk
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Configurar estilos personalizados para tema escuro
        self.style.configure('TFrame', background=self.colors["background"])
        self.style.configure('Card.TFrame', background=self.colors["card_bg"], 
                          relief="flat", borderwidth=1)
        
        self.style.configure('TLabel', background=self.colors["background"], 
                          foreground=self.colors["text"])
        self.style.configure('Card.TLabel', background=self.colors["card_bg"], 
                          foreground=self.colors["text"])
        self.style.configure('Secondary.TLabel', background=self.colors["background"], 
                          foreground=self.colors["text_secondary"])
        
        self.style.configure('TButton', font=('Arial', 10), 
                          background=self.colors["primary"], foreground=self.colors["text"],
                          borderwidth=0, focusthickness=0)
        self.style.map('TButton', 
                    background=[('active', self.colors["secondary"])],
                    foreground=[('active', self.colors["text"])])
        
        self.style.configure('TCheckbutton', background=self.colors["card_bg"], 
                          foreground=self.colors["text"])
        self.style.map('TCheckbutton', 
                    background=[('active', self.colors["card_bg"])],
                    foreground=[('active', self.colors["text"])])
        
        # Configurar bordas para elementos
        self.style.configure('TLabelframe', background=self.colors["background"], 
                          foreground=self.colors["text"], borderwidth=1, 
                          relief="solid", bordercolor=self.colors["border"])
        self.style.configure('TLabelframe.Label', background=self.colors["background"], 
                           foreground=self.colors["text"])
        
        # Configurar a barra de progresso
        self.style.configure("TProgressbar", 
                          background=self.colors["primary"],
                          troughcolor=self.colors["card_bg"], 
                          borderwidth=0)
        
    def validate_numeric_input(self, value):
        """Valida entrada para aceitar apenas números inteiros positivos"""
        if value == "":
            return True
        try:
            val = int(value)
            return val >= 0
        except ValueError:
            return False
    
    def validate_duration_input(self, value):
        """Valida entrada para aceitar números decimais positivos"""
        if value == "":
            return True
        try:
            val = float(value)
            return val >= 0 and len(value) <= 4
        except ValueError:
            return False

    def load_icons(self):
        """Carrega os ícones da pasta resources"""
        resources_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "resources")
        
        icon_files = {
            'start': 'play.png',
            'stop': 'pause.png',
            'success': 'success.png',
            'error': 'error.png'
        }
        
        for icon_name, icon_file in icon_files.items():
            icon_path = os.path.join(resources_path, icon_file)
            try:
                if os.path.exists(icon_path):
                    img = Image.open(icon_path)
                    img = img.resize((16, 16), Image.LANCZOS)
                    self.icons[icon_name] = ImageTk.PhotoImage(img)
            except Exception:
                pass

    def activity_loop(self):
        try:
            interval = int(self.interval_entry.get())
            # Remover o limite mínimo de 20 segundos para permitir valores menores
            if interval <= 0:
                interval = 1  # Garantir pelo menos 1 segundo
        except ValueError:
            interval = 60
            
        while self.running:
            try:
                # Registrar o tempo da última atividade
                self.last_activity_time = time.time()
                
                # Executar ações ativadas
                if self.use_caps_var.get():
                    pyautogui.press('capslock')
                    time.sleep(0.5)
                    pyautogui.press('capslock')
                
                if self.use_keys_var.get():
                    self.press_harmless_keys()
                
                # Adicionar um pequeno elemento aleatório ao intervalo (±10%)
                variation = random.uniform(-0.1, 0.1) * interval
                wait_time = max(0.5, interval + variation)  # Permitir intervalo mínimo de 0.5 segundos
                
                # Substituir o loop por uma única chamada de sleep para evitar granularidade de 1 segundo
                # Também verificar periodicamente se ainda estamos rodando
                start_time = time.time()
                elapsed = 0
                
                while elapsed < wait_time and self.running:
                    time.sleep(0.1)  # Verificação a cada 100ms
                    elapsed = time.time() - start_time
                    
            except Exception as e:
                print(f"Erro no loop de atividade: {e}")
                time.sleep(1)
    
    def press_harmless_keys(self):
        """Pressionar teclas que não afetam o trabalho, usando as opções configuradas"""
        try:
            # Obter tempo de segurar tecla configurado
            try:
                hold_time = float(self.key_hold_entry.get())
            except ValueError:
                hold_time = 0.1
            
            # Limitar tempo para evitar valores inválidos
            hold_time = max(0.05, min(1.0, hold_time))
            
            # Criar lista de teclas ativadas
            active_keys = []
            if self.use_f15_var.get():
                active_keys.append("f15")
            if self.use_shift_var.get():
                active_keys.append("shift")
            if self.use_alt_var.get():
                active_keys.append("alt")
            if self.use_ctrl_var.get():
                active_keys.append("ctrl")
            
            # Se nenhuma tecla estiver selecionada, retornar
            if not active_keys:
                return
            
            # Escolher uma tecla aleatória da lista ativada
            key = random.choice(active_keys)
            
            # Pressionar e soltar a tecla escolhida
            pyautogui.keyDown(key)
            time.sleep(hold_time)
            pyautogui.keyUp(key)
        except Exception as e:
            print(f"Erro ao pressionar teclas: {e}")
    
    def check_thread_active(self):
        """Verifica se a thread está ativa e a reinicia se necessário"""
        if self.running:
            current_time = time.time()
            # Se não houve atividade nos últimos 30 segundos e thread deve estar rodando
            if current_time - self.last_activity_time > 30 and self.thread:
                print("Thread de atividade inativa. Reiniciando...")
                self.restart_thread()
            
            # Verificar novamente após o intervalo definido
            self.check_thread_id = self.root.after(self.check_thread_interval, self.check_thread_active)
    
    def restart_thread(self):
        """Reinicia a thread de atividade"""
        # Tentar parar a thread atual
        if self.thread and self.thread.is_alive():
            self.thread.join(0.1)
        
        # Criar uma nova thread
        self.thread = threading.Thread(target=self.activity_loop)
        self.thread.daemon = True
        self.thread.start()
    
    def start_activity(self):
        self.running = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.status_label.config(text="Ativo", foreground=self.colors["success"])
        
        self.last_activity_time = time.time()
        self.thread = threading.Thread(target=self.activity_loop)
        self.thread.daemon = True
        self.thread.start()
        
        # Iniciar verificação periódica da thread
        self.check_thread_id = self.root.after(self.check_thread_interval, self.check_thread_active)
    
    def stop_activity(self):
        self.running = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.status_label.config(text="Inativo", foreground=self.colors["error"])
        
        # Cancelar a verificação periódica
        if self.check_thread_id:
            self.root.after_cancel(self.check_thread_id)
            self.check_thread_id = None
    
    def on_close(self):
        self.running = False
        # Cancelar a verificação periódica
        if self.check_thread_id:
            self.root.after_cancel(self.check_thread_id)
        
        if self.thread and self.thread.is_alive():
            self.thread.join(1)
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = AssistenteDigital(root)
    root.mainloop()
