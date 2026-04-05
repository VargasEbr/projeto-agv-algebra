import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import math

# Configuração da Página
st.set_page_config(page_title="Dashboard - Corredor Inteligente", layout="wide", page_icon="🤖")

# ==========================================
# INICIALIZAÇÃO DE VARIÁVEIS GLOBAIS (ESTADO)
# ==========================================
# Isso garante que se o usuário mudar de página, os dados não se percam
if 'pontos_corredor' not in st.session_state:
    # Dados padrão baseados no grupo original
    st.session_state['pontos_corredor'] = pd.DataFrame({
        'ID': ['P1', 'P2', 'P3', 'P4', 'P5', 'P9', 'P10'],
        'Elemento': ['Entrada Principal', 'Sala 01', 'Pilar 01', 'Extintor', 'Sala 02', 'Biblioteca', 'Saída'],
        'X (m)': [0.0, 2.0, 3.5, 7.5, 6.0, 13.5, 15.0],
        'Y (m)': [1.25, 2.5, 0.0, 0.0, 2.5, 2.5, 1.25]
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
        'Ponto': ['Entrada Principal', 'Sala 03', 'Biblioteca'],
        'X (m)': [0.0, 2.0, 13.5],
        'Y (m)': [1.25, 0.0, 2.5],
        'Peso': [5, 3, 4]
    })

# ==========================================
# FUNÇÕES DE PLOTAGEM GERAIS
# ==========================================
def criar_grafico_base(titulo):
    fig = go.Figure()
    fig.update_layout(
        title=titulo,
        xaxis_title="Eixo X (metros)",
        yaxis_title="Eixo Y (metros)",
        yaxis=dict(scaleanchor="x", scaleratio=1), # Mantém proporção real 1:1
        template="plotly_white"
    )
    return fig

# ==========================================
# BARRA LATERAL (MENU)
# ==========================================
st.sidebar.title("Navegação do Projeto")
st.sidebar.markdown("Preencha os dados em cada etapa. O relatório final será gerado automaticamente.")
menu = st.sidebar.radio("Etapas", [
    "🏠 Início", 
    "📍 1. Mapeamento 2D", 
    "📡 2. Triangulação", 
    "🛣️ 3. Trajetória e Colisão", 
    "📐 4. Perfil do Piso", 
    "🎯 5. Otimização Logística", 
    "📄 RELATÓRIO FINAL"
])

# ==========================================
# PÁGINAS DO DASHBOARD
# ==========================================

if menu == "🏠 Início":
    st.title("Mapeamento e Otimização de um Corredor Inteligente (2D)")
    st.subheader("Estudo Técnico Preliminar e Simulação de AGVs")
    
    st.write("""
    Bem-vindo ao Dashboard de Engenharia. 
    Esta ferramenta foi criada para aplicar conceitos de **Geometria Analítica e Álgebra Linear** na simulação do trajeto de um Veículo Guiado Automaticamente (AGV).
    
    **Instruções para novos grupos:**
    Você pode navegar pelo menu lateral e alterar os valores nas tabelas e campos de texto. Os gráficos e cálculos se adaptarão automaticamente aos seus novos dados!
    """)
    
    st.info("👈 Use o menu lateral para iniciar a inserção dos dados.")

elif menu == "📍 1. Mapeamento 2D":
    st.header("Etapa 1: Implantação do Sistema de Coordenadas")
    st.write("Edite a tabela abaixo para adicionar as portas, pilares e limites do seu corredor.")
    
    # Editor de dados interativo (Qualquer grupo pode alterar)
    df_pontos = st.data_editor(st.session_state['pontos_corredor'], num_rows="dynamic", use_container_width=True)
    st.session_state['pontos_corredor'] = df_pontos # Salva no estado
    
    st.subheader("Visualização do Corredor")
    fig = criar_grafico_base("Mapa Base do Corredor")
    fig.add_trace(go.Scatter(
        x=df_pontos['X (m)'], y=df_pontos['Y (m)'],
        mode='markers+text',
        text=df_pontos['ID'],
        textposition="top center",
        marker=dict(size=10, color='blue'),
        name="Pontos Mapeados"
    ))
    st.plotly_chart(fig, use_container_width=True)

