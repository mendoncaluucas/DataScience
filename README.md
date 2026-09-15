# Aplicação Prática do Plotly nas Fases Iniciais do CRISP-DM

Trabalho N1 — **Ciência de Dados**
Centro Universitário Católica de Santa Catarina
Prof. Dr. Claudinei Dias (Ney) — 2026

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/mendoncaluucas/DataScience/blob/main/notebooks/01_compreensao_dos_dados.ipynb)

> **Para avaliação:** clique no botão acima para abrir a análise no Google Colab.
> O notebook carrega o dataset direto deste repositório — basta executar, sem
> instalar nada.

## Integrantes

- Henrique Cordeiro de Oliveira
- Lucas Mendonça
- Victor Kunz
- Nicholas Scoz
- Kauã Lucindo

## Ferramenta escolhida

**Plotly** — ecossistema open-source de visualização de dados:

| Componente | Papel neste trabalho |
|---|---|
| Plotly Express | Análise exploratória (Fase 2) |
| Plotly Graph Objects | Gráficos customizados |
| Dash | Dashboard interativo final |
| Chart Studio | Camada low-code / GUI |

## Objetivo de negócio

> Reduzir a taxa de cancelamento de reservas, identificando quais características
> da reserva e do cliente mais se associam ao cancelamento — para que a rede
> hoteleira possa antecipar cancelamentos e agir sobre eles (política de depósito,
> overbooking calibrado, contato proativo).

## Dataset

**Hotel Booking Demand** — reservas reais de um hotel urbano e um resort em
Portugal, entre julho de 2015 e agosto de 2017.

