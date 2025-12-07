<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dissecador Forense de PDF | Compliance</title>
    
    <link rel="stylesheet" href="https://pyscript.net/releases/2023.05.1/pyscript.css" />
    <script defer src="https://pyscript.net/releases/2023.05.1/pyscript.js"></script>

    <style>
        :root { --bg-color: #0d1117; --text-color: #c9d1d9; --accent-color: #58a6ff; --border-color: #30363d; --success-color: #238636; }
        body { font-family: 'Courier New', Courier, monospace; background-color: var(--bg-color); color: var(--text-color); margin: 0; padding: 20px; line-height: 1.6; }
        .container { max-width: 900px; margin: 0 auto; }
        h1 { color: var(--accent-color); border-bottom: 1px solid var(--border-color); padding-bottom: 10px; }
        .input-section { background-color: #161b22; padding: 20px; border-radius: 6px; border: 1px solid var(--border-color); margin-bottom: 20px; }
        label { display: block; margin-bottom: 10px; font-weight: bold; }
        textarea { width: 100%; height: 200px; background-color: #0d1117; color: #79c0ff; border: 1px solid var(--border-color); border-radius: 4px; padding: 10px; font-family: monospace; resize: vertical; }
        button { background-color: var(--success-color); color: white; border: none; padding: 10px 20px; border-radius: 6px; font-size: 16px; cursor: pointer; margin-top: 10px; font-family: 'Courier New', monospace; font-weight: bold; }
        button:hover { opacity: 0.9; }
        #output { background-color: #161b22; padding: 20px; border-radius: 6px; border: 1px solid var(--border-color); white-space: pre-wrap; min-height: 100px; margin-top: 20px;}
        .loading { color: #d29922; font-size: 0.9em; margin-top: 5px; display: none;}
    </style>
</head>
<body>

<div class="container">
    <h1>🕵️ Dissecador Forense de PDF</h1>
    <p>Ferramenta de análise de integridade, UUIDs e metadados para Compliance.</p>

    <div class="input-section">
        <label for="pdf_content">Cole o Código Bruto do PDF aqui (Texto):</label>
        <textarea id="pdf_content" placeholder="Cole o conteúdo do arquivo .txt ou PDF aqui (começando com %PDF-1.7...)"></textarea>
        
        <button id="analyze-btn" py-click="analisar_codigo">Executar Análise Forense</button>
        <div id="status_msg" class="loading">Carregando motor Python... (Aguarde alguns segundos)</div>
    </div>

    <h3>Relatório de Análise:</h3>
    <div id="output">O relatório aparecerá aqui...</div>
</div>

<py-script>
import re
import uuid
import struct
# Importação direta do DOM do navegador para evitar erros do PyScript
from js import document

def formatar_data_pdf(raw_date):
    try:
        limpo = raw_date.replace("D:", "").replace("'", "")
        data_parte = limpo[:14]
        # Formatação básica
        ano = data_parte[0:4]
        mes = data_parte[4:6]
        dia = data_parte[6:8]
        hora = data_parte[8:10]
        min = data_parte[10:12]
        return f"{dia}/{mes}/{ano} às {hora}:{min}"
    except:
        return raw_date

def analisar_codigo(*args):
    # 1. Pega o valor usando a API padrão do Javascript (mais seguro)
    input_el = document.getElementById("pdf_content")
    conteudo = input_el.value
    output_div = document.getElementById("output")
    
    # Feedback visual de carregamento
    output_div.innerText = "Processando... Por favor aguarde."

    if not conteudo:
        output_div.innerText = "ERRO: A caixa de texto está vazia. Por favor, cole o código do PDF."
        return

    relatorio = []
    relatorio.append("--- RELATÓRIO TÉCNICO DE COMPLIANCE ---\n")

    try:
        # --- 1. IDENTIDADE ---
        autor = re.search(r'/Author\((.*?)\)', conteudo)
        criador = re.search(r'/Creator\((.*?)\)', conteudo)
        
        relatorio.append(f"[1] IDENTIDADE DECLARADA")
        if autor:
            relatorio.append(f"    Autor:    {autor.group(1)}")
        else:
            relatorio.append("    Autor:    Não encontrado")
            
        if criador:
            relatorio.append(f"    Software: {criador.group(1)}")

        # --- 2. INTEGRIDADE E UUIDs ---
        relatorio.append(f"\n[2] INTEGRIDADE E UUIDs")
        # Regex ajustado para pegar o conteúdo exato do XML
        doc_id_match = re.search(r'xmpMM:DocumentID>uuid:(.*?)</xmpMM:DocumentID', conteudo)
        inst_id_match = re.search(r'xmpMM:InstanceID>uuid:(.*?)</xmpMM:InstanceID', conteudo)
        
        if doc_id_match and inst_id_match:
            doc_id = doc_id_match.group(1)
            inst_id = inst_id_match.group(1)
            
            relatorio.append(f"    Document ID: {doc_id}")
            relatorio.append(f"    Instance ID: {inst_id}")
            
            if doc_id == inst_id:
                relatorio.append("    VEREDITO: ✅ ARQUIVO ORIGINAL (Não editado)")
            else:
                relatorio.append("    VEREDITO: ⚠️ ARQUIVO MODIFICADO/DERIVADO")
        else:
            relatorio.append("    IDs XMP não encontrados (Verifique se copiou o XML completo).")

        # --- 3. DATAS ---
        data_criacao = re.search(r'/CreationDate\((.*?)\)', conteudo)
        if data_criacao:
            relatorio.append(f"\n[3] DATA E FUSO")
            raw_data = data_criacao.group(1)
            relatorio.append(f"    Data Crua: {raw_data}")
            relatorio.append(f"    Formatada: {formatar_data_pdf(raw_data)}")
            if "-03'00" in raw_data:
                relatorio.append("    Fuso: -03:00 (Indicativo de Brasil)")

        # --- 4. LINKS (SOUZA FREITAS) ---
        links = re.findall(r'/URI\((http.*?)\)', conteudo)
        if links:
            relatorio.append(f"\n[4] VÍNCULOS ENCONTRADOS")
            for link in links:
                relatorio.append(f"    -> {link}")
        
    except Exception as e:
        relatorio.append(f"\n[ERRO CRÍTICO NO SCRIPT]: {str(e)}")

    # Escreve o resultado final na tela
    output_div.innerText = "\n".join(relatorio)

</py-script>

</body>
</html>
