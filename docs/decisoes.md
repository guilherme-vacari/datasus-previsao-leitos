# SC (2019 a 2024): 8 de 72 meses indisponiveis no PySUS (espelho e FTP). Escolhido PR como estado principal por ter a série completa.

# Foi identificado um problema na leitura dos dados via pySUS para 9 meses. Então a decisão foi adicionar um bloco onde olhamos para o espelho do FTP, realizar o download do arquivo .dbc, transformar em dbf e carregá-lo como parquet.