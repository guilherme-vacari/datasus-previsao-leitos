import pandas as pd

from src.ingestion import download


def test_caminho_saida_formata_nome(monkeypatch, tmp_path):
    monkeypatch.setattr(download, "RAW_DIR", tmp_path)
    resultado = download.caminho_saida("PR", 2022, 3)
    assert resultado == tmp_path / "sih_rd_PR_202203.parquet"


def test_buscar_mes_usa_ftp_quando_espelho_vazio(monkeypatch):
    chamadas = []

    def ftp_falso(uf, ano, mes):
        chamadas.append((uf, ano, mes))
        return pd.DataFrame({"N_AIH": ["1"]})

    # o espelho devolve vazio, como aconteceu com RDPR2205
    monkeypatch.setattr(download.pysus, "sih", lambda *a, **k: pd.DataFrame())
    monkeypatch.setattr(download, "buscar_via_ftp", ftp_falso)

    df = download.buscar_mes("PR", 2022, 5)

    assert chamadas == [("PR", 2022, 5)]
    assert not df.empty


def test_buscar_mes_nao_usa_ftp_quando_espelho_tem_dados(monkeypatch):
    def ftp_proibido(*args, **kwargs):
        raise AssertionError("não deveria chamar o FTP")

    monkeypatch.setattr(
        download.pysus, "sih", lambda *a, **k: pd.DataFrame({"N_AIH": ["1"]})
    )
    monkeypatch.setattr(download, "buscar_via_ftp", ftp_proibido)

    df = download.buscar_mes("PR", 2022, 5)

    assert len(df) == 1

    