elif menu == "📡 2. Triangulação":
    st.header("Etapa 2: Triangulação Experimental (Localização)")
    st.write("Insira as coordenadas das 3 antenas (Beacons) e a distância do AGV até elas.")
    
    col1, col2, col3 = st.columns(3)
    t = st.session_state['triangulacao']
    
    with col1:
        st.subheader("Beacon A")
        t['A_x'] = st.number_input("X do Beacon A", value=t['A_x'])
        t['A_y'] = st.number_input("Y do Beacon A", value=t['A_y'])
        t['Da'] = st.number_input("Raio (Distância A)", value=t['Da'])
    with col2:
        st.subheader("Beacon B")
        t['B_x'] = st.number_input("X do Beacon B", value=t['B_x'])
        t['B_y'] = st.number_input("Y do Beacon B", value=t['B_y'])
        t['Db'] = st.number_input("Raio (Distância B)", value=t['Db'])
    with col3:
        st.subheader("Beacon C")
        t['C_x'] = st.number_input("X do Beacon C", value=t['C_x'])
        t['C_y'] = st.number_input("Y do Beacon C", value=t['C_y'])
        t['Dc'] = st.number_input("Raio (Distância C)", value=t['Dc'])
        
    st.markdown("---")
    col_real1, col_real2 = st.columns(2)
    with col_real1:
        t['Real_x'] = st.number_input("X Real do AGV (Para calcular erro)", value=t['Real_x'])
    with col_real2:
        t['Real_y'] = st.number_input("Y Real do AGV (Para calcular erro)", value=t['Real_y'])
        
    st.session_state['triangulacao'] = t

    # Gráfico de interseção de círculos
    fig = criar_grafico_base("Simulação de Triangulação (GPS Indoor)")
    
    # Função para desenhar círculo no Plotly
    def add_circle(fig, x, y, r, name, color):
        fig.add_shape(type="circle", xref="x", yref="y", x0=x-r, y0=y-r, x1=x+r, y1=y+r, line_color=color, opacity=0.5)
        fig.add_trace(go.Scatter(x=[x], y=[y], mode='markers+text', text=[name], marker=dict(color=color, symbol='cross'), name=name))

    add_circle(fig, t['A_x'], t['A_y'], t['Da'], "Beacon A", "red")
    add_circle(fig, t['B_x'], t['B_y'], t['Db'], "Beacon B", "green")
    add_circle(fig, t['C_x'], t['C_y'], t['Dc'], "Beacon C", "blue")
    
    # Ponto Real
    fig.add_trace(go.Scatter(x=[t['Real_x']], y=[t['Real_y']], mode='markers', marker=dict(color='black', size=12, symbol='star'), name="Posição Real"))
    
    # Calculando ponto analítico aproximado (usando A e C do pdf como exemplo prático de visualização)
    # No sistema real, seria o MMQ ou Cramer. Aqui simplificamos a visualização mostrando o ponto real
    
    st.plotly_chart(fig, use_container_width=True)

