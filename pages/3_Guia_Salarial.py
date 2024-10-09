import pandas as pd
from google.cloud import bigquery
from google.oauth2 import service_account
import pandas_gbq
import streamlit as st
import re
import plotly.express as px

credentials_info = st.secrets["GOOGLE_APPLICATION_CREDENTIALS_JSON"]
credentials = service_account.Credentials.from_service_account_info(
    credentials_info, scopes=["https://www.googleapis.com/auth/cloud-platform"])

client = bigquery.Client(credentials=credentials, project='prefeitura-437123')

def query_lista(query):
    query_job = client.query(query)
    results = query_job.result()
    return [row[0] for row in results]

anos = query_lista("""
    SELECT DISTINCT ano FROM `prefeitura-437123.rais.vinculos` 
    ORDER BY ano DESC
""")
cbos = query_lista("""
    SELECT DISTINCT `CBO Ocupação 2002` FROM `prefeitura-437123.rais.vinculos`
    ORDER BY `CBO Ocupação 2002` ASC
""")
# Filtrar os CBOs para incluir apenas os que têm descrição
cbos = [cbo for cbo in cbos if re.search('[A-Za-z]', cbo)]
cbos.insert(0, 'Todos')

st.set_page_config(page_title='Guia Salarial RAIS - Arapiraca', layout='wide')

# Criar colunas para os selectboxes ficarem lado a lado
col1, col2 = st.columns(2)

# Colocar os selectboxes nas colunas
with col1:
    ano_selecionado = st.selectbox("Selecione o Ano", anos)

with col2:
    cbo_selecionado = st.selectbox("Selecione o CBO", cbos, index=0)

query_salarios = f"""
    SELECT 
        `Faixa Etária`,
        APPROX_QUANTILES(`Vl Remun Média Nom`, 2)[OFFSET(1)] AS mediana_salario
    FROM `prefeitura-437123.rais.vinculos`
    WHERE ano = {ano_selecionado}
"""

# Adicionar filtro de CBO se o usuário não tiver selecionado 'Todos'
if cbo_selecionado != 'Todos':
    query_salarios += f" AND `CBO Ocupação 2002` = '{cbo_selecionado}'"

# Agrupar os resultados por faixa etária
query_salarios += " GROUP BY `Faixa Etária` ORDER BY `Faixa Etária`"

# Executar a query e carregar os resultados em um DataFrame
df_salarios = pandas_gbq.read_gbq(query_salarios, project_id='prefeitura-437123', credentials=credentials)

# Formatar os valores do eixo y para exibição com R$ e vírgula
df_salarios['mediana_salario_formatted'] = df_salarios['mediana_salario'].apply(lambda x: f'R$ {x:,.2f}'.replace('.', ','))

# Criar o gráfico
fig = px.bar(df_salarios, x='Faixa Etária', y='mediana_salario',
             title=f'Mediana de Salários por Faixa Etária - Arapiraca - {ano_selecionado}',
             #labels={'Faixa Etária': 'Faixa Etária', 'mediana_salario': 'Mediana do Salário'},
             text='mediana_salario_formatted',) 
fig.update_layout(
    xaxis_title='',  # Título do eixo X
    yaxis_title='Mediana do Salário',   # Título do eixo Y
    yaxis_tickprefix='R$ '
)
fig.update_traces(hovertemplate='%{x}<br>' + 'Mediana: %{text}' + '<extra></extra>') # mostrar valores na barra quando passa o mouse nesse padrao 

st.plotly_chart(fig)
