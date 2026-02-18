# FRAMEWORK DE ANÁLISE — Knowledge Base

> Este documento é a referência metodológica do Comitê de Investimentos.
> Deve ser consultado ANTES de qualquer análise, relatório ou avaliação de posição.
> Última atualização: Fevereiro 2026

---

## 1. TEMPLATE DE TESE DE INVESTIMENTO (1-Pager)

Toda posição do portfólio deve ter uma tese documentada seguindo esta estrutura. Ao produzir um deep dive, o analista responsável preenche todos os campos.

```
═══════════════════════════════════════════════════════════
TESE DE INVESTIMENTO — [TICKER] — [EMPRESA]
Data: [DD/MM/AAAA] | Analista: [Persona responsável]
═══════════════════════════════════════════════════════════

■ RESUMO DA TESE (3-5 linhas)
[Por que esta posição está no portfólio? Qual a essência da oportunidade?]

■ O NEGÓCIO
- Modelo de negócio (como gera receita):
- Segmentos e mix de receita:
- Clientes e mercado endereçável (TAM):
- Posição competitiva (market share, ranking):

■ MOAT — VANTAGENS COMPETITIVAS
- Fonte(s) de moat identificada(s): [ver Seção 2 deste documento]
- Avaliação de durabilidade: [Ampliando / Estável / Estreitando]
- Evidências concretas:

■ QUALITY METRICS
- ROIC (últimos 3 anos):
- ROIC vs. WACC (spread):
- ROE:
- Margem operacional / EBITDA:
- Geração de caixa (FCF yield):
- Dívida líquida / EBITDA:
- Crescimento de receita (CAGR 3a):
- Crescimento de lucro (CAGR 3a):

■ GROWTH DRIVERS (Vetores de Crescimento)
1. [Driver 1 — descrição e magnitude estimada]
2. [Driver 2]
3. [Driver 3]

■ VALUATION
- Metodologia principal: [ver Seção 3 deste documento]
- Múltiplos atuais vs. histórico vs. peers:
  - EV/EBITDA:
  - P/E:
  - P/BV (se financeiro):
  - EV/Receita (se growth):
- Preço-alvo estimado:
- Upside/downside vs. cotação atual:
- Margem de segurança:

■ CATALISADORES (próximos 6-12 meses)
1. [Catalisador 1 — data esperada — impacto estimado]
2. [Catalisador 2]
3. [Catalisador 3]

■ RISCOS E KILL SWITCHES
- Risco 1: [Descrição] | Probabilidade: [Alta/Média/Baixa] | Impacto: [Alto/Médio/Baixo]
- Risco 2:
- Risco 3:
- ⚠️ KILL SWITCH: [Condição que invalida a tese — se X acontecer, a posição deve ser reavaliada imediatamente]

■ SIZING E POSIÇÃO
- Peso atual no portfólio:
- Peso-alvo recomendado:
- Convicção: [Alta / Média / Baixa]

■ STATUS DA TESE
[🟢 Ativa e confirmada | 🟡 Em revisão | 🔴 Ameaçada]
Última revisão: [Data]
Próxima revisão obrigatória: [Data/Evento — ex: "Após resultado 4T25"]
═══════════════════════════════════════════════════════════
```

---

## 2. FRAMEWORK DE MOAT (Vantagens Competitivas)

Baseado no framework Morningstar + Mauboussin (Measuring the Moat, Morgan Stanley/Counterpoint Global). O analista deve identificar **pelo menos uma fonte** e avaliar sua durabilidade.

### 2.1 Fontes de Moat

| Fonte | Definição | Sinais de presença | Como testar |
|---|---|---|---|
| **Ativos Intangíveis** | Marcas, patentes, licenças regulatórias que impedem concorrência | Pricing power acima de inflação; market share estável sem guerra de preços; barreiras regulatórias de entrada | A empresa consegue aumentar preços sem perder volume? Tem licenças/concessões difíceis de replicar? |
| **Custos de Troca (Switching Costs)** | Custo (financeiro, operacional, emocional) do cliente trocar de fornecedor | Alta retenção; receita recorrente; contratos longos; integração profunda no workflow do cliente | Quanto custaria ao cliente migrar? Qual o churn rate? |
| **Efeito de Rede** | O valor do produto/serviço aumenta com mais usuários | Crescimento orgânico acelerado; winner-takes-most dynamics; plataformas multilaterais | Cada novo usuário torna o produto mais valioso para os demais? |
| **Vantagem de Custo** | Capacidade estrutural de operar com custos menores que concorrentes | Margens superiores sustentáveis; escala; acesso privilegiado a recursos; localização | A vantagem de custo é estrutural ou temporária? Concorrentes podem replicar? |
| **Escala Eficiente** | Mercado limitado que comporta poucos players lucrativos | Poucos concorrentes; retornos adequados mas não excessivos (não atraem entrantes); nicho natural | O mercado é grande o suficiente para atrair novos entrantes? |

