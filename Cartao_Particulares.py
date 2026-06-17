"""
CARTAO_PARTICULARES - Automação de teclado convertida de macro XML
Nome original: CARTAO 2

Dependência:
    pip install pyautogui

Como usar:
    1. Coloque o valor desejado na área de transferência (Ctrl+C) ANTES de rodar.
    2. Execute o script.
    3. Você tem 3 segundos para clicar na janela/campo desejado antes de começar.
"""

import time
import pyautogui

# Tempo de pausa entre cada tecla (em segundos). Original: 50 ms.
DELAY = 0.05

# -----------------------------------------------------------------------
# Configurações de segurança do pyautogui
# -----------------------------------------------------------------------
pyautogui.PAUSE = 0.05       # pausa mínima entre ações
pyautogui.FAILSAFE = True    # mova o mouse para o canto superior esquerdo para parar

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
print("Executando macro CARTAO_PARTICULARES...")

# -----------------------------------------------------------------------
# Sequência da macro
# -----------------------------------------------------------------------

# 1. Digita "CARTOES PARTICULARES" num campo de busca/pesquisa
digitar("CARTOES PARTICULARES")

# 2. TAB para avançar o foco + desce 3 opções na lista e confirma com ENTER
pressionar("tab")
pressionar("down")
pressionar("down")
pressionar("down")
pressionar("enter")

# 3. TAB para próximo campo, digita "CART" (início de "CARTÃO" ou similar)
pressionar("tab")
digitar("CART")

# 4. ENTER para confirmar + desce uma opção e confirma
pressionar("enter")
pressionar("down")
pressionar("enter")

# 5. TAB para campo seguinte + Ctrl+V (cola o valor da área de transferência)
pressionar("tab")
hotkey("ctrl", "v")   # 1º Ctrl+V

# 6. Avança 5 campos com TAB + Ctrl+V novamente
pressionar("tab")
pressionar("tab")
pressionar("tab")
pressionar("tab")
pressionar("tab")
hotkey("ctrl", "v")   # 2º Ctrl+V

# 7. TAB + Ctrl+V mais uma vez
pressionar("tab")
hotkey("ctrl", "v")   # 3º Ctrl+V

# 8. Avança 4 campos com TAB + ENTER para confirmar/finalizar
pressionar("tab")
pressionar("tab")
pressionar("tab")
pressionar("tab")
pressionar("enter")

print("Macro concluída com sucesso!")