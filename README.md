# Dashboard SIC-SFCL

Dashboard em Streamlit para apoiar a analise de um limitador de corrente de curto-circuito indutivo saturado de nucleo aberto.

## Objetivo

A aplicacao centraliza visualizacoes e calculos usados no estudo do limitador:

- apresentacao do principio de funcionamento;
- curva B-H e permeabilidade relativa;
- calculo RMS de sinais no dominio do tempo;
- analise harmonica por FFT;
- analise de otimizacao com resultados exportados do COMSOL.

## Estrutura

```text
dashboard/
├── app.py
├── requirements.txt
├── pages/
│   ├── 02_Curva_BH.py
│   ├── 03_RMS.py
│   ├── 04_Harmonicos.py
│   └── 05_Otimizacao.py
├── Dataset/
│   ├── b_h_curve/
│   │   └── Curva_B_H_Sem_Perdas.txt
│   ├── harmonics/
│   │   ├── Corrente FFT.csv
│   │   └── Corrente FFT2.csv
│   ├── root_mean_square/
│   │   └── Tensão RMS.csv
│   └── optimization/
│       └── *.txt
└── imagens/
    └── AnaliseDinamica.gif
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

## Como executar

```powershell
streamlit run app.py
```

## Caminhos dos dados

Os arquivos locais sao acessados por caminhos relativos com `pathlib.Path`, o que permite executar o app localmente e tambem no Streamlit Cloud.

Exemplos:

```python
BASE_DIR = Path(__file__).resolve().parents[1]
arquivo_bh = BASE_DIR / "Dataset" / "b_h_curve" / "Curva_B_H_Sem_Perdas.txt"
pasta_otimizacao = BASE_DIR / "Dataset" / "optimization"
```

## Paginas

### 1. Pagina inicial

Arquivo: `app.py`

Apresenta o projeto, o principio de operacao do limitador e a animacao `imagens/AnaliseDinamica.gif`.

### 2. Curva B-H

Arquivo: `pages/02_Curva_BH.py`

Le `Dataset/b_h_curve/Curva_B_H_Sem_Perdas.txt`, calcula a permeabilidade relativa a partir da derivada numerica `dB/dH` e exibe grafico e tabela.

### 3. RMS

Arquivo: `pages/03_RMS.py`

Le arquivos TXT de `Dataset/optimization`, permite escolher a combinacao e as colunas de tempo/sinal, calcula o RMS total e plota o sinal com linha de RMS.

### 4. Harmonicos

Arquivo: `pages/04_Harmonicos.py`

Le arquivos TXT de `Dataset/optimization`, permite escolher a combinacao e as colunas de tempo/sinal, calcula FFT, amplitudes RMS por harmonico e percentual em relacao ao harmonico fundamental `n = 1`.

### 5. Otimizacao

Arquivo: `pages/05_Otimizacao.py`

Le arquivos `.txt` em `Dataset/optimization`, consolida maximos de queda de tensao e corrente de curto em janelas de tempo especificas e exibe a analise de viabilidade.

Filtros principais:

- arquivos lidos;
- faixa de queda de tensao;
- faixa de corrente de curto;
- H, W, N_DC e N_AC;
- destaques customizados por parametro/valor;
- exibicao opcional da curva aproximada;
- exibicao opcional de small multiples.

## Deploy no Streamlit Cloud

Para o deploy funcionar, mantenha:

- `requirements.txt` na raiz do repositorio;
- caminhos relativos via `Path(__file__)`;
- arquivos de dados dentro da pasta `Dataset/`;
- imagem da pagina inicial dentro de `imagens/`.

Evite versionar arquivos `desktop.ini`, `__pycache__` e outros arquivos gerados pelo Windows/Python.