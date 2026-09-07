# CLAUDE.md — Dashboard de Controle de Tráfego Pago (TEMPLATE)

> Este arquivo é lido automaticamente pelo Claude Code ao abrir o repositório.
> Repositório **configurado para o cliente MARLON MATTEDI** (Funil de Venda
> Direta; a conta roda **duas siglas**, `C20` e `EXP` — ver abaixo). A engine (`build/template.html`, `build/build.py`,
> `ia-worker/worker.js`) é genérica e não deve ser editada por cliente; os
> valores do cliente ficam em **`build/config.py`** (config do funil) e
> **`config.js`** (metadados de publicação no GitHub). Veja também `README.md`
> para a visão geral e o passo a passo completo de publicação.

---

## ✅ CHECKLIST DE NOVO CLIENTE

Ordem para colocar um cliente novo no ar. Cada item aponta o arquivo e o marcador.

1. [ ] **Config do cliente** — copie `build/config.example.py` para
   `build/config.py` e preencha (comentado campo a campo no próprio arquivo):
   - `SPREADSHEET_ID`, `GID_META`, `GID_SALES` (planilha do cliente)
   - `TAX_FACTOR`, `MAIN_PRODUCT_PREFIX`, `COUNT_ALL_AS_PAID` (regras de negócio)
   - `AD_UTM_COLUMN` — qual coluna UTM carrega o `Ad Name` do Meta (`utm_content`
     por padrão, mas **confira nos dados**: casar pela coluna errada zera as
     atribuições e a aba Meta Ads fica com gasto e zero venda)
   - `CLIENT_NAME`, `CLIENT_SUB`, `TAX_LABEL`, `MAIN_PRODUCT` (rótulos exibidos)
   - `CAC_TARGET`, `ROAS_TARGET`, `REPORT_BAND_LOW`, `REPORT_BAND_HIGH` (metas da aba Relatórios)
2. [ ] **Este arquivo (`CLAUDE.md`)** — preencher a seção "Fontes de dados" abaixo
   com a planilha real do cliente (abas/colunas) e ajustar a regra de
   atribuição/produto principal se for diferente do padrão do template.
3. [ ] **`README.md`** — preencher: título, nome do produto principal (o resto
   já lê de `config.js`/`build/config.py`).
4. [ ] **`config.js`** (raiz do repo) — copie `config.example.js` para
   `config.js` e preencha `GITHUB_USERNAME`, `GITHUB_REPOSITORY`,
   `PROJECT_NAME`. Depois substitua manualmente os placeholders
   `scale-ag`/`dash-marlon-mattedi` que aparecem em `SETUP-CRON.md` e
   `README.md` pelos mesmos valores (são docs Markdown estáticos, a
   substituição não é automática).
5. [ ] **`SETUP-CRON.md`** — depois do passo acima, gere um **token
   fine-grained novo** (GitHub → Settings → Developer settings → Fine-grained
   tokens) escopado só para esse repositório, permissão Actions: Read and
   write; cadastre no cron-job.org (nunca commitar o token).
6. [ ] **GitHub Pages** — confirmar que o workflow `.github/workflows/deploy.yml`
   está na branch `main` e que o Pages foi habilitado (ele se autoconfigura na
   1ª execução via `actions/configure-pages`).
7. [ ] **Worker da IA Insights** — criar um Worker novo na Cloudflare (nome
   próprio do cliente) e ajustar `ia-worker/wrangler.toml` (`name = "..."`,
   troque o placeholder `nomecliente-ia-insights`). Passo a passo completo em
   `SETUP-IA.md`.
8. [ ] **4 Secrets do repositório no GitHub** (Settings → Secrets and variables →
   Actions → New repository secret):
   - `CLOUDFLARE_API_TOKEN`
   - `CLOUDFLARE_ACCOUNT_ID`
   - `ANTHROPIC_API_KEY`
   - `INSIGHTS_PASSWORD`
9. [ ] **Disparar o primeiro deploy do Worker** — um commit tocando qualquer
   arquivo dentro de `ia-worker/` já dispara `.github/workflows/deploy-worker.yml`
   automaticamente (ou rode manualmente pela aba Actions, se o workflow tiver
   `workflow_dispatch`).
