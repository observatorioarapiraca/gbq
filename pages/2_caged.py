import pandas as pd
from google.cloud import bigquery
from google.oauth2 import service_account
import pandas_gbq
import streamlit as st

# Passo 1: Acessar as credenciais do arquivo secrets.toml
credentials_info = st.secrets["GOOGLE_APPLICATION_CREDENTIALS_JSON"]

# Passo 2: Criar um objeto de credenciais a partir das variáveis de ambiente
credentials = service_account.Credentials.from_service_account_info(
    credentials_info, scopes=["https://www.googleapis.com/auth/cloud-platform"]
)

client = bigquery.Client(credentials = credentials, project = 'prefeitura-437123')

query = """SELECT * FROM `prefeitura-437123.caged.movimentacoes` LIMIT 10
"""


query_job = client.query(query)
df = query_job.to_dataframe()

st.title("Dados do Google BigQuery")
st.write(df)
