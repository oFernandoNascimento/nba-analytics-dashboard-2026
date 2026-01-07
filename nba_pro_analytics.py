"""
NBA Analytics Master 2026
---------------------------------------------------------
Autor: Fernando Teixeira do Nascimento
Data: 07 de Janeiro de 2026
Descrição: Dashboard interativo para análise de dados da NBA 
           utilizando Streamlit, Pandas e Plotly.
           Inclui métricas avançadas (Expectativa Pitagórica),
           visualização de dados e feed de notícias.
"""

import streamlit as st
import pandas as pd
import numpy as np
import base64
import os
import plotly.express as px
import plotly.graph_objects as go
from typing import Optional, List

# =========================================================
# 1. CONSTANTES E CONFIGURAÇÕES GLOBAIS
# =========================================================
PAGE_TITLE = "NBA Analytics Master 2026"
PAGE_ICON = "🏀"
LAYOUT = "wide"

# URLs Base da NBA
URL_LOGO_BASE = "https://cdn.nba.com/logos/nba/{}/primary/L/logo.svg"
URL_HEADSHOT_BASE = "https://ak-static.cms.nba.com/wp-content/uploads/headshots/nba/latest/260x190/{}.png"

# Cores do Tema
COLOR_BG = "#0e1117"
COLOR_TEXT = "white"
COLOR_ACCENT = "#FFD700"  # Dourado

st.set_page_config(page_title=PAGE_TITLE, page_icon=PAGE_ICON, layout=LAYOUT, initial_sidebar_state="collapsed")

# =========================================================
# 2. CAMADA DE DADOS E UTILITÁRIOS
# =========================================================

def get_team_logo_url(team_id: int) -> str:
    """Gera a URL oficial do logo do time baseado no ID."""
    return URL_LOGO_BASE.format(team_id)

def get_player_headshot_url(player_id: int) -> str:
    """Gera a URL da foto de perfil do jogador."""
    return URL_HEADSHOT_BASE.format(player_id)

