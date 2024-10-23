import streamlit as st

st.set_page_config(
    page_title='Observatório Arapiraca', layout='wide'
)

st.sidebar.success('Selecione a página')

st.header('O que é o Observatório de Arapiraca?')
st.write("""
O Observatório de Arapiraca é uma plataforma dedicada a fornecer informações detalhadas sobre emprego e renda no município. 
Seu principal objetivo é oferecer acesso a dados atualizados e relevantes para a população, ajudando a entender melhor a dinâmica do mercado de trabalho local.
""")

st.subheader('Conceitos Importantes')

st.write("""
**Saldo de Emprego**: O saldo de emprego reflete a diferença entre o número de admissões e desligamentos formais em um determinado período. 
Quando o saldo é positivo, significa que mais pessoas foram contratadas do que demitidas, apontando para uma expansão no mercado de trabalho. 
Se o saldo for negativo, indica que houve mais demissões do que contratações, sugerindo retração no emprego.
""")

st.write("""
**Estoque de Emprego**: O estoque de emprego representa o total de postos de trabalho formais ativos. 
""")