### 2.2 Avaliação de Durabilidade

- **Ampliando:** Moat está ficando mais forte (ex: efeito de rede crescente, aquisições que consolidam posição)
- **Estável:** Moat se mantém, sem ameaças visíveis no horizonte de 5 anos
- **Estreitando:** Moat sob pressão (ex: disrupção tecnológica, mudança regulatória, perda de pricing power)

### 2.3 Red Flags — Sinais de Erosão de Moat
- ROIC em tendência de queda por 3+ trimestres
- Perda de market share para entrantes
- Necessidade de competir em preço
- Capex de manutenção crescente sem retorno proporcional
- Management turnover frequente
- Mudança regulatória adversa

---

## 3. FRAMEWORK DE VALUATION

### 3.1 Hierarquia de Métodos (por tipo de empresa)

| Tipo de Empresa | Método Primário | Método Secundário | Método de Sanidade |
|---|---|---|---|
| **Utilities / Concessões** | DCF (fluxo regulatório previsível) | Dividend Yield / P/BV regulatório | EV/EBITDA vs. peers |
| **Commodities / Cíclicas** | EV/EBITDA normalizado (mid-cycle) | P/BV vs. ROE normalizado | Preço-alvo via curva de commodity |
| **Varejo / Consumo** | EV/EBITDA + crescimento de SSS | P/E forward | DCF com cenários de margem |
| **Tecnologia / Growth** | DCF com múltiplos cenários | EV/Revenue + Rule of 40 | P/E forward normalizado |
| **Financeiro / Bancos** | P/BV vs. ROE sustentável (modelo Gordon) | P/E | Dividend Yield sustentável |
| **Real Estate / Incorporadoras** | P/BV vs. ROE | NAV (Net Asset Value) | EV/EBITDA |
| **Semicondutores** | EV/EBITDA mid-cycle | P/E forward normalizado | FCF Yield |

### 3.2 Múltiplos de Referência — Ranges Aceitáveis (GARP)

O comitê não paga "qualquer preço" por qualidade. Os ranges abaixo são guias, não regras absolutas:

- **P/E forward:** Aceitável até ~20-25x para growth sustentável; >30x exige justificativa excepcional
- **EV/EBITDA:** Varia por setor. Utilities 5-8x; Consumo 7-12x; Tech 15-25x; Commodities 4-7x normalizado
- **P/BV:** Para financeiros, >2x exige ROE > 15% sustentável
- **FCF Yield:** Mínimo desejável de 4-5% para posições core

### 3.3 Margem de Segurança

Para cada posição, calcular:
- **Bull case** (probabilidade ~20%): Tudo dá certo — catalisadores se materializam, crescimento supera expectativas
- **Base case** (probabilidade ~60%): Cenário realista — guidance se confirma, mercado normaliza
- **Bear case** (probabilidade ~20%): Riscos se materializam — desaceleração, compressão de múltiplos

**Preço-alvo ponderado** = (Bull × 20%) + (Base × 60%) + (Bear × 20%)

**Margem de segurança** = (Preço-alvo ponderado − Cotação atual) / Preço-alvo ponderado

Mínimo aceitável: **15% para posições core, 25% para posições táticas/especulativas.**

---

## 4. FRAMEWORK DE RISCO

### 4.1 Categorias de Risco

| Categoria | Exemplos | Monitoramento |
|---|---|---|
| **Risco de Mercado** | Queda generalizada, aversão a risco, correlação entre ativos | VIX, Ibovespa, S&P 500, fluxo estrangeiro |
| **Risco Macro Brasil** | Fiscal, juros, câmbio, político | CDS Brasil, curva de juros, Selic, IPCA |
| **Risco Macro Global** | Fed, recessão, geopolítica, China | Treasury 10Y, DXY, PMIs, spreads HY |
| **Risco Setorial** | Regulação, ciclo, disrupção, competição | Específico por setor — definido pelo analista |
| **Risco Idiossincrático** | Governança, execução, fraude, alavancagem | Resultados trimestrais, eventos corporativos |
| **Risco de Concentração** | Peso excessivo em setor/fator/região | Mapa de exposição do portfólio |
| **Risco Cambial** | Impacto do BRL/USD nas posições internacionais | PTAX, DXY, posição líquida em USD |

### 4.2 Mapa de Correlação (CIO deve monitorar)

Posições que tendem a se mover juntas (correlação positiva alta):
- SUZB3 + KLBN4 (celulose/papel — mesmo driver: preço de celulose + câmbio)
- TSM + NVDA + ASML + SNPS + MU (ciclo de semicondutores)
- ENGI4 + EQTL3 (utilities — mesmo driver: juros longos BR)
- MGLU3 + PLPL3 (sensíveis a ciclo de juros e crédito ao consumidor)

