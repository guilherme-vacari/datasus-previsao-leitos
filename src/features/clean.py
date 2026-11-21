import pandas as pd

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
