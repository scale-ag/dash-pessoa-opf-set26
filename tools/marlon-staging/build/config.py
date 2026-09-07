# -*- coding: utf-8 -*-
"""
Configuração do cliente — MARLON MATTEDI / Funil de Venda Direta.

Este é o ÚNICO arquivo que precisa ser editado para ajustar o funil deste
cliente. Depois de editar, teste localmente:

    python build/build.py --meta-file meta.csv --sales-file sales.csv --out dist/index.html

`build/config.example.py` é a cópia intacta do modelo, para consulta.
Todos os valores abaixo foram medidos nas planilhas reais em 07/09/2026
(ver CLAUDE.md, seção "Fontes de dados").
"""
from __future__ import annotations

# ==========================================================================
# 1) PLANILHAS DO CLIENTE (Google Sheets)
# ==========================================================================
# Este cliente usa DUAS planilhas separadas. SPREADSHEET_ID_SALES cobre esse
# caso: quando vazio, o build lê as duas abas da mesma planilha do Meta.
#
# Meta Ads:     https://docs.google.com/spreadsheets/d/1oXEzPBmdYVGD-2gplchyHK0t6nz4JdtlDTnB5skqZPY/
#               aba única "Meta Ads" (gid 0), 9 colunas.
# Compradores:  https://docs.google.com/spreadsheets/d/18OmJKQHTcjyz3z2i1cisQL9WJGRt27lxU97LRA4Znak/
#               ATENÇÃO: esta planilha tem DUAS abas com o MESMO cabeçalho —
#               "Vendas" (gid 0, histórico, ~442 linhas, desde 08/07/2026) e
#               "Novas Vendas" (gid 659512725, ~47 linhas, desde 01/09/2026).
#               O gestor pediu a aba NOVAS VENDAS: gid 659512725.
#               Trocar por engano para gid 0 muda a base inteira da dashboard.
# Ambas lidas via export CSV público — SOMENTE LEITURA, o build nunca escreve.
SPREADSHEET_ID = "1oXEzPBmdYVGD-2gplchyHK0t6nz4JdtlDTnB5skqZPY"
SPREADSHEET_ID_SALES = "18OmJKQHTcjyz3z2i1cisQL9WJGRt27lxU97LRA4Znak"
GID_META = "0"                       # aba "Meta Ads" (9 colunas)
GID_SALES = "659512725"              # aba "Novas Vendas" (19 colunas)

# ==========================================================================
# 2) REGRAS DE NEGÓCIO
# ==========================================================================
# Fator de imposto sobre o gasto do Meta Ads (toggle "Imposto Meta" na topbar).
TAX_FACTOR = 1.13806   # +13,806%

# Produto principal do funil. O match é por PREFIXO sobre o nome NORMALIZADO
# (sem acento, minúsculas) da coluna PRODUTO — por isso o valor abaixo também
# precisa estar sem acento e em minúsculas.
# Distribuição real na aba Novas Vendas (47 linhas):
#   TREINO CONTROLE 2.0 .... 42   <- produto principal
#   O Treino do Leão ........  4   (outro funil; entra só em Faturamento/ROAS)
#   Control 2.0 Training ....  1   (versão em inglês; NÃO casa com o prefixo)
MAIN_PRODUCT_PREFIX = "treino controle 2.0"

# Coluna UTM que carrega o Ad Name do Meta. Verificado nos dados em 07/09/2026,
# na aba Novas Vendas (7 linhas com UTM contra 15 Ad Names do Meta):
#   utm_campaign -> Campaign Name ..... 7 de 7 batem
#   utm_medium   -> Ad Set Name ....... 7 de 7 batem
#   utm_content  -> Ad Name ........... 7 de 7 batem   <- é esta
#   utm_term     -> Ad Name ........... 0 de 7 batem
# O utm_term deste cliente traz o Ad Name CONCATENADO com o posicionamento
# ("AD01 - Seguro 20 segundos_Instagram_Reels"), por isso não casa com nada.
# Casar pela coluna errada zeraria todas as atribuições.
AD_UTM_COLUMN = "utm_content"

# A aba Novas Vendas TEM coluna de status confiável ("Status", índice 11) com
# os valores approved / refunded / chargeback (padrão Hotmart, em inglês).
# Por isso False: o build filtra por is_paid() e descarta reembolso/chargeback.
# (Hoje as 47 linhas da aba são todas "approved", mas a aba "Vendas" já tem
#  35 refunded + 3 chargeback — deixar False evita contar estorno como venda
#  assim que o primeiro aparecer nesta aba.)
COUNT_ALL_AS_PAID = False

# ==========================================================================
# 3) RÓTULOS EXIBIDOS NA INTERFACE
# ==========================================================================
CLIENT_NAME = "MARLON MATTEDI"
CLIENT_SUB = "TRÁFEGO DIRETO"
TAX_LABEL = "Imposto Meta ×1,13806"
MAIN_PRODUCT = "Treino Controle 2.0"

# ==========================================================================
# 4) METAS (aba Relatórios) — código de cor de CAC/ROAS
# ==========================================================================
#   • ROAS: quanto MAIOR, melhor  -> desempenho = roas / ROAS_TARGET
#   • CAC : quanto MENOR, melhor  -> desempenho = CAC_TARGET / cac
# Faixas: <REPORT_BAND_LOW vermelho · até 0,99 amarelo · até REPORT_BAND_HIGH
# verde · acima disso azul-ciano.
#
# CAC_TARGET = 200,00 definido pelo gestor em 07/09/2026.
# ROAS_TARGET derivado para ficar COERENTE com esse CAC: as duas metas medem a
# mesma coisa quando ROAS_TARGET = ticket médio / CAC_TARGET. Ticket médio real
# da aba Novas Vendas no período 01–06/09/2026: R$ 11.627,68 / 47 = R$ 247,40.
#   247,40 / 200,00 = 1,237  ->  1.24
# Se o gestor definir um ROAS alvo próprio, troque abaixo e mantenha a conta em
# mente: mudar só um dos dois faz CAC e ROAS pintarem cores contraditórias.
CAC_TARGET = 200.00
ROAS_TARGET = 1.24
REPORT_BAND_LOW = 0.70
REPORT_BAND_HIGH = 1.30

# ==========================================================================
# 5) IA INSIGHTS (Cloudflare Worker) — ver SETUP-IA.md
# ==========================================================================
# Vazio = aba IA Insights indisponível (o resto da dashboard funciona normal).
# Preencher depois de publicar o Worker (passos 7-10 do checklist em CLAUDE.md).
IA_WORKER_URL = ""
