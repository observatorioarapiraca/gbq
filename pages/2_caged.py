import pandas as pd
from google.cloud import bigquery
from google.oauth2 import service_account
import pandas_gbq
import streamlit as st


key_path = st.secrets['GOOGLE_APPLICATION_CREDENTIALS_JSON']

credentials = service_account.Credentials.from_service_account_file(
              key_path, scopes = ["https://www.googleapis.com/auth/cloud-platform"])

client = bigquery.Client(credentials = credentials, project = 'prefeitura-437123')

query = """SELECT * FROM `prefeitura-437123.caged.movimentacoes` LIMIT 10
"""


query_job = client.query(query)
df = query_job.to_dataframe()

st.title("Dados do Google BigQuery")
st.write(df)