def get_local_image_as_base64(filename_list: List[str]) -> Optional[str]:
    """
    Tenta carregar uma imagem local e converter para Base64.
    Útil para carregar avatares personalizados ou assets locais.
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    for filename in filename_list:
        file_path = os.path.join(script_dir, filename)
        if os.path.exists(file_path):
            try:
                with open(file_path, "rb") as image_file:
                    encoded_string = base64.b64encode(image_file.read()).decode()
                ext = filename.split('.')[-1]
                return f"data:image/{ext};base64,{encoded_string}"
            except Exception as e:
                # Em produção, usar logging ao invés de print
                print(f"Erro ao carregar imagem local: {e}")
                continue
    # Retorna uma imagem transparente ou placeholder se falhar
    return "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII="

@st.cache_data
def load_nba_dataset() -> pd.DataFrame:
    """
    Carrega o dataset principal e realiza o pré-processamento básico.
    Usa cache para evitar recarregamento desnecessário.
    """
    try:
        # Tenta carregar o CSV local
        df = pd.read_csv("nba_data.csv")
        
        # Engenharia de Features básica
        # PCT: Porcentagem de Vitórias
        if 'V' in df.columns and 'D' in df.columns:
            df['PCT'] = df['V'] / (df['V'] + df['D'])
        
        # Mapeia o Logo se a coluna LogoID existir
        if 'LogoID' in df.columns:
            df['Logo'] = df['LogoID'].apply(lambda x: get_team_logo_url(x))
            
        return df
    except FileNotFoundError:
        st.error("⚠️ Arquivo 'nba_data.csv' não encontrado. Por favor, verifique o diretório.")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Erro ao processar dados: {e}")
        return pd.DataFrame()

# =========================================================
# 3. ESTILIZAÇÃO (CSS CUSTOMIZADO)
# =========================================================
def inject_custom_css():
    """Injeta CSS customizado para Cards, Tabelas e Layout."""
    st.markdown(f"""
        <style>
        /* Fundo e Tipografia Geral */
        .stApp {{ background-color: {COLOR_BG}; }}
        h1, h2, h3 {{ color: {COLOR_TEXT}; font-family: 'Arial', sans-serif; font-weight: 800; }}
        
        /* Ajuste de Espaçamento Principal - AUMENTADO PARA O RODAPÉ NÃO CORTAR */
        .block-container {{ padding-top: 2rem; padding-bottom: 6rem !important; }}
        div[data-testid="stDataFrame"] {{ background-color: transparent !important; width: 100%; }}
        
        /* Estilização das Abas (Tabs) */
        .stTabs [data-baseweb="tab-list"] {{ gap: 15px; justify-content: center; border-bottom: 2px solid #374151; padding-bottom: 10px; margin-bottom: 20px; }}
        .stTabs [data-baseweb="tab"] {{ height: 50px; background-color: transparent; border-radius: 5px; color: #9ca3af; font-size: 16px; font-weight: 600; }}
        .stTabs [aria-selected="true"] {{ background-color: #1f2937; color: {COLOR_ACCENT} !important; border: 1px solid {COLOR_ACCENT}; box-shadow: 0 0 10px rgba(255, 215, 0, 0.2); }}
        
        /* Componente: Player Card */
        .player-card {{ 
            background: linear-gradient(145deg, #1f2937, #111827); 
            padding: 20px; border-radius: 15px; border: 1px solid #374151; 
            margin-bottom: 15px; display: flex; align-items: center; 
            box-shadow: 0 4px 15px rgba(0,0,0,0.5); 
            transition: transform 0.2s;
        }}
        .player-card:hover {{ transform: translateY(-2px); border-color: {COLOR_ACCENT}; }}
        
        .rank-gold {{ font-size: 42px; font-weight: 900; color: {COLOR_ACCENT}; width: 65px; text-align: center; margin-right: 20px; }}
        
        /* Componente: Stat Circle */
        .stat-box {{ 
            background-color: {COLOR_BG}; width: 100px; height: 100px; border-radius: 50%; 
            display: flex; flex-direction: column; justify-content: center; align-items: center; 
            border: 3px solid #00b4d8; margin-left: auto; 
        }}
        .stat-val {{ font-size: 26px; font-weight: bold; color: #00b4d8; }}
        
        /* Componente: News Card */
        .news-container {{ 
            background: #161b22; border-radius: 12px; padding: 20px; margin-bottom: 15px; 
            border-left: 6px solid #00b4d8; display: flex; align-items: center; 
            transition: all 0.3s ease; 
        }}
        .news-container:hover {{ transform: scale(1.01); border-left: 6px solid {COLOR_ACCENT}; cursor: pointer; background: #1c2128; }}
        .news-link {{ text-decoration: none; color: white; }}
        
        /* Footer Fixo */
        .footer {{ 
            position: fixed; left: 0; bottom: 0; width: 100%; 
            background-color: #0e1117; color: #888; text-align: center; 
            font-size: 12px; padding: 15px 0; border-top: 1px solid #333; 
            z-index: 9999; /* Garante que fique sobre tudo */
        }}
        
        /* Box de Análise (GOAT Verdict) */
        .goat-analysis {{ background: #1f2937; border-radius: 10px; padding: 20px; border-left: 8px solid {COLOR_ACCENT}; color: #e6edf3; font-size: 16px; margin-top: 15px; }}
        </style>
    """, unsafe_allow_html=True)

# Funções de Estilo para Pandas (Styler)
def style_dataframe_light(df: pd.DataFrame):
    """Aplica estilo claro (White/Black) para tabelas de classificação."""
    return df.style.set_properties(**{
        'background-color': '#ffffff', 
        'color': 'black', 
        'text-align': 'center', 
        'border': '1px solid #ddd'
    }).set_table_styles([{
        'selector': 'th', 
        'props': [('background-color', '#f8f9fa'), ('color', '#000000'), ('font-weight', 'bold'), ('border', '1px solid #ddd')]
    }])

def style_dataframe_dark(df: pd.DataFrame):
    """Aplica estilo escuro (Dark/White) para tabelas de confronto."""
    return df.style.set_properties(**{
        'background-color': '#1f2937', 
        'color': 'white', 
        'text-align': 'center', 
        'border': '1px solid #444'
    }).set_table_styles([{
        'selector': 'th', 
        'props': [('background-color', '#111827'), ('color', '#FFD700'), ('border', '1px solid #444')]
    }])

# =========================================================
# 4. EXECUÇÃO PRINCIPAL
# =========================================================

# Inicialização
inject_custom_css()
df_geral = load_nba_dataset()

# Preparação de Dados por Conferência
if not df_geral.empty:
    df_east = df_geral[df_geral['Conferencia'] == 'Leste'].sort_values('PCT', ascending=False).reset_index(drop=True)
    df_west = df_geral[df_geral['Conferencia'] == 'Oeste'].sort_values('PCT', ascending=False).reset_index(drop=True)
    df_east['Pos'] = df_east.index + 1
    df_west['Pos'] = df_west.index + 1
else:
    df_east = pd.DataFrame()
    df_west = pd.DataFrame()

# --- MOCK DATA: Estatísticas de Jogadores (Snapshot 07/01/2026) ---
# Em um cenário real, isso viria de uma API.
PLAYER_STATS = {
    'pts': [
        {'#': 1, 'Nome': 'Luka Doncic', 'Time': 'LAL', 'Val': 33.7, 'Foto': get_player_headshot_url(1629029), 'Logo': get_team_logo_url(1610612747)},
        {'#': 2, 'Nome': 'S. Gilgeous-Alexander', 'Time': 'OKC', 'Val': 31.6, 'Foto': get_player_headshot_url(1628983), 'Logo': get_team_logo_url(1610612760)},
        {'#': 3, 'Nome': 'Tyrese Maxey', 'Time': 'PHI', 'Val': 31.0, 'Foto': get_player_headshot_url(1630178), 'Logo': get_team_logo_url(1610612755)},
        {'#': 4, 'Nome': 'Donovan Mitchell', 'Time': 'CLE', 'Val': 29.8, 'Foto': get_player_headshot_url(1628378), 'Logo': get_team_logo_url(1610612739)},
        {'#': 5, 'Nome': 'Nikola Jokic', 'Time': 'DEN', 'Val': 29.6, 'Foto': get_player_headshot_url(203999), 'Logo': get_team_logo_url(1610612743)},
        {'#': 6, 'Nome': 'Jaylen Brown', 'Time': 'BOS', 'Val': 29.6, 'Foto': get_player_headshot_url(1627759), 'Logo': get_team_logo_url(1610612738)}
    ],
    'ast': [
        {'#': 1, 'Nome': 'Nikola Jokic', 'Time': 'DEN', 'Val': 11.0, 'Foto': get_player_headshot_url(203999), 'Logo': get_team_logo_url(1610612743)},
        {'#': 2, 'Nome': 'Cade Cunningham', 'Time': 'DET', 'Val': 9.7, 'Foto': get_player_headshot_url(1630595), 'Logo': get_team_logo_url(1610612765)},
        {'#': 3, 'Nome': 'Josh Giddey', 'Time': 'CHI', 'Val': 9.0, 'Foto': get_player_headshot_url(1630581), 'Logo': get_team_logo_url(1610612741)},
        {'#': 4, 'Nome': 'Luka Doncic', 'Time': 'LAL', 'Val': 8.7, 'Foto': get_player_headshot_url(1629029), 'Logo': get_team_logo_url(1610612747)},
        {'#': 5, 'Nome': 'Jalen Johnson', 'Time': 'ATL', 'Val': 8.4, 'Foto': get_player_headshot_url(1630552), 'Logo': get_team_logo_url(1610612737)},
        {'#': 6, 'Nome': 'James Harden', 'Time': 'LAC', 'Val': 8.0, 'Foto': get_player_headshot_url(201935), 'Logo': get_team_logo_url(1610612746)}
    ],
    'reb': [
        {'#': 1, 'Nome': 'Nikola Jokic', 'Time': 'DEN', 'Val': 12.2, 'Foto': get_player_headshot_url(203999), 'Logo': get_team_logo_url(1610612743)},
        {'#': 2, 'Nome': 'Karl-Anthony Towns', 'Time': 'NYK', 'Val': 11.5, 'Foto': get_player_headshot_url(1626157), 'Logo': get_team_logo_url(1610612752)},
        {'#': 3, 'Nome': 'Rudy Gobert', 'Time': 'MIN', 'Val': 11.2, 'Foto': get_player_headshot_url(203497), 'Logo': get_team_logo_url(1610612750)},
        {'#': 4, 'Nome': 'Ivica Zubac', 'Time': 'LAC', 'Val': 11.0, 'Foto': get_player_headshot_url(1627826), 'Logo': get_team_logo_url(1610612746)},
        {'#': 5, 'Nome': 'Donovan Clingan', 'Time': 'POR', 'Val': 10.8, 'Foto': get_player_headshot_url(1642270), 'Logo': get_team_logo_url(1610612757)},
        {'#': 6, 'Nome': 'Jalen Duren', 'Time': 'DET', 'Val': 10.6, 'Foto': get_player_headshot_url(1631105), 'Logo': get_team_logo_url(1610612765)}
    ],
    '3pm': [
        {'#': 1, 'Nome': 'Stephen Curry', 'Time': 'GSW', 'Val': 4.8, 'Foto': get_player_headshot_url(201939), 'Logo': get_team_logo_url(1610612744)},
        {'#': 2, 'Nome': 'Donovan Mitchell', 'Time': 'CLE', 'Val': 3.9, 'Foto': get_player_headshot_url(1628378), 'Logo': get_team_logo_url(1610612739)},
        {'#': 3, 'Nome': 'Tyrese Maxey', 'Time': 'PHI', 'Val': 3.8, 'Foto': get_player_headshot_url(1630178), 'Logo': get_team_logo_url(1610612755)},
        {'#': 4, 'Nome': 'Michael Porter Jr.', 'Time': 'BKN', 'Val': 3.7, 'Foto': get_player_headshot_url(1629008), 'Logo': get_team_logo_url(1610612751)},
        {'#': 5, 'Nome': 'Kon Knueppel', 'Time': 'CHA', 'Val': 3.6, 'Foto': get_local_image_as_base64(["kon.webp", "kon.png", "Kon.webp", "1642851.webp"]) or "https://cdn.nba.com/headshots/nba/latest/260x190/fallback.png", 'Logo': get_team_logo_url(1610612766)},
        {'#': 6, 'Nome': 'Jamal Murray', 'Time': 'DEN', 'Val': 3.4, 'Foto': get_player_headshot_url(1627750), 'Logo': get_team_logo_url(1610612743)}
    ],
    'stl': [
        {'#': 1, 'Nome': 'Kawhi Leonard', 'Time': 'LAC', 'Val': 2.1, 'Foto': get_player_headshot_url(202695), 'Logo': get_team_logo_url(1610612746)},
        {'#': 2, 'Nome': 'Cason Wallace', 'Time': 'OKC', 'Val': 2.1, 'Foto': get_player_headshot_url(1641717), 'Logo': get_team_logo_url(1610612760)},
        {'#': 3, 'Nome': 'Dyson Daniels', 'Time': 'ATL', 'Val': 1.9, 'Foto': get_player_headshot_url(1630700), 'Logo': get_team_logo_url(1610612737)},
        {'#': 4, 'Nome': 'OG Anunoby', 'Time': 'NYK', 'Val': 1.8, 'Foto': get_player_headshot_url(1628384), 'Logo': get_team_logo_url(1610612752)},
        {'#': 5, 'Nome': 'Tyrese Maxey', 'Time': 'PHI', 'Val': 1.8, 'Foto': get_player_headshot_url(1630178), 'Logo': get_team_logo_url(1610612755)},
        {'#': 6, 'Nome': 'Mikal Bridges', 'Time': 'NYK', 'Val': 1.6, 'Foto': get_player_headshot_url(1628969), 'Logo': get_team_logo_url(1610612752)}
    ]
}

# --- SIDEBAR (NAVEGAÇÃO) ---
st.sidebar.image("https://cdn.nba.com/logos/leagues/logo-nba.svg", width=120)
with st.sidebar.expander("ℹ️ Entenda as Siglas"):
    st.info("""
    **PCT:** % de Vitórias
    **PPG:** Pontos por Jogo (Ataque)
    **OPPG:** Pontos Sofridos (Defesa)
    **REB:** Rebotes
    **3PM:** Bolas de 3 convertidas
    **STL:** Roubos de Bola
    """)

# Estrutura de Abas
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🏆 Classificação", 
    "📊 Líderes de Elite", 
    "👑 Corrida MVP", 
    "⚔️ Simulador H2H", 
    "📰 Notícias"
])

# ==========================
# ABA 1: CLASSIFICAÇÃO
# ==========================
with tab1:
    st.title(f"🏆 Classificação Temporada 2025-26")
    
    # 1. Tabelas Leste/Oeste
    t1, t2 = st.tabs(["Conferência Leste", "Conferência Oeste"])
    
    col_config = {
        "Pos": st.column_config.NumberColumn("Posição", format="%dº"),
        "Logo": st.column_config.ImageColumn("Logo"), 
        "Time": st.column_config.TextColumn("Equipe"),
        "V": st.column_config.NumberColumn("Vitórias"),
        "D": st.column_config.NumberColumn("Derrotas"),
        "PCT": st.column_config.ProgressColumn("Aproveitamento", format="%.3f", min_value=0, max_value=1),
        "PPG": st.column_config.NumberColumn("Pontos Feitos (Média)", format="%.1f"),
        "OPPG": st.column_config.NumberColumn("Pontos Sofridos (Média)", format="%.1f")
    }
    cols_display = ["Pos", "Logo", "Time", "V", "D", "PCT", "PPG", "OPPG"]
    
    with t1: 
        if not df_east.empty:
            st.dataframe(style_dataframe_light(df_east[cols_display]), column_config=col_config, hide_index=True, use_container_width=True, height=580)
    with t2: 
        if not df_west.empty:
            st.dataframe(style_dataframe_light(df_west[cols_display]), column_config=col_config, hide_index=True, use_container_width=True, height=580)

    st.divider()

    if not df_geral.empty:
        # 2. Scatter Plot: Ataque vs Defesa
        st.markdown("### 🔍 Análise de Eficiência: Ataque vs. Defesa")
        st.caption("Times no canto superior direito são os melhores (marcam muito e sofrem pouco).")
        
        # Gráfico Base (Bolinhas transparentes)
        fig_scatter = px.scatter(
            df_geral, x="OPPG", y="PPG", 
            color="Conferencia", hover_name="Time",
            color_discrete_map={"Leste": "#00b4d8", "Oeste": "#e41e31"},
            labels={"PPG": "Ataque (Pontos Feitos)", "OPPG": "Defesa (Pontos Sofridos)"},
            template="plotly_white"
        )
        fig_scatter.update_traces(marker=dict(opacity=0))

        # Adiciona Logos como imagens no gráfico
        logos_images = []
        for _, row in df_geral.iterrows():
            logos_images.append(dict(
                source=row['Logo'], x=row['OPPG'], y=row['PPG'], xref="x", yref="y",
                sizex=1.3, sizey=1.3, xanchor="center", yanchor="middle", layer="above"
            ))
        fig_scatter.update_layout(images=logos_images)
        
        # Camada de Texto (Nomes dos times abaixo do logo)
        fig_scatter.add_trace(go.Scatter(
            x=df_geral["OPPG"],
            y=df_geral["PPG"] - 0.8,
            text=df_geral["Time"],
            mode="text",
            textfont=dict(color="black", size=9, weight="bold"),
            textposition="bottom center",
            showlegend=False,
            hoverinfo="skip"
        ))

        fig_scatter.update_layout(
            paper_bgcolor='white', plot_bgcolor='white', font=dict(color="black"), height=650,
            xaxis=dict(title=dict(text="Defesa (Pontos Sofridos)", font=dict(color="black", size=14, weight="bold")), tickfont=dict(color="black", size=12, weight="bold"), gridcolor='#cccccc'),
            yaxis=dict(title=dict(text="Ataque (Pontos Feitos)", font=dict(color="black", size=14, weight="bold")), tickfont=dict(color="black", size=12, weight="bold"), gridcolor='#cccccc'),
            legend=dict(font=dict(color="black"), bgcolor="rgba(255,255,255,0.8)")
        )
        st.plotly_chart(fig_scatter, use_container_width=True)
        
        st.divider()

        # 3. Bar Chart: Expectativa Pitagórica
        st.markdown("### 🔮 Projeção Pitagórica: Sorte ou Competência?")
        st.caption("Esta análise matemática projeta quantas vitórias um time 'deveria' ter baseado no saldo de pontos. **Barras Verdes (Direita)** indicam times que venceram mais jogos apertados (Sorte/Clutch). **Barras Vermelhas (Esquerda)** indicam times azarados (potencial de melhora).")

        # Cálculo da Expectativa Pitagórica
        df_py = df_geral.copy()
        df_py['Jogos'] = df_py['V'] + df_py['D']
        df_py['Exp_Win_Pct'] = (df_py['PPG']**14) / ((df_py['PPG']**14) + (df_py['OPPG']**14))
        df_py['V_Esperadas'] = df_py['Exp_Win_Pct'] * df_py['Jogos']
        df_py['Diferenca_Sorte'] = df_py['V'] - df_py['V_Esperadas']
        
        # Filtragem (Top 5 Sortudos vs Top 5 Azarados)
        df_py = df_py.sort_values('Diferenca_Sorte', ascending=False)
        top_lucky = df_py.head(5)
        top_unlucky = df_py.tail(5)
        df_final_py = pd.concat([top_lucky, top_unlucky]).sort_values('Diferenca_Sorte', ascending=True)

        fig_py = px.bar(
            df_final_py, 
            x='Diferenca_Sorte', 
            y='Time', 
            orientation='h',
            text_auto='.1f',
            color='Diferenca_Sorte',
            color_continuous_scale=['#d62828', '#f1faee', '#2a9d8f']
        )
        
        # Logos nas barras
        py_logos = []
        for _, row in df_final_py.iterrows():
            offset = 0.35 if row['Diferenca_Sorte'] >= 0 else -0.35
            py_logos.append(dict(
                source=row['Logo'],
                x=row['Diferenca_Sorte'] + offset, 
                y=row['Time'],
                xref="x", yref="y",
                sizex=0.9, sizey=0.9,
                xanchor="center", yanchor="middle",
                layer="above"
            ))
        fig_py.update_layout(images=py_logos)

        fig_py.update_layout(
            paper_bgcolor='white', plot_bgcolor='white', font=dict(color="black"), height=600,
            title=dict(text="Diferença entre Vitórias Reais e Esperadas", font=dict(color="black", size=18, weight="bold")),
            xaxis=dict(
                title=dict(text="Saldo de Vitórias (Real - Esperado)", font=dict(color="black", weight="bold")),
                tickfont=dict(color="black"),
                showgrid=True, gridcolor='#e5e5e5', gridwidth=1,
                zeroline=True, zerolinecolor='black', zerolinewidth=2,
                tickformat='.1f'
            ),
            yaxis=dict(
                title=dict(text="Times (Top 5 'Sortudos' vs Top 5 'Azarados')", font=dict(color="black", weight="bold")),
                tickfont=dict(color="black", size=12, weight="bold"),
                tickmode='linear'
            ),
            coloraxis_showscale=False,
            margin=dict(l=150)
        )
        
        st.plotly_chart(fig_py, use_container_width=True)
        st.info("💡 **Insight de Recrutador:** Times no topo (Verde) estão 'superando as expectativas'. Times no fundo (Vermelho) estão jogando melhor do que a tabela mostra e tendem a subir na classificação.")
        st.divider()

# ==========================
# ABA 2: LÍDERES
# ==========================
with tab2:
    st.title("📊 Líderes por Categoria (Top 6)")
    sub_tabs = st.tabs(["🔥 PPG", "🎁 AST", "🛡️ REB", "💦 3PM", "🔒 STL"])
    
    def render_player_cards(data_list, label_stat):
        """Renderiza os cards dos jogadores em HTML/CSS."""
        for p in data_list:
            st.markdown(f"""
            <div class="player-card">
                <div class="rank-gold">#{p['#']}</div>
                <img src="{p['Foto']}" width="110" style="border-radius:10px; object-fit: cover;">
                <div style="margin-left:20px; flex-grow:1;">
                    <p style="color:white; font-size:18px; font-weight:bold; margin:0;">{p['Nome']}</p>
                    <div style="display:flex; align-items:center; margin-top:5px;">
                        <img src="{p['Logo']}" width="30"> 
                        <b style="color:#ccc; margin-left:8px;">{p['Time']}</b>
                    </div>
                </div>
                <div class="stat-box">
                    <div class="stat-val">{p['Val']}</div>
                    <div style="font-size:10px; color:#888;">{label_stat}</div>
                </div>
            </div>""", unsafe_allow_html=True)

    with sub_tabs[0]: render_player_cards(PLAYER_STATS['pts'], "PPG")
    with sub_tabs[1]: render_player_cards(PLAYER_STATS['ast'], "AST")
    with sub_tabs[2]: render_player_cards(PLAYER_STATS['reb'], "REB")
    with sub_tabs[3]: render_player_cards(PLAYER_STATS['3pm'], "3PM")
    with sub_tabs[4]: render_player_cards(PLAYER_STATS['stl'], "STL")

# ==========================
# ABA 3: MVP RACE
# ==========================
with tab3:
    st.title("👑 Kia MVP Race: Top 5")
    # Mock Data MVP
    mvps = [
        {'#': 1, 'Nome': 'Nikola Jokic', 'Time': 'DEN', 'Val': 0.23, 'Foto': get_player_headshot_url(203999), 'Logo': get_team_logo_url(1610612743)},
        {'#': 2, 'Nome': 'S. Gilgeous-Alexander', 'Time': 'OKC', 'Val': 0.20, 'Foto': get_player_headshot_url(1628983), 'Logo': get_team_logo_url(1610612760)},
        {'#': 3, 'Nome': 'Luka Doncic', 'Time': 'LAL', 'Val': 0.21, 'Foto': get_player_headshot_url(1629029), 'Logo': get_team_logo_url(1610612747)},
        {'#': 4, 'Nome': 'Jalen Brunson', 'Time': 'NYK', 'Val': 0.18, 'Foto': get_player_headshot_url(1628973), 'Logo': get_team_logo_url(1610612752)},
        {'#': 5, 'Nome': 'Victor Wembanyama', 'Time': 'SAS', 'Val': 0.20, 'Foto': get_player_headshot_url(1641705), 'Logo': get_team_logo_url(1610612759)}
    ]
    render_player_cards(mvps, "PIE INDEX")

# ==========================
# ABA 4: SIMULADOR H2H
# ==========================
with tab4:
    st.title("⚔️ Analisador de Confronto H2H")
    
    if not df_geral.empty:
        times_lista = df_geral['Time'].unique()
        c1, c2 = st.columns(2)
        t1_n = c1.selectbox("Mandante (Casa)", times_lista, index=1 if len(times_lista) > 1 else 0)
        t2_n = c2.selectbox("Visitante (Fora)", times_lista, index=0)
        
        if t1_n != t2_n:
            d1 = df_geral[df_geral['Time'] == t1_n].iloc[0]
            d2 = df_geral[df_geral['Time'] == t2_n].iloc[0]
            
            # Algoritmo simples de probabilidade baseado em PCT + Fator Casa
            prob = max(5, min(95, 50 + ((d1['PCT'] - d2['PCT']) * 100) + 6.5))
            
            col_r1, col_vs, col_r2 = st.columns([1, 0.4, 1])
            with col_r1: 
                st.image(d1['Logo'], width=150)
                st.metric("Chance de Vitória", f"{prob:.1f}%")
            with col_vs: 
                st.markdown("<h1 style='text-align:center; padding-top:80px; color:#555;'>VS</h1>", unsafe_allow_html=True)
            with col_r2: 
                st.image(d2['Logo'], width=150)
                st.metric("Chance de Vitória", f"{(100-prob):.1f}%")
            
            st.progress(prob/100)
            
            st.markdown(f"""<div class="goat-analysis"><strong>💎 Veredito do G.O.A.T.:</strong><br>O <b>{t1_n}</b> tem {d1['PCT']:.1%} de aproveitamento contra {d2['PCT']:.1%} do rival. O fator casa aumenta a probabilidade em 6.5%.</div>""", unsafe_allow_html=True)
            st.write("---")
            
            # Tabela Comparativa H2H
            h2h_data = {
                "Métrica": ["Campanha (V-D)", "Ataque (PPG)", "Defesa (OPPG)", "Aproveitamento"],
                t1_n: [f"{d1['V']}-{d1['D']}", f"{d1['PPG']:.1f}", f"{d1['OPPG']:.1f}", f"{d1['PCT']:.1%}"],
                t2_n: [f"{d2['V']}-{d2['D']}", f"{d2['PPG']:.1f}", f"{d2['OPPG']:.1f}", f"{d2['PCT']:.1%}"]
            }
            st.dataframe(style_dataframe_dark(pd.DataFrame(h2h_data).set_index("Métrica")), use_container_width=True)

# ==========================
# ABA 5: NOTÍCIAS
# ==========================
with tab5:
    st.title("📰 NBA Insider: Breaking News (Brasil)")
    
    # Notícias Simuladas para 07/01/2026 com Links Reais
    news_items = [
        ("Durant decide no último segundo e provoca Suns: 'É bom vencer um time que te expulsou'", get_player_headshot_url(201142), "ge.globo.com", "https://ge.globo.com/basquete/nba/noticia/2026/01/06/durant-decide-no-ultimo-segundo-e-provoca-suns-e-bom-vencer-um-time-que-te-expulsou.ghtml"),
        ("Pistons vencem Celtics em jogo emocionante; confira os detalhes", get_player_headshot_url(1630595), "ESPN.com.br", "https://www.espn.com.br/nba/jogo/_/jogoId/401836803/pistons-celtics"), # <--- CORREÇÃO AQUI: get_player_headshot_url para o Cade
        ("Kia MVP Ladder: Jokic lidera a primeira corrida de 2026", get_player_headshot_url(203999), "NBA.com", "https://www.nba.com/news/kia-mvp-ladder-jan-2-2026"),
        ("Aos 41 anos, LeBron impressiona Doncic em 2026: 'Uma loucura'", get_player_headshot_url(2544), "ge.globo.com", "https://ge.globo.com/basquete/nba/noticia/2026/01/07/aos-41-anos-lebron-inicia-2026-com-boas-atuacoes-e-impressiona-doncic-uma-loucura.ghtml")
    ]
    
    for title, img, source, link in news_items:
        st.markdown(f"""
        <a href="{link}" target="_blank" class="news-link">
            <div class="news-container">
                <img src="{img}" width="120" style="border-radius:12px; margin-right:25px;">
                <div>
                    <h3 style="margin:0; color:white;">{title} 🔗</h3>
                    <p style="color:#aaa; margin-top:5px;">Fonte: <b>{source}</b> | 07/01/2026</p>
                </div>
            </div>
        </a>
        """, unsafe_allow_html=True)

# Rodapé
st.markdown("""
    <div class="footer">
        <p>© 2026 NBA Analytics Project | Desenvolvido por Fernando Teixeira do Nascimento</p>
        <p>Todos os dados e logos são propriedade intelectual da NBA e seus respectivos times.</p>
    </div>
""", unsafe_allow_html=True)