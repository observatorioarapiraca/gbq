import pandas as pd
from google.cloud import bigquery
from google.oauth2 import service_account
import pandas_gbq
import streamlit as st
import numpy as np
from datetime import datetime

# Passo 1: Acessar as credenciais do arquivo secrets.toml
credentials_info = st.secrets["GOOGLE_APPLICATION_CREDENTIALS_JSON"]

# Passo 2: Criar um objeto de credenciais a partir das variáveis de ambiente
credentials = service_account.Credentials.from_service_account_info(
    credentials_info, scopes=["https://www.googleapis.com/auth/cloud-platform"]
)

client = bigquery.Client(credentials = credentials, project = 'prefeitura-437123')

st.set_page_config(page_title='Estoque e Saldo de Emprego', layout='wide')
st.sidebar.markdown("### Metodologia", help= """Foram considerados os vínculos ativos da RAIS de 2020 como estoque inicial.
A partir desse ponto, o estoque foi atualizado mensalmente pela soma do saldo de empregos do CAGED de cada mês, resultando em 
um cálculo acumulado do estoque de empregos ao longo do tempo.""")


@st.cache_data
def get_dataframe(query):
    return pandas_gbq.read_gbq(query, project_id='prefeitura-437123', credentials=credentials)

query = """SELECT * FROM `prefeitura-437123.tabelas.estoque_soma_acumulada_cbo`"""
df_table = get_dataframe(query)

# select box anos
anos = df_table['competênciamov'].unique().tolist()
anos.sort()
anos = [datetime.strptime(data, '%Y-%m').strftime('%m-%Y') for data in anos]

# select box cbo
cbos = df_table['cbo'].unique().tolist()
cbos.sort()
cbos = ["Para filtrar por um CBO específico, selecione aqui"] + cbos  # Adiciona a opção em no início
cbo_selecionado = st.selectbox("Selecione a Ocupação (CBO)", cbos, index=0)

# seletor de intervalo de datas usando os anos no formato 'mm-yyyy'
data_inicial, data_final = st.select_slider(
    "Selecione o Intervalo de Datas",
    options=anos,  # A lista de anos e meses no formato 'mm-yyyy'
    value=(anos[0], anos[-1])  # Valores padrão: primeiro e último da lista
)

# converter datas selecionadas de volta para o formato 'yyyy-mm', compativel com o dataframe
data_inicial = datetime.strptime(data_inicial, '%m-%Y').strftime('%Y-%m')
data_final = datetime.strptime(data_final, '%m-%Y').strftime('%Y-%m')


# DATAFRAME

df_filtrado = df_table[(df_table['competênciamov'] >= data_inicial) & (df_table['competênciamov'] <= data_final)]

if cbo_selecionado != 'Para filtrar por um CBO específico, selecione aqui':
    df_filtrado = df_filtrado[df_filtrado['cbo'] == cbo_selecionado]

saldo_por_cbo = df_filtrado.groupby('cbo')['saldo'].sum()

estoque_final = df_filtrado.sort_values('competênciamov').groupby('cbo')['estoque_acumulado'].last()

# DATAFRAME FINAL

resultados = pd.DataFrame({
    f'Estoque de Emprego Inicial - {data_inicial}': (estoque_final - saldo_por_cbo),
    'Saldo de Emprego Acumulado': saldo_por_cbo,
    f'Estoque de Emprego Final - {data_final}': estoque_final
}, index=estoque_final.index)
resultados.index.name = 'Ocupação (CBO)'

# regra p tirar valores negativos -> coluna estoque inicial + saldo der negativo, zera tudo
condicao = (resultados[resultados.columns[0]] + resultados[resultados.columns[1]]) < 0
resultados.loc[condicao, resultados.columns[:3]] = 0

resultados = resultados.sort_values(by=resultados.columns[2], ascending=False)
resultados['Variação Estoque de Emprego'] = (((resultados[resultados.columns[2]] / resultados[resultados.columns[0]].replace(0, np.nan)) - 1) * 100).fillna(0).round(2)

st.write(f'<p style="font-size:20px;">Estoque e Saldo de Emprego por Ocupação (CBO) | {data_inicial} até {data_final} | Arapiraca</p>', unsafe_allow_html=True)

st.data_editor(
    data=resultados,
    column_config=dict(
        **{
            'Variação Estoque de Emprego': st.column_config.NumberColumn(
                'Variação Estoque de Emprego', format='%.2f%%'
            )
        }
    ),
    hide_index=False
)
