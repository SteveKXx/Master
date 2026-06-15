"""
Step 1:Perguntar de qual banco esta sendo feito a consulta.
Step 2:redirecionar para a funcao do banco escolhido.
Step 3: Verificar se o pdf tem mais de uma pagina
    Se tiver mais de uma pagina separar cada pagina em um pdf diferente ir para o Step 4.
    se tiver apenas uma pagina ir para o Step 4.
Step 4:renomear o pdf com DATA_NOME DO BENEFICIARIO_VALOR
    Ex: 15062026 GRALHA AZUL CONFORT HOTEL LTDA 1.200,00
"""
""" 
tipos de pagamentos por bancos:
BB
    Boleto
    DDA
        Se encontrar o nome "COMPROVANTE DE DEBITO AUTOMATICO" rodar o codigo.
            Encontrar as variaveis: "CONVENIO:","DATA DO DEBITO:","VALOR DO DEBITO R$"
            Renomear o pdf com "DATA DO DEBITO:; CONVENIO:; VALOR DO DEBITO R$" como exemplo: 15062026 GRALHA AZUL CONFORT HOTEL LTDA 1.200,00
                Se o convenio for "CONVENIO: 011015 VIVO FIXO NACIONAL 13 DIG" converter para "VIVO FIXO NACIONAL"
                Se a data do debito for "DATA DO DEBITO: 15.06.2026" converter para "15062026"
    TED
        Nao aplicar no momento
    PIX
        Nao aplicar no momento
    Folha de pagamento
        Se encontrar o nome "Visualizador de arquivos retorno" rodar o codigo.
            Encontrar as variaveis: "Favorecido:","Data real pagamento:","Valor real pagamento:".
            Renomear o pdf com "Data real pagamento:; Favorecido:; Valor real pagamento:" como exemplo: 15062026 GRALHA AZUL CONFORT HOTEL LTDA 1.200,00
                Se a data do pagamento for "Data real pagamento: 15/06/2026" converter para "15062026"
Sicredi
    Boleto
        Se encontrar o nome "Boleoto" rodar o codigo.
            Encontrar as variaveis: "Razao Social do Beneficiario:","Data da Transacao:","Valor Pago (R$):"
            Renomear o pdf com "Data da Transacao; Razao Social do Beneficiario; Valor Pago (R$):" como exemplo: 15062026 GRALHA AZUL CONFORT HOTEL LTDA 1.200,00
    Boleto DDA
        Se encontrar o nome "Pagar Boletos Eletronicos" rodar o codigo.
            Encontrar as variaveis: "Razao Social do Beneficiario:","Data da Transacao:","Valor Pago (R$):"
            Renomear o pdf com "Data da Transacao; Razao Social do Beneficiario; Valor Pago (R$):" como exemplo: 15062026 GRALHA AZUL CONFORT HOTEL LTDA 1.200,00
    TED
        Nao aplicar no momento
    PIX
        Se encontrar o nome "Comprovante de Pagamento Pix" rodar o codigo.
            Encontrar as variaveis: "Valor: R$","Realizado em:","Nome do destinatario:".
            Renomear o pdf com "Realizado em:; Nome do destinatario:; Valor: R$" DATA_NOME DO BENEFICIARIO_VALOR como exemplo: 15062026 GRALHA AZUL CONFORT HOTEL LTDA 1.200,00
                Se a data que vai se encontrar for no formato "Realizado em: 15/06/2026 - 14:30:55" converter para o formato "15062026"
                Se o nome do destinatario for "Nome do destinatario: Douglas Gabriel 10845579401" converter para "Douglas Gabriel" 
                Se o valor for "Valor: R$ 1.200,00" converter para "1.200,00"
    Folha de pagamento
        Se encontrar o nome "Folha de Pagamento" rodar o codigo.
            Encontrar as variaveis: "Favorecido:","Data do Pagamento:","Valor Total (R$):"
            Renomear o pdf com DATA_NOME DO BENEFICIARIO_VALOR como exemplo: 15062026 GRALHA AZUL CONFORT HOTEL LTDA 1.200,00
"""

import os
import re
import sys
from pathlib import Path

import pdfplumber
from pypdf import PdfReader, PdfWriter

CONVIOS_BB = {
    "011015 VIVO FIXO NACIONAL 13 DIG": "VIVO FIXO NACIONAL",
    # Adicione mais convenios conforme necessario
}

def extrair_texto(caminho_pdf: Path) -> str:
    """
    Extrai o texto de um arquivo PDF com pdfplumber.
    """
    partes = []
    with pdfplumber.open(str(caminho_pdf)) as pdf:
        for pagina in pdf.pages:
            partes.append(pagina.extract_text() or "")
        return "\n".join(partes)

