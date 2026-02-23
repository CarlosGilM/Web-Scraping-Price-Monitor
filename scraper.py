import os
import time
import requests
import re  # <--- NOVO IMPORT PARA A BUSCA LITERAL
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

url_supabase: str = os.environ.get("SUPABASE_URL")
key_supabase: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url_supabase, key_supabase)


def rastrear_precos():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
    }

    print("🔍 Buscando lista de produtos no banco de dados...")
    resposta_produtos = supabase.table("produtos").select("*").execute()
    lista_produtos = resposta_produtos.data

    if not lista_produtos:
        print("Nenhum produto cadastrado no banco para monitorar.")
        return

    print(f"📦 Encontrei {len(lista_produtos)} produto(s) para monitorar!\n")
    print("=" * 60)

    for produto in lista_produtos:
        produto_id = produto['id']
        termo_busca = produto['termo_busca']

        termo_url = termo_busca.replace(' ', '-').lower()
        url = f'https://lista.mercadolivre.com.br/novo/{termo_url}'

        print(f"🌐 Raspando: \033[36m{termo_busca}\033[m")
        r = requests.get(url, headers=headers)

        if r.status_code != 200:
            print(
                f"Erro ao acessar {termo_busca}! Código HTTP: {r.status_code}\n")
            continue

        site = BeautifulSoup(r.content, 'html.parser')
        caixas_produtos = site.find_all('li', class_='ui-search-layout__item')

        if not caixas_produtos:
            print(f"Nenhum resultado encontrado para {termo_busca}.\n")
            continue

        produtos_validos = []
        termo_busca_lower = termo_busca.lower()

        # Divide o termo de busca em palavras (Ex: ['iphone', '16'])
        palavras_busca = termo_busca_lower.split()

        for i, caixa in enumerate(caixas_produtos[:15], start=1):
            link_tag = caixa.find('a', class_='poly-component__title')
            preco_tag = caixa.find(
                'span', class_='andes-money-amount__fraction')

            if link_tag and preco_tag:
                descricao = link_tag.get_text().strip()
                descricao_lower = descricao.lower()
                preco_texto = preco_tag.get_text().strip()
                link = link_tag.get('href')

        # ==========================================
        # NORMALIZAÇÃO DO TERMO DE BUSCA
        # Transforma '128 gb' em '128gb' para não dar erro na comparação
        # ==========================================
        termo_busca_lower = termo_busca.lower()
        termo_busca_norm = re.sub(
            r'(\d+)\s*(gb|tb)\b', r'\1\2', termo_busca_lower)
        palavras_busca = termo_busca_norm.split()

        for i, caixa in enumerate(caixas_produtos[:25], start=1):
            link_tag = caixa.find('a', class_='poly-component__title')
            preco_tag = caixa.find(
                'span', class_='andes-money-amount__fraction')

            if link_tag and preco_tag:
                descricao = link_tag.get_text().strip()
                descricao_lower = descricao.lower()
                preco_texto = preco_tag.get_text().strip()
                link = link_tag.get('href')

                # Normaliza o título do anúncio também (tira o espaço do GB/TB)
                descricao_norm = re.sub(
                    r'(\d+)\s*(gb|tb)\b', r'\1\2', descricao_lower)

                # ==========================================
                # VALIDAÇÃO 1: BUSCA LITERAL
                # ==========================================
                valido = True
                for palavra in palavras_busca:
                    # Agora procuramos no título normalizado (descricao_norm)
                    if not re.search(rf'\b{re.escape(palavra)}\b', descricao_norm):
                        valido = False
                        break

                if not valido:
                    print(
                        f"\033[90m[{i}] 🚫 Ignorado (Falso Positivo): {descricao}\033[m")
                    continue

                # ==========================================
                # VALIDAÇÃO 2: BARREIRA DE PALAVRAS PROIBIDAS
                # ==========================================
                palavras_proibidas = ['recondicionado',
                                      'usado', 'vitrine', 'troca']

                # Verifica se a palavra proibida está no título como palavra inteira (evita que 'pro' bloqueie a palavra 'produto')
                tem_palavra_proibida = any(
                    re.search(rf'\b{p}\b', descricao_lower) for p in palavras_proibidas)

                if tem_palavra_proibida:
                    print(
                        f"\033[90m[{i}] 🚫 Ignorado (Proibido): {descricao}\033[m")
                    continue

                # ==========================================
                # EXTRAÇÃO DO PREÇO
                # ==========================================
                try:
                    preco_num = float(preco_texto.replace('.', ''))

                    produtos_validos.append({
                        'produto_id': produto_id,
                        'descricao': descricao,
                        'preco': preco_num,
                        'preco_formatado': preco_texto,
                        'link': link
                    })
                except ValueError:
                    pass

        # ORDENAR, PEGAR OS 3 MAIS BARATOS E SALVAR
        if produtos_validos:
            produtos_validos = sorted(
                produtos_validos, key=lambda x: x['preco'])
            top_3 = produtos_validos[:3]

            print(f"🏆 Top {len(top_3)} mais baratos validados:")

            dados_insercao = []
            for index, p in enumerate(top_3, start=1):
                print(
                    f"   {index}º: \033[32mR$ {p['preco_formatado']}\033[m - {p['descricao']}")
                dados_insercao.append({
                    "produto_id": p["produto_id"],
                    "descricao": p["descricao"],
                    "preco": p["preco"],
                    "link": p["link"]
                })

            supabase.table("historico_menor_preco").insert(
                dados_insercao).execute()
            print("✅ Salvos no histórico!\n")
        else:
            print("⚠️ Nenhum produto válido passou pelos filtros.\n")

        time.sleep(2)

    print("🏁 Varredura completa para todos os produtos!")


if __name__ == "__main__":
    rastrear_precos()
