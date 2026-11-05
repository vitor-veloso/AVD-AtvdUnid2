"""Anime Insights: laboratório de análise e painel de escolha de animes."""

from __future__ import annotations

import math

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from src.data_loader import load_data


st.set_page_config(page_title="Anime Insights", page_icon="📺", layout="wide")

ORANGE = "#FF6A00"
ORANGE_SOFT = "#FFF0E4"
INK = "#343434"
VARIABLES = {"rating": "Nota", "episodes": "Episódios", "members": "Membros"}

# Os st.container(key=...) recebem bordas laranja como no rascunho.
st.markdown(
    """
    <style>
    .block-container {max-width: 1560px; padding-top: 1.4rem; padding-bottom: 2.5rem;}
    h1 {letter-spacing: -0.025em;}
    div[class*="st-key-card_"] {
        border: 2px solid #FF6A00;
        border-radius: 24px;
        padding: 1.0rem 1.2rem 0.6rem;
        margin-bottom: 0.65rem;
    }
    div[class*="st-key-card_metric_"] {min-height: 136px;}
    div[data-testid="stSidebar"] {border-right: 2px solid #FF6A00;}
    div[data-testid="stSidebar"] h2 {font-size: 1.42rem;}
    .stTabs [data-baseweb="tab"] {font-size: 1rem; font-weight: 650;}
    </style>
    """,
    unsafe_allow_html=True,
)


def fmt_int(value: int | float) -> str:
    """Formatação amigável de contagens para a interface em português."""
    return f"{value:,.0f}".replace(",", ".")


def fmt_decimal(value: float, digits: int = 2) -> str:
    return f"{value:.{digits}f}".replace(".", ",")


def slider_range(
    label: str, series: pd.Series, *, key: str, decimal: bool = False, member: bool = False
) -> tuple[tuple[int | float, int | float] | None, tuple[int | float, int | float] | None]:
    """Retorna o intervalo escolhido e o intervalo integral da base."""
    valid = pd.to_numeric(series, errors="coerce")
    valid = valid.replace([np.inf, -np.inf], np.nan).dropna()
    if valid.empty:
        st.caption(f"{label}: sem valores numéricos na base.")
        return None, None

    if decimal:
        low = float(math.floor(float(valid.min()) * 10) / 10)
        high = float(math.ceil(float(valid.max()) * 10) / 10)
        step = 0.1
    else:
        low = int(math.floor(float(valid.min())))
        high = int(math.ceil(float(valid.max())))
        if member:
            low = min(low, 0)
            step = max(1, int(math.ceil((high - low) / 500)))
        else:
            step = 1

    full = (low, high)
    if low == high:
        st.caption(f"{label}: todos os registros numéricos têm valor {fmt_decimal(low, 1) if decimal else fmt_int(low)}.")
        return full, full

    chosen = st.slider(
        label,
        min_value=low,
        max_value=high,
        value=full,
        step=step,
        format="%.1f" if decimal else "%d",
        key=key,
    )
    return chosen, full


def apply_filters(
    df: pd.DataFrame,
    selected_types: list[str],
    selected_genres: list[str],
    ranges: dict[str, tuple[tuple | None, tuple | None]],
) -> pd.DataFrame:
    """OU entre gêneros; E entre formato, gênero e intervalos."""
    if not selected_types:
        return df.iloc[0:0].copy()

    mask = df["type"].isin(selected_types)
    if selected_genres:
        genre_set = set(selected_genres)
        mask &= df["genre_list"].map(lambda values: not genre_set.isdisjoint(values))

    for column, (chosen, full) in ranges.items():
        # Seleção integral não exclui registros com valor ausente nessa coluna.
        if chosen is not None and full is not None and chosen != full:
            mask &= df[column].between(chosen[0], chosen[1], inclusive="both")

    return df.loc[mask].copy()