elif menu == "🛣️ 3. Trajetória e Colisão":
    st.header("Etapas 3 e 4: Trajetória Ideal e Colisão com Obstáculo")
    
    df = st.session_state['pontos_corredor']
    if len(df) < 2:
        st.warning("Adicione pelo menos 2 pontos na Etapa 1.")
    else:
        col1, col2 = st.columns(2)
        with col1:
            p_inicio = st.selectbox("Ponto de Partida", df['ID'].tolist(), index=0)
        with col2:
            p_fim = st.selectbox("Ponto de Destino", df['ID'].tolist(), index=len(df)-2 if len(df)>1 else 1)
            
        x1, y1 = df[df['ID'] == p_inicio].iloc[0][['X (m)', 'Y (m)']]
        x2, y2 = df[df['ID'] == p_fim].iloc[0][['X (m)', 'Y (m)']]
        
        st.subheader("Dados do Obstáculo")
        obs = st.session_state['obstaculo']
        oc1, oc2, oc3 = st.columns(3)
        with oc1: obs['X'] = st.number_input("X do Obstáculo", value=obs['X'])
        with oc2: obs['Y'] = st.number_input("Y do Obstáculo", value=obs['Y'])
        with oc3: obs['Raio'] = st.number_input("Raio de interferência (m)", value=obs['Raio'])
        st.session_state['obstaculo'] = obs
        
        # Cálculos Matemáticos
        m = (y2 - y1) / (x2 - x1) if (x2 - x1) != 0 else 0
        b = y1 - m * x1
        
        # Equação geral Ax + By + C = 0 => (m)x + (-1)y + (b) = 0
        A, B, C = m, -1, b
        dist_colisao = abs(A*obs['X'] + B*obs['Y'] + C) / math.sqrt(A**2 + B**2)
        
        st.markdown(f"**Equação da Reta (Trajetória):** `y = {m:.4f}x + {b:.2f}`")
        st.markdown(f"**Distância reta-obstáculo:** `{dist_colisao:.3f} metros`")
        
        if dist_colisao <= obs['Raio']:
            st.error(f"🚨 COLISÃO DETECTADA! A distância ({dist_colisao:.3f}m) é menor que o raio ({obs['Raio']}m).")
        else:
            st.success("✅ Rota Segura! Nenhuma colisão detectada.")
            
        # Gráfico
        fig = criar_grafico_base("Análise de Colisão")
        # Linha
        fig.add_trace(go.Scatter(x=[x1, x2], y=[y1, y2], mode='lines+markers', name='Trajetória Ideal', line=dict(color='blue', width=2)))
        # Obstaculo
        fig.add_shape(type="circle", xref="x", yref="y", x0=obs['X']-obs['Raio'], y0=obs['Y']-obs['Raio'], x1=obs['X']+obs['Raio'], y1=obs['Y']+obs['Raio'], line_color="red", fillcolor="red", opacity=0.3)
        fig.add_trace(go.Scatter(x=[obs['X']], y=[obs['Y']], mode='markers+text', text=['Obstáculo'], marker=dict(color='red'), name='Centro Obstáculo'))
        
        st.plotly_chart(fig, use_container_width=True)
        st.session_state['trajetoria'] = {'x1':x1, 'y1':y1, 'x2':x2, 'y2':y2, 'm':m, 'b':b, 'dist':dist_colisao}

elif menu == "📐 4. Perfil do Piso":
    st.header("Etapa 5: Análise do Perfil do Piso (Desnível)")
    st.write("Insira os dados topográficos para calcular a parábola do desnível.")
    
    df_piso = st.data_editor(st.session_state['piso'], num_rows="dynamic", use_container_width=True)
    st.session_state['piso'] = df_piso
    
    # Ajuste de curva (Polinômio grau 2)
    x = df_piso['X (m)'].values
    y = df_piso['Y (cm) - Altura'].values
    
    try:
        coef = np.polyfit(x, y, 2)
        a, b, c = coef
        
        x_v = -b / (2*a)
        y_v = -((b**2) - 4*a*c) / (4*a)
        
        st.latex(f"Função: y = {a:.2f}x^2 + {b:.2f}x + {c:.2f}")
        st.markdown(f"**Vértice (Ponto Máximo do desnível):** X = {x_v:.2f}m | Altura Máxima = {y_v:.2f}cm")
        
        # Plot
        x_linha = np.linspace(min(x), max(x), 100)
        y_linha = a*(x_linha**2) + b*x_linha + c
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=x, y=y, mode='markers', name='Dados Medidos', marker=dict(size=10, color='black')))
        fig.add_trace(go.Scatter(x=x_linha, y=y_linha, mode='lines', name='Curva Modelada (Parábola)', line=dict(color='orange')))
        fig.add_trace(go.Scatter(x=[x_v], y=[y_v], mode='markers+text', text=['Vértice Máximo'], textposition="top center", marker=dict(size=12, color='red'), name='Ponto Crítico'))
        
        fig.update_layout(title="Perfil Topográfico do Piso", xaxis_title="Distância (m)", yaxis_title="Altura (cm)", template="plotly_white")
        st.plotly_chart(fig, use_container_width=True)
        st.session_state['parabola'] = {'a':a, 'b':b, 'c':c, 'xv':x_v, 'yv':y_v}
    except Exception as e:
        st.warning("Adicione pelo menos 3 pontos com coordenadas X diferentes para calcular a parábola.")

