# Dashboard SIC-SFCL

Dashboard em Streamlit para apoiar a analise de um limitador de corrente de curto-circuito indutivo saturado de nucleo aberto.

## Objetivo

A aplicacao centraliza visualizacoes e calculos usados no estudo do limitador:

- apresentacao do principio de funcionamento;
- curva B-H e permeabilidade relativa;
- visualizacao de corrente e tensao no dominio do tempo;
- calculo RMS de sinais no dominio do tempo;
- analise harmonica por FFT;
- analise de otimizacao com resultados exportados do COMSOL.

## Estrutura

```text
dashboard/
|-- app.py
|-- requirements.txt
|-- app_pages/
|   |-- 02_Curva_BH.py
|   |-- 03_Otimizacao.py
|   |-- 04_Visualizar_Sinal.py
|   |-- 05_RMS.py
|   |-- 06_Harmonicos.py
|   |-- 07_Otimizacao_2_Nucleos_1_Bobina.py
|   |-- 08_Otimizacao_2_Nucleos_2_Bobinas.py
|   |-- 09_Otimizacao_1_Nucleo_2_Bobinas.py
|   `-- otimizacao_base.py
|-- Dataset/
|   |-- b_h_curve/
|   |   `-- Curva_B_H_Sem_Perdas.txt
|   |-- optimization_1_core_1_coil/
|   |   `-- *.txt
|   |-- optimization_1_core_2_coil/
|   |   `-- *.txt
|   |-- optimization_2_core_1_coil/
|   |   `-- *.txt
|   `-- optimization_2_core_2_coil/
|       `-- *.txt
`-- imagens/
    `-- AnaliseDinamica.gif
```

## Dependencias

Instale com:

```powershell
pip install -r requirements.txt
```

Principais bibliotecas:

- streamlit
- pandas
- numpy
- plotly
- scipy
- openpyxl
- scikit-learn

## Como executar

```powershell
streamlit run app.py
```

## Caminhos dos dados

Os arquivos locais da aplicacao sao acessados por caminhos relativos com `pathlib.Path`, o que permite executar o app localmente e tambem no Streamlit Cloud.

Exemplos:

```python
BASE_DIR = Path(__file__).resolve().parents[1]
arquivo_bh = BASE_DIR / "Dataset" / "b_h_curve" / "Curva_B_H_Sem_Perdas.txt"
pasta_otimizacao = BASE_DIR / "Dataset" / "optimization_1_core_1_coil"
```

As paginas Visualizar sinal, RMS e Harmonicos nao monitoram uma pasta fixa. Elas aguardam o usuario selecionar manualmente um arquivo `.txt` exportado do COMSOL.

## Paginas

### 1. Pagina inicial

Arquivo: `app.py`

Apresenta o projeto, o principio de operacao do limitador e a animacao `imagens/AnaliseDinamica.gif`.

### 2. Curva B-H

Arquivo: `app_pages/02_Curva_BH.py`

Le `Dataset/b_h_curve/Curva_B_H_Sem_Perdas.txt`, calcula a permeabilidade relativa a partir da derivada numerica `dB/dH` e exibe grafico e tabela.

### 3. Otimizacao - 1 Nucleo & 1 Bobina

Arquivo: `app_pages/03_Otimizacao.py`

Le arquivos `.txt` em `Dataset/optimization_1_core_1_coil` e tambem aceita multiplos arquivos TXT carregados manualmente, consolida maximos de queda de tensao e corrente de curto em janelas de tempo especificas, exibe a analise de viabilidade e inclui uma analise opcional de sensibilidade por modelo.

### 4. Otimizacao - 1 Nucleo & 2 Bobinas

Arquivo: `app_pages/09_Otimizacao_1_Nucleo_2_Bobinas.py`

Usa a mesma interface, logica, graficos, filtros e comportamento da pagina de otimizacao de 1 nucleo e 1 bobina, lendo exclusivamente os arquivos `.txt` de `Dataset/optimization_1_core_2_coil`. O espaco do esboco 3D permanece em branco temporariamente.

### 5. Otimizacao - 2 Nucleos & 1 Bobina

Arquivo: `app_pages/07_Otimizacao_2_Nucleos_1_Bobina.py`

Usa a mesma interface, logica, graficos, filtros e comportamento da pagina de otimizacao de 1 nucleo e 1 bobina, lendo exclusivamente os arquivos `.txt` de `Dataset/optimization_2_core_1_coil`.

### 6. Otimizacao - 2 Nucleos & 2 Bobinas

Arquivo: `app_pages/08_Otimizacao_2_Nucleos_2_Bobinas.py`

Usa a mesma interface, logica, graficos, filtros e comportamento da pagina de otimizacao de 1 nucleo e 1 bobina, lendo exclusivamente os arquivos `.txt` de `Dataset/optimization_2_core_2_coil`.

Filtros principais das paginas de otimizacao:

- arquivos embutidos e arquivos carregados;
- faixa de queda de tensao;
- faixa de corrente de curto;
- H, W, N_DC e N_AC;
- destaques customizados por parametro/valor;
- exibicao opcional da curva aproximada.

### 6. Visualizar sinal


Arquivo: `app_pages/04_Visualizar_Sinal.py`

Aguarda o envio manual de um arquivo TXT exportado do COMSOL e exibe corrente de curto e queda de tensao no dominio do tempo em um unico grafico com eixo secundario para tensao.

### 7. RMS

Arquivo: `app_pages/05_RMS.py`

Aguarda o envio manual de um arquivo TXT exportado do COMSOL pelo seletor de arquivos. Depois do carregamento, permite escolher a combinacao e as colunas de tempo/sinal, calcula o RMS total e plota o sinal com linha de RMS.

### 8. Harmonicos

Arquivo: `app_pages/06_Harmonicos.py`

Aguarda o envio manual de um arquivo TXT exportado do COMSOL pelo seletor de arquivos. Depois do carregamento, permite escolher a combinacao e as colunas de tempo/sinal, calcula FFT, amplitudes RMS por harmonico e percentual em relacao ao harmonico fundamental 
 = 1`.
## Deploy no Streamlit Cloud

Para o deploy funcionar, mantenha:

- `requirements.txt` na raiz do repositorio;
- caminhos relativos via `Path(__file__)`;
- arquivos de dados dentro da pasta `Dataset/`;
- imagem da pagina inicial dentro de `imagens/`.

Evite versionar arquivos `desktop.ini`, `__pycache__` e outros arquivos gerados pelo Windows/Python.



