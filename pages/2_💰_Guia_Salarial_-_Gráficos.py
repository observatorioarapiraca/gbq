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

ultimo_ano_rais = 2022 # ATUALIZAR SE FOR ADICIONADO NOVA RAIS

st.set_page_config(page_title='Guia Salarial', layout='wide')
st.sidebar.markdown("### Fonte", help=f"""Até {ultimo_ano_rais}: RAIS.  
                                         Após {ultimo_ano_rais}: CAGED.""")

anos = [2020,2021,2022,2023,2024] # adicionar novo ano só quando tiver mt informação do caged


@st.cache_data
def get_dataframe(query):
    return pandas_gbq.read_gbq(query, project_id='prefeitura-437123', credentials=credentials)

# sexo
query = """SELECT * FROM `prefeitura-437123.tabelas_salario.sexo`"""
df_sexo = get_dataframe(query)
# faixa etaria
query = """SELECT * FROM `prefeitura-437123.tabelas_salario.faixa_etaria`"""
df_faixa_etaria = get_dataframe(query)
# escolaridade
query = """SELECT * FROM `prefeitura-437123.tabelas_salario.escolaridade`"""
df_escolaridade = get_dataframe(query)


# Criar colunas para os selectboxes ficarem lado a lado
col0, col1, col2, col3, col5, col6 = st.columns([2,3.5,5,2.5,0.5,2.5])

# Colocar os selectboxes nas colunas
with col0:
    ano_selecionado = st.selectbox("Selecione o Ano", anos)

with col1:
    horas_trabalhadas = ['Até 12 horas', '13 a 20 horas', '21 a 30 horas', '31 a 39 horas', '40 horas ou mais']
    horas_trabalhadas_selecionado = st.selectbox("Selecione a Quantidade de Horas Contratuais", horas_trabalhadas, index=horas_trabalhadas.index("40 horas ou mais"))

with col2:
    # uso o df_sexo p pegar os unique de CBO
    cbos = df_sexo['CBO Ocupação 2002'].unique().tolist()
    cbos.sort()
    cbo_selecionado = st.selectbox("Selecione a Ocupação (CBO)", cbos, index=cbos.index("Todos"))

# filtrando pelos valores do selectbox
df_sexo_filtrado = df_sexo[(df_sexo['ano'] == ano_selecionado) & 
                           (df_sexo['CBO Ocupação 2002'] == cbo_selecionado) &
                           (df_sexo['classe_horas_trabalhadas'] == horas_trabalhadas_selecionado)].reset_index(drop=True)

df_faixa_etaria_filtrado = df_faixa_etaria[(df_faixa_etaria['ano'] == ano_selecionado) & 
                                           (df_faixa_etaria['CBO Ocupação 2002'] == cbo_selecionado) & 
                                           (df_faixa_etaria['classe_horas_trabalhadas'] == horas_trabalhadas_selecionado)].reset_index(drop=True)

df_escolaridade_filtrado = df_escolaridade[(df_escolaridade['ano'] == ano_selecionado) & 
                                           (df_escolaridade['CBO Ocupação 2002'] == cbo_selecionado) &
                                           (df_escolaridade['classe_horas_trabalhadas'] == horas_trabalhadas_selecionado)].reset_index(drop=True)


with col3:
    try:
        st.metric(label="Salário Mediano - Homens", 
                value=f"R$ {df_sexo_filtrado[df_sexo_filtrado['Sexo Trabalhador'] == 'Homem']['mediana_salario'].values[0]:.2f}".replace('.',','))
    except:
        st.metric(label="Salário Mediano - Homens", 
                value=f"Sem Dados")
#with col4:
#    try:
#        st.metric(label="Salário Médio - Homens", 
#                value=f"R$ {df_sexo_filtrado[df_sexo_filtrado['Sexo Trabalhador'] == 'Homem']['media_salario'].values[0]:.2f}".replace('.',','))
#    except:
#        st.metric(label="Salário Médio - Homens", 
#                value=f"Sem Dados")
with col5:
    st.markdown("<div style='border-left: 2px solid #FFA500; height: 50px;'></div>", unsafe_allow_html=True)

with col6:
    try:
        st.metric(label="Salário Mediano - Mulheres", 
                value=f"R$ {df_sexo_filtrado[df_sexo_filtrado['Sexo Trabalhador'] == 'Mulher']['mediana_salario'].values[0]:.2f}".replace('.',','))
    except:
        st.metric(label="Salário Mediano - Mulheres", 
                value=f"Sem Dados")

#with col7:
#    try:
#        st.metric(label="Salário Médio - Mulheres", 
#                value=f"R$ {df_sexo_filtrado[df_sexo_filtrado['Sexo Trabalhador'] == 'Mulher']['media_salario'].values[0]:.2f}".replace('.',','))
#    except:
#        st.metric(label="Salário Médio - Mulheres", 
#                value=f"Sem Dados")

