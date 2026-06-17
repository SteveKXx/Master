import time
import pyautogui

DELAY = 0.05  # Tempo de espera entre ações (em segundos)

pyautogui.PAUSE = 0.05
pyautogui.FAILSAFE = True

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
    
print("Iniciando em 3 segundos... clique na janela de destino!")
for i in range(3, 0, -1):
    print(f"  {i}...")
    time.sleep(1)
print("Executando macro DEPOSITO_CAIXA_CAPIVARI...")

digitar("DEPOSITO CAIXA CAPIVARI")
pressionar("tab")
for _ in range(3):
    pressionar("down")
pressionar("enter")

pressionar("tab")
digitar("CX $$ CAP")
pressionar("enter")
pressionar("down")
pressionar("enter")

pressionar("tab")
hotkey("ctrl", "v")

for _ in range(5):
    pressionar("tab")
hotkey("ctrl", "v")

pressionar("tab")
hotkey("ctrl", "v")

for _ in range(4):
    pressionar("tab")
pressionar("enter")

pressionar("tab")
pressionar("space")

pyautogui.keyDown("shift")
for _ in range(7):
    pressionar("tab")
pyautogui.keyUp("shift")

print("Macro concluída com sucesso!")