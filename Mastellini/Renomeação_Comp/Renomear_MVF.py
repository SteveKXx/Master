import os
import re
import pdfplumber

# A pasta sera perguntada ao executar o script

# Dicionario CNPJ -> Cidade
CNPJ_CIDADES = {
    "11.082.876/0009-06": "ARACATUBA",
    "11.082.876/0003-02": "GUARACAI",
    "11.082.876/0018-99": "BIRIGUI",
    "11.082.876/0006-55": "MIRANDOPOLIS",
    "11.082.876/0005-74": "GUARARAPES",
    "11.082.876/0012-01": "SANTO ANASTACIO",
    "11.082.876/0004-93": "AURIFLAMA",
    "11.082.876/0011-12": "DRACENA",
    "11.082.876/0008-17": "PIRAPOZINHO",
    "11.082.876/0017-08": "ADAMANTINA",
    "11.082.876/0007-36": "PRESIDENTE PRUDENTE",
    "06.201.312/0001-40": "ANDRADINA",
}


def extrair_cnpj_do_pdf(caminho_pdf):
    """
    Abre o PDF e procura pelo texto 'CPF/CNPJ do Pagador:' retornando
    o CNPJ encontrado logo apos, ou None se nao encontrar.
    """
    padrao_cnpj = re.compile(r"\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}")

    try:
        with pdfplumber.open(caminho_pdf) as pdf:
            for pagina in pdf.pages:
                texto = pagina.extract_text() or ""

                if "CPF/CNPJ do Pagador:" in texto:
                    trecho = texto[texto.index("CPF/CNPJ do Pagador:"):]
                    match = padrao_cnpj.search(trecho)
                    if match:
                        return match.group()
    except Exception as e:
        print(f"  [ERRO ao ler PDF] {e}")

    return None


def construir_novo_nome(nome_atual, cidade):
    """
    Dado o nome atual do arquivo (sem extensao), substitui o trecho
    entre 'MVF ' e os ultimos 2 blocos numericos pelo nome da cidade.
    Remove sufixos do Windows como (1), (2) etc. antes de processar.

    Exemplos:
      '22062026 MVF PRUDENTE AGENCIA DE ESTAGIOS EIRELI 122 00'
      -> '22062026 MVF PRESIDENTE PRUDENTE 122 00'

      '22062026 MVF PRUDENTE AGENCIA DE ESTAGIOS EIRELI 122 00 (1)'
      -> '22062026 MVF PRESIDENTE PRUDENTE 122 00'
    """
    # Remove sufixos do Windows: (1), (2), (10) etc. no final do nome
    nome_limpo = re.sub(r"\s*\(\d+\)\s*$", "", nome_atual).strip()

    # Padrao: <prefixo ate MVF> <qualquer texto> <2 ultimos blocos numericos>
    padrao = re.compile(
        r"^(.*?MVF\s+)"      # grupo 1: tudo ate 'MVF ' (inclusive)
        r".+"                 # nome da empresa (descartado)
        r"(\s+\d+\s+\d+)$"   # grupo 2: ultimos 2 blocos numericos (ex: ' 122 00')
    )
    m = padrao.match(nome_limpo)
    if not m:
        return None

    prefixo = m.group(1)   # ex: '22062026 MVF '
    sufixo  = m.group(2)   # ex: ' 122 00'

    return f"{prefixo}{cidade}{sufixo}"


def processar_pasta(pasta):
    if not os.path.isdir(pasta):
        print(f"[ERRO] Pasta nao encontrada: {pasta}")
        return

    pdfs = [f for f in os.listdir(pasta) if f.lower().endswith(".pdf")]

    if not pdfs:
        print("Nenhum arquivo PDF encontrado na pasta.")
        return

    print(f"Encontrados {len(pdfs)} PDF(s). Iniciando processamento...\n")

    renomeados = 0
    sem_cnpj   = []
    cnpj_fora  = []
    erro_nome  = []

    for arquivo in pdfs:
        caminho = os.path.join(pasta, arquivo)
        nome_sem_ext = os.path.splitext(arquivo)[0]

        print(f"Processando: {arquivo}")

        # 1. Extrair CNPJ do PDF
        cnpj = extrair_cnpj_do_pdf(caminho)
        if not cnpj:
            print(f"  [!] 'CPF/CNPJ do Pagador:' nao encontrado. Pulando.\n")
            sem_cnpj.append(arquivo)
            continue

        print(f"  [OK] CNPJ encontrado: {cnpj}")

        # 2. Consultar dicionario
        cidade = CNPJ_CIDADES.get(cnpj)
        if not cidade:
            print(f"  [!] CNPJ nao esta na lista. Arquivo mantido sem alteracao.\n")
            cnpj_fora.append((arquivo, cnpj))
            continue

        print(f"  [OK] Cidade: {cidade}")

        # 3. Montar novo nome
        novo_nome_sem_ext = construir_novo_nome(nome_sem_ext, cidade)
        if not novo_nome_sem_ext:
            print(f"  [!] Nao foi possivel identificar o padrao de nome. Pulando.\n")
            erro_nome.append(arquivo)
            continue

        novo_arquivo = novo_nome_sem_ext + ".pdf"
        novo_caminho = os.path.join(pasta, novo_arquivo)

        # 4. Renomear
        if novo_arquivo == arquivo:
            print(f"  [i] Nome ja esta correto. Nada a fazer.\n")
            continue

        if os.path.exists(novo_caminho):
            print(f"  [!] Ja existe um arquivo com o nome '{novo_arquivo}'. Pulando.\n")
            continue

        os.rename(caminho, novo_caminho)
        print(f"  [OK] Renomeado para: {novo_arquivo}\n")
        renomeados += 1

    # Resumo final
    print("=" * 60)
    print("RESUMO")
    print("=" * 60)
    print(f"Total de PDFs processados : {len(pdfs)}")
    print(f"Renomeados com sucesso    : {renomeados}")

    if sem_cnpj:
        print(f"\n[!] Sem 'CPF/CNPJ do Pagador' ({len(sem_cnpj)}):")
        for f in sem_cnpj:
            print(f"   - {f}")

    if cnpj_fora:
        print(f"\n[!] CNPJ nao encontrado na lista ({len(cnpj_fora)}):")
        for f, c in cnpj_fora:
            print(f"   - {f}  ->  CNPJ: {c}")

    if erro_nome:
        print(f"\n[!] Padrao de nome nao reconhecido ({len(erro_nome)}):")
        for f in erro_nome:
            print(f"   - {f}")


if __name__ == "__main__":
    print("=" * 60)
    print("  RENOMEADOR DE PDFs - MVF")
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