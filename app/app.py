"""
Dashboard interativo — Trabalho N1 de Ciência de Dados
Centro Universitário Católica de Santa Catarina · 2026

Objetivo de negócio: identificar onde estão os cancelamentos de reserva,
para que a rede hoteleira possa agir sobre eles.

Este arquivo é autocontido de propósito: carrega os dados brutos, aplica o
mesmo pipeline do notebook 02 e sobe o dashboard. Um arquivo só é mais fácil
de explicar e de rodar na apresentação.

Para executar:
    pip install -r requirements.txt
    python app/app.py
    -> http://127.0.0.1:8050
"""

from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio
from dash import Dash, Input, Output, dcc, html

# ---------------------------------------------------------------------------
# Identidade visual — a mesma dos notebooks, para os slides ficarem coesos.
# As duas cores de série foram validadas para daltonismo.
# ---------------------------------------------------------------------------
SUPERFICIE       = "#fcfcfb"
CARTAO           = "#ffffff"
TEXTO_PRIMARIO   = "#0b0b0b"
TEXTO_SECUNDARIO = "#52514e"
GRADE            = "#e5e4e0"
SERIE_1 = "#2a78d6"   # azul
SERIE_2 = "#eb6834"   # laranja

pio.templates["n1"] = go.layout.Template(
    layout=dict(
        font=dict(family="Inter, Segoe UI, sans-serif", size=13, color=TEXTO_PRIMARIO),
        title=dict(font=dict(size=15), x=0, xanchor="left"),
        paper_bgcolor=CARTAO,
        plot_bgcolor=CARTAO,
        colorway=[SERIE_1, SERIE_2],
        xaxis=dict(showgrid=False, linecolor=GRADE, ticks="outside", tickcolor=GRADE,
                   title=dict(font=dict(color=TEXTO_SECUNDARIO))),
        yaxis=dict(gridcolor=GRADE, zeroline=False, linecolor=GRADE,
                   title=dict(font=dict(color=TEXTO_SECUNDARIO))),
        showlegend=False,
        margin=dict(t=50, r=20, b=50, l=60),
    )
)
pio.templates.default = "n1"

URL = ("https://raw.githubusercontent.com/mendoncaluucas/DataScience/"
       "main/data/raw/hotel_bookings.csv")

# O CSV vive no próprio repositório. Preferir o arquivo local deixa a partida
# quase instantânea e — o que importa na apresentação — faz o dashboard rodar
# sem internet. A URL fica como reserva, para quem só tem este arquivo.
ARQUIVO_LOCAL = Path(__file__).resolve().parent.parent / "data" / "raw" / "hotel_bookings.csv"

FAIXAS = ["Até 1 semana", "1 sem. a 1 mês", "1 a 3 meses", "3 a 6 meses", "Mais de 6 meses"]


def carregar_dados():
    """Carrega os dados brutos e aplica o pipeline da Fase 3 do CRISP-DM.

    É o mesmo pipeline de notebooks/02_preparacao_dos_dados.ipynb. Mantê-lo em
    código — e não em cliques numa interface — é o que permite que o dashboard
    se reconstrua sozinho a partir da fonte original.
    """
    if ARQUIVO_LOCAL.exists():
        origem = ARQUIVO_LOCAL
    else:
        print("CSV local não encontrado — baixando do GitHub.")
        origem = URL

    df = pd.read_csv(origem)

    # 1. Valores ausentes: uma estratégia por coluna, conforme o motivo da ausência.
    df["children"] = df["children"].fillna(0).astype(int)
    df["country"] = df["country"].fillna("Desconhecido")
    df["agent"] = df["agent"].fillna(0).astype(int)

    # 2. Valores inconsistentes: "Undefined" e "SC" significam a mesma coisa.
    df["meal"] = df["meal"].replace({"Undefined": "SC"})

    # 3. Registros impossíveis: reserva sem hóspede e diária fora da faixa.
    df = df[(df["adults"] + df["children"] + df["babies"]) > 0]
    df = df[df["adr"].between(0, 1000)].copy()

    # 4. Engenharia de features.
    df["total_noites"] = df["stays_in_week_nights"] + df["stays_in_weekend_nights"]
    df["receita_estimada"] = (df["adr"] * df["total_noites"]).round(2)
    df["faixa_antecedencia"] = pd.cut(
        df["lead_time"], bins=[-1, 7, 30, 90, 180, 10**6], labels=FAIXAS
    )
    df["data_chegada"] = pd.to_datetime(
        df["arrival_date_year"].astype(str) + "-"
        + df["arrival_date_month"] + "-"
        + df["arrival_date_day_of_month"].astype(str),
        format="%Y-%B-%d",
    )

    # 5. Colunas removidas. reservation_status determina is_canceled com 100%
    #    de precisão — é vazamento de dados, não informação preditiva.
    df = df.drop(columns=["reservation_status", "reservation_status_date", "company",
                          "arrival_date_year", "arrival_date_month",
                          "arrival_date_day_of_month"])
    return df


