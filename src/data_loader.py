# [IA] ChatGPT - Implementação do carregamento
# do dataset tratado, resolução do caminho e cache.

"""Leitura e preparação da base histórica de animes utilizada nos dashboards."""

from pathlib import Path

import pandas as pd
import streamlit as st


# O caminho é independente do diretório em que `streamlit run` foi executado.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATASET_PATH = PROJECT_ROOT / "data" / "clean" / "dataset.csv"
REQUIRED_COLUMNS = (
    "anime_id",
    "name",
    "genre",
    "type",
    "episodes",
    "rating",
    "members",
)


def _split_genres(value: str) -> tuple[str, ...]:
    """Separa gêneros por vírgula, sem repetir um gênero dentro do mesmo anime."""
    return tuple(dict.fromkeys(part.strip() for part in value.split(",") if part.strip()))


@st.cache_data(show_spinner=False)
def _read_and_prepare(csv_path: str, modified_ns: int) -> pd.DataFrame:
    """Mantém o CSV em cache; a data de modificação invalida o cache local."""
    # modified_ns faz parte da chave do cache, mesmo não sendo usado na leitura.
    _ = modified_ns
    df = pd.read_csv(csv_path, low_memory=False)

    missing = [column for column in REQUIRED_COLUMNS if column not in df.columns]
    if missing:
        raise ValueError("O dataset tratado não possui as colunas: " + ", ".join(missing))

    df = df.copy()
    df["anime_id"] = pd.to_numeric(df["anime_id"], errors="coerce").astype("Int64")
    for column in ("rating", "episodes", "members"):
        # Valores como 'Unknown' em episodes tornam-se ausentes, sem inventar zeros.
        df[column] = pd.to_numeric(df[column], errors="coerce")

    df["name"] = df["name"].fillna("Título sem nome").astype(str).str.strip()
    df["name"] = df["name"].replace("", "Título sem nome")
    df["type"] = df["type"].fillna("Não informado").astype(str).str.strip()
    df["type"] = df["type"].replace("", "Não informado")
    df["genre"] = df["genre"].fillna("").astype(str).str.strip()
    df["genre_list"] = df["genre"].map(_split_genres)

    return df


def load_data() -> pd.DataFrame:
    """Carrega exclusivamente data/clean/dataset.csv, a partir da raiz do projeto."""
    if not DATASET_PATH.is_file():
        raise FileNotFoundError(
            f"Base tratada não encontrada em {DATASET_PATH}. "
            "Coloque dataset.csv em data/clean/ antes de iniciar o app."
        )
    return _read_and_prepare(str(DATASET_PATH), DATASET_PATH.stat().st_mtime_ns)
