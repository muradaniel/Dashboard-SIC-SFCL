import numpy as np
import plotly.graph_objects as go


COR_NUCLEO = "#5B6472"
COR_DC = "#2563EB"
COR_AC = "#DC2626"

OPACIDADE_NUCLEO = 0.96
OPACIDADE_ENROLAMENTO = 0.96

TAMANHO_NUCLEO = (0.46, 0.46, 3.1)
RAIO_DC = 0.38
RAIO_AC = 0.56
MEIA_LARGURA_FITA_DC = 0.18
LARGURA_LINHA_AC = 5

Z_MIN_DC = -1.42
Z_MAX_DC = 1.42
Z_MIN_AC = -1.55
Z_MAX_AC = 1.55

CENTRO_1_NUCLEO = (0.0,)
CENTROS_2_NUCLEOS = (-0.68, 0.68)
CENTROS_AC_1_NUCLEO_2_BOBINAS = (-0.52, 0.52)


def adicionar_nucleo(fig, centro_x, nome="Núcleo de ferro", mostrar_legenda=True):
    cx, cy, cz = centro_x, 0, 0
    sx, sy, sz = TAMANHO_NUCLEO
    x0, x1 = cx - sx / 2, cx + sx / 2
    y0, y1 = cy - sy / 2, cy + sy / 2
    z0, z1 = cz - sz / 2, cz + sz / 2
    vertices = np.array([
        [x0, y0, z0], [x1, y0, z0], [x1, y1, z0], [x0, y1, z0],
        [x0, y0, z1], [x1, y0, z1], [x1, y1, z1], [x0, y1, z1],
    ])
    faces = np.array([
        [0, 1, 2], [0, 2, 3], [4, 6, 5], [4, 7, 6],
        [0, 4, 5], [0, 5, 1], [1, 5, 6], [1, 6, 2],
        [2, 6, 7], [2, 7, 3], [3, 7, 4], [3, 4, 0],
    ])
    fig.add_trace(go.Mesh3d(
        x=vertices[:, 0],
        y=vertices[:, 1],
        z=vertices[:, 2],
        i=faces[:, 0],
        j=faces[:, 1],
        k=faces[:, 2],
        name=nome,
        color=COR_NUCLEO,
        opacity=OPACIDADE_NUCLEO,
        flatshading=True,
        showlegend=mostrar_legenda,
        legendrank=1,
        hovertemplate=f"{nome}<extra></extra>",
    ))


def malha_fita_helicoidal(
    centro_x,
    raio,
    voltas,
    z_inicio,
    z_fim,
    pontos,
    meia_largura,
    sentido=1,
):
    theta = np.linspace(0, sentido * voltas * 2 * np.pi, pontos)
    z = np.linspace(z_inicio, z_fim, theta.size)
    theta_bordas = np.column_stack([
        theta - meia_largura,
        theta + meia_largura,
    ])
    z_bordas = np.column_stack([
        z - meia_largura * 0.34,
        z + meia_largura * 0.34,
    ])
    x = centro_x + (raio * np.cos(theta_bordas)).ravel()
    y = (raio * np.sin(theta_bordas)).ravel()
    z_malha = z_bordas.ravel()
    i, j, k = [], [], []
    for indice in range(theta.size - 1):
        a = 2 * indice
        b = a + 1
        c = a + 2
        d = a + 3
        i.extend([a, b])
        j.extend([c, d])
        k.extend([b, c])
    return x, y, z_malha, i, j, k


def malha_fita_helicoidal_eliptica(
    centro_x,
    raio_x,
    raio_y,
    voltas,
    z_inicio,
    z_fim,
    pontos,
    meia_largura,
):
    theta = np.linspace(0, voltas * 2 * np.pi, pontos)
    z = np.linspace(z_inicio, z_fim, theta.size)
    theta_bordas = np.column_stack([
        theta - meia_largura,
        theta + meia_largura,
    ])
    z_bordas = np.column_stack([
        z - meia_largura * 0.34,
        z + meia_largura * 0.34,
    ])
    x = centro_x + (raio_x * np.cos(theta_bordas)).ravel()
    y = (raio_y * np.sin(theta_bordas)).ravel()
    z_malha = z_bordas.ravel()
    i, j, k = [], [], []
    for indice in range(theta.size - 1):
        a = 2 * indice
        b = a + 1
        c = a + 2
        d = a + 3
        i.extend([a, b])
        j.extend([c, d])
        k.extend([b, c])
    return x, y, z_malha, i, j, k


