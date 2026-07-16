import os
import re
import pdfplumber

# A pasta sera perguntada ao executar o script

# Dicionario CNPJ -> Cidade
CNPJ_CIDADES = {
    "01.189.884/0001-37": "LABSYSTEM ASSIS",
    "06.201.312/0001-40": "ANDRADINA",
    "11.082.876/0001-40": "MATRIZ",
    "11.082.876/0002-21": "PAULICEIA",
    "11.082.876/0003-02": "GUARACAI",
    "11.082.876/0004-93": "AURIFLAMA",
    "11.082.876/0005-74": "GUARARAPES",
    "11.082.876/0006-55": "MIRANDOPOLIS",
    "11.082.876/0007-36": "PRESIDENTE PRUDENTE",
    "11.082.876/0008-17": "PIRAPOZINHO",
    "11.082.876/0009-06": "ARACATUBA",
    "11.082.876/0010-31": "MARTINOPOLIS",
    "11.082.876/0011-12": "DRACENA",
    "11.082.876/0012-01": "SANTO ANASTACIO",
    "11.082.876/0015-46": "CAMPINAS",
    "11.082.876/0016-27": "CAPIVARI",
    "11.082.876/0017-08": "ADAMANTINA",
    "11.082.876/0018-99": "BIRIGUI I",
    "11.082.876/0020-03": "BIRIGUI II",
    "11.082.876/0022-75": "CUBATAO",
    "11.082.876/0024-37": "TAUBATE I",
    "11.082.876/0025-18": "TAUBATE II",
    "11.082.876/0026-07": "TAUBATE III",
    "11.082.876/0027-80": "TAUBATE IV",
}

TEXTO_DESTINATARIO_ALVO = "CONSELHO REGIONAL DE BIOMEDICINA"


def extrair_texto_completo(caminho_pdf):
    """
    Retorna o texto completo do PDF (todas as paginas concatenadas).
    """
    texto_completo = ""
    with pdfplumber.open(caminho_pdf) as pdf:
        for pagina in pdf.pages:
            texto_completo += (pagina.extract_text() or "") + "\n"
    return texto_completo


def destinatario_valido(texto):
    """
    Verifica se o beneficiario/destinatario do documento e o CRBM.
    Tenta varios campos possiveis, dependendo do layout do comprovante
    (boleto ou Pix), na seguinte ordem:
      1. Nome Fantasia do Beneficiário:
      2. Razão Social do Beneficiário:
      3. Nome do destinatário:
    (checa numa janela de caracteres para evitar falso positivo vindo
    de outro trecho do texto)
    """
    campos_para_checar = [
        "Nome Fantasia do Beneficiário:",
        "Razão Social do Beneficiário:",
        "Nome do destinatário:",
    ]

    for campo in campos_para_checar:
        if campo in texto:
            idx = texto.index(campo)
            janela = texto[idx: idx + 150]
            if TEXTO_DESTINATARIO_ALVO in janela:
                return True

    return False


def extrair_cnpj_do_texto(texto):
    """
    Procura o CNPJ no texto. Tenta primeiro 'CPF/CNPJ do Pagador:';
    se esse campo nao existir no PDF, tenta 'CNPJ do devedor:' como
    alternativa. Retorna o CNPJ encontrado logo apos o campo, ou None
    se nao encontrar nenhum dos dois.
    """
    padrao_cnpj = re.compile(r"\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}")

    campos_para_checar = [
        "CPF/CNPJ do Pagador:",
        "CNPJ do devedor:",
    ]

    for campo in campos_para_checar:
        if campo in texto:
            trecho = texto[texto.index(campo):]
            match = padrao_cnpj.search(trecho)
            if match:
                return match.group()

    return None