def plot_heatmap(df: pd.DataFrame, selected: list[str]) -> go.Figure:
    """Spearman nas colunas originais: nunca correlacionar ID ou log como variáveis extras."""
    corr = df[selected].corr(method="spearman", min_periods=3)
    values = corr.to_numpy(dtype=float)
    label_values = [
        ["—" if not np.isfinite(v) else f"{v:.2f}" for v in row]
        for row in values
    ]
    labels = [VARIABLES[c] for c in selected]
    fig = go.Figure(
        data=go.Heatmap(
            z=np.where(np.isfinite(values), values, np.nan),
            x=labels,
            y=labels,
            zmin=-1,
            zmax=1,
            zmid=0,
            colorscale=[
                [0.0, "#4263BA"],
                [0.5, "#F9F8F6"],
                [1.0, "#F27137"],
            ],
            colorbar={"title": "ρ", "thickness": 13, "len": 0.87},
            hoverongaps=False,
            hovertemplate="%{y} × %{x}<br>Spearman: %{z:.2f}<extra></extra>",
        )
    )
    # As anotações mudam de cor conforme a intensidade da célula.
    for row, y_label in enumerate(labels):
        for col, x_label in enumerate(labels):
            value = values[row, col]
            fig.add_annotation(
                x=x_label,
                y=y_label,
                text=label_values[row][col],
                showarrow=False,
                font={
                    "size": 17,
                    "color": "#FFFFFF" if np.isfinite(value) and abs(value) >= 0.65 else INK,
                },
            )
    fig.update_layout(
        height=310 if len(selected) <= 2 else 365,
        margin={"l": 8, "r": 8, "t": 12, "b": 8},
        xaxis={"side": "bottom", "showgrid": False, "tickfont": {"size": 13}},
        yaxis={"autorange": "reversed", "showgrid": False, "tickfont": {"size": 13}},
    )
    return fig


def plot_histogram(df: pd.DataFrame, variable: str, log_view: bool) -> go.Figure | None:
    """Com log, o binning é feito depois de transformar os valores (não só o eixo)."""
    values = pd.to_numeric(df[variable], errors="coerce")
    values = values.replace([np.inf, -np.inf], np.nan).dropna()
    transformed = log_view and variable in ("episodes", "members")
    if transformed:
        values = values[values >= 0]
        values = np.log1p(values)
    if values.empty:
        return None

    x_title = VARIABLES[variable]
    if transformed:
        x_title += " — log(1 + x)"

    fig = go.Figure(
        data=go.Histogram(
            x=values,
            nbinsx=24,
            marker={"color": ORANGE, "line": {"color": "#FFFFFF", "width": 0.5}},
            hovertemplate="Faixa: %{x}<br>Títulos: %{y}<extra></extra>",
            name="Títulos",
        )
    )
    fig.update_layout(
        height=260,
        margin={"l": 8, "r": 8, "t": 8, "b": 10},
        bargap=0.035,
        xaxis_title=x_title,
        yaxis_title="Quantidade de títulos",
        showlegend=False,
    )
    return fig


def plot_ranking(df: pd.DataFrame) -> go.Figure:
    ranked = df.sort_values(
        ["rating", "members", "anime_id"],
        ascending=[False, False, True],
        na_position="last",
        kind="stable",
    ).head(10).copy()
    ranked["position"] = range(1, len(ranked) + 1)
    ranked["short_name"] = ranked["name"].map(
        lambda name: name if len(name) <= 49 else name[:46] + "…"
    )
    ranked["axis_label"] = ranked.apply(
        lambda r: f"{r['position']:02d}. {r['short_name']}", axis=1
    )
    custom = ranked[["name", "members", "episodes", "genre"]].fillna("N/D").to_numpy()
    fig = go.Figure(
        data=go.Bar(
            x=ranked["rating"],
            y=ranked["axis_label"],
            orientation="h",
            marker_color=ORANGE,
            customdata=custom,
            hovertemplate=(
                "<b>%{customdata[0]}</b><br>Nota: %{x:.2f}"
                "<br>Membros: %{customdata[1]}"
                "<br>Episódios: %{customdata[2]}"
                "<br>Gêneros: %{customdata[3]}<extra></extra>"
            ),
        )
    )
    fig.update_layout(
        height=max(290, 62 + 38 * len(ranked)),
        margin={"l": 12, "r": 15, "t": 8, "b": 10},
        xaxis_title="Nota média do anime",
        xaxis_range=[0, max(10.0, float(ranked["rating"].max()) + 0.2)],
        yaxis={"autorange": "reversed", "title": ""},
        showlegend=False,
    )
    return fig


