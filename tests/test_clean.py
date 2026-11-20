import pandas as pd
from src.features import clean

def _df(**colunas):
    base = {
        "DIAS_PERM": ["5"],
        "QT_DIARIAS": ["5"],
        "IDADE": ["40"],
        "MORTE": ["0"],
        "VAL_TOT": ["1000.5"],
        "DT_INTER": ["20230101"],
        "DT_SAIDA": ["20230106"],
        "CNES": ["12345"],
    }
    base.update(colunas)
    return pd.DataFrame(base)

def test_converte_numericas():
    resultado = clean.converter_tipos(_df(DIAS_PERM=['7']))
    assert resultado["DIAS_PERM"].iloc[0] == 7

