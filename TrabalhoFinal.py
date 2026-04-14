import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.io as pio
import math
import tempfile
import os
import time
from fpdf import FPDF

#configsPag

st.set_page_config(
    page_title="AGV Dashboard | Corredor Inteligente", 
    layout="wide", 
    page_icon="🤖",
    initial_sidebar_state="expanded"
)

#Css(gerado por IA - Gemini) todo código css utilizado aqui foi gerado pelo gemini odeio e não sei mexer com css/tenho nojo kkk mas nada contra (particularmente acho que o gemini mandou bem pra caramba)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;500;600;700;800;900&display=swap');

    html, body, [class*="css"] {
        font-family: 'Montserrat', sans-serif !important;
    }

    .stApp {
        background-color: #050505;
        background-image: radial-gradient(circle at 50% 0%, #11141f 0%, #050505 70%);
        color: #e0e0e0;
    }

    [data-testid="stSidebar"] {
        background-color: #0a0b10 !important;
        border-right: 1px solid #1f2335;
    }

    /* === ESTILIZAÇÃO AVANÇADA DO MENU DE NAVEGAÇÃO === */
    [data-testid="stSidebar"] .stRadio [role="radio"] { display: none !important; }
    [data-testid="stSidebar"] .stRadio label > div:last-child { padding-left: 0 !important; }

    [data-testid="stSidebar"] .stRadio label {
        padding: 12px 16px;
        background-color: transparent;
        border-radius: 8px;
        cursor: pointer;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        border: 1px solid transparent;
        margin-bottom: 4px;
        display: flex;
        align-items: center;
    }

    [data-testid="stSidebar"] .stRadio label:hover {
        background-color: rgba(0, 240, 255, 0.05);
        transform: translateX(6px);
        border-color: rgba(0, 240, 255, 0.15);
    }

    [data-testid="stSidebar"] .stRadio label:has(input:checked) {
        background-color: rgba(0, 240, 255, 0.1);
        border-left: 4px solid #00f0ff;
        border-radius: 4px 8px 8px 4px;
        box-shadow: 0 4px 15px rgba(0, 240, 255, 0.05);
    }
    
    [data-testid="stSidebar"] .stRadio label:has(input:checked) p {
        color: #00f0ff !important;
        font-weight: 700 !important;
    }
    /* ================================================= */

    .stAlert { border-radius: 8px; }
    div[data-testid="stMetricValue"] { color: #00f0ff !important; font-weight: 700; }
    
    .dev-copyright {
        position: fixed;
        bottom: 20px;
        right: 20px;
        background-color: rgba(0, 240, 255, 0.05);
        border: 1px solid rgba(0, 240, 255, 0.4);
        color: #00f0ff;
        padding: 10px 20px;
        border-radius: 12px;
        font-weight: 600;
        font-size: 14px;
        z-index: 99999;
        backdrop-filter: blur(5px);
        box-shadow: 0 0 15px rgba(0, 240, 255, 0.15);
        transition: all 0.3s ease;
    }
    .dev-copyright:hover {
        background-color: rgba(0, 240, 255, 0.15);
        box-shadow: 0 0 25px rgba(0, 240, 255, 0.3);
        transform: translateY(-2px);
    }
    
    .group-panel {
        text-align: center;
        background-color: #0a0b10;
        padding: 30px;
        border-radius: 12px;
        border: 1px solid #1f2335;
        box-shadow: 0 4px 20px rgba(0,0,0,0.5);
    }
    .group-panel h3 {
        color: #00f0ff;
        margin-bottom: 20px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .group-panel p {
        font-size: 18px;
        font-weight: 500;
        margin: 8px 0;
        color: #ffffff;
    }
    </style>
    
    <div class="dev-copyright">
        🚀 Desenvolvido por <b>@joaovvargasb</b>
    </div>
""", unsafe_allow_html=True)

#variaveisGlobais

if 'pontos_corredor' not in st.session_state:
    st.session_state['pontos_corredor'] = pd.DataFrame({
        'ID': ['P1', 'P2', 'P3', 'P4', 'P5', 'P6', 'P7', 'P8', 'P9', 'P10', 'P11', 'P12', 'P13', 'P14'],
        'Elemento': [
            'Entrada Principal', 'Sala 01', 'Pilar 01', 'Extintor', 'Sala 02', 
            'Bebedouro', 'Pilar 02', 'Banheiro Masc', 'Biblioteca', 'Saída Emergência',
            'Sala 03', 'Pilar 03', 'Escada', 'Pilar 04'
        ],
        'X (m)': [0.0, 2.0, 3.5, 7.5, 6.0, 11.5, 10.0, 12.0, 13.5, 15.0, 2.0, 3.5, 8.0, 10.0],
        'Y (m)': [1.25, 2.5, 0.0, 0.0, 2.5, 0.0, 0.0, 0.0, 2.5, 1.25, 0.0, 2.5, 2.5, 2.5]
    })

if 'triangulacao' not in st.session_state:
    st.session_state['triangulacao'] = {
        'A_x': 1.0, 'A_y': 2.0, 'Da': 3.61,
        'B_x': 8.0, 'B_y': 3.0, 'Db': 4.12,
        'C_x': 4.0, 'C_y': 5.0, 'Dc': 1.00,
        'Real_x': 4.0, 'Real_y': 4.0
    }

if 'obstaculo' not in st.session_state:
    st.session_state['obstaculo'] = {'X': 6.0, 'Y': 1.5, 'Raio': 0.5}

if 'piso' not in st.session_state:
    st.session_state['piso'] = pd.DataFrame({
        'X (m)': [0.0, 0.5, 1.0, 1.5, 2.0],
        'Y (cm) - Altura': [0.0, 1.5, 2.0, 1.5, 0.0]
    })

if 'demanda' not in st.session_state:
    st.session_state['demanda'] = pd.DataFrame({
        'Ponto': ['Entrada Principal', 'Sala 01', 'Biblioteca'],
        'X (m)': [0.0, 2.0, 13.5],
        'Y (m)': [1.25, 2.5, 2.5],
        'Peso': [5, 3, 4]
    })

#darkMode

def criar_grafico_base(titulo: str) -> go.Figure:
    fig = go.Figure()
    fig.update_layout(
        title=dict(text=titulo, font=dict(size=20, color='#e0e0e0', family='Montserrat, sans-serif')),
        xaxis_title="Eixo X (metros)",
        yaxis_title="Eixo Y (metros)",
        font=dict(color='#a0a0b0', family='Montserrat, sans-serif'),
        yaxis=dict(scaleanchor="x", scaleratio=1, showgrid=True, gridcolor="#1f2335", zerolinecolor="#1f2335"),
        xaxis=dict(showgrid=True, gridcolor="#1f2335", zerolinecolor="#1f2335"),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=40, r=40, t=60, b=40),
        hovermode="closest",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(color='#e0e0e0'))
    )
    return fig

#converter
def s_pdf(texto):
    return str(texto).encode('latin-1', 'replace').decode('latin-1')

#barraLateral | quero trocar os icones da barra lateral caso o projeto va para frente em algum futuro para icones mais reais

with st.sidebar:
    st.markdown("""
        <div style="text-align: center; margin-top: 10px; margin-bottom: 30px;">
            <div style="font-family: 'Montserrat', sans-serif; font-weight: 900; font-size: 34px; color: #ffffff; letter-spacing: 1px; margin-bottom: 6px;">
                MULTIVIX
            </div>
            <div style="height: 2px; width: 100%; background: linear-gradient(90deg, rgba(255,255,255,0) 0%, rgba(255,255,255,0.9) 50%, rgba(255,255,255,0) 100%);"></div>
        </div>
    """, unsafe_allow_html=True)
        
    st.title("Corredor Inteligente")
    st.markdown("Sistema de Mapeamento de AGVs")
    st.markdown("---")
    
    menu = st.radio("Navegação", [
        "🏠 Início", 
        "📍 1. Mapeamento 2D", 
        "📡 2. Triangulação", 
        "🛣️ 3. Trajetória e Colisão", 
        "📐 4. Perfil do Piso", 
        "🎯 5. Otimização Logística", 
        "📄 Relatório Final"
    ], label_visibility="collapsed")

#paginas (parte mais demorada e chata do codigo todo(exceto a parte de logica e matematica), mesclar html com python nao é nada legal, ja disse que odeio front hoje?)

if menu == "🏠 Início":
    st.title("Mapeamento e Otimização de um Corredor Inteligente")
    st.markdown("#### Estudo Técnico Preliminar e Simulação de AGVs (2D)")
    st.write("---")
    
    col_intro, col_grupo = st.columns([2, 1], gap="large")
    
    with col_intro:
        st.markdown("### 🎯 Sobre o Projeto")
        st.write("""
        O transporte manual de equipamentos em um ambiente acadêmico pode ser cansativo, gerar riscos de acidentes e causar atrasos. 
        Para solucionar esse problema, este dashboard simula o planejamento de **Veículos Guiados Automaticamente (AGVs)** num corredor inteligente.
        
        Aqui, você vai descobrir como a **Geometria Analítica e a Álgebra Linear** saem dos livros e se transformam em ferramentas essenciais para a Engenharia. Vamos guiar você desde a transformação do espaço físico em um mapa matemático até as tomadas de decisão autônomas do robô!
        """)
        st.info("👈 **Use o menu lateral para avançar nas etapas.** Todos os gráficos e cálculos são interativos, experimente mudar os valores!", icon="🚀")

    with col_grupo:
        st.markdown("""
        <div class="group-panel">
            <h3>📋 Grupo</h3>
            <p>Cezar Augusto</p>
            <p>Guilherme Mello</p>
            <p>João Vitor Vargas</p>
            <p>Lucas Bayerl</p>
            <p>Pedro Samuel Vieira</p>
            <hr style="border-color: #1f2335; margin: 15px 0;">
            <span style="font-size: 12px; color: #888;">Disciplina: Geometria Analítica e Álgebra Linear<br>Faculdade MULTIVIX</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### 🧩 Entenda o Passo a Passo da Simulação")
    
    c1, c2, c3 = st.columns(3)
    with c1:
        with st.container(border=True):
            st.markdown("#### 📍 1. Mapeamento")
            st.write("Transformamos o corredor real da faculdade em um **Plano Cartesiano (X, Y)**. Assim, o robô entende distâncias e localizações exatas matematicamente.")
    with c2:
        with st.container(border=True):
            st.markdown("#### 📡 2. Triangulação")
            st.write("Como o robô sabe onde está? Simulamos sinais de antenas e usamos a **Intersecção de Circunferências** para achar sua posição exata e medir erros.")
    with c3:
        with st.container(border=True):
            st.markdown("#### 🛣️ 3. Rota Segura")
            st.write("Criamos a equação da reta que o AGV deve seguir. Também calculamos a distância até possíveis obstáculos para o robô **desviar e evitar colisões** autônomas.")
            
    st.markdown("<br>", unsafe_allow_html=True)
    c4, c5, c6 = st.columns(3)
    with c4:
        with st.container(border=True):
            st.markdown("#### 📐 4. Análise de Piso")
            st.write("O chão nem sempre é perfeitamente plano. Aplicamos **Funções Quadráticas (Parábolas)** para prever lombadas e ordenar que o robô reduza a velocidade.")
    with c5:
        with st.container(border=True):
            st.markdown("#### 🎯 5. Otimização")
            st.write("Onde a estação de recarga do robô deve ficar? Usamos o método de **Centroide Ponderado** para encontrar o local central que gasta menos bateria.")
    with c6:
        with st.container(border=True):
            st.markdown("#### 📄 6. Relatório Final")
            st.write("Ao finalizar todas as suas simulações, o sistema compila os seus resultados em um **Relatório Executivo em PDF**, incluindo um mapa completo.")

elif menu == "📍 1. Mapeamento 2D":
    st.title("Etapa 1: Implantação do Sistema de Coordenadas")
    st.write("Defina as portas, pilares e limites do seu corredor na tabela abaixo.")
    
    col_tabela, col_grafico = st.columns([1, 2], gap="large")
    with col_tabela:
        st.markdown("### 📝 Dados Topográficos")
        df_pontos = st.data_editor(st.session_state['pontos_corredor'], num_rows="dynamic", use_container_width=True, hide_index=True)
        st.session_state['pontos_corredor'] = df_pontos
    with col_grafico:
        st.markdown("### 🗺️ Visualização do Corredor")
        fig = criar_grafico_base("")
        fig.add_trace(go.Scatter(
            x=df_pontos['X (m)'], y=df_pontos['Y (m)'],
            mode='markers+text', text=df_pontos['ID'], textposition="top center",
            marker=dict(size=12, color='#00f0ff', line=dict(width=2, color='#000')), name="Pontos Mapeados"
        ))
        st.plotly_chart(fig, use_container_width=True)

elif menu == "📡 2. Triangulação":
    st.title("Etapa 2: Triangulação Experimental")
    st.info("""
    💡 **Para entender esta aba:** O robô capta o sinal de 3 antenas de rádio (Beacons) e mede a distância. O cruzamento forma um ponto que diz onde ele está no mapa.
    **Por que tem um 'AGV Real' e um 'Calculado'?** Nós inserimos a posição do **AGV Real** como um "gabarito secreto". A matemática cruza os sinais para encontrar o **AGV Calculado**. Vamos testar?
    """)
    st.write("---")
    
    st.markdown("### 📡 Passo 1: O que as antenas estão lendo?")
    with st.container(border=True):
        col1, col2, col3 = st.columns(3)
        t = st.session_state['triangulacao']
        with col1:
            t['A_x'] = st.number_input("X da Antena A", value=t['A_x'], step=0.5)
            t['A_y'] = st.number_input("Y da Antena A", value=t['A_y'], step=0.5)
            t['Da'] = st.number_input("Distância lida (Raio A)", value=t['Da'], step=0.1)
        with col2:
            t['B_x'] = st.number_input("X da Antena B", value=t['B_x'], step=0.5)
            t['B_y'] = st.number_input("Y da Antena B", value=t['B_y'], step=0.5)
            t['Db'] = st.number_input("Distância lida (Raio B)", value=t['Db'], step=0.1)
        with col3:
            t['C_x'] = st.number_input("X da Antena C", value=t['C_x'], step=0.5)
            t['C_y'] = st.number_input("Y da Antena C", value=t['C_y'], step=0.5)
            t['Dc'] = st.number_input("Distância lida (Raio C)", value=t['Dc'], step=0.1)
    
    x1, y1, r1 = t['A_x'], t['A_y'], t['Da']
    x2, y2, r2 = t['B_x'], t['B_y'], t['Db']
    x3, y3, r3 = t['C_x'], t['C_y'], t['Dc']
    
    A = np.array([[2*(x1 - x2), 2*(y1 - y2)], [2*(x1 - x3), 2*(y1 - y3)]])
    B = np.array([r2**2 - r1**2 - x2**2 + x1**2 - y2**2 + y1**2, r3**2 - r1**2 - x3**2 + x1**2 - y3**2 + y1**2])
    
    try:
        p_calc = np.linalg.solve(A, B)
        calc_x, calc_y = p_calc[0], p_calc[1]
        erro = math.sqrt((calc_x - t['Real_x'])**2 + (calc_y - t['Real_y'])**2)
        sucesso_calc = True
    except np.linalg.LinAlgError:
        calc_x, calc_y, erro = 0.0, 0.0, 0.0
        sucesso_calc = False

    st.markdown("---")
    st.markdown("### 🎯 Passo 2: O Teste de Realidade (Gabarito vs Cálculo)")
    col_dados, col_grafico = st.columns([1, 2], gap="large")
    
    with col_dados:
        with st.container(border=True):
            st.markdown("#### 🌟 Onde o robô realmente está?")
            t['Real_x'] = st.number_input("Coordenada X (Gabarito)", value=t['Real_x'], step=0.5)
            t['Real_y'] = st.number_input("Coordenada Y (Gabarito)", value=t['Real_y'], step=0.5)
            st.session_state['triangulacao'] = t
            
        with st.container(border=True):
            st.markdown("#### 🧮 Onde a matemática diz que ele está?")
            if sucesso_calc:
                c1, c2 = st.columns(2)
                c1.metric("X Calculado", f"{calc_x:.2f} m")
                c2.metric("Y Calculado", f"{calc_y:.2f} m")
                if erro > 0.05:
                    st.metric("Margem de Erro", f"{erro:.3f} m", delta="Atenção: Os raios não batem com o gabarito!", delta_color="inverse")
                else:
                    st.metric("Margem de Erro", f"{erro:.3f} m", delta="Perfeito! Cálculo = Gabarito", delta_color="normal")
            else:
                st.error("Erro matemático: Antenas alinhadas.")
                
    with col_grafico:
        fig = criar_grafico_base("Visão Superior do GPS Indoor")
        def add_circle(fig, x, y, r, name, color):
            fig.add_shape(type="circle", xref="x", yref="y", x0=x-r, y0=y-r, x1=x+r, y1=y+r, line_color=color, opacity=0.6, fillcolor=f"rgba{tuple(list(int(color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4)) + [0.15])}")
            fig.add_trace(go.Scatter(x=[x], y=[y], mode='markers+text', text=[name], textposition="bottom center", marker=dict(color=color, symbol='cross', size=10), name=name))

        add_circle(fig, t['A_x'], t['A_y'], t['Da'], "Beacon A", "#ff3366")
        add_circle(fig, t['B_x'], t['B_y'], t['Db'], "Beacon B", "#33ff99")
        add_circle(fig, t['C_x'], t['C_y'], t['Dc'], "Beacon C", "#00f0ff")
        
        fig.add_trace(go.Scatter(x=[t['Real_x']], y=[t['Real_y']], mode='markers+text', text=["AGV Real (Gabarito)"], textposition="top center", marker=dict(color='#ffffff', size=16, symbol='star', line=dict(width=2, color='#000')), name="Posição Real"))
        
        if sucesso_calc:
            fig.add_trace(go.Scatter(x=[calc_x], y=[calc_y], mode='markers+text', text=["AGV Calculado"], textposition="bottom right", marker=dict(color='#ff9933', size=12, symbol='x', line=dict(width=3, color='#ff9933')), name="Posição Calculada"))
            if erro > 0.05:
                fig.add_trace(go.Scatter(x=[t['Real_x'], calc_x], y=[t['Real_y'], calc_y], mode='lines', line=dict(color='yellow', dash='dash', width=2), name="Vetor de Erro"))

        st.plotly_chart(fig, use_container_width=True)

elif menu == "🛣️ 3. Trajetória e Colisão":
    st.title("Etapas 3 e 4: Trajetória Ideal e Colisão")
    df = st.session_state['pontos_corredor']
    if len(df) < 2:
        st.warning("⚠️ Adicione pelo menos 2 pontos na Etapa 1 para calcular rotas.", icon="⚠️")
    else:
        col_setup, col_mapa = st.columns([1, 2], gap="large")
        
        with col_setup:
            with st.container(border=True):
                st.markdown("#### 🛤️ Definição de Rota")
                p_inicio = st.selectbox("Ponto de Partida", df['ID'].tolist(), index=0)
                idx_p9 = df.index[df['ID'] == 'P9'].tolist()[0] if 'P9' in df['ID'].values else len(df)-1
                p_fim = st.selectbox("Ponto de Destino", df['ID'].tolist(), index=idx_p9)
                
                x1, y1 = float(df[df['ID'] == p_inicio].iloc[0]['X (m)']), float(df[df['ID'] == p_inicio].iloc[0]['Y (m)'])
                x2, y2 = float(df[df['ID'] == p_fim].iloc[0]['X (m)']), float(df[df['ID'] == p_fim].iloc[0]['Y (m)'])
                
            with st.container(border=True):
                st.markdown("#### 📦 Obstáculo no Caminho")
                obs = st.session_state['obstaculo']
                obs['X'] = float(st.number_input("Posição X", value=float(obs['X']), step=0.5))
                obs['Y'] = float(st.number_input("Posição Y", value=float(obs['Y']), step=0.5))
                obs['Raio'] = float(st.number_input("Raio (m)", value=float(obs['Raio']), step=0.1))
                st.session_state['obstaculo'] = obs
                
            m = (y2 - y1) / (x2 - x1) if (x2 - x1) != 0 else 0
            b = y1 - m * x1
            A, B, C = m, -1.0, b
            dist_colisao = abs(A*obs['X'] + B*obs['Y'] + C) / math.sqrt(A**2 + B**2) if (A**2 + B**2) != 0 else 0.0
            
            st.metric(label="Distância Reta-Obstáculo", value=f"{dist_colisao:.3f} m")
            
        with col_mapa:
            fig = criar_grafico_base("Análise de Colisão e Desvios")
            tem_desvio = False
            desvio_x, desvio_y = 0.0, 0.0
            
            if dist_colisao <= obs['Raio']:
                st.error(f"🚨 COLISÃO DETECTADA! A distância ({dist_colisao:.3f}m) é menor que a margem de segurança ({obs['Raio']}m).")
                with st.expander("🛠️ Configurar Ponto de Desvio (D)", expanded=True):
                    od1, od2 = st.columns(2)
                    with od1: desvio_x = st.number_input("X do Desvio", value=float(obs['X']), step=0.5)
                    with od2: desvio_y = st.number_input("Y do Desvio", value=float(obs['Y'] - obs['Raio'] - 0.5), step=0.5)
                
                fig.add_trace(go.Scatter(x=[x1, x2], y=[y1, y2], mode='lines', name='Rota Original (Bloqueada)', line=dict(color='rgba(255,255,255,0.3)', dash='dot', width=2)))
                fig.add_trace(go.Scatter(x=[x1, desvio_x, x2], y=[y1, desvio_y, y2], mode='lines+markers', name='Rota Alternativa Segura', line=dict(color='#33ff99', width=4)))
                fig.add_trace(go.Scatter(x=[desvio_x], y=[desvio_y], mode='markers+text', text=['Desvio'], textposition="bottom center", marker=dict(color='#33ff99', symbol='diamond', size=14), name='Ponto D'))
                tem_desvio = True
            else:
                st.success("✅ Rota Segura! O trajeto atual não intercepta o obstáculo.", icon="✅")
                fig.add_trace(go.Scatter(x=[x1, x2], y=[y1, y2], mode='lines+markers', name='Trajetória Ideal', line=dict(color='#00f0ff', width=4)))
                
            fig.add_shape(type="circle", xref="x", yref="y", x0=obs['X']-obs['Raio'], y0=obs['Y']-obs['Raio'], x1=obs['X']+obs['Raio'], y1=obs['Y']+obs['Raio'], line_color="#ff3366", fillcolor="rgba(255, 51, 102, 0.2)")
            fig.add_trace(go.Scatter(x=[obs['X']], y=[obs['Y']], mode='markers+text', text=['Obstáculo'], marker=dict(color='#ff3366', size=10), name='Centro Obstáculo'))
            
            fig.add_trace(go.Scatter(x=[x1, x2], y=[y1, y2], mode='markers', marker=dict(color='#ffffff', size=12), showlegend=False))
            st.plotly_chart(fig, use_container_width=True)
            
            st.session_state['trajetoria'] = {'x1':x1, 'y1':y1, 'x2':x2, 'y2':y2, 'm':m, 'b':b, 'dist':dist_colisao, 'tem_desvio': tem_desvio, 'desvio_x': desvio_x if tem_desvio else 0, 'desvio_y': desvio_y if tem_desvio else 0}

elif menu == "📐 4. Perfil do Piso":
    st.title("Etapa 5: Análise Topográfica do Piso")
    
    col_tabela, col_grafico = st.columns([1, 2], gap="large")
    with col_tabela:
        st.markdown("#### 📏 Coletas de Campo")
        df_piso = st.data_editor(st.session_state['piso'], num_rows="dynamic", use_container_width=True, hide_index=True)
        st.session_state['piso'] = df_piso
        x = df_piso['X (m)'].values
        y = df_piso['Y (cm) - Altura'].values
        
    with col_grafico:
        try:
            coef = np.polyfit(x, y, 2)
            a, b, c = coef
            x_v = -b / (2*a)
            y_v = -((b**2) - 4*a*c) / (4*a)
            
            cm1, cm2, cm3 = st.columns(3)
            cm1.metric("Coeficiente 'a'", f"{a:.3f}")
            cm2.metric("X do Vértice", f"{x_v:.2f} m")
            cm3.metric("Y do Vértice (Altura)", f"{y_v:.2f} cm", delta="Atenção", delta_color="inverse")
            
            x_linha = np.linspace(min(x)-0.2, max(x)+0.2, 100)
            y_linha = a*(x_linha**2) + b*x_linha + c
            
            fig = criar_grafico_base("Perfil Parobólico do Desnível")
            fig.update_layout(xaxis_title="Distância Percorrida (m)", yaxis_title="Altura do Desnível (cm)", yaxis=dict(scaleanchor=None, autorange=True)) 
            fig.add_trace(go.Scatter(x=x, y=y, mode='markers', name='Coletas', marker=dict(size=12, color='#ffffff', symbol='square')))
            fig.add_trace(go.Scatter(x=x_linha, y=y_linha, mode='lines', name='Curva Ajustada', line=dict(color='#ff9933', width=3)))
            fig.add_trace(go.Scatter(x=[x_v], y=[y_v], mode='markers+text', text=['Pico do Desnível'], textposition="top center", marker=dict(size=14, color='#ff3366', symbol='triangle-down'), name='Vértice'))
            
            st.plotly_chart(fig, use_container_width=True)
            st.session_state['parabola'] = {'a':a, 'b':b, 'c':c, 'xv':x_v, 'yv':y_v}
        except Exception:
            st.warning("⚠️ Insira pelo menos 3 pontos distintos para permitir o cálculo quadrático.")

elif menu == "🎯 5. Otimização Logística":
    st.title("Etapa 6: Base do AGV (Centroide Ponderado)")
    
    col_tabela, col_grafico = st.columns([1, 2], gap="large")
    with col_tabela:
        st.markdown("#### 📊 Pesos de Demanda")
        df_demanda = st.data_editor(st.session_state['demanda'], num_rows="dynamic", use_container_width=True, hide_index=True)
        st.session_state['demanda'] = df_demanda
        soma_pesos = df_demanda['Peso'].sum()
        
        if soma_pesos > 0:
            x_c = sum(df_demanda['X (m)'] * df_demanda['Peso']) / soma_pesos
            y_c = sum(df_demanda['Y (m)'] * df_demanda['Peso']) / soma_pesos
            st.divider()
            st.markdown("#### 📍 Resultado Ótimo")
            c1, c2 = st.columns(2)
            c1.metric("Coordenada X Ideal", f"{x_c:.2f} m")
            c2.metric("Coordenada Y Ideal", f"{y_c:.2f} m")
            st.session_state['centroide'] = {'xc': x_c, 'yc': y_c}
        else:
            st.warning("A soma dos pesos deve ser maior que zero.")

    with col_grafico:
        if soma_pesos > 0:
            fig = criar_grafico_base("Mapa de Demanda e Centroide")
            df_pontos = st.session_state['pontos_corredor']
            fig.add_trace(go.Scatter(x=df_pontos['X (m)'], y=df_pontos['Y (m)'], mode='markers', marker=dict(color='#333b5c', size=8), name="Planta do Corredor"))
            fig.add_trace(go.Scatter(
                x=df_demanda['X (m)'], y=df_demanda['Y (m)'], mode='markers+text', text=df_demanda['Ponto'], textposition="bottom center",
                marker=dict(size=df_demanda['Peso']*7, color='rgba(0, 240, 255, 0.4)', line=dict(width=2, color='#00f0ff')), name="Demanda"
            ))
            fig.add_trace(go.Scatter(x=[x_c], y=[y_c], mode='markers+text', text=["ESTAÇÃO BASE"], textposition="top center", marker=dict(size=20, color='#33ff99', symbol='star', line=dict(width=2, color='#fff')), name="Centroide (Ótimo)"))
            st.plotly_chart(fig, use_container_width=True)

elif menu == "📄 Relatório Final":
    st.title("📄 Relatório Executivo de Otimização")
    st.markdown("Visualize o resumo matemático do seu projeto e exporte o documento completo em **PDF**.")
    st.markdown("---")
    
    
    #gerarGrafico
    
    fig_mapa_completo = criar_grafico_base("Planta Cartesiana do Corredor (Resumo)")
    df_pontos = st.session_state['pontos_corredor']
    
    #pontosBase
    fig_mapa_completo.add_trace(go.Scatter(
        x=df_pontos['X (m)'], y=df_pontos['Y (m)'], mode='markers+text', text=df_pontos['ID'], textposition="top center",
        marker=dict(size=10, color='#1f77b4'), name="Pontos Estruturais"
    ))
    
    #obstaculo
    if 'obstaculo' in st.session_state:
        obs = st.session_state['obstaculo']
        fig_mapa_completo.add_shape(type="circle", xref="x", yref="y", x0=obs['X']-obs['Raio'], y0=obs['Y']-obs['Raio'], x1=obs['X']+obs['Raio'], y1=obs['Y']+obs['Raio'], line_color="#d62728", fillcolor="rgba(214, 39, 40, 0.2)")
        fig_mapa_completo.add_trace(go.Scatter(x=[obs['X']], y=[obs['Y']], mode='markers', marker=dict(color='#d62728', size=8), name='Obstáculo Mapeado'))
    
    #trajetoria
    if 'trajetoria' in st.session_state:
        tj = st.session_state['trajetoria']
        if tj.get('tem_desvio'):
            fig_mapa_completo.add_trace(go.Scatter(x=[tj['x1'], tj['desvio_x'], tj['x2']], y=[tj['y1'], tj['desvio_y'], tj['y2']], mode='lines+markers', name='Trajeto de Desvio', line=dict(color='#2ca02c', width=3)))
        else:
            fig_mapa_completo.add_trace(go.Scatter(x=[tj['x1'], tj['x2']], y=[tj['y1'], tj['y2']], mode='lines+markers', name='Trajeto Ideal', line=dict(color='#1f77b4', width=3)))

    #estacaoBase
    if 'centroide' in st.session_state:
        xc, yc = st.session_state['centroide']['xc'], st.session_state['centroide']['yc']
        fig_mapa_completo.add_trace(go.Scatter(x=[xc], y=[yc], mode='markers+text', text=["BASE (Recarga)"], textposition="bottom center", marker=dict(size=16, color='#ff7f0e', symbol='star'), name="Base Operacional"))

    #mostrarnaTela
    st.plotly_chart(fig_mapa_completo, use_container_width=True)
    st.markdown("---")
    
   
    #resumo
   
    with st.container(border=True):
        st.subheader("1. Parâmetros de Trajetória")
        if 'trajetoria' in st.session_state:
            tj = st.session_state['trajetoria']
            c1, c2, c3 = st.columns(3)
            c1.metric("Distância ao Obstáculo", f"{tj['dist']:.2f} m")
            if tj.get('tem_desvio', False):
                c3.metric("Status Rota", "DESVIO ATIVADO", delta="Evitou Colisão", delta_color="off")
            else:
                c3.metric("Status Rota", "SEGURA", delta="Caminho Livre")
        else:
            st.write("*(Pendente - Visite a Etapa 3)*")

    with st.container(border=True):
        st.subheader("2. Condições do Piso")
        if 'parabola' in st.session_state:
            p = st.session_state['parabola']
            c1, c2 = st.columns(2)
            c1.metric("Altura Máxima do Desnível", f"{p['yv']:.2f} cm")
            c2.metric("Localização (X)", f"{p['xv']:.2f} m")
        else:
            st.write("*(Pendente - Visite a Etapa 4)*")

    with st.container(border=True):
        st.subheader("3. Estação Base Otimizada")
        if 'centroide' in st.session_state:
            st.success(f"🎯 **Coordenada de Instalação Recomendada:** X = {st.session_state['centroide']['xc']:.2f} m | Y = {st.session_state['centroide']['yc']:.2f} m")
        else:
            st.write("*(Pendente - Visite a Etapa 6)*")
            
    st.markdown("---")
    
  
    #gerarpdf

    class PDFReport(FPDF):
        def header(self):
            self.set_font('Arial', 'B', 16)
            self.cell(0, 10, s_pdf('Relatório de Otimização - Corredor Inteligente'), border=0, ln=1, align='C')
            self.set_font('Arial', 'I', 11)
            self.cell(0, 8, s_pdf('Desenvolvido por: @joaovvargasb'), border=0, ln=1, align='C')
            self.ln(5)

        def footer(self):
            self.set_y(-15)
            self.set_font('Arial', 'I', 8)
            self.cell(0, 10, s_pdf(f'Página {self.page_no()}'), 0, 0, 'C')

    def generate_pdf_bytes():
        pdf = PDFReport()
        pdf.add_page()
        
        #bloco1
        pdf.set_font('Arial', 'B', 13)
        pdf.cell(0, 10, s_pdf('1. Trajetória e Análise de Colisão'), 0, 1)
        pdf.set_font('Arial', '', 12)
        if 'trajetoria' in st.session_state:
            tj = st.session_state['trajetoria']
            obs = st.session_state['obstaculo']
            pdf.cell(0, 8, s_pdf(f"- Distância da reta projetada ao obstáculo: {tj['dist']:.2f} m"), 0, 1)
            pdf.cell(0, 8, s_pdf(f"- Raio de segurança do obstáculo: {obs['Raio']:.2f} m"), 0, 1)
            if tj.get('tem_desvio'):
                pdf.set_text_color(200, 0, 0)
                pdf.cell(0, 8, s_pdf(f"- STATUS: RISCO DE COLISÃO. Desvio programado para D({tj['desvio_x']}, {tj['desvio_y']})."), 0, 1)
                pdf.set_text_color(0, 0, 0)
            else:
                pdf.set_text_color(0, 128, 0)
                pdf.cell(0, 8, s_pdf("- STATUS: ROTA SEGURA."), 0, 1)
                pdf.set_text_color(0, 0, 0)
        else:
            pdf.cell(0, 8, s_pdf("- Dados não calculados no sistema."), 0, 1)
            
        pdf.ln(5)
        
        #bloco2
        pdf.set_font('Arial', 'B', 13)
        pdf.cell(0, 10, s_pdf('2. Condições Topográficas do Piso (Desnível)'), 0, 1)
        pdf.set_font('Arial', '', 12)
        if 'parabola' in st.session_state:
            p = st.session_state['parabola']
            pdf.cell(0, 8, s_pdf(f"- Altura máxima (Vértice Y): {p['yv']:.2f} cm"), 0, 1)
            pdf.cell(0, 8, s_pdf(f"- Posição longitudinal (Vértice X): {p['xv']:.2f} m"), 0, 1)
            pdf.cell(0, 8, s_pdf("- Recomendação: Aplicar redução de velocidade na coordenada crítica."), 0, 1)
        else:
            pdf.cell(0, 8, s_pdf("- Dados não calculados no sistema."), 0, 1)
            
        pdf.ln(5)
        
        #bloco3
        pdf.set_font('Arial', 'B', 13)
        pdf.cell(0, 10, s_pdf('3. Otimização da Base Operacional'), 0, 1)
        pdf.set_font('Arial', '', 12)
        if 'centroide' in st.session_state:
            xc = st.session_state['centroide']['xc']
            yc = st.session_state['centroide']['yc']
            pdf.cell(0, 8, s_pdf(f"- Coordenada ideal (Centroide Ponderado): X = {xc:.2f} m | Y = {yc:.2f} m"), 0, 1)
        else:
            pdf.cell(0, 8, s_pdf("- Dados não calculados no sistema."), 0, 1)

        pdf.ln(10)
        
        #Img
        pdf.set_font('Arial', 'B', 13)
        pdf.cell(0, 10, s_pdf('4. Planta Cartesiana do Corredor'), 0, 1)
        
        #mudarCorGrafico
        fig_mapa_completo.update_layout(plot_bgcolor="white", paper_bgcolor="white", font=dict(color="black"))
        fig_mapa_completo.update_xaxes(showgrid=True, gridcolor="lightgray", zerolinecolor="black")
        fig_mapa_completo.update_yaxes(showgrid=True, gridcolor="lightgray", zerolinecolor="black")
        
        try:
            # MOVIDO: Só desativa o mathjax no exato momento que precisa gerar o PDF!
            pio.kaleido.scope.mathjax = None
            
            with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmpfile:
                fig_mapa_completo.write_image(tmpfile.name, engine="kaleido", width=900, height=450)
                time.sleep(0.5) 
                pdf.image(tmpfile.name, x=10, w=190)
            os.remove(tmpfile.name) # Limpar arquivo temporário
        #except Exception as e:
            #pdf.set_font('Arial', 'I', 10)
            #pdf.set_text_color(150, 150, 150)
            #pdf.cell(0, 10, s_pdf("(Não foi possível gerar a imagem do gráfico. Certifique-se de instalar 'kaleido')"), 0, 1)
            #pdf.set_text_color(0, 0, 0)
            
        raw = pdf.output(dest='S')
        return bytes(raw) if isinstance(raw, (bytes, bytearray)) else raw.encode('latin-1')

    #exportarStreamlitPdf
    st.download_button(
        label="📥 Fazer Download do Relatório Executivo (.PDF)",
        data=generate_pdf_bytes(),
        file_name="relatorio_agv.pdf",
        mime="application/pdf",
        type="primary"
    )

    #um breve fim, espero mexer nesse código novamente algum dia
