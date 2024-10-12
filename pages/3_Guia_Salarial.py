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
col1, col2, col3, col4, col5, col6, col7 = st.columns([2,5,2.5,2.5,0.5,2.5,2.5])

# Colocar os selectboxes nas colunas
with col1:
    ano_selecionado = st.selectbox("Selecione o Ano", anos)

with col2:
    cbo_selecionado = st.selectbox("Selecione o CBO", cbos, index=0)

query_salarios = f"""
    SELECT 
        `Sexo Trabalhador`,
        APPROX_QUANTILES(`Vl Remun Média Nom`, 2)[OFFSET(1)] AS mediana_salario,
        AVG(`Vl Remun Média Nom`) AS media_salario
    FROM `prefeitura-437123.rais.vinculos`
    WHERE ano = {ano_selecionado}
"""
if cbo_selecionado != 'Todos':
    query_salarios += f" AND `CBO Ocupação 2002` = '{cbo_selecionado}'"

query_salarios += " GROUP BY `Sexo Trabalhador` ORDER BY `Sexo Trabalhador`"
df_salarios = pandas_gbq.read_gbq(query_salarios, project_id='prefeitura-437123', credentials=credentials)

with col3:
    st.metric(label="Salário Mediano - Homens", 
            value=f"R$ {df_salarios[df_salarios['Sexo Trabalhador'] == 'Masculino']['mediana_salario'].values[0]:.2f}".replace('.',','))

with col4:
    st.metric(label="Salário Médio - Homens", 
            value=f"R$ {df_salarios[df_salarios['Sexo Trabalhador'] == 'Masculino']['media_salario'].values[0]:.2f}".replace('.',','))
with col5:
    st.markdown("<div style='border-left: 2px solid #FFA500; height: 50px;'></div>", unsafe_allow_html=True)

with col6:
    st.metric(label="Salário Mediano - Mulheres", 
            value=f"R$ {df_salarios[df_salarios['Sexo Trabalhador'] == 'Feminino']['mediana_salario'].values[0]:.2f}".replace('.',','))

with col7:
    st.metric(label="Salário Médio - Mulheres", 
            value=f"R$ {df_salarios[df_salarios['Sexo Trabalhador'] == 'Feminino']['media_salario'].values[0]:.2f}".replace('.',','))

# Gráfico salário por faixa etária -----------
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

faixas_etarias_completas = query_lista("""
    SELECT DISTINCT `Faixa Etária` FROM `prefeitura-437123.rais.vinculos`
    ORDER BY `Faixa Etária` ASC
""")

df_salarios = pd.DataFrame({'Faixa Etária': faixas_etarias_completas}).merge(df_salarios, on='Faixa Etária', how='left').fillna(0)


# Formatar os valores do eixo y para exibição com R$ e vírgula
df_salarios['mediana_salario_formatted'] = df_salarios['mediana_salario'].apply(lambda x: f'R$ {x:.2f}'.replace('.', ','))

# Criar o gráfico
fig = px.bar(df_salarios, x='Faixa Etária', y='mediana_salario',
             title=f'Salário Mediano por Faixa Etária - Arapiraca - {ano_selecionado}  | CBO - {cbo_selecionado}',
             #labels={'Faixa Etária': 'Faixa Etária', 'mediana_salario': 'Mediana do Salário'},
             text='mediana_salario_formatted',
             color_discrete_sequence=['#003366']) 
fig.update_layout(
    title=dict(font=dict(size=20)),
    xaxis_title='',  # Título do eixo X
    yaxis_title='',   # Título do eixo Y
    yaxis_tickprefix='R$ ',
    height=350,
    xaxis=dict(tickfont=dict(size=16)),  
    yaxis=dict(tickfont=dict(size=16)),
)
fig.update_traces(hovertemplate='%{x}<br>' + 'Mediana: %{text}' + '<extra></extra>', # mostrar valores na barra quando passa o mouse nesse padrao 
    textfont=dict(size=16)) 

st.plotly_chart(fig)


#st.markdown("<hr style='border:2px solid gray'>", unsafe_allow_html=True)
# Gráfico salário por escolaridade -----------

query_salarios = f"""
    SELECT 
        `Escolaridade após 2005`,
        APPROX_QUANTILES(`Vl Remun Média Nom`, 2)[OFFSET(1)] AS mediana_salario
    FROM `prefeitura-437123.rais.vinculos`
    WHERE ano = {ano_selecionado}
"""

# Adicionar filtro de CBO se o usuário não tiver selecionado 'Todos'
if cbo_selecionado != 'Todos':
    query_salarios += f" AND `CBO Ocupação 2002` = '{cbo_selecionado}'"

# Agrupar os resultados por faixa etária
query_salarios += " GROUP BY `Escolaridade após 2005` ORDER BY `Escolaridade após 2005`"

# Executar a query e carregar os resultados em um DataFrame
df_salarios = pandas_gbq.read_gbq(query_salarios, project_id='prefeitura-437123', credentials=credentials)

faixas_etarias_completas = ['Analfabeto', 'Até 5ª Incompleto', '5ª Completo Fundamental', '6ª a 9ª Fundamental', 'Fundamental Completo', 
                            'Médio Incompleto', 'Médio Completo', 'Superior Incompleto', 'Superior Completo', 'Mestrado', 'Doutorado']

df_salarios = pd.DataFrame({'Escolaridade após 2005': faixas_etarias_completas}).merge(df_salarios, on='Escolaridade após 2005', how='left').fillna(0)

# Formatar os valores do eixo y para exibição com R$ e vírgula
df_salarios['mediana_salario_formatted'] = df_salarios['mediana_salario'].apply(lambda x: f'R$ {x:.2f}'.replace('.', ','))

# Criar o gráfico
fig = px.bar(df_salarios, x='Escolaridade após 2005', y='mediana_salario',
             title=f'Salário Mediano por Escolaridade - Arapiraca - {ano_selecionado} | CBO - {cbo_selecionado}',
             #labels={'Faixa Etária': 'Faixa Etária', 'mediana_salario': 'Mediana do Salário'},
             text='mediana_salario_formatted',
             color_discrete_sequence=['#003366']) 
fig.update_layout(
    title=dict(font=dict(size=20)),
    xaxis_title='',  # Título do eixo X
    yaxis_title='',   # Título do eixo Y
    yaxis_tickprefix='R$ ',
    height=350,
    xaxis_tickangle=-15,
    xaxis=dict(tickfont=dict(size=16)),  
    yaxis=dict(tickfont=dict(size=16)),
)
fig.update_traces(hovertemplate='%{x}<br>' + 'Mediana: %{text}' + '<extra></extra>', # mostrar valores na barra quando passa o mouse nesse padrao 
    textfont=dict(size=16)) 

st.plotly_chart(fig)
