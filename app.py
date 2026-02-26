import pandas as pd
import plotly.express as px
import streamlit as st

# =========================================================
# CONFIGURAÇÃO
# =========================================================
st.set_page_config(page_title="Dashboard UFSM-CS", layout="wide")
st.title("Dashboard Inteligente - Pesquisa de Cursos")

CSV_URL = "https://raw.githubusercontent.com/luanportella/Questionarios/main/raw_data.csv"


# =========================================================
# CARREGAR DADOS
# =========================================================
@st.cache_data
def carregar_dados():
    df = pd.read_csv(CSV_URL)
    df = df.dropna(how="all")
    return df


df = carregar_dados()


# =========================================================
# NOMES DAS COLUNAS
# =========================================================
col_idade = "1 - Qual a sua idade?"
col_cachoeira = "2 - Reside em Cachoeira do sul ou se mudaria para a cidade:"
col_cidade = "3 - Se não reside em Cachoeira do Sul, mora em qual cidade?"
col_escolaridade = "4 - Qual a sua escolaridade:"
col_formacao = "5 - Se possuí formação superior, qual o nível:"
col_trabalho = "6 - Se você trabalha, qual a sua área de atuação:"
col_UFSM = "7 - Seria a sua primeira vez estudando na UFSM-CS:"
col_curso_UFSM = "8 - Qual curso está cursando na UFSM-CS?"
col_tempo = "9 - Em quanto tempo pretende iniciar uma graduação?"
col_exatas = (
    "10 - Teria interesse em cursos da área de Exatas (como Matemática, Física, Química, Engenharia, entre outros)? "
    "Essa área abrange cursos voltados para o raciocínio lógico, cálculo, experimentação e tecnologia, podendo ter foco em pesquisa, "
    "indústria ou ensino (Licenciatura)."
)
col_dificuldade = "11 - Na sua opinião, qual a maior dificuldade para iniciar ou concluir uma graduação:"
col_interesse_sust = "12 - Sobre o curso apresentado (Ciências Exatas e Sustentabilidade Tecnológica), você teria interesse em cursá-lo na UFSM-CS?"
col_nivel = "13 - Qual seu nível de interesse em fazer o curso apresentado?"
col_turno = "14 - Qual turno seria mais adequado para você fazer o curso?"
col_fatores = "15 - Quais fatores te influenciam na escolha do curso? (marque até 2)"
col_trab_estudo = "16 - Você estaria disposto a fazer o curso mesmo se precisasse trabalhar e estudar ao mesmo tempo?"
col_eng = "17 - Qual é o seu nível de interesse em um curso de Engenharia de Software?"
col_outros = "18 -  Se não tem interesse em nenhum desses cursos, teria interesse em algum outro:"
col_ofertados = "19 - Em qual dos cursos ofertados pela UFSM-CS você tem interesse?"
col_nao_ofertados = "20 - Em qual curso,  não ofertado pela UFSM-CS ,  você tem interesse?"
col_conhece = "24 - Você conhece alguém que teria interesse em fazer alguns dos cursos apresentados?"
col_id = "Identificação"

todas_colunas = [
    col_idade,
    col_cachoeira,
    col_cidade,
    col_escolaridade,
    col_formacao,
    col_trabalho,
    col_UFSM,
    col_curso_UFSM,
    col_tempo,
    col_exatas,
    col_dificuldade,
    col_interesse_sust,
    col_nivel,
    col_turno,
    col_fatores,
    col_trab_estudo,
    col_eng,
    col_outros,
    col_ofertados,
    col_nao_ofertados,
    col_conhece,
    col_id,
]

faltantes = [c for c in todas_colunas if c not in df.columns]
if faltantes:
    st.error("As seguintes colunas não foram encontradas no arquivo CSV:")
    for c in faltantes:
        st.write(f"- {c}")
    st.stop()


# =========================================================
# FUNÇÕES AUXILIARES
# =========================================================
def limpar_serie(serie: pd.Series) -> pd.Series:
    s = serie.dropna().astype(str).str.strip()
    s = s[s != ""]
    return s


