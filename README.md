# Assistente Anti-Idle

App desktop que simula atividade do usuário (teclado + mouse) para evitar bloqueio/standby. Interface escura com CustomTkinter.

## Funcionalidades

- Alternar Caps Lock
- Simular teclas inofensivas (F15, Shift, Alt, Ctrl)
- Mouse jiggler com intensidade configurável
- Intervalo e duração configuráveis
- Tema escuro nativo
- Suporte Linux e Windows

## Estrutura

```
src/
├── main.py          # entry point
├── app.py           # UI (CustomTkinter)
└── core/
    ├── activity.py  # loop de atividade
    ├── keys.py      # simulação de teclas
    └── mouse.py     # mouse jiggler
build_exe.py         # build PyInstaller
requirements.txt     # dependências
resources/
└── app_icon.ico
```

## Instalação e Uso

```bash
pip install -r requirements.txt
python -m src.main
```

## Build executável

```bash
python build_exe.py
```

Gera `dist/AssistenteAntiIdle` (Linux) ou `dist/AssistenteAntiIdle.exe` (Windows).

## Dependências

- pyautogui
- pillow
- customtkinter
- pyinstaller (opcional, só para build)