def plot_genre_means(df: pd.DataFrame) -> go.Figure | None:
    # Explode: o mesmo título integra cada gênero associado a ele (sem duplicar KPIs).
    exploded = df[["anime_id", "genre_list", "rating"]].explode("genre_list")
    exploded = exploded.rename(columns={"genre_list": "genre_name"})
    exploded = exploded[exploded["genre_name"].notna() & exploded["genre_name"].ne("")]
    if exploded.empty:
        return None

    frequency = exploded["genre_name"].value_counts().head(12).index
    grouped = (
        exploded[exploded["genre_name"].isin(frequency)]
        .groupby("genre_name", as_index=False)
        .agg(mean_rating=("rating", "mean"), titles=("anime_id", "size"))
        .dropna(subset=["mean_rating"])
        .sort_values(["mean_rating", "titles", "genre_name"], ascending=[False, False, True])
    )
    if grouped.empty:
        return None

    fig = go.Figure(
        data=go.Bar(
            x=grouped["mean_rating"],
            y=grouped["genre_name"],
            customdata=grouped[["titles"]].to_numpy(),
            orientation="h",
            marker_color=ORANGE,
            hovertemplate=(
                "Gênero: %{y}<br>Nota média: %{x:.2f}"
                "<br>Títulos do gênero: %{customdata[0]}<extra></extra>"
            ),
        )
    )
    fig.update_layout(
        height=max(320, 60 + 28 * len(grouped)),
        margin={"l": 8, "r": 12, "t": 8, "b": 8},
        xaxis_title="Nota média (cada anime tem o mesmo peso)",
        xaxis_range=[0, max(10.0, float(grouped["mean_rating"].max()) + 0.2)],
        yaxis={"autorange": "reversed", "title": ""},
        showlegend=False,
    )
    return fig


def plot_scatter(df: pd.DataFrame) -> go.Figure | None:
    # Plotly requer x > 0 em eixo logarítmico; zeros permanecem nas métricas.
    points = df.loc[
        df["members"].gt(0)
        & df["members"].notna()
        & df["rating"].notna()
    ].copy()
    if points.empty:
        return None

    fig = px.scatter(
        points,
        x="members",
        y="rating",
        color="type",
        hover_name="name",
        hover_data={
            "members": ":,.0f",
            "rating": ":.2f",
            "episodes": True,
            "genre": True,
            "type": False,
        },
        labels={
            "members": "Membros (escala logarítmica)",
            "rating": "Nota",
            "episodes": "Episódios",
            "genre": "Gêneros",
            "type": "Formato",
        },
        log_x=True,
        opacity=0.65,
        render_mode="webgl",
        color_discrete_sequence=[
            "#FF6A00", "#3165B5", "#14A38B", "#9B59B6", "#D64E66", "#8D7145", "#64748B"
        ],
    )
    fig.update_traces(marker={"size": 7})
    fig.update_layout(
        height=440,
        margin={"l": 10, "r": 10, "t": 12, "b": 10},
        legend={"title": {"text": "Formato"}, "orientation": "h", "y": -0.28},
    )
    return fig


# A base é histórica; os valores nunca são baixados ou inventados a cada interação.
try:
    data = load_data()
except (FileNotFoundError, ValueError, pd.errors.ParserError) as exc:
    st.error(f"Não foi possível carregar a base tratada: {exc}")
    st.stop()

st.title("📺 Anime Insights")
st.caption("Explore distribuições e avaliações para escolher títulos da base histórica do Anime Recommendations Database.")

if data.empty:
    st.warning("O arquivo dataset.csv não possui registros para análise.")
    st.stop()

all_types = sorted(data["type"].dropna().unique().tolist())
all_genres = sorted({genre for genres in data["genre_list"] for genre in genres})