def opcoes_filtro(serie: pd.Series):
    s = limpar_serie(serie)
    return sorted(s.unique().tolist())


def aplicar_filtro(df_base: pd.DataFrame, coluna: str, valores: list):
    if valores:
        s = df_base[coluna].astype(str).str.strip()
        return df_base[s.isin(valores)]
    return df_base


def contagem_respostas(df_base: pd.DataFrame, coluna: str) -> pd.DataFrame:
    s = limpar_serie(df_base[coluna])
    if s.empty:
        return pd.DataFrame(columns=["Categoria", "Quantidade"])
    out = s.value_counts().reset_index()
    out.columns = ["Categoria", "Quantidade"]
    return out


def grafico_barra(df_base: pd.DataFrame, coluna: str, titulo: str):
    dados = contagem_respostas(df_base, coluna)
    if dados.empty:
        st.info(f"Sem dados para: {titulo}")
        return

    fig = px.bar(
        dados,
        x="Categoria",
        y="Quantidade",
        text="Quantidade",
        title=titulo,
    )
    fig.update_layout(xaxis_title="", yaxis_title="Quantidade")
    st.plotly_chart(fig, width="stretch")


def grafico_pizza(df_base: pd.DataFrame, coluna: str, titulo: str):
    dados = contagem_respostas(df_base, coluna)
    if dados.empty:
        st.info(f"Sem dados para: {titulo}")
        return

    fig = px.pie(
        dados,
        names="Categoria",
        values="Quantidade",
        title=titulo,
    )
    fig.update_traces(
        textposition="inside",
        textinfo="percent",
        hovertemplate="%{label}: %{percent}<br>Quantidade: %{value}",
    )
    st.plotly_chart(fig, width="stretch")


def heatmap_crosstab(df_base: pd.DataFrame, col_linha: str, col_coluna: str, titulo: str):
    base = df_base[[col_linha, col_coluna]].copy()
    base[col_linha] = base[col_linha].astype(str).str.strip()
    base[col_coluna] = base[col_coluna].astype(str).str.strip()
    base = base.dropna()
    base = base[(base[col_linha] != "") & (base[col_coluna] != "")]

    if base.empty:
        st.info(f"Sem dados para: {titulo}")
        return

    cruz = pd.crosstab(base[col_linha], base[col_coluna])
    if cruz.empty:
        st.info(f"Sem dados para: {titulo}")
        return

    fig = px.imshow(cruz, text_auto=True, title=titulo)
    fig.update_traces(hovertemplate="%{x} | %{y}<br>Quantidade: %{z}")
    st.plotly_chart(fig, width="stretch")


def valor_predominante(df_base: pd.DataFrame, coluna: str):
    s = limpar_serie(df_base[coluna])
    if s.empty:
        return "N/A"
    return s.value_counts().idxmax()


# =========================================================
# FILTROS
# =========================================================
st.sidebar.header("Filtros")

df_filtrado = df.copy()

