import pandas as pd
from google.cloud import bigquery
from google.oauth2 import service_account
import pandas_gbq
import streamlit as st

credentials_info = st.secrets["GOOGLE_APPLICATION_CREDENTIALS_JSON"]
credentials = service_account.Credentials.from_service_account_info(
    credentials_info, scopes=["https://www.googleapis.com/auth/cloud-platform"])

client = bigquery.Client(credentials=credentials, project='prefeitura-437123')

ultimo_ano_rais = 2022 # ATUALIZAR SE FOR ADICIONADO NOVA RAIS

st.set_page_config(page_title='Guia Salarial - Tabela', layout='wide')
st.sidebar.markdown("### Fonte", help=f"""Até {ultimo_ano_rais}: RAIS.  
                                         Após {ultimo_ano_rais}: CAGED.""")

                                        
@st.cache_data
def get_dataframe(query):
    return pandas_gbq.read_gbq(query, project_id='prefeitura-437123', credentials=credentials)

query = """SELECT * FROM `prefeitura-437123.tabelas_salario.df_salarios`"""
df_salarios_ordenados = get_dataframe(query)

df_salarios_ordenados['mediana_salario'] = df_salarios_ordenados['mediana_salario'].round(2)
df_salarios_ordenados['media_salario'] = df_salarios_ordenados['media_salario'].round(2)

anos = [2020,2021,2022,2023,2024]

col0, col1, col2, col3 = st.columns([2,3.5,5,5])

with col0:
    select_ano = st.selectbox("Selecione o Ano", anos, index=0, key="select_ano")
with col1:
    select_sexo = st.selectbox("Selecione o Sexo", ['Homem', 'Mulher'], index=0, key="select_sexo")
with col2:
    select_quantidade = st.selectbox("Selecione a Quantidade Mínima de Empregados", [1, 5, 10, 20, 50], index=0, key="select_quantidade")

df_filtrado = df_salarios_ordenados[(df_salarios_ordenados['ano'] == st.session_state.select_ano) &
                            (df_salarios_ordenados['Sexo Trabalhador'] == st.session_state.select_sexo) &
                            (df_salarios_ordenados['quantidade'] >= st.session_state.select_quantidade) ]

df_filtrado = df_filtrado.rename(columns={'CBO Ocupação 2002':'Ocupação (CBO)',
                                          'ano':'Ano',
                                          'mediana_salario':'Salário Mediano',
                                          'media_salario':'Salário Médio',
                                          'quantidade': 'Quantidade'})     

df_filtrado = df_filtrado.sort_values(by='Salário Mediano', ascending=False).reset_index(drop=True)

st.write(f'<p style="font-size:25px;">Salário Mediano e Salário Médio por Ocupação (CBO) | Ano: {select_ano} | Arapiraca</p>', unsafe_allow_html=True)

df_style = df_filtrado.style.format(
    {"Salário Médio": lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
    "Salário Mediano": lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")})

st.dataframe(df_style, hide_index=True,
        column_config={"Ocupação (CBO)": st.column_config.Column(width="large")}, 
        width = 1200, height=460)

st.write('Você pode ordenar a tabela clicando no título da coluna desejada **🔼🔽**')