O CIO deve alertar quando múltiplas posições correlacionadas representem >30% do portfólio.

---

## 5. CHECKLIST DE MONITORAMENTO

### 5.1 Triggers de Revisão Obrigatória

A tese de uma posição **deve ser revisada** quando:

- [ ] Resultado trimestral divulgado
- [ ] Guidance revisado pela empresa (para cima ou para baixo)
- [ ] Mudança relevante de management (CEO, CFO)
- [ ] Mudança regulatória que afeta o setor
- [ ] Preço da ação caiu >15% em menos de 30 dias sem motivo macro geral
- [ ] Preço da ação subiu >30% — reavaliar upside remanescente
- [ ] Kill switch acionado (condição pré-definida na tese)
- [ ] Mudança material no cenário macro que afeta premissas da tese
- [ ] Novo concorrente ou disrupção tecnológica relevante
- [ ] Insider selling significativo

### 5.2 Calendário de Resultados

O comitê deve manter awareness do calendário de resultados das posições. Antes de cada temporada de earnings, o CIO deve solicitar um preview das expectativas.

### 5.3 Métricas de Monitoramento por Setor

**Energia & Materiais:**
- Preço Brent, preço celulose BHKP, USD/BRL, spreads de crack
- Curva futura de celulose, estoques em portos chineses
- Produção e lifting cost (BRAV3)
- Volume de vendas e preço médio (UGPA3)

**Utilities:**
- Selic e curva de juros longa (NTN-B)
- Decisões ANEEL, revisões tarifárias
- Nível dos reservatórios, PLD (Preço de Liquidação das Diferenças)
- RAP contratada e pipeline de leilões

**Consumo & Imobiliário:**
- Selic, spread bancário, inadimplência PF
- Confiança do consumidor (FGV), vendas no varejo (PMC)
- SSS das varejistas, GMV e-commerce
- Lançamentos e vendas líquidas (PLPL3), taxa de ocupação (ALOS3)
- Emplacamentos e produção ANFAVEA (RAPT4)

**Tecnologia & Semicondutores:**
- Capex de hyperscalers (MSFT, GOOGL, AMZN, META)
- Pricing de DRAM/NAND (MU)
- Wafer starts e utilização de fabs (TSM)
- Backlog de pedidos EUV (ASML)
- Revenue growth de Cloud/AI (GOOGL)
- TPV e take rate LatAm (MELI)

**Financeiro:**
- NIM (margem de intermediação)
- Inadimplência (NPL ratio) e cobertura de provisões
- CAC, LTV, ARPAC (métricas de fintech)
- Crescimento de carteira e mix (crédito, investimentos, seguros)

---

## 6. TEMPLATES DE RELATÓRIO

### 6.1 Relatório Consolidado (/relatorio)
```
RELATÓRIO DE PORTFÓLIO — [MÊS/ANO]
Comitê de Investimentos

1. SUMÁRIO EXECUTIVO (CIO)
2. PANORAMA MACROECONÔMICO (Estrategista Macro)
3. ANÁLISE POR SETOR
   3.1 Energia & Materiais Básicos
   3.2 Utilities & Concessões
   3.3 Consumo, Varejo & Imobiliário
   3.4 Tecnologia & Semicondutores
   3.5 Financeiro & Crédito
4. MAPA DE RISCO DO PORTFÓLIO (CIO)
5. RECOMENDAÇÕES E AÇÕES (CIO)
6. DISCLAIMER
```

### 6.2 Deep Dive (/deepdive [TICKER])
```
DEEP DIVE — [TICKER] — [EMPRESA]
[Data] | [Analista responsável]

1. TESE DE INVESTIMENTO (template completo da Seção 1)
2. ANÁLISE DO SETOR E POSICIONAMENTO COMPETITIVO
3. ANÁLISE FINANCEIRA DETALHADA (últimos 12 trimestres)
4. VALUATION (3 cenários)
5. CATALISADORES E TIMELINE
6. RISCOS E KILL SWITCHES
7. PARECER DO CIO
8. DISCLAIMER
```

### 6.3 Update Macro (/macro)
```
UPDATE MACROECONÔMICO — [DATA]

1. CENÁRIO GLOBAL (Estrategista Macro)
2. CENÁRIO BRASIL (Estrategista Macro)
3. IMPACTO NAS POSIÇÕES (cada analista, brevemente)
4. AÇÕES RECOMENDADAS (CIO)
```

### 6.4 Screening (/screening)
```
SCREENING DE OPORTUNIDADES — [DATA]

1. CRITÉRIOS DE BUSCA (CIO)
2. GAPS IDENTIFICADOS NO PORTFÓLIO (CIO)
3. CANDIDATOS (analistas setoriais)
4. AVALIAÇÃO PRELIMINAR (por candidato)
5. RECOMENDAÇÃO (CIO)
```
