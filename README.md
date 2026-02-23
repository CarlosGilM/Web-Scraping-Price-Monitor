# 🛒 Mercado Livre Price Tracker

Este projeto é um rastreador de preços automatizado que realiza web scraping no Mercado Livre para monitorar produtos específicos cadastrados em um banco de dados Supabase. Ele foi desenvolvido com foco em precisão, filtrando resultados irrelevantes e armazenando o histórico de preços para análise.

## 🚀 Funcionalidades

* **Busca Dinâmica:** Lê a lista de termos de busca diretamente da tabela `produtos` no Supabase.
* **Filtro Literal Inteligente:** Utiliza expressões regulares (Regex) para garantir que o título do anúncio contenha exatamente os termos buscados (ex: evita que "iPhone 16" retorne resultados de "iPhone 15").
* **Normalização de Unidades:** Trata variações de escrita de armazenamento (ex: transforma `128 GB` e `128GB` em um padrão único para comparação).
* **Barreira de Qualidade:** Ignora automaticamente anúncios que contenham palavras como "recondicionado", "usado", "vitrine" ou "troca".
* **Histórico Automatizado:** Ordena os resultados pelo menor preço e salva o **Top 3** na tabela `historico_menor_preco`.

## 🛠️ Tecnologias

* **Linguagem:** Python 3.x
* **Scraping:** [BeautifulSoup4](https://www.crummy.com/software/BeautifulSoup/bs4/doc/) & [Requests](https://requests.readthedocs.io/)
* **Banco de Dados:** [Supabase](https://supabase.com/) (PostgreSQL)
* **Regex:** Módulo `re` para validação rigorosa de títulos.

## 📋 Pré-requisitos

1.  Uma conta no **Supabase**.
2.  Estrutura de tabelas necessária:
    * **Tabela `produtos`**: Coluna `termo_busca` (text) e `id`.
    * **Tabela `historico_menor_preco`**: Colunas `produto_id` (FK), `descricao` (text), `preco` (float) e `link` (text).

## ⚙️ Configuração e Instalação

1.  Clone o repositório:
    ```bash
    git clone https://github.com/CarlosGilM/Web-Scraping-Price-Monitor.git
    cd Web-Scraping-Price-Monitor
    ```

2.  Instale as dependências:
    ```bash
    pip install -r requirements.txt
    ```

3.  Configure o arquivo `.env`:
    Crie um arquivo `.env` na raiz do projeto e adicione suas credenciais:
    ```env
    SUPABASE_URL=https://seu-projeto.supabase.co
    SUPABASE_KEY=sua-chave-anon-publica
    ```

## 🚀 Como Executar

Para iniciar o rastreamento, execute o comando:
```bash
python main.py
 ```

O script percorrerá cada item da sua tabela de produtos, aplicará os filtros de limpeza e atualizará seu histórico no banco de dados.

## ⚠️ Observação sobre Bloqueios
Este script foi projetado para execução em ambiente local (Fins de estudos). A execução via GitHub Actions ou servidores de Data Center pode ser bloqueada pelo Mercado Livre devido a restrições de segurança.