print("Carregando e preparando os dados...")
DADOS = carregar_dados()
print(f"{len(DADOS):,} reservas prontas.".replace(",", "."))


# ---------------------------------------------------------------------------
# Componentes reutilizáveis
# ---------------------------------------------------------------------------
def cartao_kpi(titulo, id_valor):
    return html.Div(
        [
            html.Div(titulo, style={"fontSize": "12px", "color": TEXTO_SECUNDARIO,
                                    "textTransform": "uppercase", "letterSpacing": ".04em"}),
            html.Div(id=id_valor, style={"fontSize": "28px", "fontWeight": 600,
                                         "marginTop": "6px", "color": TEXTO_PRIMARIO}),
        ],
        style={"background": CARTAO, "border": f"1px solid {GRADE}", "borderRadius": "10px",
               "padding": "16px 20px", "flex": "1 1 180px"},
    )


ALTURA_GRAFICO = 340

def caixa_grafico(id_grafico):
    # responsive=True faz o gráfico acompanhar a largura da coluna — sem isso o
    # Plotly assume a largura padrão dele e o layout quebra em duas linhas.
    # Com responsive ligado a altura precisa vir do CSS: o container não tem
    # altura própria, e o gráfico colapsaria para zero.
    return html.Div(
        dcc.Graph(id=id_grafico, responsive=True,
                  style={"width": "100%", "height": f"{ALTURA_GRAFICO}px"},
                  config={"displaylogo": False}),
        style={"background": CARTAO, "border": f"1px solid {GRADE}",
               "borderRadius": "10px", "padding": "8px", "minWidth": 0},
    )


# Grid de duas colunas que vira uma só em tela estreita.
ESTILO_GRID = {
    "display": "grid",
    "gridTemplateColumns": "repeat(auto-fit, minmax(380px, 1fr))",
    "gap": "14px",
    "marginBottom": "14px",
}


def seletor(rotulo, id_componente, opcoes):
    return html.Div(
        [
            html.Label(rotulo, style={"fontSize": "12px", "color": TEXTO_SECUNDARIO,
                                      "display": "block", "marginBottom": "6px"}),
            dcc.Dropdown(id=id_componente, options=opcoes, value=[], multi=True,
                         placeholder="Todos"),
        ],
        style={"flex": "1 1 240px"},
    )


# ---------------------------------------------------------------------------
# Layout
# ---------------------------------------------------------------------------
app = Dash(__name__, title="Cancelamentos de Reserva | Trabalho N1")

app.layout = html.Div(
    [
        html.Div(
            [
                html.H1("Onde estão os cancelamentos de reserva",
                        style={"fontSize": "22px", "margin": "0 0 6px", "fontWeight": 600}),
                html.P(
                    "Trabalho N1 · Ciência de Dados · Católica SC · "
                    "Dataset: Hotel Booking Demand · Ferramenta: Plotly + Dash",
                    style={"margin": 0, "fontSize": "13px", "color": TEXTO_SECUNDARIO},
                ),
            ],
            style={"marginBottom": "22px"},
        ),

        # Filtros — numa linha só, acima dos gráficos.
        html.Div(
            [
                seletor("Tipo de hotel", "filtro-hotel",
                        sorted(DADOS["hotel"].unique())),
                seletor("Segmento de mercado", "filtro-segmento",
                        sorted(DADOS["market_segment"].unique())),
                seletor("Antecedência da reserva", "filtro-faixa", FAIXAS),
            ],
            style={"display": "flex", "gap": "14px", "flexWrap": "wrap",
                   "marginBottom": "18px"},
        ),

        html.Div(
            [
                cartao_kpi("Reservas", "kpi-reservas"),
                cartao_kpi("Taxa de cancelamento", "kpi-taxa"),
                cartao_kpi("Receita cancelada", "kpi-receita"),
                cartao_kpi("Antecedência mediana", "kpi-antecedencia"),
            ],
            style={"display": "flex", "gap": "14px", "flexWrap": "wrap",
                   "marginBottom": "18px"},
        ),

        html.Div(
            [caixa_grafico("g-antecedencia"), caixa_grafico("g-deposito")],
            style=ESTILO_GRID,
        ),
        html.Div(
            [caixa_grafico("g-receita"), caixa_grafico("g-segmento")],
            style=ESTILO_GRID,
        ),

        html.P(
            "Os filtros acima recalculam todos os indicadores e gráficos.",
            style={"fontSize": "12px", "color": TEXTO_SECUNDARIO, "marginTop": "20px"},
        ),
    ],
    style={"maxWidth": "1180px", "margin": "0 auto", "padding": "28px 20px",
           "background": SUPERFICIE, "minHeight": "100vh",
           "fontFamily": "Inter, Segoe UI, sans-serif"},
)


