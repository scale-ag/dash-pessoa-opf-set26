# CLAUDE.md — Dashboard de Controle de Tráfego Pago (TEMPLATE)

> Este arquivo é lido automaticamente pelo Claude Code ao abrir o repositório.
> Repositório **configurado para o cliente FERNANDO PESSOA** (funil "Operação
> da Prova à Farda", sigla `OPF-SET26`). A engine (`build/template.html`, `build/build.py`,
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
   `scale-ag`/`dash-pessoa-opf-set26` que aparecem em `SETUP-CRON.md` e
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

- **URL pública:** `https://scale-ag.github.io/dash-pessoa-opf-set26/`
  (preencha `config.js` — ver checklist acima)
- **Cliente/projeto:** preencher em `build/config.py` (`CLIENT_NAME`/`CLIENT_SUB`)
- **Tipo de funil:** VSL / tráfego direto (não há etapa de Leads/MQL) —
  `Gasto → Impressões → Cliques → Page Views → Checkouts → Vendas → Faturamento`

## Fontes de dados (Google Sheets)

Este cliente usa **duas planilhas separadas** (o template padrão assume uma só,
com dois gids). Por isso `build/config.py` tem `SPREADSHEET_ID_SALES` além de
`SPREADSHEET_ID`; quando `SPREADSHEET_ID_SALES` está vazio, o build volta ao
comportamento original (as duas abas na mesma planilha). Leitura via export CSV,
**somente leitura**.

| Fonte | Planilha (`SPREADSHEET_ID*`) | gid | Aba |
|-------|------------------------------|-----|-----|
| **Meta Ads** | `1BLv_PQ3eHD0hPQjUckx5SkkUTpHLaU-ODAHWA_biKpU` | `0` | 1ª aba (9 colunas) |
| **Compradores** | `1DXw8stvgyBo7AO-7hf2TSX1nt34v7yroJHmfge3bnPI` | `151354425` | **BASE COMPLETA** (55 colunas) |

⚠️ Na planilha de Compradores, `gid=0` é uma aba **vazia** (13 colunas, 0 linhas).
A aba de dados é a `151354425`. As outras abas (`152695175`, `225612892`) são
listas parciais/respostas de formulário e **não** devem ser usadas.

**Colunas reais — Meta Ads** (ordem diferente do template; o `header_index` casa
por nome, então a ordem não importa):
`Day · Campaign Name · Ad Set Name · Ad Name · Impressions · Link Clicks ·
Landing Page Views · Checkouts Initiated · Amount Spent`

**Colunas reais — BASE COMPLETA** (55 colunas; as usadas pelo build):
`DATA` (índice 0) · `HORA` · `PRODUTO` (2) · `PAGINA` · `FORM` · `NOME` (5) ·
`EMAIL` (6) · `ZAP` · `utm_source` (8) · `utm_medium` (9) · `utm_campaign` (10) ·
`utm_term` (11) · `utm_content` (12) · `Order Bump?` · **`Faturamento líquido`**
(14, coluna de receita) · `Carimbo de data/hora` · e mais ~39 colunas de
perguntas do formulário de captação.

### Pontos de atenção deste cliente (verificados na planilha em 04/09/2026)

1. **O Ad Name vem de `utm_term`, não de `utm_content`** (medido em 06/09/2026,
   com 123 vendas e 31 linhas de Meta). Cada coluna UTM contra cada campo do Meta,
   contando quantos valores batem exatamente:

   | coluna UTM | preenchidas | Campaign Name | Ad Set Name | Ad Name |
   |---|---|---|---|---|
   | `utm_campaign` | 5 | **4** | 0 | 0 |
   | `utm_medium` | 5 | 0 | **4** | 0 |
   | `utm_term` | 4 | 0 | 0 | **4** |
   | `utm_content` | 5 | 0 | 0 | **0** |

   O `utm_content` deste cliente carrega o **posicionamento** (`Instagram_Feed`,
   `Instagram_Stories`, `Facebook_Mobile_Feed`) — casar por ele zerava a
   atribuição. Corrigido via `AD_UTM_COLUMN = "utm_term"` em `build/config.py`
   (a engine continua genérica; o padrão do template segue `utm_content`).
   Mapeamento deste cliente:
   `utm_campaign → Campaign Name` · `utm_medium → Ad Set Name` · `utm_term → Ad Name`.

   ⚠️ **Limite que permanece:** só **5 das 123** linhas da BASE COMPLETA têm
   qualquer UTM preenchida — as outras 118 chegam sem rastreamento nenhum. Com o
   match corrigido, 4 dessas 5 casam com o Meta (a 5ª é orgânica: `utm_campaign=bio`,
   `utm_medium=organic`, com a macro não substituída `{{adset.name}}` em
   `utm_content`). Ou seja: a aba Meta Ads passa a mostrar vendas, mas ainda é uma
   fração do total. Isso é rastreamento faltando no checkout, não bug do build —
   garantir que o link do anúncio leve as UTMs para o checkout em **todas** as
   compras.
2. **Janelas de data quase sem sobreposição**: o Meta Ads começa em 03/09/2026 e
   a BASE COMPLETA vai de 13/08 a 03/09/2026 — a maior parte das inscrições é
   anterior ao início do tráfego exportado. Enquanto isso durar, CAC/ROAS por
   período comparam gasto e vendas de janelas diferentes.
3. **Sem coluna de status de pagamento** → `COUNT_ALL_AS_PAID = True` (toda linha
   da BASE COMPLETA é uma inscrição paga).
4. **Receita**: usar `Faturamento líquido`. Os valores mudam por lote do ingresso
   (8,56 → 17,12 → 19,66 → 39,33 líquidos), não por comprador — confirmar com o
   gestor se é receita líquida do ingresso antes de bater metas.
5. **Sem coluna de permalink do criativo** na aba Meta Ads → o Top/Piores anúncios
   da aba Relatórios aparece **sem link** para o criativo. Para ativar, basta
   acrescentar a coluna `Creative Instagram Permalink` na planilha do Meta.
6. **Alias de e-mail**: existem duas colunas de e-mail (`EMAIL`, índice 6, e
   `Endereço de e-mail`, índice 16). O alias `"e-mail"` do `build.py` casa com a
   16 (a 6 se chama `EMAIL`, sem hífen), que só tem 45 de 119 linhas — a coluna
   e-mail da tabela de Vendas fica vazia (`—`) no restante. É cosmético: o e-mail
   é mascarado de qualquer forma antes de ir para a página pública.
7. **Colunas resíduo de outro funil**: a BASE COMPLETA carrega perguntas de um
   formulário antigo ("Curso Prático de Gestão de Projetos Digitais", "FORMAÇÃO
   GESTORA PRÓSPERA"), todas vazias. Ignoradas pelo build.

### Sigla do funil / convenção de campanha

Campanha única no período sondado:
`OPF-SET26 | E4-VEN | P1-QUENTE | VND | ABO | 2026-09-03 | Teste de criativos`
→ **sigla do funil = `OPF-SET26`**. Anúncios no padrão
`AD02_ING_VD_ST_LXPAGO.SET26.mov` (AD02/03/04/07/09); conjuntos no padrão
`AUTO | ALL | 25 a 54 | BR | All in one | NN`.

### Critério de MQL

O briefing original citava MQL ("ser terapeuta familiar e faturar acima de 5 mil"),
mas esse critério é de **outro cliente** — o formulário desta operação pergunta
sobre concursos/carreira policial, e o funil aqui não tem etapa de Leads/MQL.
Por decisão do gestor, **não há etapa de MQL nesta dashboard**.

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
`Campaign Name = utm_campaign` · `Ad Set Name = utm_medium` · **`Ad Name = utm_term`**
(o `utm_content` carrega o posicionamento). Qual coluna o build usa para o anúncio
é definido por `AD_UTM_COLUMN` em `build/config.py` — aqui, `"utm_term"`.

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
   convenção** — nos dados deste cliente é `utm_term`, e o `utm_content` traz o
   posicionamento (`Instagram_Feed`/`Stories`); em outros é o contrário. Jeito rápido
   de decidir: contar, para cada coluna UTM, quantos valores batem exatamente com o
   conjunto de `Ad Name` do Meta — a coluna certa bate quase 100%, as outras batem 0.
   Casar pela coluna errada zera as atribuições. Além disso, nomes de anúncio podem se
   repetir entre campanhas diferentes — o match precisa ser **campanha+anúncio juntos**
   (`UTM Campaign`+`UTM Content`), senão a venda pode ser atribuída à campanha errada.
   Confira o valor real do `Ad Name` na API/painel do Meta e compare com as colunas
   UTM antes de mexer no alias.
