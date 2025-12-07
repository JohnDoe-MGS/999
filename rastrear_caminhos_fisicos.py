import re
import zlib

def rastrear_caminhos_fisicos(caminho_arquivo):
    print(f"--- Varredura Forense de Caminhos de Diretório (Localização Física) ---\n")
    
    try:
        # Lemos o arquivo em modo binário para não corromper os dados comprimidos
        with open(caminho_arquivo, 'rb') as f:
            conteudo_binario = f.read()

        # 1. Encontrar todos os streams de dados (onde o texto e metadados profundos vivem)
        padrao_stream = re.compile(b'stream\r\n(.*?)\r\nendstream', re.DOTALL)
        streams = padrao_stream.findall(conteudo_binario)
        
        print(f"[1] Processando {len(streams)} blocos de dados profundos...")
        
        texto_total = ""
        
        # Descomprimir e acumular tudo o que for texto
        for dados in streams:
            try:
                # Tenta descomprimir
                descomprimido = zlib.decompress(dados)
                # Tenta converter bytes para texto (latin-1 para garantir que lemos tudo)
                texto_total += descomprimido.decode('latin-1', errors='ignore')
            except:
                continue # Se falhar (ex: imagem), ignora

        # Adicionar também o texto não comprimido (cabeçalhos, trailers)
        texto_total += conteudo_binario.decode('latin-1', errors='ignore')

        # 2. Padrões de Busca Forense (Regex)
        # Procura por: C:\Users\..., D:\..., \\Servidor\..., /Users/... (Mac)
        padrao_win = r'[a-zA-Z]:\\[\\\S| ]+' 
        padrao_rede = r'\\\\[a-zA-Z0-9-]+\\[\\\S| ]+'
        padrao_mac = r'/Users/[a-zA-Z0-9-]+/[/\S| ]+'
        
        caminhos_win = re.findall(padrao_win, texto_total)
        caminhos_rede = re.findall(padrao_rede, texto_total)
        caminhos_mac = re.findall(padrao_mac, texto_total)

        encontrou_algo = False

        print(f"\n[2] Resultados da Varredura de Diretórios")
        
        if caminhos_win:
            encontrou_algo = True
            print("   [ALERTA] Caminhos Windows encontrados:")
            for c in set(caminhos_win): # set() remove duplicatas
                # Filtra lixo curto
                if len(c) > 8 and "Windows" not in c: 
                    print(f"    -> {c}")
                    print("       (Análise: O nome após 'Users' revela o login real da máquina)")

        if caminhos_rede:
            encontrou_algo = True
            print("   [ALERTA] Caminhos de Rede (Servidor) encontrados:")
            for c in set(caminhos_rede):
                print(f"    -> {c}")
                print("       (Análise: Revela o nome do servidor físico da empresa)")

        if caminhos_mac:
            encontrou_algo = True
            print("   [ALERTA] Caminhos Apple/Mac encontrados:")
            for c in set(caminhos_mac):
                print(f"    -> {c}")

        if not encontrou_algo:
            print("   [-] Nenhum caminho de diretório explícito encontrado.")
            print("   Isso indica que o Word limpou o 'Title' ou o arquivo não foi salvo antes de exportar.")

        # 3. Busca por padrões de 'Save As' no XMP
        # Às vezes o histórico de salvamento fica no XML
        print(f"\n[3] Análise de Histórico XMP")
        if "History" in texto_total:
            print("   [!] O bloco de histórico XMP foi detectado.")
            # Tentativa de extrair ações de salvamento
            acoes = re.findall(r'stEvt:action>(.*?)</stEvt:action', texto_total)
            print(f"   Ações registradas: {acoes}")
        else:
            print("   [-] Histórico de edição limpo ou inexistente.")

    except Exception as e:
        print(f"Erro Crítico: {e}")

# Executar
rastrear_caminhos_fisicos('analise_pdf.txt') # Use o nome do seu arquivo aqui
