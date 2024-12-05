import pandas as pd
from google.cloud import bigquery
from google.oauth2 import service_account
import pandas_gbq
import streamlit as st
import pydeck as pdk

credentials_info = st.secrets["GOOGLE_APPLICATION_CREDENTIALS_JSON"]
credentials = service_account.Credentials.from_service_account_info(
    credentials_info, scopes=["https://www.googleapis.com/auth/cloud-platform"])

client = bigquery.Client(credentials=credentials, project='prefeitura-437123')

st.set_page_config(page_title='CNPJ - Mapa', layout='wide')
                                    
@st.cache_data
def get_dataframe(query):
    return pandas_gbq.read_gbq(query, project_id='prefeitura-437123', credentials=credentials)

query = """SELECT data, lat, long, cnae FROM `prefeitura-437123.cnpj.cnpj_loc`"""
cnpj = get_dataframe(query)

cnpj["lat"] = pd.to_numeric(cnpj["lat"], errors="coerce")
cnpj["long"] = pd.to_numeric(cnpj["long"], errors="coerce")
cnpj = cnpj.dropna(subset=["lat", "long"])

col0, col1 = st.columns([1,5])

periodos = cnpj["data"].unique()
with col0:
    periodo_selecionado = st.selectbox("Selecione o período:", sorted(periodos))

# Seleção do CNAE com a opção "Todos", configurando "Todos" como padrão
cnae = cnpj["cnae"].unique()
with col1:
    cnae_selecionado = st.selectbox("Selecione a Classificação Nacional das Atividades Econômicas (CNAE):", ["Todos"] + sorted(cnae), index=0)  # "index=0" define "Todos" como padrão

# Filtrar o DataFrame com base no período selecionado e CNAE
if cnae_selecionado == "Todos":
    cnpj_filtrado = cnpj[cnpj["data"] == periodo_selecionado]  # Filtra apenas pelo período
    get_radius_value = 10  # Valor do raio quando "Todos" é selecionado
else:
    cnpj_filtrado = cnpj[(cnpj["data"] == periodo_selecionado) & (cnpj["cnae"] == cnae_selecionado)]  # Filtra pelo CNAE e período
    get_radius_value = 80  # Valor do raio quando "Todos" é selecionado

# Exibir o mapa usando pydeck
if not cnpj_filtrado.empty:
    # Configuração do mapa
    mapa = pdk.Deck(
        map_style="mapbox://styles/mapbox/streets-v11",  # Estilo do mapa
        initial_view_state=pdk.ViewState(
            latitude=cnpj_filtrado["lat"].mean() -0.009,
            longitude=cnpj_filtrado["long"].mean(),
            zoom=11,  # Ajuste do nível de zoom
            pitch=0,  # Inclinação do mapa
        ),
        layers=[
            pdk.Layer(
                "ScatterplotLayer",  # Camada de dispersão para os pontos
                data=cnpj_filtrado,
                get_position="[long, lat]",  # Latitude e Longitude
                get_color="[0, 0, 255, 140]",  # Cor azul com opacidade
                get_radius=get_radius_value ,  # Tamanho dos círculos, você pode ajustar conforme necessário
                pickable=False,  # Permite interação com os pontos
            ),
        ],
    )

    # Renderizar o mapa
    st.pydeck_chart(mapa)
else:
    st.warning("Nenhum dado disponível para o período selecionado.")