def combinar_malhas(partes):
    xs, ys, zs, faces_i, faces_j, faces_k = [], [], [], [], [], []
    deslocamento = 0
    for x, y, z, i, j, k in partes:
        xs.extend(x)
        ys.extend(y)
        zs.extend(z)
        faces_i.extend(indice + deslocamento for indice in i)
        faces_j.extend(indice + deslocamento for indice in j)
        faces_k.extend(indice + deslocamento for indice in k)
        deslocamento += len(x)
    return xs, ys, zs, faces_i, faces_j, faces_k


def adicionar_trace_fita_dc(fig, malha):
    x, y, z, i, j, k = malha
    fig.add_trace(go.Mesh3d(
        x=x,
        y=y,
        z=z,
        i=i,
        j=j,
        k=k,
        name="Enrolamento DC",
        color=COR_DC,
        opacity=OPACIDADE_ENROLAMENTO,
        flatshading=True,
        showlegend=True,
        legendrank=2,
        hovertemplate="Enrolamento DC<extra></extra>",
    ))


def adicionar_fita_dc_circular(fig, centros_x):
    partes = [
        malha_fita_helicoidal(
            centro_x,
            RAIO_DC,
            voltas=8,
            z_inicio=Z_MIN_DC,
            z_fim=Z_MAX_DC,
            pontos=1400,
            meia_largura=MEIA_LARGURA_FITA_DC,
        )
        for centro_x in centros_x
    ]
    adicionar_trace_fita_dc(fig, combinar_malhas(partes))


def adicionar_fita_dc_oval_externa(fig, raio_x, raio_y, centro_x=0):
    adicionar_trace_fita_dc(
        fig,
        malha_fita_helicoidal_eliptica(
            centro_x=centro_x,
            raio_x=raio_x,
            raio_y=raio_y,
            voltas=8,
            z_inicio=Z_MIN_DC,
            z_fim=Z_MAX_DC,
            pontos=1400,
            meia_largura=MEIA_LARGURA_FITA_DC,
        ),
    )


def pontos_helice(centro_x, raio, voltas, z_inicio, z_fim, pontos, sentido=1):
    theta = np.linspace(0, sentido * voltas * 2 * np.pi, pontos)
    z = np.linspace(z_inicio, z_fim, theta.size)
    x = centro_x + raio * np.cos(theta)
    y = raio * np.sin(theta)
    return x, y, z


def adicionar_helice_ac_continua(fig, centros_x, raio=RAIO_AC, conectar=True):
    xs, ys, zs = [], [], []
    ponto_anterior = None

    for indice, centro_x in enumerate(centros_x):
        z_inicio, z_fim = (Z_MIN_AC, Z_MAX_AC)
        if conectar and indice % 2 == 1:
            z_inicio, z_fim = (Z_MAX_AC, Z_MIN_AC)

        x, y, z = pontos_helice(
            centro_x,
            raio,
            voltas=37.5,
            z_inicio=z_inicio,
            z_fim=z_fim,
            pontos=3200,
        )

        if conectar and ponto_anterior is not None:
            xs.extend([ponto_anterior[0], x[0]])
            ys.extend([ponto_anterior[1], y[0]])
            zs.extend([ponto_anterior[2], z[0]])
        elif not conectar and xs:
            xs.append(None)
            ys.append(None)
            zs.append(None)

        xs.extend(x)
        ys.extend(y)
        zs.extend(z)
        ponto_anterior = (x[-1], y[-1], z[-1])

    fig.add_trace(go.Scatter3d(
        x=xs,
        y=ys,
        z=zs,
        mode="lines",
        name="Enrolamento CA",
        line=dict(color=COR_AC, width=LARGURA_LINHA_AC),
        legendrank=3,
        hovertemplate="Enrolamento CA<extra></extra>",
    ))



