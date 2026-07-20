import os
import re

# A pasta sera perguntada ao executar o script


def limpar_nome(nome_sem_extensao):
    """Substitui pontos e virgulas por espacos no nome."""
    resultado = nome_sem_extensao.replace(".", " ").replace(",", " ")
    return re.sub(r" {2,}", " ", resultado).strip()


def processar_pasta(pasta):
    if not os.path.isdir(pasta):
        print(f"[ERRO] Pasta nao encontrada: {pasta}")
        return

    arquivos_pdf = [
        f for f in os.listdir(pasta)
        if f.lower().endswith(".pdf") and os.path.isfile(os.path.join(pasta, f))
    ]

    if not arquivos_pdf:
        print("Nenhum arquivo PDF encontrado na pasta.")
        return

    print(f"Encontrados {len(arquivos_pdf)} PDF(s). Iniciando processamento...\n")

    renomeados = 0
    ignorados = 0
    conflitos = []

    for nome_arquivo in sorted(arquivos_pdf):
        nome_sem_ext, extensao = os.path.splitext(nome_arquivo)
        novo_nome_sem_ext = limpar_nome(nome_sem_ext)
        novo_nome = novo_nome_sem_ext + extensao

        print(f"Processando: {nome_arquivo}")

        if novo_nome == nome_arquivo:
            print("  [i] Sem alteracao necessaria.\n")
            ignorados += 1
            continue

        caminho_antigo = os.path.join(pasta, nome_arquivo)
        caminho_novo = os.path.join(pasta, novo_nome)

        if os.path.exists(caminho_novo):
            print(f"  [!] Ja existe um arquivo com o nome '{novo_nome}'. Pulando.\n")
            conflitos.append(nome_arquivo)
            continue

        os.rename(caminho_antigo, caminho_novo)
        print(f"  [OK] Renomeado para: {novo_nome}\n")
        renomeados += 1

    # Resumo final
    print("=" * 60)
    print("RESUMO")
    print("=" * 60)
    print(f"Total de PDFs processados : {len(arquivos_pdf)}")
    print(f"Renomeados com sucesso    : {renomeados}")
    print(f"Sem alteracao necessaria  : {ignorados}")

    if conflitos:
        print(f"\n[!] Nome de destino ja existia ({len(conflitos)}):")
        for f in conflitos:
            print(f"   - {f}")


if __name__ == "__main__":
    print("=" * 60)
    print("  REMOVEDOR DE PONTOS E VIRGULAS - NOMES DE PDF")
    print("=" * 60)

    while True:
        pasta = input("\nDigite o caminho completo da pasta com os PDFs:\n> ").strip().strip('"')

        if not pasta:
            print("[ERRO] Nenhum caminho informado. Tente novamente.")
            continue

        if not os.path.isdir(pasta):
            print(f"[ERRO] Pasta nao encontrada: {pasta}")
            print("Verifique se o caminho esta correto e tente novamente.")
            continue

        break

    print(f"\nPasta selecionada: {pasta}\n")
    processar_pasta(pasta)
    input("\nPressione ENTER para sair...")
