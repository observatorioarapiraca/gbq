import pandas as pd
from google.cloud import bigquery
from google.oauth2 import service_account
import pandas_gbq
import streamlit as st
from datetime import datetime

credentials_info = st.secrets["GOOGLE_APPLICATION_CREDENTIALS_JSON"]
credentials = service_account.Credentials.from_service_account_info(
    credentials_info, scopes=["https://www.googleapis.com/auth/cloud-platform"])

client = bigquery.Client(credentials=credentials, project='prefeitura-437123')

st.set_page_config(page_title='CNPJ - Tabela', layout='wide')

@st.cache_data
def get_dataframe(query):
    return pandas_gbq.read_gbq(query, project_id='prefeitura-437123', credentials=credentials)

query = """SELECT * FROM `prefeitura-437123.tabelas.cnpj`"""

df_table = get_dataframe(query)

# select box anos
anos = df_table['data'].unique().tolist()
anos.sort()
anos = [datetime.strptime(data, '%m-%Y').strftime('%m-%Y') for data in anos]

# select box cbo
cnae = df_table['cnae'].unique().tolist()
cnae.sort()
cnae = ["Para filtrar por um CNAE específico, selecione aqui"] + cnae  # Adiciona a opção em branco no início
cnae_selecionado = st.selectbox("Selecione a Classificação Nacional das Atividades Econômicas (CNAE)", cnae, index=0)

# Criar o seletor de intervalo de datas usando os anos no formato 'mm-yyyy'
data_inicial, data_final = st.select_slider(
    "Selecione o Intervalo de Datas",
    options=anos,  # A lista de anos e meses no formato 'mm-yyyy'
    value=(anos[0], anos[-1])  # Valores padrão: primeiro e último da lista
)

# Converter datas selecionadas de volta para o formato 'm-y'
data_inicial = datetime.strptime(data_inicial, '%m-%Y').strftime('%m-%Y')
data_final = datetime.strptime(data_final, '%m-%Y').strftime('%m-%Y')

# DATAFRAME
estoque_inicial = df_table[df_table['data'] == data_inicial]

estoque_final = df_table[df_table['data'] == data_final][['cnae','quantidade_empresas']]

df_merged = pd.merge(estoque_inicial, estoque_final, on='cnae', how='outer')


if cnae_selecionado != 'Para filtrar por um CNAE específico, selecione aqui':
    df_merged = df_merged[df_merged['cnae'] == cnae_selecionado]

df_merged = df_merged.rename(
    columns={
        'quantidade_empresas_x': f'Estoque CNPJ Inicial - {data_inicial}',
        'quantidade_empresas_y': f'Estoque CNPJ Final - {data_final}',
        'cnae': 'CNAE'
    }
)
df_merged = df_merged.drop(columns='data').set_index('CNAE')
# sort values
df_merged = df_merged.sort_values(by=df_merged.columns[1], ascending=False)
df_merged['Variação Estoque de CNPJ'] = (((df_merged[df_merged.columns[1]] / df_merged[df_merged.columns[0]]) - 1) * 100).round(2)

st.write(f'<p style="font-size:25px;">Estoque de CNPJ por Classificação Nacional das Atividades Econômicas (CNAE) | {data_inicial} até {data_final} | Arapiraca</p>', unsafe_allow_html=True)

st.data_editor(
    data=df_merged,
    column_config=dict(
        **{
            'Variação Estoque de CNPJ': st.column_config.NumberColumn(
                'Variação Estoque de CNPJ', format='%.2f%%'
            )
        }
    ),
    hide_index=False, height=460
)

st.write('Você pode ordenar a tabela clicando no título da coluna desejada **🔼🔽**')