def adicionar_helices_ac_superior_inferior(fig):
    meia_altura_gap = (Z_MAX_AC - Z_MIN_AC) * 0.10
    z_gap_superior = meia_altura_gap
    z_gap_inferior = -meia_altura_gap
    voltas_segmento = 15.0
    pontos_segmento = 1300

    x_superior, y_superior, z_superior = pontos_helice(
        0.0,
        RAIO_AC,
        voltas=voltas_segmento,
        z_inicio=Z_MAX_AC,
        z_fim=z_gap_superior,
        pontos=pontos_segmento,
        sentido=1,
    )
    x_inferior, y_inferior, z_inferior = pontos_helice(
        0.0,
        RAIO_AC,
        voltas=voltas_segmento,
        z_inicio=z_gap_inferior,
        z_fim=Z_MIN_AC,
        pontos=pontos_segmento,
        sentido=-1,
    )

    x = [*x_superior, x_superior[-1], x_inferior[0], *x_inferior]
    y = [*y_superior, y_superior[-1], y_inferior[0], *y_inferior]
    z = [*z_superior, z_gap_superior, z_gap_inferior, *z_inferior]

    fig.add_trace(go.Scatter3d(
        x=x,
        y=y,
        z=z,
        mode="lines",
        name="Enrolamento CA",
        line=dict(color=COR_AC, width=LARGURA_LINHA_AC),
        legendrank=3,
        hovertemplate="Enrolamento CA<extra></extra>",
    ))
def adicionar_legendas(fig, dois_nucleos=False):
    if dois_nucleos:
        x = [-1.1, -1.25, 1.28]
        y = [-0.64, -0.72, -0.72]
        z = [1.68, 0.52, -0.25]
    else:
        x = [0, -0.72, 0.78]
        y = [-0.64, -0.7, -0.72]
        z = [1.68, 0.52, -0.25]

    fig.add_trace(go.Scatter3d(
        x=x,
        y=y,
        z=z,
        mode="text",
        text=["Núcleo de ferro", "Enrolamento DC", "Enrolamento CA"],
        textfont=dict(size=12, color="#0F172A"),
        showlegend=False,
        hoverinfo="skip",
    ))


def configurar_layout_3d(fig):
    fig.update_layout(
        scene=dict(
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            zaxis=dict(visible=False),
            aspectmode="data",
            camera=dict(eye=dict(x=1.8, y=2.2, z=1.15)),
        ),
        legend=dict(orientation="h", y=0.02, x=0.5, xanchor="center"),
        margin=dict(l=0, r=0, t=8, b=0),
        height=560,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )


def criar_figura_limitador_3d():
    fig = go.Figure()
    adicionar_nucleo(fig, 0.0)
    adicionar_fita_dc_circular(fig, CENTRO_1_NUCLEO)
    adicionar_helice_ac_continua(fig, CENTRO_1_NUCLEO)
    adicionar_legendas(fig)
    configurar_layout_3d(fig)
    return fig


def criar_figura_limitador_3d_1_core_2_coil():
    fig = go.Figure()
    adicionar_nucleo(fig, 0.0)
    adicionar_fita_dc_circular(fig, CENTRO_1_NUCLEO)
    adicionar_helices_ac_superior_inferior(fig)
    adicionar_legendas(fig)
    configurar_layout_3d(fig)
    return fig


def criar_figura_limitador_3d_2_core_1_coil():
    fig = go.Figure()
    for indice, centro_x in enumerate(CENTROS_2_NUCLEOS):
        adicionar_nucleo(fig, centro_x, mostrar_legenda=indice == 0)
    adicionar_helice_ac_continua(fig, CENTROS_2_NUCLEOS)
    adicionar_fita_dc_oval_externa(fig, raio_x=1.58, raio_y=0.86)
    adicionar_legendas(fig, dois_nucleos=True)
    configurar_layout_3d(fig)
    return fig


def criar_figura_limitador_3d_2_core_2_coil():
    fig = go.Figure()
    for indice, centro_x in enumerate(CENTROS_2_NUCLEOS):
        adicionar_nucleo(fig, centro_x, mostrar_legenda=indice == 0)
    adicionar_fita_dc_circular(fig, CENTROS_2_NUCLEOS)
    adicionar_helice_ac_continua(fig, CENTROS_2_NUCLEOS)
    adicionar_legendas(fig, dois_nucleos=True)
    configurar_layout_3d(fig)
    return fig


def criar_figura_limitador_3d_por_topologia(chave_estado):
    figuras = {
        "otimizacao_1_core_1_coil": criar_figura_limitador_3d,
        "otimizacao_1_core_2_coil": criar_figura_limitador_3d_1_core_2_coil,
        "otimizacao_2_core_1_coil": criar_figura_limitador_3d_2_core_1_coil,
        "otimizacao_2_core_2_coil": criar_figura_limitador_3d_2_core_2_coil,
    }
    return figuras.get(chave_estado, criar_figura_limitador_3d)()






