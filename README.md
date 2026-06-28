# Dashboard de Analise de Sinais Eletricos

Este projeto e um dashboard desenvolvido em Python com Streamlit para apoiar a analise de sinais eletricos, curva B-H, valor RMS, harmonicos por FFT e resultados de otimizacao obtidos por simulacao.

## Objetivo

O dashboard centraliza visualizacoes e calculos usados no estudo de um limitador de corrente de curto-circuito. A aplicacao permite:

- visualizar uma animacao introdutoria do campo magnetico;
- analisar a curva B-H e a permeabilidade relativa do material;
- calcular o valor RMS total de sinais no dominio do tempo;
- decompor sinais em harmonicos por FFT;
- filtrar e comparar combinacoes de parametros de otimizacao.

## Estrutura do projeto

```text
dashboard/
├── app.py
├── pages/
│   ├── 02_Curva_BH.py
│   ├── 03_RMS.py
│   ├── 04_Harmonicos.py
│   └── 05_Otimizacao.py
├── Dataset/
│   ├── Curva_B_H_Sem_Perdas.txt
│   ├── otimization 2.0/
│   ├── NOVA OTIMIZACAO.txt
│   ├── otimizacao_V1.txt
│   ├── otimizacao_V2.txt
│   └── onda_senoidal_perfeita_60Hz_dt_10us.csv
└── imagens/
    └── AnaliseDinamica.gif
```

## Dependencias

O projeto usa as seguintes bibliotecas principais:

- `streamlit`
- `pandas`
- `numpy`
- `plotly`
- `scipy`
- `openpyxl`

Instalacao sugerida:

```powershell
pip install streamlit pandas numpy plotly scipy openpyxl
```

## Como executar

Abra o terminal na pasta do projeto:

```powershell
cd "G:\Meu Drive\01 - Faculdade\TCC\python\dashboard"
```

Execute o dashboard:

```powershell
streamlit run app.py
```

Depois disso, o Streamlit deve abrir a aplicacao no navegador.

## Ordem das paginas

A organizacao das paginas foi feita por numeracao dos arquivos:

1. `app.py` - pagina inicial
2. `pages/02_Curva_BH.py` - curva B-H e permeabilidade relativa
3. `pages/03_RMS.py` - calculo RMS
4. `pages/04_Harmonicos.py` - analise harmonica por FFT
5. `pages/05_Otimizacao.py` - analise de otimizacao COMSOL

## Pagina inicial

Arquivo: `app.py`

A pagina inicial apresenta o titulo do projeto e exibe a animacao:

```text
imagens/AnaliseDinamica.gif
```

Essa animacao representa o campo magnetico no dominio do tempo.

## Curva B-H e permeabilidade relativa

Arquivo: `pages/02_Curva_BH.py`

Esta pagina le o arquivo:

```text
Dataset/Curva_B_H_Sem_Perdas.txt
```

O arquivo e interpretado com duas colunas:

- `H`: intensidade de campo magnetico;
- `B`: densidade de fluxo magnetico.

A permeabilidade relativa e calculada a partir da derivada numerica da curva B-H:

```text
mu_r = (dB/dH) / mu_0
```

Onde `mu_0` e a permeabilidade magnetica do vacuo.

A pagina exibe:

- grafico de `B` em funcao de `H`;
- grafico de `mu_r` em escala logaritmica;
- tabela com os dados calculados.

## Analise RMS

Arquivo: `pages/03_RMS.py`

Esta pagina permite carregar um arquivo CSV contendo um sinal no dominio do tempo.

Fluxo da pagina:

1. O usuario carrega um arquivo CSV.
2. Seleciona a coluna de tempo.
3. Seleciona a coluna do sinal eletrico.
4. O sistema remove valores invalidos.
5. Os dados sao ordenados pelo tempo.
6. O valor RMS total e calculado.

Formula usada:

```text
RMS = sqrt(mean(sinal^2))
```

Saidas exibidas:

- valor RMS total com 2 casas decimais;
- grafico do sinal original;
- linha horizontal representando o RMS total.

## Analise de harmonicos por FFT

Arquivo: `pages/04_Harmonicos.py`

Esta pagina realiza a decomposicao harmonica de um sinal usando FFT.

Entrada esperada:

- arquivo CSV separado por ponto e virgula (`;`);
- uma coluna de tempo;
- uma coluna de sinal.

Controles disponiveis:

- limite de frequencia exibida;
- frequencia fundamental;
- amplitude minima para destacar picos em RMS.

Processamento realizado:

1. Conversao das colunas selecionadas para arrays numericos.
2. Remocao de valores invalidos.
3. Ordenacao dos dados pelo tempo.
4. Calculo da FFT.
5. Conversao do espectro unilateral para RMS.
6. Amostragem dos multiplos inteiros da frequencia fundamental.
7. Calculo do percentual de cada harmonico em relacao ao harmonico fundamental.

O percentual harmonico usa:

```text
percentual_n = (RMS_n / RMS_1) * 100
```

Assim, o harmonico `n = 1` representa `100%`.

Saidas exibidas:

- grafico de barras dos harmonicos em RMS;
- marcadores para componentes acima da amplitude minima;
- percentual de cada harmonico no hover e nos rotulos destacados;
- tabela com harmonico, frequencia, amplitude RMS e percentual relativo ao `n=1`;
- grafico do sinal no dominio do tempo.

## Analise de otimizacao COMSOL

Arquivo: `pages/05_Otimizacao.py`

Esta pagina concatena todos os arquivos TXT encontrados em:

```text
Dataset/otimization 2.0/*.txt
```

As colunas utilizadas são:

- `Time (s)`;
- `Corrente de Curto (A)`;
- `Queda de Tensao (V)`;
- `H(cm)`;
- `W(cm)`;
- `N_DC`;
- `N_AC`;
- `Chave`.

O tratamento dos dados:

1. Filtra a queda de tensão entre `0.01 s` e `0.03 s`.
2. Filtra a corrente de curto-circuito entre `0.0437 s` e `0.0525 s`.
3. Calcula o valor máximo de cada grandeza para cada `Chave`.
4. Combina os resultados de tensão e corrente pela coluna `Chave`.

A página permite filtrar os resultados por `H`, `W`, `N_DC` e `N_AC`.

As combinações são exibidas em um gráfico de dispersão com:

- queda de tensão no eixo horizontal;
- corrente de curto-circuito no eixo vertical;
- cor dos pontos definida pelo valor de `H`;
- parâmetros completos de cada combinação no hover;
- tabela com os dados consolidados.

## Observacoes importantes

Alguns arquivos sao carregados por caminhos absolutos apontando para a pasta atual do projeto. Se o projeto for movido para outra pasta, pode ser necessario atualizar os caminhos dentro dos arquivos Python.
A pagina de otimizacao ja usa caminho relativo com `pathlib`.

Arquivos principais com caminhos absolutos:

- `app.py`
- `pages/02_Curva_BH.py`

## Manutencao recomendada

Para melhorar a portabilidade do projeto, uma melhoria futura seria substituir os caminhos absolutos por caminhos relativos usando `pathlib.Path`.

Exemplo:

```python
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
arquivo = BASE_DIR / "Dataset" / "Curva_B_H_Sem_Perdas.txt"
```

## Estado atual

O projeto esta organizado como uma aplicacao Streamlit multipagina, com paginas numeradas para controlar a ordem de exibicao no menu lateral.
