from pathlib import Path

import streamlit as st



BASE_DIR = Path(__file__).resolve().parent

st.set_page_config(
    page_title="Limitador de Corrente de Curto-Circuito",
    layout="wide",
)

st.title("Limitador de Corrente de Curto-Circuito Indutivo Saturado")
st.caption(
    "Dashboard de apoio ao desenvolvimento e análise de um limitador "
    "indutivo de núcleo aberto com polarização DC."
)

st.markdown(
    """
    Este projeto investiga um **limitador de corrente de curto-circuito**
    baseado no comportamento magnético de um núcleo ferromagnético saturado.
    Em regime permanente, a bobina DC mantém o núcleo em uma região de baixa
    permeabilidade relativa, reduzindo a indutância equivalente e mantendo a
    impedância inserida no sistema em um nível baixo. Durante uma falta, a
    bobina AC associada ao circuito promove a dessaturação do núcleo, elevando
    a permeabilidade magnética, aumentando a indutância e, consequentemente,
    limitando a corrente de curto.

    A proposta combina modelagem eletromagnética por elementos finitos,
    análise de circuitos e exploração de dados em Python. As simulações foram
    realizadas no COMSOL para avaliar diferentes geometrias, números de espiras
    e condições de operação. Este dashboard organiza esses resultados para
    facilitar a comparação entre configurações e apoiar a escolha de uma
    solução que reduza a corrente de curto sem introduzir queda de tensão
    excessiva em regime permanente.
    """
)

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Corrente nominal", "5 A RMS")
    st.caption("Condição de operação em regime permanente.")

with col2:
    st.metric("Corrente prospectiva", "50 A RMS")
    st.caption("Condição de curto-circuito sem limitação.")

with col3:
    st.metric("Alvo de limitação", "~10 A")
    st.caption("Referência de corrente desejada durante a falta.")

st.divider()

col_texto, col_imagem = st.columns([1.05, 1.25], gap="large")

with col_texto:
    st.subheader("Princípio de funcionamento")
    st.markdown(
        """
        - **Bobina DC:** polariza o núcleo e busca mantê-lo saturado em regime
          permanente, aproximando a permeabilidade relativa de 1.
        - **Bobina AC:** fica associada ao circuito principal e atua no momento
          do curto, quando a mudança do estado magnético aumenta a impedância.
        - **Núcleo aberto:** exige avaliação numérica, pois a dispersão de fluxo
          torna a formulação analítica simplificada pouco precisa.
        - **Critério de desempenho:** limitar a corrente de falta mantendo a
          queda de tensão dentro de uma faixa aceitável para qualidade de energia.
        """
    )

    st.subheader("Como o dashboard ajuda")
    st.markdown(
        """
        As abas reúnem ferramentas para estudar a curva B-H, calcular valores
        RMS, observar harmônicos e comparar resultados de otimização. A análise
        de otimização filtra combinações por parâmetros geométricos e elétricos,
        calcula os máximos nas janelas de tempo de interesse e destaca quais
        configurações ficam mais próximas da região ideal de projeto.
        """
    )

with col_imagem:
    st.image(
        BASE_DIR / "imagens" / "AnaliseDinamica.gif",
        caption="Campo magnético no domínio do tempo",
        use_container_width=True,
    )

st.divider()

st.subheader("Etapas de análise")

etapas = st.columns(4)

with etapas[0]:
    st.markdown("**1. Curva B-H**")
    st.write(
        "Avalia a saturação do material ferromagnético e a variação da "
        "permeabilidade magnética relativa."
    )

with etapas[1]:
    st.markdown("**2. RMS**")
    st.write(
        "Calcula grandezas eficazes em regiões de tempo selecionadas para "
        "comparar operação nominal e transitórios."
    )

with etapas[2]:
    st.markdown("**3. Harmônicos**")
    st.write(
        "Aplica FFT para observar o conteúdo harmônico e a participação "
        "relativa de cada componente."
    )

with etapas[3]:
    st.markdown("**4. Otimização**")
    st.write(
        "Compara queda de tensão e corrente de curto para diferentes "
        "combinações de H, W, N_DC e N_AC."
    )