# ---------------------------------------------------------------------------
# Gráficos
# ---------------------------------------------------------------------------
def barras_taxa(df, coluna, titulo, ordenar=False, minimo=0):
    """Taxa de cancelamento (%) por categoria."""
    agrupado = df.groupby(coluna, observed=True)["is_canceled"]
    taxa = agrupado.mean().mul(100).round(1)
    taxa = taxa[agrupado.size() > minimo]
    if ordenar:
        taxa = taxa.sort_values(ascending=False)

    figura = go.Figure(
        go.Bar(
            x=[str(i) for i in taxa.index], y=taxa.values,
            marker=dict(color=SERIE_1, cornerradius=4),
            text=taxa.values, texttemplate="%{text:.0f}%", textposition="outside",
            textfont=dict(color=TEXTO_SECUNDARIO),
            hovertemplate="<b>%{x}</b><br>%{y:.1f}% canceladas<extra></extra>",
        )
    )
    figura.update_layout(title=titulo, height=ALTURA_GRAFICO,
                         yaxis=dict(title="% canceladas", range=[0, 112]))
    figura.update_xaxes(tickangle=-20)
    return figura


def linha_receita(df):
    perdida = (df[df["is_canceled"] == 1]
               .groupby(df["data_chegada"].dt.to_period("M"), observed=True)["receita_estimada"]
               .sum()
               .div(1_000_000))
    figura = go.Figure(
        go.Scatter(
            x=perdida.index.astype(str), y=perdida.values, mode="lines+markers",
            line=dict(color=SERIE_2, width=2), marker=dict(size=7),
            hovertemplate="<b>%{x}</b><br>R$ %{y:.2f} mi cancelados<extra></extra>",
        )
    )
    figura.update_layout(title="Receita cancelada por mês de chegada", height=ALTURA_GRAFICO,
                         yaxis=dict(title="R$ milhões"))
    figura.update_xaxes(tickangle=-20)
    return figura


def figura_vazia(mensagem):
    figura = go.Figure()
    figura.add_annotation(text=mensagem, showarrow=False,
                          font=dict(size=14, color=TEXTO_SECUNDARIO))
    figura.update_layout(height=ALTURA_GRAFICO, xaxis=dict(visible=False), yaxis=dict(visible=False))
    return figura


# ---------------------------------------------------------------------------
# Callback — liga os filtros a tudo que está na tela
# ---------------------------------------------------------------------------
@app.callback(
    Output("kpi-reservas", "children"),
    Output("kpi-taxa", "children"),
    Output("kpi-receita", "children"),
    Output("kpi-antecedencia", "children"),
    Output("g-antecedencia", "figure"),
    Output("g-deposito", "figure"),
    Output("g-receita", "figure"),
    Output("g-segmento", "figure"),
    Input("filtro-hotel", "value"),
    Input("filtro-segmento", "value"),
    Input("filtro-faixa", "value"),
)
def atualizar(hoteis, segmentos, faixas):
    df = DADOS
    if hoteis:
        df = df[df["hotel"].isin(hoteis)]
    if segmentos:
        df = df[df["market_segment"].isin(segmentos)]
    if faixas:
        df = df[df["faixa_antecedencia"].isin(faixas)]

    if df.empty:
        vazio = figura_vazia("Nenhuma reserva atende aos filtros")
        return ("0", "—", "—", "—", vazio, vazio, vazio, vazio)

    canceladas = df[df["is_canceled"] == 1]

    kpi_reservas = f"{len(df):,}".replace(",", ".")
    kpi_taxa = f"{df['is_canceled'].mean() * 100:.1f}%"
    kpi_receita = f"R$ {canceladas['receita_estimada'].sum() / 1_000_000:.1f} mi"
    kpi_antecedencia = f"{df['lead_time'].median():.0f} dias"

    return (
        kpi_reservas,
        kpi_taxa,
        kpi_receita,
        kpi_antecedencia,
        barras_taxa(df, "faixa_antecedencia", "Cancelamento por antecedência da reserva"),
        barras_taxa(df, "deposit_type", "Cancelamento por tipo de depósito"),
        linha_receita(df),
        barras_taxa(df, "market_segment", "Cancelamento por segmento de mercado",
                    ordenar=True, minimo=200),
    )


if __name__ == "__main__":
    # use_reloader=False de propósito: com o recarregador ligado, o Flask sobe um
    # segundo processo e o dataset de 17 MB é baixado e preparado DUAS vezes,
    # dobrando o tempo de partida. Numa apresentação isso custa caro.
    app.run(debug=False, use_reloader=False)
