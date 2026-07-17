import tkinter as tk
from tkinter import messagebox
import subprocess
import sys
import os

PIX_PARTICULARES = r"C:\Users\Usuario\Desktop\Teste\Mastellini\Baixa_Recebimento\PIX_PARTICULARES.py"
Cartao_Particulares = r"C:\Users\Usuario\Desktop\Teste\Mastellini\Baixa_Recebimento\Cartao_Particulares.py"
Deposito_Caixa_Capivari = r"C:\Users\Usuario\Desktop\Teste\Mastellini\Baixa_Recebimento\Deposito_Caixa_Capivari.py"

def rodar_script(caminho, nome_script):
    if not os.path.exists(caminho):
        messagebox.showerror("Erro", f"Arquivo não encontrado:\n{caminho}")
        return
    try:
        subprocess.Popen([sys.executable, caminho])
        status_label.config(text=f"'{nome_script}' iniciado ✅")
    except Exception as e:
        messagebox.showerror("Erro ao executar", str(e))
        
        
# -------------- Interface --------------
janela = tk.Tk()
janela.title("Painel de Automações")
janela.geometry("300x220")
janela.resizable(False, False)

titulo = tk.Label(janela, text="Escolha a automação", font=("Segoe UI", 13, "bold"))
titulo.pack(pady=15)

btn1 = tk.Button(
    janela, text="Pix Particulares", width=25, height=2,
    command=lambda: rodar_script(PIX_PARTICULARES, "Pix Particulares")
)
btn1.pack(pady=5)

btn2 = tk.Button(
    janela, text="Cartão Particulares", width=25, height=2,
    command=lambda: rodar_script(Cartao_Particulares, "Cartão Particulares")
)
btn2.pack(pady=5)

btn3 = tk.Button(
    janela, text="Depósito Caixa Capivari", width=25, height=2,
    command=lambda: rodar_script(Deposito_Caixa_Capivari, "Depósito Caixa Capivari")
)
btn3.pack(pady=5)

status_label = tk.Label(janela, text="", fg="green")
status_label.pack(pady=10)

janela.mainloop()