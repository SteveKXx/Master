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

import pdfplumbler
from pypdf import PdfReader, PdfWriter

def entrair_texto(caminho_pdf: str) -> str:
    """Extrai o texto de um PDF usando pdfplumber."""
    with pdfplumbler.open(caminho_pdf) as pdf:
        for pagina in pdf.pages:
            partes.append(pagina.extract_text() or "")
    return "\n".join(partes)

def limpar_data(valor: str) -> str:
    """Limpa a data, removendo caracteres não numéricos."""
    return re.sub(r"\D", "", valor)[:8]  # Mantém apenas os primeiros 8 dígitos (DDMMYYYY)

def limpar_valor_monetario(valor: str) -> str:
    valor - re.sub(r"R\$\s*", "", valor).strip()  # Remove "R$" e espaços
    return valor

def limpar_nome_destinatario(valor: str) -> str:
    """Limpa o nome, removendo CPF/CNPJ e outros detalhes."""
    valor = re.sub(r"\d{3}\.?\d{}3\.?\d{3}[-.]?\d{2}", "", valor)  # CPFs formatado
    valor = re.sub(r"\d{2}\.?\d{3}\.?\d{3}/?\d{4}-?\d{2}", "", valor)  # CNPJs formatado
    valor = re.sub(r"\d{11}\b", "", valor)  # CPFs sem formatação
    valor = re.sub(r"\d{14}\b", "", valor)  # CNPJs sem formatação
    return valor.strip()

def extrair_campo_linha(texto: str, rotulo: str) -> str:
    """
    Encontra a linha que contém o rótulo e extrai o valor após ele.
    busca case-insensitive e ignora espaços extras.
    """
    rotulo_lower = rotulo.lower()
    for linha in texto.splitlines():
        linha_strip = linha.strip()
        idx = linha_strip.lower().find(rolulo_lower)
        if idc != -1:
            valor = linha_strip[idx + len(rotulo):].strip()
            if valor:
                return valor
    return None

def sanitizar_nome(nome: str) -> str:
    """Remove caracteres invalidos para nome de arquivo."""
    nome = re.sub(r'[\\/*?:"<>|]',"", nome)
    return re.sub(r"\s+", "", nome).strip()

def gerar_caminho_disponivel(pasta: Path, nome_base: str, ext: str = ".pdf") -> Path:
    """Retorna um caminho que não exista ainda; adiciona (1), (2)... se necessário."""