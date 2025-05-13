
import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Calculadora de Multa por Cancelamento", layout="wide")

st.title("📊 Calculadora de Multa por Cancelamento")

# 🔼 Upload do arquivo Excel
uploaded_file = st.file_uploader("📂 Faça o upload da planilha Excel", type=["xlsx"])

if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file)

        st.subheader("Pré-visualização dos dados:")
        st.dataframe(df.head())

        cnpjs = df['Documento'].dropna().unique()
        selected_cnpj = st.selectbox("Selecione um CNPJ para calcular a multa:", cnpjs)

        contratos = df[df['Documento'] == selected_cnpj]

        required_columns = ['Documento', 'Data Primeiro Faturamento', 'Quantidade Licenças', 'Preço Unitário', 'Faturas Restantes']
        if not all(col in contratos.columns for col in required_columns):
            st.error(f"A planilha deve conter as colunas: {', '.join(required_columns)}")
        else:
            def calcular_meses(data_inicio):
                hoje = datetime.today()
                delta = hoje - pd.to_datetime(data_inicio)
                return delta.days // 30

            def percentual_multa(meses):
                if meses <= 12:
                    return 0.50
                elif meses <= 24:
                    return 0.30
                elif meses <= 36:
                    return 0.15
                else:
                    return 0.0

            contratos['Meses de Contrato'] = contratos['Data Primeiro Faturamento'].apply(calcular_meses)
            contratos['% Multa'] = contratos['Meses de Contrato'].apply(percentual_multa)
            contratos['Valor Base'] = contratos['Quantidade Licenças'] * contratos['Preço Unitário'] * contratos['Faturas Restantes']
            contratos['Multa (R$)'] = contratos['Valor Base'] * contratos['% Multa']

            st.subheader("💰 Detalhamento por contrato:")
            st.dataframe(contratos[['CNPJ', 'Data Primeiro Faturamento', 'Quantidade Licenças', 'Preço Unitário',
                                    'Faturas Restantes', 'Meses de Contrato', '% Multa', 'Multa (R$)']])

            total_multa = contratos['Multa (R$)'].sum()
            st.subheader(f"🔢 Multa Total para o CNPJ selecionado: R$ {total_multa:,.2f}")

    except Exception as e:
        st.error(f"⚠️ Erro ao processar o arquivo: {e}")
else:
    st.info("Por favor, faça o upload de uma planilha Excel para iniciar.")