10. [ ] **Embutir a URL do Worker no build** — copiar a URL do Worker (exibida na
    Cloudflare) para `IA_WORKER_URL` em `build/config.py` e rodar/disparar um novo
    build. Isso faz os insights aparecerem para **qualquer visitante**, em qualquer
    navegador, sem precisar configurar nada — a persistência é no Worker (KV), não
    no navegador. Na aba **IA Insights** → **⚙ Configurar**, só é preciso colar a
    senha (a mesma do secret `INSIGHTS_PASSWORD`) para poder **gerar** novos
    insights; o campo "Worker URL" ali é opcional (só para apontar a um backend
    diferente do padrão embutido).
11. [ ] **Testar** — clicar em **Gerar insights** e confirmar que os cards aparecem
    (e continuam aparecendo depois de recarregar a página em outro navegador).

---

## O que é

Dashboard de **Controle de Tráfego Pago** — app de BI estático (HTML/CSS/JS + Chart.js
via CDN) publicado no **GitHub Pages**, que cruza o gerenciador **Meta Ads** com a lista
de **Compradores** e se atualiza a cada ~30 min (build na nuvem via GitHub Actions,
disparado pelo cron-job.org). **Somente leitura** das planilhas.

- **URL pública:** `https://scale-ag.github.io/dash-marlon-mattedi/`
  (preencha `config.js` — ver checklist acima)
- **Cliente/projeto:** MARLON MATTEDI — TRÁFEGO DIRETO (`CLIENT_NAME`/`CLIENT_SUB` em `build/config.py`)
- **Tipo de funil:** Venda direta / tráfego direto (não há etapa de Leads/MQL) —
  `Gasto → Impressões → Cliques → Page Views → Checkouts → Vendas → Faturamento`

## Fontes de dados (Google Sheets)

Este cliente usa **duas planilhas separadas** (o template padrão assume uma só,
com dois gids). Por isso `build/config.py` tem `SPREADSHEET_ID_SALES` além de
`SPREADSHEET_ID`; quando `SPREADSHEET_ID_SALES` está vazio, o build volta ao
comportamento original (as duas abas na mesma planilha). Leitura via export CSV,
**somente leitura**.

| Fonte | Planilha (`SPREADSHEET_ID*`) | gid | Aba |
|-------|------------------------------|-----|-----|
| **Meta Ads** | `1oXEzPBmdYVGD-2gplchyHK0t6nz4JdtlDTnB5skqZPY` | `0` | **Meta Ads** (aba única, 9 colunas) |
| **Compradores** | `18OmJKQHTcjyz3z2i1cisQL9WJGRt27lxU97LRA4Znak` | `659512725` | **Novas Vendas** (19 colunas) |

⚠️ A planilha de Compradores tem **duas abas com o cabeçalho idêntico**:
`Vendas` (gid `0`, histórico completo — ~442 linhas desde 08/07/2026) e
`Novas Vendas` (gid `659512725` — ~47 linhas desde 01/09/2026). O gestor pediu
a **Novas Vendas**. Como os cabeçalhos são iguais, trocar o gid por engano
**não gera erro nenhum** — só muda silenciosamente a base inteira da dashboard
(de 47 para 442 vendas). Confira o gid antes de mexer.

**Colunas reais — Meta Ads** (9 colunas; o `header_index` casa por nome, então
a ordem não importa):
`Day · Campaign Name · Ad Set Name · Ad Name · Impressions · Link Clicks ·
Landing Page Views · Checkouts Initiated · Amount Spent`

**Colunas reais — Novas Vendas** (19 colunas, todas listadas):
`Transação` (0) · `Produto` (1) · `Nome` (2) · `E-mail` (3) · `Data` (4) ·
`Valor` (5) · `Moeda` (6) · `Taxas` (7) · **`Faturamento`** (8, coluna de
receita) · `Moeda da comissão` (9) · `Pagamento` (10) · **`Status`** (11) ·
`Canal` (12) · `Origem` (13) · `utm_source` (14) · `utm_medium` (15) ·
`utm_term` (16) · `utm_campaign` (17) · **`utm_content`** (18)

### Pontos de atenção deste cliente (verificados na planilha em 07/09/2026)