with st.sidebar:
    st.header("Painel lateral · Filtros")
    selected_types = st.multiselect(
        "Formato",
        options=all_types,
        default=all_types,
        help="Se nenhum formato for escolhido, nenhum título será exibido.",
    )
    selected_genres = st.multiselect(
        "Gênero",
        options=all_genres,
        default=[],
        placeholder="Todos os gêneros",
        help="Um anime entra no recorte se possuir pelo menos UM dos gêneros selecionados (OU).",
    )
    st.caption("**Gêneros:** nenhum selecionado = todos; vários selecionados = OU. **Formato:** nenhum = nenhum título.")
    st.divider()
    st.subheader("Intervalos")
    ranges = {
        "rating": slider_range("Nota", data["rating"], key="rating_range", decimal=True),
        "episodes": slider_range("Episódios", data["episodes"], key="episodes_range"),
        "members": slider_range("Membros", data["members"], key="members_range", member=True),
    }
    st.divider()
    st.subheader("Laboratório")
    selected_vars = st.multiselect(
        "Variáveis quantitativas",
        options=list(VARIABLES),
        default=list(VARIABLES),
        format_func=lambda value: VARIABLES[value],
        help="Controla apenas o mapa de calor e os histogramas do Dashboard 1.",
    )
    logarithmic_hist = st.toggle(
        "Usar log(1 + x) em episódios e membros",
        value=True,
        help="A transformação muda somente a visualização dos histogramas. A correlação e as métricas permanecem nos dados originais.",
    )
    st.divider()
    st.caption("Fonte: CooperUnion / Kaggle. A base é histórica; membros não são a quantidade de avaliações, receita ou espectadores únicos.")

filtered = apply_filters(data, selected_types, selected_genres, ranges)
st.caption(f"**{fmt_int(len(filtered))}** de **{fmt_int(len(data))}** registros no recorte selecionado. Os filtros laterais valem para os dois dashboards.")

tab_lab, tab_choice = st.tabs(["🔬 Laboratório de análise", "🎯 Escolha seu anime"])

with tab_lab:
    st.header("Dashboard 1 — Laboratório de análise")
    if filtered.empty:
        st.warning("Nenhum anime atende aos filtros atuais. Amplie os intervalos, gêneros ou formatos.")
    elif not selected_vars:
        st.info("Selecione pelo menos uma variável quantitativa no painel lateral para exibir o laboratório.")
    else:
        with st.container(key="card_lab_heatmap"):
            st.subheader("Correlação de Spearman · mapa de calor")
            if len(selected_vars) < 2:
                st.info("Selecione pelo menos duas variáveis para visualizar correlações.")
            elif len(filtered) < 3:
                st.info("São necessários pelo menos três registros para interpretar a correlação.")
            else:
                st.plotly_chart(plot_heatmap(filtered, selected_vars), use_container_width=True, key="spearman_map")
                nonconstant = [
                    column for column in selected_vars if filtered[column].dropna().nunique() > 1
                ]
                if len(nonconstant) < len(selected_vars):
                    st.caption("'—' indica correlação indefinida (por exemplo, variável constante ou poucos pares válidos).")
            st.caption("ρ de Spearman calculado sobre valores originais (−1 a +1). Correlação não implica causalidade.")

        for start in range(0, len(selected_vars), 2):
            pair = selected_vars[start : start + 2]
            cols = st.columns(2, gap="small")
            for col, variable in zip(cols, pair):
                with col:
                    with st.container(key=f"card_hist_{variable}"):
                        st.subheader(f"Histograma de {VARIABLES[variable].lower()}")
                        histogram = plot_histogram(filtered, variable, logarithmic_hist)
                        if histogram is None:
                            st.info("Não há valores válidos para este histograma.")
                        else:
                            st.plotly_chart(histogram, use_container_width=True, key=f"hist_{variable}")
                        if logarithmic_hist and variable in ("episodes", "members"):
                            st.caption("Classes calculadas em log(1 + x); eixo horizontal transformado.")
                        else:
                            st.caption("Classes na escala original; sem exclusão automática de outliers.")
            if len(pair) == 1:
                with cols[1]:
                    with st.container(key="card_lab_notes"):
                        st.subheader("Como interpretar")
                        st.markdown(
                            "Os histogramas mostram quantos **títulos** estão em cada faixa. "
                            "A transformação `log(1 + x)` ajuda a visualizar variáveis assimétricas, "
                            "sem modificar os filtros ou os cálculos das métricas."
                        )
                        st.caption("Valores ausentes não são contados no histograma correspondente.")