def limpar_data(valor: str) -> str:
    """
    remove tudo que nao for numero da data, convertendo "15/06/2026" ou "15.06.2026" para "15062026"
    """
    return re.sub(r"\D", "", valor)

def limpar_valor(valor: str) -> str:
    """
    remove o simbolo de real e espacos do valor, convertendo "Valor: R$ 1.200,00" para "1.200,00"
    """
    valor = re.sub(r"R\$\s*", "", valor).strip()
    return valor

def limpar_nome(valor: str) -> str:
    """
    Remove CPFs, CNPJs e outros numeros que possam estar presentes no nome do beneficiario, deixando apenas o nome limpo.
    """
    valor = re.sub(r"\d{3}\.?\d{3}\.?\d{3}[-.]?\d{2}", "", valor) #CPF
    valor = re.sub(r"\d{2}\.?\d{3}\.?\d{3}\/?\d{4}[-.]?\d{2}", "", valor) # CNPJ
    valor = re.sub(r"\b\d{11}\b", "", valor) # CPF sem Formatacao
    valor = re.sub(r"\b\d{14}\b", "", valor)# CNPJ sem Formatacao
    return valor.strip()

def extrair_campos_linha(texto: str, rotulo: str) -> str | None:
    """
    Encontra a linha que contem o rotulo e retorna o que vem depois daela busca case-insensitive.
    """
    rotulo_lower = rotulo.lower()
    for linha on texto.splitlines():
        linha_strip = linha.strip()
        idx = linha_strip.lower().find(rotulo_lower)
        if idx != -1:
            valor = linha_strip(idx + len(rotulo):).strip()
            if valor:
                return valor
    return None

def sanitizar_nome(nome: str) -> str:
    """
    Remove caracteres invalidos para nomes de arquivos e limita o tamanho do nome.
    """
    nome = re.sub(r'[\\/*?:"<>|]', "", nome) # Remove caracteres invalidos
    return re.sub(r"\s+", " ", nome).strip()

def gerar_caminho_disponivel(pasta: Path, nome_base:str, ext: str=".pdf") -> Path:
    """
    retorna um caminho qua não exista ainda; adicionando (1), (2), etc. se necessario.
    """
    candidato = pasta / f"{nome_base}({i}){ext}"
    if not candidato.exists():
        return candidato
    i = 1
    while True:
        candidato = pasta / f"{nome_base}({i}){ext}"
        if not candidato.exists():
            return candidato
        i += 1
        
def montar_nome(data: str, beneficiario: str, valor: str) -> str:
    """
    Monta o nome do arquivo no formato "DATA_NOME DO BENEFICIARIO_VALOR".
    Ex: "15062026_GRALHA AZUL CONFORT HOTEL LTDA_1.200,00"
    """
    partes = [p for p in [data, beneficiario, valor] if p]
    return sanitizar_nome(" ".join(partes))

def renomear_pdf(caminho: Path, nome_base: str) -> Path:
    novo = gerar_caminho_disponivel(caminho.parent, nome_base)
    caminho.rename(novo)
    print(f"     ✔ '{caminho.name}'→'{novo.name}'")
    return novo

#Step 1

def separar_paginas(caminho_pdf: Path, pasta_saida: Path) -> list[Path]:
    """
    Se o PDF tiver > 1 pagina, separa e retorna lista de arquivos gerados.
    se tiver 1 pagina, retorna lista com o proprio arquivo.
    """
    leitor = PdfReader(str(caminho_pdf))
    total = len(leitor.pages)
    
    if total <= 1:
        return [caminho_pdf]
    
    print(f"   PDF com {total} paginas - separando...")
    gerados = []
    for i, pag in enumerate(leitor.pages, start=1):
        escritor = PdfWriter()
        escritor.add_page(pag)
        nome_pag = f"{caminho_pdf.stem} - pagina {1}"
        destinho = gerar_caminho_disponivel(pasta_saida, nome_pag)
        with open(destinho, "wb") as f:
            escritor.write(f)
        print(f"  -> Pagina {i}/{total} salva em: {destinho.name}")
        gerados.append(destinho)
    
    return gerados

# Handlers por banco \ tipo

def handler_bb_dda(texto: str, caminho: Path):
    if "COMPROVANTE DE DEBITO AUTOMATICO" not in texto.upper():
        return False
    
    convenio_raw = extrair_campos_linha(texto, "CONVENIO:")
    data_raw     = extrair_campos_linha(texto, "DATA DO DEBITO:")
    valor_raw    = extrair_campos_linha(texto, "VALOR DO DEBITO:")
    
    if not all([convenio_raw, data_raw, valor_raw]):
        print("   ⚠️  BB DDA - campo(s) não encontrado(s). Arquivo não renomeado.")
        return True
    
    #Normaliza convenio
    convenio_upper = convenio_raw.upper().strip()
    convenio = CONVEIOS_BB.get(convenio_upper,convenio_raw.strip())