1. **O Ad Name vem de `utm_content`** (o padrão do template). Medido na aba
   Novas Vendas — 7 linhas com UTM preenchida contra os 15 `Ad Name` do Meta:

   | coluna UTM | preenchidas | Campaign Name | Ad Set Name | Ad Name |
   |---|---|---|---|---|
   | `utm_campaign` | 7 | **7** | 0 | 0 |
   | `utm_medium` | 7 | 0 | **7** | 0 |
   | `utm_term` | 7 | 0 | 0 | 0 |
   | `utm_content` | 7 | 0 | 0 | **7** |

   Mapeamento deste cliente:
   `utm_campaign → Campaign Name` · `utm_medium → Ad Set Name` · `utm_content → Ad Name`.
   O `utm_term` traz o Ad Name **concatenado com o posicionamento**
   (`AD01 - Seguro 20 segundos_Instagram_Reels`), por isso casa com zero — é a
   armadilha do problema conhecido #8. Configurado em `AD_UTM_COLUMN = "utm_content"`.

   ⚠️ **Limite que permanece:** só **7 das 47** linhas da aba Novas Vendas têm
   UTM preenchida — as outras 40 chegam sem rastreamento (`Canal` = `direto` em
   36 delas). Com o match correto, as 7 casam **100%** com o Meta (campanha
   *e* anúncio juntos). Ou seja: a aba Meta Ads mostra vendas corretamente, mas
   cobre ~15% do total. Isso é rastreamento faltando no checkout, não bug do
   build — garantir que o link do anúncio leve as UTMs até o checkout em
   **todas** as compras.
2. **Janelas de data batem** (diferente de outros clientes): Meta Ads
   01–07/09/2026 e Novas Vendas 01–06/09/2026. CAC/ROAS por período comparam
   gasto e vendas da mesma janela — os números são confiáveis.
3. **Tem coluna de status de pagamento** (`Status`, índice 11, valores
   `approved` / `refunded` / `chargeback`) → `COUNT_ALL_AS_PAID = False`, o
   build filtra estorno e chargeback por `is_paid()`.
   ⚠️ **Correção feita na engine por causa disso:** o `is_paid()` original só
   reconhecia status em português — e `"aprov"` **não** é substring de
   `"approved"` (a-p-**p**-r-o-v). Com `COUNT_ALL_AS_PAID = False`, isso
   descartaria **todas** as 47 vendas e a dashboard zeraria. Foi acrescentado
   `"approv"` à lista em `build/build.py`. A correção é genérica (serve a
   qualquer cliente Hotmart em inglês), não específica deste cliente.
4. **Receita**: usar `Faturamento` (índice 8) = `Valor` − `Taxas`. Ticket médio
   no período: **R$ 247,40** (R$ 11.627,68 / 47 vendas aprovadas).
5. **Sem coluna de permalink do criativo** na aba Meta Ads → o Top/Piores
   anúncios da aba Relatórios aparece **sem link** para o criativo. Para
   ativar, basta acrescentar a coluna `Creative Instagram Permalink` na
   planilha do Meta.
6. **Três produtos na aba**, só um é o principal:
   `TREINO CONTROLE 2.0` (42 linhas, **produto principal**) ·
   `O Treino do Leão` (4, outro funil) · `Control 2.0 Training` (1, versão em
   inglês — **não** casa com o prefixo `treino controle 2.0`, então conta só em
   Faturamento/ROAS, não em Vendas/CAC).
7. **As colunas `Nome` e `E-mail` vêm vazias** em toda a amostra inspecionada —
   a tabela de Vendas mostra `—` nessas colunas. É cosmético: o e-mail é
   mascarado de qualquer forma antes de ir para a página pública.

### Sigla do funil / convenção de campanha

**Esta conta roda DUAS siglas de funil**, e por decisão do gestor (07/09/2026)
a dashboard **cobre as duas**, sem eleger uma principal e sem filtrar nada:

| sigla | campanhas | linhas | gasto no período | anúncios |
|---|---|---|---|---|
| **C20** | 3 | 74 | R$ 2.232,02 (95%) | `AD01`–`AD07` e `AD0x-20-RM` |
| **EXP** | 1 | 11 | R$ 118,33 (5%) | `AD01-EX`, `AD05-EX`, `AD10-EX`, `AD14-EX` |

