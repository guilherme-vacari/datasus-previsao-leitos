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

