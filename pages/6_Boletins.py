import streamlit as st
from google.cloud import storage
from google.oauth2 import service_account

credentials_info = st.secrets["GOOGLE_APPLICATION_CREDENTIALS_JSON"]

credentials = service_account.Credentials.from_service_account_info(
    credentials_info, scopes=["https://www.googleapis.com/auth/cloud-platform"]
)

client = storage.Client(credentials=credentials)
bucket_name = 'observatorio-bucket'

def listar_arquivos(bucket_name):
    blobs = client.list_blobs(bucket_name)
    arquivos_por_ano = {}  
    
    for blob in blobs:
        # Extrair o nome do arquivo e o ano
        nome_arquivo = blob.name
        link = f"https://storage.googleapis.com/{bucket_name}/{nome_arquivo}"
        try:
            # Supõe que o ano está no final do nome, separado por "-"
            ano = nome_arquivo.split("-")[-1][:4]  # Pega os 4 primeiros dígitos no final
            if ano.isdigit():
                if ano not in arquivos_por_ano:
                    arquivos_por_ano[ano] = []  # Inicializa a lista para o ano
                arquivos_por_ano[ano].append(link)
        except IndexError:
            pass
    
    return arquivos_por_ano

# Obter arquivos organizados por ano
arquivos_agrupados = listar_arquivos(bucket_name)

st.markdown("### Mercado de Trabalho Formal")

for ano, links in sorted(arquivos_agrupados.items(), reverse=True):  # Anos mais recentes primeiro
    with st.expander(f"Ano: {ano} ({len(links)} arquivos)"):
        for link in links:
            nome_arquivo = link.split("/")[-1]
            st.markdown(f"- [{nome_arquivo}]({link})")
