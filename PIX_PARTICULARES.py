"""
PIX_PARTICULARES - Automação de teclado convertida de macro XML
Nome original: PIX 4

Dependência:
    pip install pyautogui

Como usar:
    1. Coloque o valor da chave PIX na área de transferência (Ctrl+C) ANTES de rodar.
    2. Execute o script.
    3. Você tem 3 segundos para clicar na janela/campo desejado antes de começar.
"""

import time
import pyautogui

# Tempo de pausa entre cada tecla (em segundos). Original: 60 ms.
DELAY = 0.06

# -----------------------------------------------------------------------
# Configurações de segurança do pyautogui
# -----------------------------------------------------------------------
pyautogui.PAUSE = 0.05          # pausa mínima entre ações
pyautogui.FAILSAFE = True       # mova o mouse para o canto superior esquerdo para parar

def pressionar(tecla: str) -> None:
    """Pressiona e solta uma tecla com o delay configurado."""
    pyautogui.press(tecla)
    time.sleep(DELAY)

def digitar(texto: str) -> None:
    """Digita um texto caractere por caractere com o delay configurado."""
    pyautogui.write(texto, interval=DELAY)

def hotkey(*teclas) -> None:
    """Executa uma combinação de teclas (ex.: Ctrl+V)."""
    pyautogui.hotkey(*teclas)
    time.sleep(DELAY)

# -----------------------------------------------------------------------
# Contagem regressiva para o usuário posicionar a janela
# -----------------------------------------------------------------------
print("Iniciando em 3 segundos... clique na janela de destino!")
for i in range(3, 0, -1):
    print(f"  {i}...")
    time.sleep(1)
print("Executando macro PIX_PARTICULARES...")

# -----------------------------------------------------------------------
# Sequência da macro
# -----------------------------------------------------------------------

# 1. Digita "PIX PARTICULARES" num campo de busca/pesquisa
digitar("PIX PARTICULARES")

# 2. TAB para avançar o foco + ENTER para confirmar/pesquisar
pressionar("tab")
pressionar("enter")

# 3. Desce duas opções na lista e confirma
pressionar("down")
pressionar("down")
pressionar("enter")

# 4. TAB para próximo campo, digita "TRA" (início de "TRANSFERÊNCIA" ou similar)
pressionar("tab")
digitar("TRA")

# 5. ENTER para confirmar + desce uma opção e confirma
pressionar("enter")
pressionar("down")
pressionar("enter")

# 6. TAB para campo seguinte + Ctrl+V (cola chave PIX / valor da área de transferência)
pressionar("tab")
hotkey("ctrl", "v")   # 1º Ctrl+V

# 7. Avança 5 campos com TAB + Ctrl+V novamente
pressionar("tab")
pressionar("tab")
pressionar("tab")
pressionar("tab")
pressionar("tab")
hotkey("ctrl", "v")   # 2º Ctrl+V

# 8. TAB + Ctrl+V mais uma vez
pressionar("tab")
hotkey("ctrl", "v")   # 3º Ctrl+V

# 9. Avança 4 campos com TAB + ENTER para confirmar
pressionar("tab")
pressionar("tab")
pressionar("tab")
pressionar("tab")
pressionar("enter")

# 10. TAB + SPACE (marca/desmarca um checkbox ou botão de rádio)
pressionar("tab")
pressionar("space")

# 11. Shift+TAB (volta um campo) seguido de 7 TABs para avançar
#     Nota: o XML mostra Shift pressionado, depois 7 TABs e Shift solto —
#     equivale a Shift+TAB (foco anterior) e depois 6 TABs normais.
pyautogui.keyDown("shift")
pressionar("tab")   # Shift+TAB = volta um campo
pressionar("tab")   # Shift+TAB = volta um campo
pressionar("tab")   # Shift+TAB = volta um campo
pressionar("tab")   # Shift+TAB = volta um campo
pressionar("tab")   # Shift+TAB = volta um campo
pressionar("tab")   # Shift+TAB = volta um campo
pressionar("tab")   # Shift+TAB = volta um campo
pyautogui.keyUp("shift")

print("Macro concluída com sucesso!")