f_idade = st.sidebar.multiselect("Idade", opcoes_filtro(df[col_idade]))
f_cachoeira = st.sidebar.multiselect("Reside em Cachoeira do Sul?", opcoes_filtro(df[col_cachoeira]))
f_cidade = st.sidebar.multiselect("Cidade", opcoes_filtro(df[col_cidade]))
f_escolaridade = st.sidebar.multiselect("Escolaridade", opcoes_filtro(df[col_escolaridade]))
f_formacao = st.sidebar.multiselect("Formação superior", opcoes_filtro(df[col_formacao]))
f_trabalho = st.sidebar.multiselect("Área de trabalho", opcoes_filtro(df[col_trabalho]))
f_ufsm = st.sidebar.multiselect("Primeira vez na UFSM-CS?", opcoes_filtro(df[col_UFSM]))
f_curso_ufsm = st.sidebar.multiselect("Curso que está cursando na UFSM-CS", opcoes_filtro(df[col_curso_UFSM]))
f_tempo = st.sidebar.multiselect("Tempo para iniciar graduação", opcoes_filtro(df[col_tempo]))
f_exatas = st.sidebar.multiselect("Interesse em Exatas", opcoes_filtro(df[col_exatas]))
f_dificuldade = st.sidebar.multiselect("Maior dificuldade", opcoes_filtro(df[col_dificuldade]))
f_sust = st.sidebar.multiselect("Interesse em Ciências Exatas e Sustentabilidade Tecnológica", opcoes_filtro(df[col_interesse_sust]))
f_nivel = st.sidebar.multiselect("Nível de interesse no curso apresentado", opcoes_filtro(df[col_nivel]))
f_turno = st.sidebar.multiselect("Turno", opcoes_filtro(df[col_turno]))
f_fatores = st.sidebar.multiselect("Fatores de escolha", opcoes_filtro(df[col_fatores]))
f_trab_estudo = st.sidebar.multiselect("Trabalho + estudo", opcoes_filtro(df[col_trab_estudo]))
f_eng = st.sidebar.multiselect("Interesse em Engenharia de Software", opcoes_filtro(df[col_eng]))
f_outros = st.sidebar.multiselect("Outros cursos", opcoes_filtro(df[col_outros]))
f_ofertados = st.sidebar.multiselect("Cursos ofertados pela UFSM-CS", opcoes_filtro(df[col_ofertados]))
f_nao_ofertados = st.sidebar.multiselect("Cursos não ofertados pela UFSM-CS", opcoes_filtro(df[col_nao_ofertados]))
f_conhece = st.sidebar.multiselect("Conhece alguém interessado?", opcoes_filtro(df[col_conhece]))
f_id = st.sidebar.multiselect("Fonte", opcoes_filtro(df[col_id]))

df_filtrado = aplicar_filtro(df_filtrado, col_idade, f_idade)
df_filtrado = aplicar_filtro(df_filtrado, col_cachoeira, f_cachoeira)
df_filtrado = aplicar_filtro(df_filtrado, col_cidade, f_cidade)
df_filtrado = aplicar_filtro(df_filtrado, col_escolaridade, f_escolaridade)
df_filtrado = aplicar_filtro(df_filtrado, col_formacao, f_formacao)
df_filtrado = aplicar_filtro(df_filtrado, col_trabalho, f_trabalho)
df_filtrado = aplicar_filtro(df_filtrado, col_UFSM, f_ufsm)
df_filtrado = aplicar_filtro(df_filtrado, col_curso_UFSM, f_curso_ufsm)
df_filtrado = aplicar_filtro(df_filtrado, col_tempo, f_tempo)
df_filtrado = aplicar_filtro(df_filtrado, col_exatas, f_exatas)
df_filtrado = aplicar_filtro(df_filtrado, col_dificuldade, f_dificuldade)
df_filtrado = aplicar_filtro(df_filtrado, col_interesse_sust, f_sust)
df_filtrado = aplicar_filtro(df_filtrado, col_nivel, f_nivel)
df_filtrado = aplicar_filtro(df_filtrado, col_turno, f_turno)
df_filtrado = aplicar_filtro(df_filtrado, col_fatores, f_fatores)
df_filtrado = aplicar_filtro(df_filtrado, col_trab_estudo, f_trab_estudo)
df_filtrado = aplicar_filtro(df_filtrado, col_eng, f_eng)
df_filtrado = aplicar_filtro(df_filtrado, col_outros, f_outros)
df_filtrado = aplicar_filtro(df_filtrado, col_ofertados, f_ofertados)
df_filtrado = aplicar_filtro(df_filtrado, col_nao_ofertados, f_nao_ofertados)
df_filtrado = aplicar_filtro(df_filtrado, col_conhece, f_conhece)
df_filtrado = aplicar_filtro(df_filtrado, col_id, f_id)

if df_filtrado.empty:
    st.warning("Nenhum dado encontrado com os filtros selecionados.")
    st.stop()


# =========================================================
# KPIs
# =========================================================
total = len(df_filtrado)
idade_pred = valor_predominante(df_filtrado, col_idade)
esc_pred = valor_predominante(df_filtrado, col_escolaridade)