Campanhas (período 01–07/09/2026, gasto total R$ 2.350,35):
- `C20 | E4-VEN | P2-FRIO | VND | CBO | 2026-07-23 | BR | Aberto ADV — 04.Ago`
- `C20 | E4-VEN | P1-QUENTE | VND | ABO | 2026-08-14 | BR | All in one`
- `C20 | E4-VEN | P2-FRIO | VND | CBO | 2026-09-03 | BR | Aberto ADV`
- `EXP | E4-VEN | P2-FRIO | VND | ABO | 2026-08-22 | BR | Aberto ADV`

`C20` casa com o produto principal (**TREINO CONTROLE 2.0**) — as 7 vendas
atribuídas no período vieram todas de campanhas `C20`. A `EXP` teve gasto no
período mas nenhuma venda atribuída.

⚠️ **A engine não filtra por sigla** — ela lê todas as linhas do Meta. Se um dia
o gestor quiser a dashboard restrita a um funil só, isso é uma alteração de
engine (filtro por prefixo de `Campaign Name`), que hoje não existe.

Conjuntos no padrão `AUTO | H | 18 a 65 | BR | Aberto ADV`
(3 distintos: `18 a 65 | BR | Aberto ADV`, `18 a 54 | BR | All in one`,
`18 a 65 | BR | Aberto ADV | LPV2`).

### Critério de MQL

Funil de **venda direta**: o comprador vai do anúncio ao checkout, sem etapa de
captação. **Não há etapa de Leads/MQL nesta dashboard.**

URL de export CSV: `https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/export?format=csv&gid={GID}`

### Métricas do funil (`build.py` + `template.html`)
`Gasto → Impressões → Cliques → Page Views → Checkouts → Vendas → Faturamento`

Gasto · Impressões · CPM · Cliques · CPC · CTR · Page Views · CPV · CR (Cliques/PageViews) ·
Checkouts · CPIC · VisCHK (Checkouts/PageViews) · Vendas · CAC (Gasto/Vendas) ·
ConvCHK (Vendas/Checkouts) · Faturamento · ROAS (Faturamento/Gasto) · Ticket (Faturamento/Vendas).

### Produto principal / atribuição
- **Produto principal** = `MAIN_PRODUCT_PREFIX` (definido em `build/config.py`). Base de
  **Vendas / CAC / ConvCHK / Ticket**.
- **Faturamento / ROAS** = soma de **todos os produtos** do funil (orderbumps/upsells).
- Uma venda entra no funil se: é o produto principal **OU** a combinação **`UTM Campaign`
  + `UTM Content`** (campanha + anúncio) casa com uma linha real do Meta (captura
  orderbumps/upsells que carregam a UTM do anúncio). O match exige campanha **e**
  anúncio juntos — nomes de anúncio (`AD01`, `AD02`...) podem se repetir entre campanhas
  diferentes; casar só pelo nome do anúncio atribuiria a venda à campanha errada. Quando
  casa, a venda herda a campanha/conjunto **reais do Meta** (fica na mesma linha do
  gasto nas tabelas). Vendas de outros funis (UTM/produto não relacionados) ficam de
  fora. Só conta status pago.
- Se não houver coluna de Receita, não há Receita/ROAS/Ticket — ajuste o texto desta
  seção se o cliente novo tiver uma regra diferente.

### Imposto Meta Ads
Toggle ON aplica o `TAX_FACTOR` (definido em `build/config.py`) sobre os custos do Meta.