def construir_novo_nome(nome_atual, cidade):
    """
    Dado o nome atual do arquivo (sem extensao), substitui o trecho
    'CONSELHO REGIONAL DE BIOMEDICINA' (com ou sem 'CRBM <numero>' logo
    apos) pelo padrao 'CRBM <CIDADE>'. Remove sufixos do Windows como
    (1), (2) etc. antes de processar.

    Exemplos:
      '30062026 CONSELHO REGIONAL DE BIOMEDICINA 148 85'
      -> '30062026 CRBM PRESIDENTE PRUDENTE 148 85'

      '30062026 CONSELHO REGIONAL DE BIOMEDICINA CRBM 1 148 85'
      -> '30062026 CRBM PRESIDENTE PRUDENTE 148 85'
    """
    # Remove sufixos do Windows: (1), (2), (10) etc. no final do nome
    nome_limpo = re.sub(r"\s*\(\d+\)\s*$", "", nome_atual).strip()

    # Padrao: <data> CONSELHO REGIONAL DE BIOMEDICINA [CRBM <n>] <2 blocos numericos finais>
    padrao = re.compile(
        r"^(\d+)\s+"                                  # grupo 1: data/prefixo numerico
        r"CONSELHO REGIONAL DE BIOMEDICINA"            # texto fixo
        r"(?:\s+CRBM\s+\d+)?"                          # opcional: 'CRBM 1', 'CRBM 2' etc.
        r"\s+(\d+\s+\d+)$"                             # grupo 2: ultimos 2 blocos numericos
    )
    m = padrao.match(nome_limpo)
    if not m:
        return None

    data   = m.group(1)
    sufixo = m.group(2)

    return f"{data} CRBM {cidade} {sufixo}"


def processar_pasta(pasta):
    if not os.path.isdir(pasta):
        print(f"[ERRO] Pasta nao encontrada: {pasta}")
        return

    pdfs = [f for f in os.listdir(pasta) if f.lower().endswith(".pdf")]

    if not pdfs:
        print("Nenhum arquivo PDF encontrado na pasta.")
        return

    print(f"Encontrados {len(pdfs)} PDF(s). Iniciando processamento...\n")

    renomeados      = 0
    nao_crbm        = []
    sem_cnpj        = []
    cnpj_fora       = []
    erro_nome       = []

    for arquivo in pdfs:
        caminho = os.path.join(pasta, arquivo)
        nome_sem_ext = os.path.splitext(arquivo)[0]

        print(f"Processando: {arquivo}")

        try:
            texto = extrair_texto_completo(caminho)
        except Exception as e:
            print(f"  [ERRO ao ler PDF] {e}\n")
            continue

        # 1. Validar destinatario
        if not destinatario_valido(texto):
            print(f"  [!] Destinatario nao e '{TEXTO_DESTINATARIO_ALVO}'. Pulando.\n")
            nao_crbm.append(arquivo)
            continue

        print(f"  [OK] Destinatario confirmado: {TEXTO_DESTINATARIO_ALVO}")

        # 2. Extrair CNPJ do devedor
        cnpj = extrair_cnpj_do_texto(texto)
        if not cnpj:
            print(f"  [!] 'CNPJ do devedor:' nao encontrado. Pulando.\n")
            sem_cnpj.append(arquivo)
            continue

        print(f"  [OK] CNPJ encontrado: {cnpj}")

        # 3. Consultar dicionario
        cidade = CNPJ_CIDADES.get(cnpj)
        if not cidade:
            print(f"  [!] CNPJ nao esta na lista. Arquivo mantido sem alteracao.\n")
            cnpj_fora.append((arquivo, cnpj))
            continue

        print(f"  [OK] Cidade: {cidade}")

        # 4. Montar novo nome
        novo_nome_sem_ext = construir_novo_nome(nome_sem_ext, cidade)
        if not novo_nome_sem_ext:
            print(f"  [!] Nao foi possivel identificar o padrao de nome. Pulando.\n")
            erro_nome.append(arquivo)
            continue

        novo_arquivo = novo_nome_sem_ext + ".pdf"
        novo_caminho = os.path.join(pasta, novo_arquivo)

        # 5. Renomear
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

    if nao_crbm:
        print(f"\n[!] Destinatario diferente de CRBM ({len(nao_crbm)}):")
        for f in nao_crbm:
            print(f"   - {f}")

    if sem_cnpj:
        print(f"\n[!] Sem 'CNPJ do devedor' ({len(sem_cnpj)}):")
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
    print("  RENOMEADOR DE PDFs - CRBM")
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