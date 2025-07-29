
# Assistente de Produtividade Digital

Este projeto é um assistente digital desenvolvido para evitar que o computador entre em modo inativo (idle) no Windows. Ele simula atividades de teclado de forma segura e configurável, sendo ideal para manter a tela ativa, evitar o bloqueio automático, prevenir a desconexão de sistemas e manter sessões funcionando durante o trabalho remoto. É especialmente útil para quem precisa deixar scripts rodando em segundo plano, mesmo em ambientes com políticas que desligam a tela automaticamente, ou para não aparecer como ausente em ferramentas como Microsoft Teams e outros mensageiros corporativos.

## Funcionalidades

- Interface gráfica (Tkinter)
- Simulação de teclas inofensivas (F15, Shift, Alt, Ctrl, Caps Lock)
- Intervalo e duração configuráveis
- Ícones e feedback visual
- Threading seguro para não travar a interface
- Totalmente configurável pelo usuário
- Compatível com Windows

## Estrutura do Projeto

```
assist-anti-idle-bot/
├── assistente_produtividade.py   # Código principal da aplicação
├── requirements.txt              # Dependências do projeto
├── AssistenteProducao.spec       # Configuração do PyInstaller para gerar o executável
├── build_exe.py                  # (Opcional) Script auxiliar para build
├── resources/                    # Ícones e imagens usados na interface
│   ├── app_icon.ico
│   ├── error.png
│   ├── pause.png
│   ├── play.png
│   └── success.png
└── ...
```

## Instalação e Execução

1. Clone o repositório ou baixe os arquivos.
2. Instale as dependências do projeto:
   ```bash
   pip install -r requirements.txt
   ```
3. Execute o programa:
   ```bash
   python assistente_produtividade.py
   ```

## Como gerar o executável (.exe)

Você pode transformar o programa em um executável Windows usando o PyInstaller. Isso permite rodar o assistente em qualquer máquina Windows sem precisar instalar Python ou dependências manualmente.

### Passo a passo:

1. Instale o PyInstaller (se ainda não tiver):
   ```bash
   pip install pyinstaller
   ```
2. Gere o executável usando o arquivo de especificação já pronto:
   ```bash
   python build_exe.py
   ```
   - O arquivo `.spec` já está configurado para incluir a pasta `resources` e o ícone do app.
   - O executável será gerado na pasta `dist/AssistenteProducao/`.
   - Todos os recursos necessários (imagens, ícones) serão incluídos automaticamente.

#### Dicas para build
- Se alterar o nome do script principal ou adicionar recursos, ajuste o arquivo `.spec`.
- Para atualizar dependências, edite o `requirements.txt`.
- O parâmetro `console=False` faz com que o executável rode sem abrir um terminal junto.

## Dependências

O projeto depende das seguintes bibliotecas (listadas em `requirements.txt`):
- tkinter (nativo do Python)
- pyautogui
- pillow

## Uso

1. Abra o programa e configure o intervalo entre atividades (em segundos).
2. Escolha quais teclas simular (F15, Shift, Alt, Ctrl, Caps Lock).
3. Clique em "Iniciar Assistente" para ativar. O status mudará para "Ativo".
4. Para pausar, clique em "Pausar Assistente".
5. O programa pode ser minimizado e continuará funcionando.

### Observações
- O uso de teclas inofensivas (como F15) garante que não haja impacto no seu trabalho, mas só ative quando estiver AFK. Foge do propósito deixar ele ativo enquanto usa a máquina.
- O assistente não interfere em programas abertos, apenas simula atividade para evitar bloqueio de tela.
- O programa foi testado no Windows 10 e 11.