### Convenções de campanha
Neste cliente (verificado nos dados, ver "Pontos de atenção" #1):
`Campaign Name = utm_campaign` · `Ad Set Name = utm_medium` · **`Ad Name = utm_content`**
(o `utm_term` carrega o Ad Name concatenado com o posicionamento e casa com zero).
Qual coluna o build usa para o anúncio é definido por `AD_UTM_COLUMN` em
`build/config.py` — aqui, `"utm_content"`.

O match com o Meta (campo `meta`, usado pela aba Meta Ads) exige `utm_campaign` +
a coluna de `AD_UTM_COLUMN` batendo com uma linha real do Meta; quando casa, a venda
herda a campanha/conjunto reais do Meta (para o gasto e a venda caírem na mesma linha
das tabelas).

## IA Insights

Aba de análise por IA (Claude) do funil e das estruturas ativas — ver `SETUP-IA.md`
para o passo a passo completo de configuração do backend (Cloudflare Worker +
deploy automático via GitHub Actions).

**Persistência:** o último resultado gerado fica salvo no **Worker (KV namespace
`INSIGHTS_KV`)**, não no navegador — por isso qualquer visitante, em qualquer
navegador, vê os mesmos insights sem precisar gerar de novo. A URL do Worker vem
embutida no build (`IA_WORKER_URL` em `build/config.py`); a senha (`INSIGHTS_PASSWORD`)
só é exigida para **gerar** novos insights (POST), não para ler os já gerados
(GET, público). O workflow `deploy-worker.yml` cria o KV namespace sozinho no
primeiro deploy; se o `CLOUDFLARE_API_TOKEN` não tiver a permissão "Workers KV
Storage: Edit", ele publica o Worker sem persistência (volta ao comportamento
antigo, sem quebrar o deploy) e avisa no log do Actions.

## Arquitetura / arquivos

A dashboard é montada a partir de **arquivos separados** (visual x lógica), costurados
pelo `build.py` no `render()` — assim dá para mexer só em cor/layout sem tocar na lógica:

```
build/build.py             # ENGINE: lê os 2 CSVs (read-only), emite meta[]/sales[] e COSTURA os arquivos abaixo
build/config.py            # CONFIG DO CLIENTE (copie de config.example.py e preencha)
build/config.example.py    # modelo comentado de build/config.py
build/template.html        # esqueleto HTML (placeholders __STYLES__ / __APP_JS__ / __DATA_JSON__)
build/identidade-visual.css # ⭐ TODAS as cores (temas claro/escuro, paleta de gráficos, heatmap). Edite AQUI p/ mexer só em cor.
build/estilos.css          # layout/componentes (CSS não-cor)
build/app.js               # lógica + renderização (gráficos/heatmap leem as cores via CSS vars)
.github/workflows/deploy.yml         # roda build.py e publica no Pages
.github/workflows/deploy-worker.yml  # publica o Worker da IA Insights (Cloudflare)
.github/workflows/gerar-relatorios-metrics.yml # 23:50 BRT: busca as planilhas e commita relatorios_metrics.json
ia-worker/worker.js    # backend da aba IA Insights (ENGINE — não editar por cliente)
ia-worker/wrangler.toml # nome do Worker (preencher por cliente, placeholder nomecliente-ia-insights)
build/relatorios.json  # briefings do Gestor por período (aba Relatórios) — VERSIONADO
build/relatorios_metrics.json # números por período (gerado pelo Actions, lido pela Routine) — VERSIONADO
build/gerar_relatorios.py # calcula as métricas por período (rodado pelo Actions, não pela Routine)
build/GUIA-RELATORIOS.md  # passo a passo da Routine que regenera os briefings
dist/index.html        # saída gerada (gitignored; o Actions reconstrói)
GUIA-REPLICACAO.md     # engine explicada + solução dos problemas de publicação
config.js               # metadados de publicação (GitHub) — copie de config.example.js
SETUP-CRON.md          # valores do cron-job.org (owner/repo com placeholders)
SETUP-IA.md            # passo a passo da aba IA Insights
```

### Aba Relatórios (relatórios automáticos do funil)
Aba entre **Meta Ads** e **IA Insights**. Reaproveita os filtros de data da topbar
e os dados já embutidos (`meta[]`/`sales[]`) — tudo calculado no navegador (custo
zero): cards **Visão Geral Total** (todas as vendas) e **Tráfego** (só Meta Ads),
tabela diária resumida (Total | Ads), visão por campanha, **Top 5 / Piores 5
anúncios** (com link do criativo via coluna *Creative Instagram Permalink* →
`ad_links`, se a planilha do cliente tiver essa coluna). **Código de cor**
(vermelho/amarelo/verde/ciano) só em **CAC** e **ROAS**, conforme
`CAC_TARGET`/`ROAS_TARGET` em `build/config.py` (desempenho = ROAS `valor/meta`,
CAC `meta/valor`).