with tab_choice:
    st.header("Dashboard 2 — Escolha seu anime")
    if filtered.empty:
        st.warning("Nenhum anime atende aos filtros atuais. Amplie o recorte para consultar as métricas e o ranking.")
    else:
        total = len(filtered)
        mean_rating = filtered["rating"].mean()
        high_score = 100 * filtered["rating"].ge(8).sum() / total
        tv = filtered[filtered["type"].eq("TV")]
        short_tv = (100 * tv["episodes"].le(12).sum() / len(tv)) if len(tv) else None

        metric_specs = [
            ("Títulos disponíveis", fmt_int(total), "Registros após os filtros"),
            ("Nota média", fmt_decimal(mean_rating) if pd.notna(mean_rating) else "N/D", "Média simples, não ponderada"),
            ("Com nota ≥ 8", f"{fmt_decimal(high_score, 1)}%", "Entre todos os títulos filtrados"),
            ("Séries TV curtas", f"{fmt_decimal(short_tv, 1)}%" if short_tv is not None else "N/A", "Até 12 episódios entre séries TV" if short_tv is not None else "Sem séries TV no recorte"),
        ]
        metric_columns = st.columns(4, gap="small")
        for index, (label, value, explanation) in enumerate(metric_specs):
            with metric_columns[index]:
                with st.container(key=f"card_metric_{index}"):
                    st.metric(label, value)
                    st.caption(explanation)

        with st.container(key="card_choice_ranking"):
            st.subheader("Animes mais bem avaliados · ranking")
            max_members = max(0, int(filtered["members"].max())) if filtered["members"].notna().any() else 0
            min_ranking = st.number_input(
                "Mínimo de membros para entrar no ranking (não altera KPIs ou outros gráficos)",
                min_value=0,
                max_value=max_members,
                value=0,
                step=1000 if max_members >= 1000 else 1,
                key="ranking_min_members",
            )
            ranking = filtered[
                filtered["rating"].notna() & filtered["members"].ge(min_ranking)
            ]
            if ranking.empty:
                st.info("Nenhum título com nota válida atende ao mínimo de membros do ranking.")
            else:
                st.plotly_chart(plot_ranking(ranking), use_container_width=True, key="ranking_chart")
                st.caption("Até dez títulos; desempate por mais membros e, depois, menor anime_id.")

        with st.container(key="card_choice_genres"):
            st.subheader("Nota média por gênero")
            genres_chart = plot_genre_means(filtered)
            if genres_chart is None:
                st.info("Não há gêneros com avaliações válidas neste recorte.")
            else:
                st.plotly_chart(genres_chart, use_container_width=True, key="genres_chart")
            st.caption("Os 12 gêneros mais frequentes no recorte. Um título pode participar de vários gêneros; cada nota tem peso igual dentro do gênero.")

        with st.container(key="card_choice_scatter"):
            st.subheader("Popularidade × avaliação")
            scatter = plot_scatter(filtered)
            if scatter is None:
                st.info("Não há títulos com nota válida e membros maiores que zero para o gráfico logarítmico.")
            else:
                st.plotly_chart(scatter, use_container_width=True, key="scatter_chart")
            st.caption("Eixo horizontal logarítmico de membros (apenas membros > 0). Cores por formato. Membros não equivalem ao número de avaliações.")

        with st.expander("📋 Consultar títulos filtrados", expanded=False):
            search = st.text_input("Buscar por nome (somente nesta tabela)", placeholder="Digite parte do nome do anime")
            table = filtered
            if search.strip():
                table = table[table["name"].str.contains(search.strip(), case=False, na=False, regex=False)]
            table = table.sort_values(["rating", "members"], ascending=[False, False], na_position="last")
            st.caption(f"{fmt_int(len(table))} título(s) nesta tabela.")
            st.dataframe(
                table[["anime_id", "name", "genre", "type", "episodes", "rating", "members"]].rename(
                    columns={
                        "anime_id": "ID", "name": "Anime", "genre": "Gêneros",
                        "type": "Formato", "episodes": "Episódios", "rating": "Nota", "members": "Membros",
                    }
                ),
                hide_index=True,
                use_container_width=True,
            )

st.divider()
st.caption(
    "Base histórica: Anime Recommendations Database (CooperUnion / Kaggle). "
    "Os indicadores descrevem o recorte da base, não disponibilidade atual em streaming. "
    "Associação estatística não estabelece causalidade."
)
