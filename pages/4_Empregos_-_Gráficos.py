import pandas as pd
from google.cloud import bigquery
from google.oauth2 import service_account
import pandas_gbq
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go


credentials_info = st.secrets["GOOGLE_APPLICATION_CREDENTIALS_JSON"]

# Passo 2: Criar um objeto de credenciais a partir das variáveis de ambiente
credentials = service_account.Credentials.from_service_account_info(
    credentials_info, scopes=["https://www.googleapis.com/auth/cloud-platform"]
)

client = bigquery.Client(credentials = credentials, project = 'prefeitura-437123')

st.set_page_config(page_title='Estoque e Saldo de Emprego', layout='wide')
st.sidebar.markdown("### Metodologia", help="""Foram considerados os vínculos ativos da RAIS de 2020 como estoque inicial.
A partir desse ponto, o estoque foi atualizado mensalmente pela soma do saldo de empregos do CAGED de cada mês, resultando em 
um cálculo acumulado do estoque de empregos ao longo do tempo.""")


def query_lista(query):
    query_job = client.query(query)
    results = query_job.result()
    return [row[0] for row in results]

# Obter e cachear os CBOs
@st.cache_data
def get_cbos():
    cbos = query_lista("""
        SELECT DISTINCT cbo FROM `prefeitura-437123.rais.estoque`
        ORDER BY cbo ASC
    """)
    # Filtrar CBOs válidos e adicionar a opção 'Todos'
    #cbos = [cbo for cbo in cbos if re.search('[A-Za-z]', cbo)]
    cbos.insert(0, 'Todos')
    return cbos

cbos = get_cbos()
cbo_selecionado = st.selectbox("Selecione a Ocupação (CBO)", cbos, index=0)


# SEGUNDA QUERY POR CBO

@st.cache_data
def get_grafico_dataframe(query):
    return pandas_gbq.read_gbq(query, project_id='prefeitura-437123', credentials=credentials)

query = """SELECT * FROM `prefeitura-437123.tabelas.estoque_soma_acumulada_cbo`"""
df_grafico = get_grafico_dataframe(query)


df_grafico_cbo = df_grafico[df_grafico['cbo'] == cbo_selecionado].reset_index(drop=True)



df_grafico_cbo = df_grafico_cbo.groupby(['competênciamov']).sum()[['saldo', 'estoque_acumulado']]

df_grafico_cbo.index = pd.to_datetime(df_grafico_cbo.index, format='%Y-%m')
date_range = pd.date_range(start=df_grafico['competênciamov'].min(), end=df_grafico['competênciamov'].max(), freq='MS')  
df_grafico_cbo = df_grafico_cbo.reindex(date_range)
df_grafico_cbo['saldo'] = df_grafico_cbo['saldo'].fillna(0)
df_grafico_cbo['estoque_acumulado'] = df_grafico_cbo['estoque_acumulado'].fillna(method='ffill')
# regra para pegar o ultimo valor nao nan e preencher a coluna estoque, util para quando os primeiros meses nao tem saldo e o estoque seria 0 
first_valid_value = df_grafico_cbo['estoque_acumulado'].iloc[0]
if pd.isnull(first_valid_value):
    # Se o primeiro valor for NaN, pegue o primeiro valor não nulo na coluna
    first_valid_value = df_grafico_cbo['estoque_acumulado'].bfill().iloc[0] if not df_grafico_cbo['estoque_acumulado'].bfill().empty else None
    # Preencher todos os NaNs com esse valor, se existir
    if first_valid_value is not None:
        df_grafico_cbo['estoque_acumulado'].fillna(first_valid_value, inplace=True)
df_grafico_cbo.index = df_grafico_cbo.index.strftime('%m-%Y')


# grafico

fig1 = go.Figure()
fig1.add_trace(go.Bar(x=df_grafico_cbo.index, y=df_grafico_cbo['saldo'], text=df_grafico_cbo['saldo'], marker_color='#003366'))
fig1.update_layout(title=f'Saldo de Emprego | CBO {cbo_selecionado}')
fig1.update_layout(
    title=dict(font=dict(size=20)),
    xaxis_title='',  # Título do eixo X
    yaxis_title='',   # Título do eixo Y
    yaxis_tickprefix='',
    height=350,
    xaxis=dict(tickfont=dict(size=16)),  # Aumentar tamanho do texto do eixo X
    yaxis=dict(tickfont=dict(size=16)),
)

# Gráfico para Estoque Acumulado
fig2 = go.Figure()
fig2.add_trace(go.Scatter(x=df_grafico_cbo.index, y=df_grafico_cbo['estoque_acumulado'], mode='lines'))
fig2.update_layout(title=f'Estoque de Emprego Acumulado | CBO {cbo_selecionado}')
fig2.update_layout(
    title=dict(font=dict(size=20)),
    xaxis_title='',  # Título do eixo X
    yaxis_title='',   # Título do eixo Y
    yaxis_tickprefix='',
    height=350,
    xaxis=dict(tickfont=dict(size=16)),  # Aumentar tamanho do texto do eixo X
    yaxis=dict(tickfont=dict(size=16)),
)


# Exibir o gráfico
st.plotly_chart(fig1)

st.plotly_chart(fig2)


