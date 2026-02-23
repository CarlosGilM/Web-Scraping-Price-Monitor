from playwright.sync_api import sync_playwright


def pegar_10_precos():
    with sync_playwright() as p:
        # Iniciamos em modo headless (invisível)
        browser = p.chromium.launch(headless=True)

        # AQUI ESTÁ A MÁGICA: Criamos um "contexto" disfarçado
        contexto = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        )

        # Abrimos a página usando esse contexto disfarçado
        page = contexto.new_page()

        print("Acessando a lista de busca de forma oculta...")
        page.goto("https://lista.mercadolivre.com.br/xiaomi-poco-x7-pro")

        try:
            print("Aguardando os resultados carregarem...")
            page.wait_for_selector('.ui-search-layout__item')

            print("Coletando os links dos 10 primeiros produtos...\n")
            produtos_na_tela = page.locator('.ui-search-layout__item').all()
            links_coletados = []

            for produto in produtos_na_tela[:10]:
                url_produto = produto.locator('a').first.get_attribute('href')
                if url_produto:
                    links_coletados.append(url_produto)

            for index, url in enumerate(links_coletados, start=1):
                try:
                    page.goto(url)
                    page.wait_for_selector('h1.ui-pdp-title', timeout=10000)

                    titulo = page.locator('h1.ui-pdp-title').inner_text()
                    preco = page.locator(
                        '.ui-pdp-price__second-line .andes-money-amount__fraction').first.inner_text()

                    print(f"[{index}/10] {titulo[:200]}")
                    print(f"         💰 Preço: R$ {preco}")
                    print(f"         🔗 Link:  {url}")
                    print("         " + "-"*40)

                except Exception as erro_individual:
                    print(f"[{index}/10] ❌ Erro ao ler este produto. Pulando...")
                    print("         " + "-"*40)

            print("\n🏁 Finalizado! Todos os produtos foram processados.")

        except Exception as e:
            print(f"Erro geral no script: {e}")

        browser.close()


if __name__ == "__main__":
    pegar_10_precos()
