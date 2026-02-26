import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Dashboard UFSM-CS", layout="wide")
st.title("Dashboard Inteligente - Pesquisa de Cursos")

CSV_URL = "https://raw.githubusercontent.com/luanportella/Questionarios/main/raw_data.csv"

@st.cache_data
def carregar_dados():
    df = pd.read_csv(CSV_URL)
    df = df.dropna(how="all")
    return df

df = carregar_dados()

col_idade = "1 - Qual a sua idade?"
col_escolaridade = "4 - Qual a sua escolaridade:"
col_cachoeira = "2 - Reside em Cachoeira do sul ou se mudaria para a cidade:"
col_interesse_sust = "12 - Sobre o curso apresentado (Ciências Exatas e Sustentabilidade Tecnológica), você teria interesse em cursá-lo na UFSM-CS?"
col_nivel = "13 - Qual seu nível de interesse em fazer o curso apresentado?"
col_eng = "17 - Qual é o seu nível de interesse em um curso de Engenharia de Software?"

st.sidebar.header("Filtros")

idades = sorted(df[col_idade].dropna().astype(str).unique())
escolaridades = sorted(df[col_escolaridade].dropna().astype(str).unique())

filtro_idade = st.sidebar.multiselect("Idade", idades)
filtro_escolaridade = st.sidebar.multiselect("Escolaridade", escolaridades)

df_filtrado = df.copy()

if filtro_idade:
    df_filtrado = df_filtrado[df_filtrado[col_idade].astype(str).isin(filtro_idade)]

if filtro_escolaridade:
    df_filtrado = df_filtrado[df_filtrado[col_escolaridade].astype(str).isin(filtro_escolaridade)]

if df_filtrado.empty:
    st.warning("Nenhum dado encontrado com os filtros selecionados.")
    st.stop()

total = len(df_filtrado)
st.metric("Total de respostas", total)

def grafico_barra(coluna, titulo):
    dados = (
        df_filtrado[coluna]
        .dropna()
        .astype(str)
        .str.strip()
    )
    dados = dados[dados != ""]

    if dados.empty:
        st.info(f"Sem dados para {titulo}")
        return

    contagem = dados.value_counts().reset_index()
    contagem.columns = ["Categoria", "Quantidade"]

    fig = px.bar(
        contagem,
        x="Categoria",
        y="Quantidade",
        text="Quantidade",
        title=titulo
    )
    st.plotly_chart(fig, width="stretch")

def grafico_pizza(coluna, titulo):
    dados = (
        df_filtrado[coluna]
        .dropna()
        .astype(str)
        .str.strip()
    )
    dados = dados[dados != ""]

    if dados.empty:
        st.info(f"Sem dados para {titulo}")
        return

    contagem = dados.value_counts().reset_index()
    contagem.columns = ["Categoria", "Quantidade"]

    fig = px.pie(
        contagem,
        names="Categoria",
        values="Quantidade",
        title=titulo
    )
    fig.update_traces(
        textposition="inside",
        textinfo="percent",
        hovertemplate="%{label}: %{percent}<br>Quantidade: %{value}"
    )
    st.plotly_chart(fig, width="stretch")

grafico_barra(col_idade, "Idades")
grafico_pizza(col_escolaridade, "Escolaridade")
grafico_pizza(col_cachoeira, "Reside em Cachoeira do Sul?")
grafico_pizza(col_interesse_sust, "Interesse em Ciências Exatas e Sustentabilidade Tecnológica")
grafico_barra(col_nivel, "Nível de interesse no curso apresentado")
grafico_barra(col_eng, "Interesse em Engenharia de Software")

st.markdown("### Dados filtrados")
st.dataframe(df_filtrado, width="stretch")

csv = df_filtrado.to_csv(index=False).encode("utf-8")

st.download_button(
    label="Baixar dados filtrados",
    data=csv,
    file_name="dados_filtrados.csv",
    mime="text/csv"
)