# SC (2019 a 2024): 8 de 72 meses indisponiveis no PySUS (espelho e FTP). Escolhido PR como estado principal por ter a série completa.

# Foi identificado um problema na leitura dos dados via pySUS para 9 meses. Então a decisão foi adicionar um bloco onde olhamos para o espelho do FTP, realizar o download do arquivo .dbc, transformar em dbf e carregá-lo como parquet.

# No SIH-RD do PR (2019 a 2024), o mês do arquivo é sempre igual à competência (ANO_CMPT/MES_CMPT) das linhas. Competência é mês de processamento do pagamento, não mês da internação; para demanda, agregar por DT_INTER.

# DT_INTER anterior a 2019-01: ~59 mil linhas, 25 meses distintos. Internações de longa permanência faturadas depois. Filtradas na limpeza para manter a série coerente com a janela 2019-2024.

# Competência coincide com o mês da alta em só 55% das linhas; o restante é faturado depois. A censura à direita afeta os últimos meses da série. Agregação por DT_INTER; descartar os últimos 3 últimos meses conforme a distribuição de defasagem.