O **Briefing do Gestor** (texto interpretativo por período) é **pré-gerado por IA**
e lido de `build/relatorios.json` — **sem chamada de API no navegador nem créditos
da Anthropic**. Regeneração em **2 etapas diárias** (o sandbox do agente não alcança
o Google Sheets, só o runner do GitHub Actions — ver "problemas conhecidos" #4):
**23:50 BRT** o workflow `gerar-relatorios-metrics.yml` busca as planilhas e commita
`build/relatorios_metrics.json` (só números); **23:59 BRT** uma **Routine do
Claude Code** lê esse arquivo, migra o texto que estava em "hoje" para "ontem" e
redige os 9 briefings do zero seguindo `build/GUIA-RELATORIOS.md`, commitando
`relatorios.json`. Rodar no fim do dia (não de manhã) garante que "hoje" seja
analisado com o dia quase completo. Se o JSON não existir, a aba mostra tudo
menos o briefing (cards/tabelas seguem funcionando). Configure essa Routine (ou
equivalente) por cliente — não vem pronta neste template.

O `build.py` **não agrega**: exporta as linhas cruas e toda a lógica (filtros, KPIs,
tabelas, gráficos, heatmap, imposto, tema) roda no navegador.

Teste local:
`python build/build.py --meta-file meta.csv --sales-file sales.csv --out dist/index.html`

## Publicação — problemas conhecidos e soluções

1. **Push com integração somente‑leitura:** se `git push`/MCP derem `403 Resource not
   accessible by integration`, faça push com o **PAT do usuário** direto ao github.com
   (`git push https://x-access-token:<TOKEN>@github.com/<owner>/<repo>.git main:main`).
   **Nunca** grave o token no `.git/config` (use a URL efêmera).
2. **cron-job.org só funciona na `main`:** `workflow_dispatch` só existe na branch padrão.
3. **Pages liga sozinho:** `actions/configure-pages@v5` com `enablement: true`
   (+ `permissions: {pages: write, id-token: write}`).
4. **Proxy do sandbox:** o agente NÃO alcança `docs.google.com`, `*.github.io` nem a API
   REST de Actions/Pages e nem `api.cloudflare.com` — mas o runner do Actions alcança
   tudo. Teste dados com CSV local; deploys da Cloudflare passam pelo GitHub Actions.
5. **Token exposto no chat:** revogar e gerar um novo (fine‑grained, só Actions: r/w no repo).
6. **"Senha incorreta" na aba IA Insights após um deploy:** normalmente indica que os
   secrets `ANTHROPIC_API_KEY`/`INSIGHTS_PASSWORD` não estão cadastrados como Secrets
   do repositório no GitHub — o workflow `deploy-worker.yml` os reaplica no Worker a
   cada deploy; sem eles cadastrados, o Worker fica sem senha válida.
7. **Insights "somem":** se estiverem salvos só no navegador (versões antigas do
   template), limpar dados do navegador apaga tudo. A partir desta versão a
   persistência é no Worker (KV) — ver seção "IA Insights" acima; confirme que
   `IA_WORKER_URL` está preenchido em `build/config.py` e que o log do deploy do Worker
   não mostrou o aviso de KV sem permissão.
8. **Venda não aparece na aba Meta Ads (ou aparece na campanha errada):** confirme
   qual coluna UTM da planilha do cliente carrega o identificador real do anúncio do
   Meta (`Ad Name`) e ajuste `AD_UTM_COLUMN` em `build/config.py`. **Não assuma pela
   convenção** — nos dados deste cliente é `utm_content`, e o `utm_term` traz o Ad Name
   grudado no posicionamento (`..._Instagram_Reels`); em outros é o contrário. Jeito rápido
   de decidir: contar, para cada coluna UTM, quantos valores batem exatamente com o
   conjunto de `Ad Name` do Meta — a coluna certa bate quase 100%, as outras batem 0.
   Casar pela coluna errada zera as atribuições. Além disso, nomes de anúncio podem se
   repetir entre campanhas diferentes — o match precisa ser **campanha+anúncio juntos**
   (`UTM Campaign`+`UTM Content`), senão a venda pode ser atribuída à campanha errada.
   Confira o valor real do `Ad Name` na API/painel do Meta e compare com as colunas
   UTM antes de mexer no alias.
