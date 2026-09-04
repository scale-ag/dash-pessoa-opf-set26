# -*- coding: utf-8 -*-
"""
Configuração do cliente — FERNANDO PESSOA / Operação da Prova à Farda.

Este é o ÚNICO arquivo que precisa ser editado para ajustar o funil deste
cliente. Depois de editar, teste localmente:

    python build/build.py --meta-file meta.csv --sales-file sales.csv --out dist/index.html

`build/config.example.py` é a cópia intacta do modelo, para consulta.
"""
from __future__ import annotations

# ==========================================================================
# 1) PLANILHAS DO CLIENTE (Google Sheets)
# ==========================================================================
# Este cliente usa DUAS planilhas separadas (o template padrão assume uma só,
# com dois gids). SPREADSHEET_ID_SALES cobre esse caso: quando vazio, o build
# lê as duas abas da mesma planilha do Meta (comportamento original).
#
# Meta Ads:     https://docs.google.com/spreadsheets/d/1BLv_PQ3eHD0hPQjUckx5SkkUTpHLaU-ODAHWA_biKpU/
# Compradores:  https://docs.google.com/spreadsheets/d/1DXw8stvgyBo7AO-7hf2TSX1nt34v7yroJHmfge3bnPI/
# Ambas lidas via export CSV público — SOMENTE LEITURA, o build nunca escreve.
SPREADSHEET_ID = "1BLv_PQ3eHD0hPQjUckx5SkkUTpHLaU-ODAHWA_biKpU"
SPREADSHEET_ID_SALES = "1DXw8stvgyBo7AO-7hf2TSX1nt34v7yroJHmfge3bnPI"
GID_META = "0"                      # aba Meta Ads (9 colunas)
GID_SALES = "151354425"              # aba BASE COMPLETA (55 colunas)

# ==========================================================================
# 2) REGRAS DE NEGÓCIO
# ==========================================================================
# Fator de imposto sobre o gasto do Meta Ads (toggle "Imposto Meta" na topbar).
TAX_FACTOR = 1.13806   # +13,806%

# Produto principal do funil. O match é por PREFIXO sobre o nome NORMALIZADO
# (sem acento, minúsculas) da coluna PRODUTO — por isso o valor abaixo também
# precisa estar sem acento e em minúsculas.
# Na planilha, PRODUTO = "OPERAÇÃO DA PROVA À FARDA" em 100% das linhas.
MAIN_PRODUCT_PREFIX = "operacao da prova a farda"

# A aba BASE COMPLETA não tem coluna de status de pagamento — toda linha já é
# uma inscrição paga (ingresso do evento). Por isso True.
COUNT_ALL_AS_PAID = True

# ==========================================================================
# 3) RÓTULOS EXIBIDOS NA INTERFACE
# ==========================================================================
CLIENT_NAME = "FERNANDO PESSOA"
CLIENT_SUB = "OPERAÇÃO DA PROVA À FARDA"
TAX_LABEL = "Imposto Meta ×1,13806"
MAIN_PRODUCT = "Operação da Prova à Farda"

# ==========================================================================
# 4) METAS (aba Relatórios) — código de cor de CAC/ROAS
# ==========================================================================
#   • ROAS: quanto MAIOR, melhor  -> desempenho = roas / ROAS_TARGET
#   • CAC : quanto MENOR, melhor  -> desempenho = CAC_TARGET / cac
# Faixas: <REPORT_BAND_LOW vermelho · até 0,99 amarelo · até REPORT_BAND_HIGH
# verde · acima disso azul-ciano.
#
# PROVISÓRIO — alinhar com o gestor. Critério usado: break-even no front-end,
# ou seja, CAC alvo = ticket líquido do lote atual do ingresso (R$ 39,33) e
# ROAS alvo = 1,00. Num lançamento pago o resultado real vem do back-end
# (Mentoria Elite), que não está nesta planilha; se a meta for adquirir
# inscrito no prejuízo controlado, suba o CAC_TARGET e baixe o ROAS_TARGET.
CAC_TARGET = 39.33
ROAS_TARGET = 1.00
REPORT_BAND_LOW = 0.70
REPORT_BAND_HIGH = 1.30

# ==========================================================================
# 5) IA INSIGHTS (Cloudflare Worker) — ver SETUP-IA.md
# ==========================================================================
# Vazio = aba IA Insights indisponível. Preencher depois de publicar o Worker
# (passos 7-10 do checklist em CLAUDE.md).
IA_WORKER_URL = ""