| | |
|---|---|
| **Dimensões** | 119.390 linhas × 32 colunas |
| **Download** | [Kaggle](https://www.kaggle.com/datasets/jessemostipak/hotel-booking-demand) · [TidyTuesday 2020-02-11](https://github.com/rfordatascience/tidytuesday/tree/master/data/2020/2020-02-11) · [cópia neste repo](data/raw/hotel_bookings.csv) |
| **Publicação original** | Antonio, Almeida & Nunes (2019), *Data in Brief* 22, 41–49 — [doi:10.1016/j.dib.2018.11.126](https://doi.org/10.1016/j.dib.2018.11.126) |
| **Licença** | CC0 (domínio público) |

Atende aos requisitos do enunciado com folga: mais de 1.000 instâncias, mais de
5 atributos, tipos mistos (numérico, categórico, data) e valores ausentes em
quatro níveis distintos:

| Coluna | Ausentes | Tratamento previsto |
|---|---|---|
| `company` | 94,3% | Remoção — praticamente sem informação |
| `agent` | 13,7% | Categoria explícita ("sem agência") |
| `country` | 0,4% | Moda ou marcação como desconhecido |
| `children` | 4 registros | Preenchimento com 0 |

## Estrutura do repositório

```
data/raw/          Dataset original, sem modificações
data/processed/    Dataset após o pipeline de preparação
notebooks/         Análise por fase do CRISP-DM
app/               Dashboard Dash
docs/              Slides e prints usados na apresentação
```

## Como executar

### Google Colab (recomendado)

Clique no botão **Open in Colab** no topo deste README. Não exige instalação:
pandas e Plotly já vêm no ambiente e o dataset é carregado pela URL do próprio
repositório.

Para salvar alterações de volta aqui: `Arquivo → Salvar uma cópia no GitHub`,
escolhendo `mendoncaluucas/DataScience` e o caminho `notebooks/<arquivo>.ipynb`.

> **Atenção:** o preview de notebook do GitHub é estático e **não renderiza
> gráficos Plotly** — eles são JavaScript e aparecem em branco. Por isso a última
> seção do notebook exporta cada gráfico como PNG para `docs/prints/`.

### Localmente

```powershell
git clone https://github.com/mendoncaluucas/DataScience.git
cd DataScience
py -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
jupyter lab notebooks/
```

Dashboard:

```powershell
py app/app.py
```

Acesse `http://127.0.0.1:8050`.

O app lê o CSV da pasta `data/raw/` do próprio repositório, então **sobe em
segundos e funciona sem internet** — só recorre ao GitHub se o arquivo local não
existir. Traz quatro indicadores e quatro gráficos, todos recalculados pelos
filtros de tipo de hotel, segmento de mercado e faixa de antecedência.

## Mapeamento CRISP-DM → Plotly

### Fase 1 — Compreensão do Negócio

Esta fase não produz gráfico: produz uma pergunta. O papel da ferramenta aqui é
encurtar o caminho entre a conversa com quem conhece o negócio e algo concreto
de se olhar.

| Como o Plotly/Dash apoia | Na prática |
|---|---|
| **Protótipo descartável** | Um painel provisório em Dash fica pronto em minutos. Mostrar um rascunho a quem decide revela desacordos que uma reunião não revelaria — é mais barato descobrir que o indicador está errado antes de construir o pipeline. |
| **Definição de KPIs** | Tentar desenhar o indicador força a pergunta difícil: *o que exatamente conta como cancelamento?* Aqui, `is_canceled` reúne `Canceled` e `No-Show` — decisão que só aparece quando alguém precisa escrever a fórmula. |
| **Registro da decisão** | Por ser código versionado, a definição do KPI fica rastreável. Seis meses depois o `git log` responde por que o número mudou — coisa que um painel editado no lugar não guarda. |

**Objetivo de negócio definido nesta fase:** reduzir a taxa de cancelamento,
identificando quais características da reserva se associam ao cancelamento.
Ele é o critério que decide o que entra nas fases seguintes — a coluna
`reservation_status`, por exemplo, só foi removida na Fase 3 porque este
objetivo é *antecipar* o cancelamento, e não descrevê-lo depois do fato.

### Fase 2 — Compreensão dos Dados

Notebook: `notebooks/01_compreensao_dos_dados.ipynb`
([abrir no Colab](https://colab.research.google.com/github/mendoncaluucas/DataScience/blob/main/notebooks/01_compreensao_dos_dados.ipynb))

**Extração** — quem conecta é o pandas; o Plotly desenha o que ele traz.
`read_csv` aqui, mas também Excel, JSON, SQL, Parquet e APIs: qualquer fonte
que o Python alcance.

**Análise exploratória** — o equivalente aos painéis *Qualidade da Coluna* e
*Perfil da Coluna* do Power Query, escrito em vez de clicado:

| Recurso | O que respondeu neste dataset |
|---|---|
| `df.info()` / `df.describe()` | Estatísticas descritivas e tipos — 32 colunas, 4 delas com ausentes |
| `df.isna()` + `px.bar` | Mapa visual de valores ausentes, em quatro intensidades |
| `px.box` | Dispersão e atípicos — `lead_time` mediano de 113 dias entre canceladas contra 45 das mantidas |
| `px.imshow` | Matriz de correlação com escala divergente e cinza no centro |

**Hipóteses formuladas a partir da EDA** (exigidas pelo enunciado):

1. Reservas com maior antecedência cancelam mais — **confirmada**, `r = +0,293`.
2. Hóspedes com pedidos especiais cancelam menos — **confirmada**, `r = −0,235`.

### Fase 3 — Preparação dos Dados

Pipeline de seis etapas em `notebooks/02_preparacao_dos_dados.ipynb`
([abrir no Colab](https://colab.research.google.com/github/mendoncaluucas/DataScience/blob/main/notebooks/02_preparacao_dos_dados.ipynb)):

**1. Tratamento de nulos** — uma estratégia por coluna, conforme o motivo da ausência:

| Coluna | Estratégia | Justificativa |
|---|---|---|
| `children` | Preenche com 0 | Ausência é ruído de digitação |
| `country` | `"Desconhecido"` | País não informado é uma categoria, não um erro |
| `agent` | Código 0 | Ausência **significa** "sem intermediário" |
| `company` | Remoção da coluna | 94,3% ausente |

**2. Substituição de valores** — `meal`: `Undefined` e `SC` designam o mesmo conceito
(sem refeição) e foram unificados.

**3. Filtragem** — 182 registros removidos (0,15%): 180 reservas sem hóspede algum e
2 com diária fora da faixa plausível.

**4. Engenharia de features** — seis colunas novas: `total_noites`, `total_hospedes`,
`tem_criancas`, `receita_estimada`, `faixa_antecedencia` e `data_chegada`.
`receita_estimada` traduz o cancelamento em dinheiro.

**5. Remoção de colunas** — quatro remoções, com destaque para **vazamento de dados**:
`reservation_status` determina `is_canceled` com 100% de precisão (Check-Out → 0;
Canceled e No-Show → 1), pois só existe *depois* do desfecho. Mantê-la produziria um
modelo perfeito e inútil. Junto saem `reservation_status_date`, `company` e os três
campos `arrival_date_*`, condensados em `data_chegada`.

**6. Conversão de tipos** — colunas de texto de baixa cardinalidade viraram
`category`: memória de 98,5 MB para 22,4 MB (−77%).

**Resultado:** 119.390 → 119.208 linhas · 129.425 células ausentes → 0.

> O CSV preparado **não** é versionado: são 17 MB derivados, que o notebook
> reproduz em segundos. A última célula da Fase 3 o gera e oferece o download.

## Entregáveis

- [x] **Apresentação de slides** — [`docs/slides.pdf`](docs/slides.pdf) · [`docs/slides.pptx`](docs/slides.pptx) (21 slides, com notas do apresentador)
- [x] **Arquivo do projeto** — este repositório. O Plotly não gera um binário
  como o `.pbix` do Power BI ou o `.twbx` do Tableau: o "arquivo do projeto" é o
  código que reconstrói a análise inteira a partir do dataset original.
- [x] **Link para o dataset original** — [Kaggle](https://www.kaggle.com/datasets/jessemostipak/hotel-booking-demand) (seção *Dataset*)
