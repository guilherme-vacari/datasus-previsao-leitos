import argparse
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parents[2]
RAW_DIR = RAIZ / "data" / "raw"
PROCESSED_DIR = RAIZ / "data" / "processed"

COLUNAS_NUMERICAS = ["DIAS_PERM", "QT_DIARIAS", "IDADE", "MORTE", "VAL_TOT"]
COLUNAS_DATA = ["DT_INTER", "DT_SAIDA"]

JANELA_INICIO = pd.Timestamp("2019-01-01")
MESES_DESCARTADOS = 3

def converter_tipos(df: pd.DataFrame) -> pd.DataFrame:
    '''Converte as colunas de texto da camada raw para número e data'''
    df = df.copy()
    for coluna in COLUNAS_NUMERICAS:
        df[coluna]  = pd.to_numeric(df[coluna], errors='coerce')
    for coluna in COLUNAS_DATA:
        df[coluna] = pd.to_datetime(df[coluna], format='%Y%m%d', errors= 'coerce')
    df['CNES'] = df['CNES'].astype('string').str.zfill(7)
    return df

def filtrar_janela(df: pd.DataFrame, inicio: pd.Timestamp = JANELA_INICIO) -> pd.DataFrame:
    """Mantém apenas as internações com DT_INTER a partir de 'inicio'."""
    filtrado = df[df["DT_INTER"] >= inicio]
    return filtrado.copy()

def agregar_mensal(df: pd.DataFrame) -> pd.DataFrame:
    """"Conta internações e soma dias-leito por mês de DT_INTER"""
    return (
        df.assign(mes=df["DT_INTER"].dt.to_period("M").dt.to_timestamp())
        .groupby("mes", as_index=False)
        .agg(
            internacoes=("N_AIH", "size"), 
            dias_leito=("DIAS_PERM", "sum"),
        )
    )

def descartar_meses_incompletos(serie: pd.DataFrame, n: int = MESES_DESCARTADOS) -> pd.DataFrame:
    """"Remove os n últimos meses da série, que ainda estão incompletos."""
    if n < 0:
        raise ValueError("n não pode ser negativo")
    ordenada = serie.sort_values("mes")
    return ordenada.iloc[: len(ordenada) - n].reset_index(drop=True)

def limpar_arquivo(caminho: Path) -> pd.DataFrame:
    """Lê um Parquet da camada raw e devolve a agregação mensal dele."""
    df = pd.read_parquet(caminho)
    df = converter_tipos(df)
    df = filtrar_janela(df)
    return agregar_mensal(df)

def construir_serie(
    uf: str = "PR",
    raw_dir: Path = RAW_DIR,
    n_descartar: int = MESES_DESCARTADOS,
) -> pd.DataFrame:
    """Constrói a série mensal de internações e dias-leito de uma UF."""
    arquivos = sorted(Path(raw_dir).glob(f"sih_rd_{uf}_*.parquet"))
    if not arquivos:
        raise FileNotFoundError(f"Nenhum arquivo sih_rd_{uf}_*.parquet em {raw_dir}")
    parciais = [limpar_arquivo(arquivo) for arquivo in arquivos]
    total = pd.concat(parciais, ignore_index=True).groupby("mes", as_index=False).sum()
    return descartar_meses_incompletos(total, n_descartar)

def main() -> None:
    parser = argparse.ArgumentParser(description="Constrói a série mensal limpa.")
    parser.add_argument("--uf", default="PR")
    args = parser.parse_args()
    serie = construir_serie(args.uf)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    saida = PROCESSED_DIR / f"serie_mensal_{args.uf}.parquet"
    serie.to_parquet(saida, index=False)
    print(f"Salvo: {saida} ({len(serie)} meses)")


if __name__ == "__main__":
    main()

