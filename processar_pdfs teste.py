#!/usr/bin/env python3
"""
Script de processamento de PDFs:

Etapa 1: Se o PDF tiver mais de 1 pagina, separa em N PDFs (1 pagina cada).
Etapa 2: Para cada PDF de 1 pagina (original ou gerado na etapa 1),
         identifica o tipo de pagamento e renomeia o arquivo de acordo
         com os campos extraidos do texto.
"""

import os
import re
import sys
from pathlib import Path

import pdfplumber
from pypdf import PdfReader, PdfWriter


# ---------------------------------------------------------------------------
# Configuracao dos tipos de pagamento
# ---------------------------------------------------------------------------
# Para cada tipo: titulo de identificacao no PDF, rotulos dos campos a ler
# (na ordem em que aparecem no documento) e a ordem final de montagem do
# nome do arquivo (indices baseados em 1, referentes aos campos abaixo).

TIPOS_PAGAMENTO = {
    "Folha de pagamento": {
        "campos": [
            "Favorecido:",
            "Data do Pagamento:",
            "Valor Total (R$):",
        ],
        "ordem_renomear": [2, 1, 3],
    },
    "Pagar Boletos Eletronicos": {
        "campos": [
            "Razao Social do Beneficiario:",
            "Data da Transacao:",
            "Valor Pago (R$):",
        ],
        "ordem_renomear": [2, 1, 3],
    },
    "Comprovante de Pagamento Pix": {
        "campos": [
            "Valor:",
            "Realizado em:",
            "Nome do destinatario:",
        ],
        "ordem_renomear": [2, 3, 1],
    },
}


# ---------------------------------------------------------------------------
# Funcoes auxiliares
# ---------------------------------------------------------------------------

def extrair_texto_pdf(caminho_pdf):
    """Extrai todo o texto de um PDF (todas as paginas)."""
    texto_total = ""
    with pdfplumber.open(caminho_pdf) as pdf:
        for pagina in pdf.pages:
            texto_pagina = pagina.extract_text() or ""
            texto_total += texto_pagina + "\n"
    return texto_total


def identificar_tipo_pagamento(texto):
    """Procura no texto qual dos tipos de pagamento conhecidos esta presente."""
    for tipo in TIPOS_PAGAMENTO:
        if tipo.lower() in texto.lower():
            return tipo
    return None


def limpar_valor(rotulo, valor_bruto):
    """
    Limpa o valor extraido.

    Se o rotulo indicar que se trata de uma data (contem 'Data' ou
    'Realizado em'), remove tudo que nao for numero.
    Ex: '11/06/2026 - 16:33:04' -> '11062026'
    """
    valor = valor_bruto.strip()

    rotulo_lower = rotulo.lower()
    eh_data = "data" in rotulo_lower or "realizado em" in rotulo_lower

    if eh_data:
        # Mantem apenas os digitos da data (descartando horario, separadores, etc.)
        # Pega so os 8 primeiros digitos (DDMMAAAA) para evitar incluir o horario.
        digitos = re.sub(r"\D", "", valor)
        return digitos[:8]

    # Para valores nao-data, apenas normaliza espacos extras
    valor = re.sub(r"\s+", " ", valor)
    return valor


def extrair_campo(texto, rotulo):
    """
    Extrai o valor que vem apos o rotulo na mesma linha.
    Ex: rotulo='Favorecido:' em uma linha 'Favorecido: JOAO DA SILVA'
    retorna 'JOAO DA SILVA'.
    """
    for linha in texto.splitlines():
        linha_strip = linha.strip()
        if linha_strip.lower().startswith(rotulo.lower()):
            valor_bruto = linha_strip[len(rotulo):].strip()
            return limpar_valor(rotulo, valor_bruto)

        # Caso o rotulo apareca no meio da linha (nao so no inicio)
        if rotulo.lower() in linha_strip.lower():
            idx = linha_strip.lower().find(rotulo.lower())
            valor_bruto = linha_strip[idx + len(rotulo):].strip()
            if valor_bruto:
                return limpar_valor(rotulo, valor_bruto)

    return None


def sanitizar_nome_arquivo(nome):
    """Remove caracteres invalidos para nomes de arquivo no Windows/Linux."""
    nome = re.sub(r'[\\/*?:"<>|]', "", nome)
    nome = re.sub(r"\s+", " ", nome).strip()
    return nome


def gerar_nome_disponivel(pasta, nome_base, extensao=".pdf"):
    """
    Gera um caminho de arquivo que nao exista ainda.
    Se 'nome_base.pdf' ja existir, tenta 'nome_base (1).pdf', '(2).pdf', etc.
    """
    candidato = pasta / f"{nome_base}{extensao}"
    if not candidato.exists():
        return candidato

    contador = 1
    while True:
        candidato = pasta / f"{nome_base} ({contador}){extensao}"
        if not candidato.exists():
            return candidato
        contador += 1


# ---------------------------------------------------------------------------
# Etapa 1: separar PDF em paginas individuais
# ---------------------------------------------------------------------------

