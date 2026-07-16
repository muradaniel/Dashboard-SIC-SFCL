import numpy as np


def consolidar_tempo(tempo, *sinais):
    """Ordena o tempo e calcula a media dos sinais em instantes duplicados."""
    tempo = np.asarray(tempo, dtype=float)
    sinais = [np.asarray(sinal, dtype=float) for sinal in sinais]
    if any(len(sinal) != len(tempo) for sinal in sinais):
        raise ValueError("Tempo e sinais precisam ter o mesmo tamanho.")
    if len(tempo) == 0:
        return (tempo, *sinais)

    ordem = np.argsort(tempo, kind="stable")
    tempo = tempo[ordem]
    sinais = [sinal[ordem] for sinal in sinais]
    tempo_unico, inverso, contagens = np.unique(
        tempo,
        return_inverse=True,
        return_counts=True,
    )
    if len(tempo_unico) == len(tempo):
        return (tempo, *sinais)

    sinais_medios = [
        np.bincount(inverso, weights=sinal) / contagens
        for sinal in sinais
    ]
    return (tempo_unico, *sinais_medios)


def indices_visualizacao(quantidade, maximo=5000):
    """Retorna uma amostra uniforme apenas para exibicao de graficos."""
    quantidade = int(quantidade)
    maximo = max(2, int(maximo))
    if quantidade <= maximo:
        return slice(None)
    return np.linspace(0, quantidade - 1, maximo, dtype=int)
