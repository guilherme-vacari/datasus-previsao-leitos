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

def _escrever_raw(pasta, nome, datas):
    df = pd.DataFrame(
        {
            "N_AIH": [str(i) for i in range(len(datas))],
            "DIAS_PERM": ["2"] * len(datas),
            "QT_DIARIAS": ["2"] * len(datas),
            "IDADE": ["40"] * len(datas),
            "MORTE": ["0"] * len(datas),
            "VAL_TOT": ["100"] * len(datas),
            "DT_INTER": datas,
            "DT_SAIDA": datas,
            "CNES": ["12345"] * len(datas),
        }
    )
    df.to_parquet(pasta / nome, index=False)


def test_construir_serie_soma_meses_entre_arquivos(tmp_path):
    _escrever_raw(tmp_path, "sih_rd_PR_202301.parquet", ["20230110", "20230120", "20230205"])
    _escrever_raw(tmp_path, "sih_rd_PR_202302.parquet", ["20230210", "20230301"])
    resultado = clean.construir_serie("PR", raw_dir=tmp_path, n_descartar=1)
    assert list(resultado["internacoes"]) == [2, 2]