def separar_pdf_em_paginas(caminho_pdf, pasta_saida):
    """
    Se o PDF tiver mais de 1 pagina, separa em N arquivos PDF (1 pagina cada)
    e retorna a lista de caminhos gerados.

    Se o PDF tiver apenas 1 pagina, retorna uma lista com o proprio caminho
    (nada e separado).
    """
    leitor = PdfReader(str(caminho_pdf))
    total_paginas = len(leitor.pages)

    if total_paginas <= 1:
        return [caminho_pdf]

    nome_base = caminho_pdf.stem
    arquivos_gerados = []

    for i, pagina in enumerate(leitor.pages, start=1):
        escritor = PdfWriter()
        escritor.add_page(pagina)

        nome_pagina = f"{nome_base} - pagina {i}"
        caminho_saida = gerar_nome_disponivel(pasta_saida, nome_pagina)

        with open(caminho_saida, "wb") as f:
            escritor.write(f)

        arquivos_gerados.append(caminho_saida)
        print(f"  -> Pagina {i}/{total_paginas} salva em: {caminho_saida.name}")

    return arquivos_gerados


# ---------------------------------------------------------------------------
# Etapa 2: identificar tipo e renomear
# ---------------------------------------------------------------------------

def processar_renomeio(caminho_pdf):
    """
    Le o conteudo do PDF (1 pagina), identifica o tipo de pagamento,
    extrai os campos necessarios e renomeia o arquivo conforme a ordem
    configurada para aquele tipo.
    """
    texto = extrair_texto_pdf(caminho_pdf)

    tipo = identificar_tipo_pagamento(texto)
    if tipo is None:
        print(f"  [AVISO] Tipo de pagamento nao identificado em '{caminho_pdf.name}'. "
              f"Arquivo nao foi renomeado.")
        return

    config = TIPOS_PAGAMENTO[tipo]
    campos = config["campos"]
    ordem = config["ordem_renomear"]

    valores = []
    for rotulo in campos:
        valor = extrair_campo(texto, rotulo)
        if valor is None or valor == "":
            valor = "DESCONHECIDO"
            print(f"  [AVISO] Campo '{rotulo}' nao encontrado em '{caminho_pdf.name}'.")
        valores.append(valor)

    # Monta o nome final na ordem configurada (ordem e baseada em 1)
    partes_nome = [valores[i - 1] for i in ordem]
    nome_base = " ".join(partes_nome)
    nome_base = sanitizar_nome_arquivo(nome_base)

    if not nome_base:
        print(f"  [AVISO] Nome gerado ficou vazio para '{caminho_pdf.name}'. "
              f"Arquivo nao foi renomeado.")
        return

    pasta = caminho_pdf.parent
    novo_caminho = gerar_nome_disponivel(pasta, nome_base)

    caminho_pdf.rename(novo_caminho)
    print(f"  -> [{tipo}] '{caminho_pdf.name}' renomeado para '{novo_caminho.name}'")


# ---------------------------------------------------------------------------
# Fluxo principal
# ---------------------------------------------------------------------------

def processar_arquivo(caminho_pdf, pasta_saida):
    print(f"\nProcessando: {caminho_pdf.name}")

    # Etapa 1
    arquivos = separar_pdf_em_paginas(caminho_pdf, pasta_saida)

    if len(arquivos) > 1:
        print(f"  PDF separado em {len(arquivos)} paginas.")
        # Etapa 2 roda em cada pagina gerada
        for arq in arquivos:
            processar_renomeio(arq)
    else:
        # Ja era 1 pagina (nao houve separacao) -> Etapa 2 direto
        processar_renomeio(arquivos[0])


def main():
    print("=== Processador de PDFs ===\n")

    caminho_entrada = input("Caminho do arquivo PDF ou pasta com PDFs: ").strip().strip('"')
    caminho_entrada = Path(caminho_entrada)

    if not caminho_entrada.exists():
        print(f"Erro: o caminho '{caminho_entrada}' nao existe.")
        sys.exit(1)

    pasta_saida_input = input(
        "Pasta de saida para os PDFs separados (ENTER para usar a mesma pasta do arquivo): "
    ).strip().strip('"')

    if caminho_entrada.is_dir():
        pasta_padrao = caminho_entrada
        arquivos_pdf = sorted(caminho_entrada.glob("*.pdf"))
    else:
        pasta_padrao = caminho_entrada.parent
        arquivos_pdf = [caminho_entrada]

    if pasta_saida_input:
        pasta_saida = Path(pasta_saida_input)
        pasta_saida.mkdir(parents=True, exist_ok=True)
    else:
        pasta_saida = pasta_padrao

    if not arquivos_pdf:
        print("Nenhum arquivo .pdf encontrado.")
        sys.exit(0)

    for pdf in arquivos_pdf:
        try:
            processar_arquivo(pdf, pasta_saida)
        except Exception as e:
            print(f"  [ERRO] Falha ao processar '{pdf.name}': {e}")

    print("\nProcessamento concluido.")


if __name__ == "__main__":
    main()