elif menu == "🎯 5. Otimização Logística":
    st.header("Etapa 6: Otimização Logística (Centroide Ponderado)")
    st.write("Defina os pontos de parada e o peso (demanda/frequência) de cada um para encontrar a base ideal do AGV.")
    
    df_demanda = st.data_editor(st.session_state['demanda'], num_rows="dynamic", use_container_width=True)
    st.session_state['demanda'] = df_demanda
    
    soma_pesos = df_demanda['Peso'].sum()
    if soma_pesos > 0:
        x_c = sum(df_demanda['X (m)'] * df_demanda['Peso']) / soma_pesos
        y_c = sum(df_demanda['Y (m)'] * df_demanda['Peso']) / soma_pesos
        
        st.success(f"📍 **Coordenada Ótima para a Base (Centroide):** X = {x_c:.2f}m , Y = {y_c:.2f}m")
        
        fig = criar_grafico_base("Centroide Ponderado - Base do AGV")
        
        # Desenha os limites do corredor baseado no mapeamento geral
        df_pontos = st.session_state['pontos_corredor']
        fig.add_trace(go.Scatter(x=df_pontos['X (m)'], y=df_pontos['Y (m)'], mode='markers', marker=dict(color='lightgrey', size=5), name="Limites"))
        
        # Pontos de demanda (tamanho baseado no peso)
        fig.add_trace(go.Scatter(
            x=df_demanda['X (m)'], y=df_demanda['Y (m)'],
            mode='markers+text', text=df_demanda['Ponto'], textposition="bottom center",
            marker=dict(size=df_demanda['Peso']*5, color='blue', opacity=0.6), name="Pontos de Demanda"
        ))
        
        # Base
        fig.add_trace(go.Scatter(
            x=[x_c], y=[y_c], mode='markers+text', text=["BASE AGV (Centroide)"], textposition="top center",
            marker=dict(size=15, color='green', symbol='star'), name="Base Operacional"
        ))
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("A soma dos pesos deve ser maior que zero.")

elif menu == "📄 RELATÓRIO FINAL":
    st.title("Relatório de Otimização do Corredor Inteligente")
    st.markdown("Este relatório foi gerado automaticamente com base nos dados inseridos nas etapas anteriores.")
    st.markdown("---")
    
    st.header("1. Georreferenciamento (Mapeamento)")
    st.dataframe(st.session_state['pontos_corredor'], use_container_width=True)
    
    st.header("2. Navegação e Segurança")
    if 'trajetoria' in st.session_state:
        tj = st.session_state['trajetoria']
        obs = st.session_state['obstaculo']
        st.write(f"- **Equação da Reta Gerada:** `y = {tj['m']:.4f}x + {tj['b']:.2f}`")
        st.write(f"- **Obstáculo posicionado em:** `({obs['X']}, {obs['Y']})` com raio de `{obs['Raio']}m`")
        st.write(f"- **Distância Calculada (Ponto a Reta):** `{tj['dist']:.3f}m`")
        if tj['dist'] <= obs['Raio']:
            st.error("Status de Segurança: ALERTA DE COLISÃO. Requer manobra de desvio.")
        else:
            st.success("Status de Segurança: TRAJETO LIMPO.")
    else:
        st.warning("Passe pela aba 'Trajetória e Colisão' para gerar estes dados.")
        
    st.header("3. Análise Topográfica do Piso")
    if 'parabola' in st.session_state:
        p = st.session_state['parabola']
        st.write(f"- **Modelagem Matemática:** `y = {p['a']:.2f}x² + {p['b']:.2f}x + {p['c']:.2f}`")
        st.write(f"- **Elevação Máxima Detectada:** `{p['yv']:.2f} cm` na posição X = `{p['xv']:.2f} m`")
        st.info("Recomendação: Aplicar redução de velocidade no AGV nesta coordenada específica para evitar trepidações e instabilidade da carga.")
    else:
        st.warning("Passe pela aba 'Perfil do Piso' para gerar estes dados.")

    st.header("4. Base Operacional (Otimização Logística)")
    df_demanda = st.session_state['demanda']
    soma = df_demanda['Peso'].sum()
    xc = sum(df_demanda['X (m)'] * df_demanda['Peso']) / soma
    yc = sum(df_demanda['Y (m)'] * df_demanda['Peso']) / soma
    st.write(f"Através do método de Centroide Ponderado, considerando as demandas de {len(df_demanda)} setores, o local matematicamente ideal para instalar a base de recarga do AGV é:")
    st.success(f"**Coordenada Ótima: X = {xc:.2f} m | Y = {yc:.2f} m**")
    
    st.markdown("---")
    st.caption("Trabalho desenvolvido para a disciplina de Geometria Analítica e Álgebra Linear - Faculdade MULTIVIX")