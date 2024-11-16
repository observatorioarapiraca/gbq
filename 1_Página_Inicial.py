import streamlit as st

st.set_page_config(
    page_title='Observatório Arapiraca', layout='wide'
)

# o que é o observatorio
st.subheader('O que é o Observatório de Arapiraca? 🔍' )

st.markdown(
    "<p style='font-size: 18px;'>"
    "O Observatório de Arapiraca é uma plataforma dedicada a fornecer informações detalhadas sobre emprego e renda no município. "
    "Seu principal objetivo é oferecer acesso a dados atualizados e relevantes para a população, ajudando a entender melhor a dinâmica do mercado de trabalho local."
    "</p>", 
    unsafe_allow_html=True
)

# Conceitos importantes 
st.subheader('Conceitos Importantes 💡')

st.markdown(
    "<p style='font-size: 18px;'>"
    "- <strong>Saldo de Emprego</strong>: O saldo de emprego reflete a diferença entre o número de admissões e desligamentos formais em um determinado período. "
    "Quando o saldo é positivo, significa que mais pessoas foram contratadas do que demitidas, apontando para uma expansão no mercado de trabalho. "
    "Se o saldo for negativo, indica que houve mais demissões do que contratações, sugerindo retração no emprego."
    "</p>",
    unsafe_allow_html=True
)

st.markdown(
    "<p style='font-size: 18px;'>"
    "- <strong>Estoque de Emprego</strong>: O estoque de emprego representa o total de postos de trabalho formais ativos."
    "</p>", 
    unsafe_allow_html=True
)

# Guia salarial
st.subheader('Sobre o Guia Salarial 💰')

st.markdown(
    "<p style='font-size: 18px;'>"
    "O Guia Salarial é baseado em dados da RAIS e do CAGED:"
    "</p>", 
    unsafe_allow_html=True
)

st.markdown(
    "<p style='font-size: 18px;'>"
    "- <strong>RAIS</strong>: Utiliza o estoque de emprego, considerando todos os trabalhadores empregados no período e refletindo o salário médio dos empregados."
    "</p>", 
    unsafe_allow_html=True
)

st.markdown(
    "<p style='font-size: 18px;'>"
    "- <strong>CAGED</strong>: Os salários são baseados nas admissões e desligamentos."
    "</p>", 
    unsafe_allow_html=True
)

st.markdown(
    "<p style='font-size: 18px;'>"
    "<strong>⚠️ Atenção</strong>: As duas fontes têm metodologias diferentes. A RAIS reflete o total de empregados, enquanto o CAGED foca nas movimentações de contratação e demissão. "
    "Por isso, ao interpretar os dados, considere o contexto de cada uma dessas fontes."
    "</p>", 
    unsafe_allow_html=True
)
