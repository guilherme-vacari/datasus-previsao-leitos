import argparse
from pathlib import Path
import pysus

RAW_DIR = Path("data/raw")

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

def baixar_sih(uf, ano, mes):

    saida = caminho_saida(uf, ano, mes)

    if saida.exists():
        print(f'Já existe, nada a fazer: {saida}')
        return

    df = pysus.sih(uf, ano, mes, group='RD', as_dataframe=True)
    df = df[colunas]

    saida.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(saida, index=False)
    print(f'Salvo: {saida} ({len(df)} linhas)')

def main():
    parser = argparse.ArgumentParser(description="Baixa o SIH-RD do DATASUS")
    parser.add_argument("--uf", required=True)
    parser.add_argument("--ano", type=int, required=True)
    parser.add_argument("--mes", type=int, required=True)
    args = parser.parse_args()

    baixar_sih(args.uf.upper(), args.ano, args.mes)

if __name__ == "__main__":
    main()