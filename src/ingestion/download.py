import argparse
from pathlib import Path
import pysus
from ftplib import FTP
import pandas as pd
import pyreaddbc
from dbfread import DBF

RAIZ = Path(__file__).resolve().parents[2]
RAW_DIR = RAIZ / "data" / "raw"
PASTA_FTP = "/dissemin/publicos/SIHSUS/200801_/Dados/"
DBC_DIR = RAW_DIR / "dbc"
COLUNAS_NUMERICAS = ["DIAS_PERM", "QT_DIARIAS", "IDADE", "MORTE", "VAL_TOT"]

colunas = [
    "UF_ZI",
    "ANO_CMPT",
    "MES_CMPT",
    "N_AIH",
    "IDENT",
    "CNES",
    "MUNIC_MOV",
    "MUNIC_RES",
    "DT_INTER",
    "DT_SAIDA",
    "DIAG_PRINC",
    "DIAS_PERM",
    "QT_DIARIAS",
    "ESPEC",
    "CAR_INT",
    "IDADE",
    "COD_IDADE",
    "SEXO",
    "MORTE",
    "VAL_TOT"
]

def caminho_saida(uf, ano, mes):

    return RAW_DIR/ f"sih_rd_{uf}_{ano}{mes:02d}.parquet"

def buscar_via_ftp(uf, ano, mes):
    nome = f"RD{uf}{ano % 100:02d}{mes:02d}"
    dbc = DBC_DIR / f"{nome}.dbc"
    dbf = DBC_DIR / f"{nome}.dbf"
    DBC_DIR.mkdir(parents=True, exist_ok=True)

    # baixar o .dbc em modo binário
    try:
        with FTP("ftp.datasus.gov.br", timeout=60) as ftp:
            ftp.login()
            ftp.cwd(PASTA_FTP)
            with open(dbc, "wb") as arquivo:
                ftp.retrbinary(f"RETR {nome}.dbc", arquivo.write)
    except Exception:
        dbc.unlink(missing_ok=True)   # não deixa um arquivo pela metade
        raise

    pyreaddbc.dbc2dbf(str(dbc), str(dbf))

    if not dbf.exists():
        raise FileNotFoundError(
            f"A conversão de {dbc.name} não gerou o .dbf. "
            "Rode a conversão no terminal para ver a mensagem de erro."
        )

    # ler o .dbf
    df = pd.DataFrame(iter(DBF(str(dbf), encoding="iso-8859-1")))

    for coluna in COLUNAS_NUMERICAS:
        df[coluna] = df[coluna].astype(str)

    dbf.unlink()
    return df

def buscar_mes(uf, ano, mes):
    df = pysus.sih(uf, ano, mes, group="RD", as_dataframe=True)

    if df.empty:
        print(f"Espelho sem dados para {ano}-{mes:02d}; buscando no FTP oficial...")
        df = buscar_via_ftp(uf, ano, mes)

    return df

def baixar_sih(uf, ano, mes):

    saida = caminho_saida(uf, ano, mes)

    if saida.exists():
        print(f"Já existe, nada a fazer: {saida}")
        return

    df = buscar_mes(uf, ano, mes)

    if df.empty:
        raise ValueError(f"Nenhum dado retornado para {uf} {ano}-{mes:02d}")

    df = df[colunas]

    saida.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(saida, index=False)
    print(f"Salvo: {saida} ({len(df)} linhas)")

def baixar_periodos(uf, ano_inicio, ano_fim):
    falhas = []

    for ano in range(ano_inicio, ano_fim + 1):
        for mes in range (1, 13):
            try:
                baixar_sih(uf, ano, mes)
            except Exception as erro:
                print(f'Falhou {ano}-{mes:02d}: {erro}')
                falhas.append((ano, mes))

    print(f'Concluído. Meses com falha: {len(falhas)}')
    for ano, mes in falhas:
        print(f' - {ano}-{mes:02d}')


def main():
    parser = argparse.ArgumentParser(description="Baixa o SIH-RD do DATASUS")
    parser.add_argument("--uf", required=True)
    parser.add_argument("--ano", type=int, required=True)
    parser.add_argument("--mes", type=int)
    parser.add_argument("--ano-fim", type=int)
    args = parser.parse_args()

    uf = args.uf.upper()

    if args.ano_fim:
        baixar_periodos(uf, args.ano, args.ano_fim)
    elif args.mes:
        baixar_sih(uf, args.ano, args.mes)
    else:
        parser.error("Informe --mes (um mês) ou --ano_fim (um período).")

if __name__ == "__main__":
    main()