# gráfico faixa etária ---------------
faixas_etarias_completas = df_faixa_etaria['Faixa Etária'].unique()[:-1] # tem um none na faixa etária, remove ele
faixas_etarias_completas.sort()

df_salarios = pd.DataFrame({'Faixa Etária': faixas_etarias_completas}).merge(df_faixa_etaria_filtrado, on='Faixa Etária', how='left').fillna(0)

# Formatar os valores do eixo y para exibição com R$ e vírgula
df_salarios['mediana_salario_formatted'] = df_salarios['mediana_salario'].apply(lambda x: f'R$ {x:.2f}'.replace('.', ','))
df_salarios['media_salario_formatted'] = df_salarios['media_salario'].apply(lambda x: f'R$ {x:.2f}'.replace('.', ','))

# Criar o gráfico
fig = px.bar(df_salarios, x='Faixa Etária', y='mediana_salario',
            title=f'Salário Mediano por Faixa Etária - Arapiraca - {ano_selecionado}  | CBO - {cbo_selecionado} | Horas Contratuais - {horas_trabalhadas_selecionado}',
            #labels={'Faixa Etária': 'Faixa Etária', 'mediana_salario': 'Mediana do Salário'},
            text='mediana_salario_formatted',
            color_discrete_sequence=['#003366']) 
fig.update_layout(
    title=dict(font=dict(size=20)),
    xaxis_title='',  # Título do eixo X
    yaxis_title='',   # Título do eixo Y
    yaxis_tickprefix='R$ ',
    height=330,
    xaxis=dict(tickfont=dict(size=16)),  # Aumentar tamanho do texto do eixo X
    yaxis=dict(tickfont=dict(size=16)),
)
fig.update_traces(
    hovertemplate='%{x}<br>' + 
                  'Mediana: %{text}<br>' +  # Mostrar o valor da mediana (já formatado)
                  'Média: %{customdata[0]}<br>' +  # Valor da média
                  'Com Base em %{customdata[1]} Salários' +  # Valor da quantidade
                  '<extra></extra>', 
    textfont=dict(size=16),
    customdata=df_salarios[['media_salario_formatted', 'quantidade']])

st.plotly_chart(fig)

#st.markdown("<hr style='border:2px solid gray'>", unsafe_allow_html=True)


# Gráfico salário por escolaridade -----------
faixas_etarias_completas = ['Analfabeto', 'Até 5ª Incompleto', '5ª Completo Fundamental', '6ª a 9ª Fundamental', 'Fundamental Completo', 
                            'Médio Incompleto', 'Médio Completo', 'Superior Incompleto', 'Superior Completo', 'Mestrado', 'Doutorado']

df_salarios = pd.DataFrame({'Escolaridade após 2005': faixas_etarias_completas}).merge(df_escolaridade_filtrado, on='Escolaridade após 2005', how='left').fillna(0)

# Formatar os valores do eixo y para exibição com R$ e vírgula
df_salarios['mediana_salario_formatted'] = df_salarios['mediana_salario'].apply(lambda x: f'R$ {x:.2f}'.replace('.', ','))
df_salarios['media_salario_formatted'] = df_salarios['media_salario'].apply(lambda x: f'R$ {x:.2f}'.replace('.', ','))

# Criar o gráfico
fig = px.bar(df_salarios, x='Escolaridade após 2005', y='mediana_salario',
            title=f'Salário Mediano por Escolaridade - Arapiraca - {ano_selecionado} | CBO - {cbo_selecionado} | Horas Contratuais - {horas_trabalhadas_selecionado}',
            #labels={'Faixa Etária': 'Faixa Etária', 'mediana_salario': 'Mediana do Salário'},
            text='mediana_salario_formatted',
            color_discrete_sequence=['#003366']) 
fig.update_layout(
    title=dict(font=dict(size=20)),
    xaxis_title='',  # Título do eixo X
    yaxis_title='',   # Título do eixo Y
    yaxis_tickprefix='R$ ',
    height=330,
    xaxis_tickangle=-15,
    xaxis=dict(tickfont=dict(size=16)),  # Aumentar tamanho do texto do eixo X
    yaxis=dict(tickfont=dict(size=16)),
)
fig.update_traces(
    hovertemplate='%{x}<br>' + 
                  'Mediana: %{text}<br>' +  # Mostrar o valor da mediana (já formatado)
                  'Média: %{customdata[0]}<br>' +  # Valor da média
                  'Com Base em %{customdata[1]} Salários' +  # Valor da quantidade
                  '<extra></extra>', 
    textfont=dict(size=16),
    customdata=df_salarios[['media_salario_formatted', 'quantidade']])

st.plotly_chart(fig)
