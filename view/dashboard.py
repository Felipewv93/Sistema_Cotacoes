import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import sys
import os

# Adicionar o diretório raiz ao path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.data_analysis import cotacoes_do_dia, calcular_variacao


def gerar_dashboard():
    st.set_page_config(page_title="Dashboard de Cotações", page_icon="💰", layout="wide")
    
    st.title("💰 Dashboard de Cotações")
    st.markdown("---")
    
    # Obter dados usando analytics
    cotacoes_hoje, primeira_cotacao, ultima_cotacao = cotacoes_do_dia()
    
    if cotacoes_hoje is None:
        st.error("Não há cotações registradas para hoje.")
        return
    
    # Calcular variações usando analytics
    var_dolar, var_euro, var_bitcoin = calcular_variacao(primeira_cotacao, ultima_cotacao)
    
    if var_dolar is None:
        st.error("Não foi possível calcular as variações.")
        return
    
    # Métricas principais
    st.subheader("📊 Resumo do Dia")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            label="💵 Dólar (USD → BRL)",
            value=f"R$ {ultima_cotacao['dolar']:.2f}",
            delta=f"{var_dolar:.2f}%"
        )
    
    with col2:
        st.metric(
            label="💶 Euro (EUR → BRL)",
            value=f"R$ {ultima_cotacao['euro']:.2f}",
            delta=f"{var_euro:.2f}%"
        )
    
    with col3:
        st.metric(
            label="₿ Bitcoin (BTC → BRL)",
            value=f"R$ {ultima_cotacao['bitcoin']:,.0f}",
            delta=f"{var_bitcoin:.2f}%"
        )
    
    st.markdown("---")
    
    # Gráficos de Linha
    st.subheader("📈 Evolução das Cotações do Dia")
    
    tab1, tab2, tab3, tab4 = st.tabs(["Todas as Moedas", "Dólar", "Euro", "Bitcoin"])
    
    with tab1:
        # Gráfico com todas as moedas (normalizado)
        fig_todas = go.Figure()
        
        fig_todas.add_trace(go.Scatter(
            x=cotacoes_hoje['data_hora'],
            y=cotacoes_hoje['dolar'],
            mode='lines+markers',
            name='Dólar',
            line=dict(color='green', width=2)
        ))
        
        fig_todas.add_trace(go.Scatter(
            x=cotacoes_hoje['data_hora'],
            y=cotacoes_hoje['euro'],
            mode='lines+markers',
            name='Euro',
            line=dict(color='blue', width=2)
        ))
        
        # Bitcoin em eixo secundário (valores muito diferentes)
        fig_todas.add_trace(go.Scatter(
            x=cotacoes_hoje['data_hora'],
            y=cotacoes_hoje['bitcoin'],
            mode='lines+markers',
            name='Bitcoin',
            line=dict(color='orange', width=2),
            yaxis='y2'
        ))
        
        fig_todas.update_layout(
            title="Comparação de Cotações",
            xaxis_title="Horário",
            yaxis_title="Reais (BRL) - Dólar e Euro",
            yaxis2=dict(
                title="Reais (BRL) - Bitcoin",
                overlaying='y',
                side='right'
            ),
            hovermode='x unified',
            height=500,
            legend=dict(orientation="h", yanchor="bottom", y=1.1, xanchor="right", x=1)
        )
        
        st.plotly_chart(fig_todas, use_container_width=True)
    
    with tab2:
        fig_dolar = px.line(
            cotacoes_hoje,
            x='data_hora',
            y='dolar',
            title='Cotação do Dólar',
            markers=True,
            labels={'data_hora': 'Horário', 'dolar': 'Valor (BRL)'}
        )
        fig_dolar.update_traces(line_color='green')
        st.plotly_chart(fig_dolar, use_container_width=True)
    
    with tab3:
        fig_euro = px.line(
            cotacoes_hoje,
            x='data_hora',
            y='euro',
            title='Cotação do Euro',
            markers=True,
            labels={'data_hora': 'Horário', 'euro': 'Valor (BRL)'}
        )
        fig_euro.update_traces(line_color='blue')
        st.plotly_chart(fig_euro, use_container_width=True)
    
    with tab4:
        fig_bitcoin = px.line(
            cotacoes_hoje,
            x='data_hora',
            y='bitcoin',
            title='Cotação do Bitcoin',
            markers=True,
            labels={'data_hora': 'Horário', 'bitcoin': 'Valor (BRL)'}
        )
        fig_bitcoin.update_traces(line_color='orange')
        st.plotly_chart(fig_bitcoin, use_container_width=True)
    
    st.markdown("---")
    
    # Gráfico de Barras - Variação Percentual
    st.subheader("📊 Variação Percentual do Dia")
    
    import pandas as pd
    variacoes_df = pd.DataFrame({
        'Moeda': ['Dólar', 'Euro', 'Bitcoin'],
        'Variação (%)': [var_dolar, var_euro, var_bitcoin]
    })
    
    fig_barras = px.bar(
        variacoes_df,
        x='Moeda',
        y='Variação (%)',
        title='Comparação de Variação',
        color='Variação (%)',
        color_continuous_scale=['red', 'yellow', 'green'],
        text='Variação (%)',
        text_auto='.2f'
    )
    
    fig_barras.update_traces(texttemplate='%{text:.2f}%', textposition='outside')
    fig_barras.update_layout(height=475, xaxis_title=None)
    
    st.plotly_chart(fig_barras, use_container_width=True)
    
    st.markdown("---")
    
    # Tabela de dados
    st.subheader("📋 Dados Detalhados")
    st.dataframe(
        cotacoes_hoje[['data_hora', 'dolar', 'euro', 'bitcoin']].sort_values('data_hora', ascending=False),
        use_container_width=True,
        hide_index=True
    )

# Executar o dashboard
if __name__ == "__main__":
    gerar_dashboard()