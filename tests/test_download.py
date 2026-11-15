import pandas as pd
from src.ingestion import download

def test_caminho_saida_formata_nome(monkeypatch, tmp_path):
    monkeypatch.setattr(download, "RAW_DIR", tmp_path)
    resultado = download.caminho_saida("PR", 2022, 3)
    assert resultado == tmp_path / "sih_rd_PR_202203.parquet"

def test_buscar_mes_usa_ftp_quando_espelho_vazio(monkeypatch):
    chamadas = []

    