interesse_counts = limpar_serie(df_filtrado[col_nivel]).value_counts()
mapa_nivel = {
    "1 – Não tenho interesse": "Nenhum",
    "2 – Tenho pouco interesse": "Pouco",
    "3 – Interesse moderado": "Moderado",
    "4 – Tenho interesse": "Normal",
    "5 – Tenho muito interesse": "Muito",
}
if not interesse_counts.empty:
    nivel_original = interesse_counts.idxmax()
    nivel_top = mapa_nivel.get(nivel_original, nivel_original)
    percentual = (interesse_counts.max() / total) * 100
else:
    nivel_top = "N/A"
    percentual = 0.0

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total de respostas", total)
c2.metric("Idade predominante", idade_pred)
c3.metric("Escolaridade predominante", esc_pred)
c4.metric("Interesse predominante", f"{nivel_top} ({percentual:.1f}%)")

st.markdown("---")


# =========================================================
# ABAS
# =========================================================
aba1, aba2, aba3, aba4, aba5, aba6 = st.tabs([
    "Perfil",
    "UFSM e Graduação",
    "Curso 1",
    "Curso 2",
    "Outros Cursos",
    "Cruzamentos e Dados",
])

with aba1:
    grafico_barra(df_filtrado, col_idade, "Idade")
    grafico_pizza(df_filtrado, col_cachoeira, "Reside em Cachoeira do Sul ou se mudaria para a cidade")
    grafico_barra(df_filtrado, col_cidade, "Cidade")
    grafico_pizza(df_filtrado, col_escolaridade, "Escolaridade")
    grafico_barra(df_filtrado, col_formacao, "Nível de formação superior")
    grafico_barra(df_filtrado, col_trabalho, "Área de atuação profissional")

with aba2:
    grafico_pizza(df_filtrado, col_UFSM, "Primeira vez estudando na UFSM-CS")
    grafico_barra(df_filtrado, col_curso_UFSM, "Curso que está cursando na UFSM-CS")
    grafico_barra(df_filtrado, col_tempo, "Tempo para iniciar uma graduação")
    grafico_pizza(df_filtrado, col_exatas, "Interesse em cursos da área de Exatas")
    grafico_barra(df_filtrado, col_dificuldade, "Maior dificuldade para iniciar ou concluir uma graduação")

with aba3:
    grafico_pizza(df_filtrado, col_interesse_sust, "Interesse em Ciências Exatas e Sustentabilidade Tecnológica")
    grafico_barra(df_filtrado, col_nivel, "Nível de interesse no curso apresentado")
    grafico_barra(df_filtrado, col_turno, "Turno mais adequado para cursar")
    grafico_barra(df_filtrado, col_fatores, "Fatores que influenciam a escolha do curso")
    grafico_pizza(df_filtrado, col_trab_estudo, "Faria o curso se precisasse trabalhar e estudar ao mesmo tempo")

with aba4:
    grafico_barra(df_filtrado, col_eng, "Interesse em Engenharia de Software")
    heatmap_crosstab(df_filtrado, col_idade, col_eng, "Idade x Interesse em Engenharia de Software")

with aba5:
    grafico_barra(df_filtrado, col_outros, "Interesse em outros cursos")
    grafico_barra(df_filtrado, col_ofertados, "Interesse nos cursos ofertados pela UFSM-CS")
    grafico_barra(df_filtrado, col_nao_ofertados, "Interesse em cursos não ofertados pela UFSM-CS")
    grafico_pizza(df_filtrado, col_conhece, "Conhece alguém que teria interesse nos cursos apresentados")
    grafico_barra(df_filtrado, col_id, "Fonte / identificação")

with aba6:
    heatmap_crosstab(
        df_filtrado,
        col_idade,
        col_interesse_sust,
        "Idade x Interesse em Ciências Exatas e Sustentabilidade Tecnológica",
    )

    st.markdown("### Dados filtrados")
    st.dataframe(df_filtrado, width="stretch")

    csv = df_filtrado.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="Baixar dados filtrados",
        data=csv,
        file_name="dados_filtrados.csv",
        mime="text/csv",
    )