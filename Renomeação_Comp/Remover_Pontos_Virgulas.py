import os
import re
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext


# ─────────────────────────────────────────────
#  Lógica de renomeação
# ─────────────────────────────────────────────

def limpar_nome(nome_sem_extensao: str) -> str:
    """Substitui pontos e vírgulas por espaços no nome."""
    resultado = nome_sem_extensao.replace(".", " ").replace(",", " ")
    return re.sub(r" {2,}", " ", resultado).strip()


def processar_pasta(pasta: str, simular: bool, log_fn):
    arquivos_pdf = [
        f for f in os.listdir(pasta)
        if f.lower().endswith(".pdf") and os.path.isfile(os.path.join(pasta, f))
    ]

    if not arquivos_pdf:
        log_fn("⚠️  Nenhum arquivo PDF encontrado na pasta.\n")
        return 0, 0

    renomeados = 0
    ignorados = 0

    for nome_arquivo in sorted(arquivos_pdf):
        nome_sem_ext, extensao = os.path.splitext(nome_arquivo)
        novo_nome_sem_ext = limpar_nome(nome_sem_ext)
        novo_nome = novo_nome_sem_ext + extensao

        if novo_nome == nome_arquivo:
            log_fn(f"✅ Sem alteração: {nome_arquivo}\n")
            ignorados += 1
            continue

        caminho_antigo = os.path.join(pasta, nome_arquivo)
        caminho_novo   = os.path.join(pasta, novo_nome)

        log_fn(f"DE:   {nome_arquivo}\n")
        log_fn(f"PARA: {novo_nome}\n")

        if os.path.exists(caminho_novo):
            log_fn("⚠️  Destino já existe, pulando.\n\n")
            ignorados += 1
            continue

        if not simular:
            os.rename(caminho_antigo, caminho_novo)
            log_fn("✔️  Renomeado!\n\n")
        else:
            log_fn("🔵 (simulação)\n\n")

        renomeados += 1

    return renomeados, ignorados


# ─────────────────────────────────────────────
#  Interface gráfica
# ─────────────────────────────────────────────

class App:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Renomeador de PDFs")
        self.root.geometry("700x500")
        self.root.resizable(True, True)
        self.pasta_var = tk.StringVar()

        self._build_ui()

    def _build_ui(self):
        # ── Linha de seleção de pasta ──
        frame_pasta = tk.Frame(self.root, pady=10, padx=10)
        frame_pasta.pack(fill="x")

        tk.Label(frame_pasta, text="Pasta:").pack(side="left")

        entry = tk.Entry(frame_pasta, textvariable=self.pasta_var, width=55)
        entry.pack(side="left", padx=6)

        tk.Button(
            frame_pasta, text="📂 Escolher pasta",
            command=self._escolher_pasta
        ).pack(side="left")

        # ── Botões de ação ──
        frame_botoes = tk.Frame(self.root, pady=4, padx=10)
        frame_botoes.pack(fill="x")

        tk.Button(
            frame_botoes, text="🔵 Simular (ver prévia)",
            width=22, bg="#d0e8ff",
            command=self._simular
        ).pack(side="left", padx=(0, 8))

        tk.Button(
            frame_botoes, text="✔️  Renomear arquivos",
            width=22, bg="#c8f0c8",
            command=self._renomear
        ).pack(side="left")

        tk.Button(
            frame_botoes, text="🗑 Limpar log",
            command=self._limpar_log
        ).pack(side="right")

        # ── Área de log ──
        frame_log = tk.Frame(self.root, padx=10, pady=4)
        frame_log.pack(fill="both", expand=True)

        tk.Label(frame_log, text="Log:", anchor="w").pack(fill="x")

        self.log_area = scrolledtext.ScrolledText(
            frame_log, wrap=tk.WORD, state="disabled",
            font=("Courier New", 10)
        )
        self.log_area.pack(fill="both", expand=True)

        # ── Barra de status ──
        self.status_var = tk.StringVar(value="Aguardando...")
        tk.Label(
            self.root, textvariable=self.status_var,
            anchor="w", relief="sunken", padx=6
        ).pack(fill="x", side="bottom")

    def _escolher_pasta(self):
        pasta = filedialog.askdirectory(title="Selecione a pasta com os PDFs")
        if pasta:
            self.pasta_var.set(pasta)
            self._log(f"📂 Pasta selecionada: {pasta}\n\n")
            self.status_var.set(f"Pasta: {pasta}")

    def _log(self, texto: str):
        self.log_area.config(state="normal")
        self.log_area.insert(tk.END, texto)
        self.log_area.see(tk.END)
        self.log_area.config(state="disabled")

    def _limpar_log(self):
        self.log_area.config(state="normal")
        self.log_area.delete("1.0", tk.END)
        self.log_area.config(state="disabled")

    def _executar(self, simular: bool):
        pasta = self.pasta_var.get().strip()
        if not pasta:
            messagebox.showwarning("Atenção", "Selecione uma pasta primeiro!")
            return
        if not os.path.isdir(pasta):
            messagebox.showerror("Erro", f"Pasta não encontrada:\n{pasta}")
            return

        modo = "SIMULAÇÃO" if simular else "RENOMEANDO"
        self._log(f"{'─'*50}\n  {modo}\n{'─'*50}\n")

        renomeados, ignorados = processar_pasta(pasta, simular, self._log)

        resumo = f"Concluído — Renomeados: {renomeados} | Sem alteração: {ignorados}\n"
        self._log(f"{'─'*50}\n{resumo}{'─'*50}\n\n")
        self.status_var.set(resumo.strip())

    def _simular(self):
        self._executar(simular=True)

    def _renomear(self):
        pasta = self.pasta_var.get().strip()
        if not pasta:
            messagebox.showwarning("Atenção", "Selecione uma pasta primeiro!")
            return
        if messagebox.askyesno(
            "Confirmar",
            f"Renomear os PDFs em:\n{pasta}\n\nEsta ação não pode ser desfeita. Continuar?"
        ):
            self._executar(simular=False)


# ─────────────────────────────────────────────
#  Entrada
# ─────────────────────────────────────────────

if __name__ == "__main__":
    root = tk.Tk()
    App(root)
    root.mainloop()