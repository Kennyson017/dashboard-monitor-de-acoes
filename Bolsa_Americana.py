import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go

# Configurações da pagina
st.set_page_config(
    page_title="Monitor de Ações",
    page_icon="💲",
    layout="wide",
    initial_sidebar_state="expanded")

sidebar = True

# Style CSS
with open('style.css', 'r') as fp:
    st.markdown(f"<style>{fp.read()}</style>", unsafe_allow_html=True)

# Funções
def create_block(title, value, change_percent, change): # Cria um bloco de visualização de dados
    formatted_value = "${:.2f}".format(value)
    formatted_change = "${:.2f}".format(change)
    formatted_change_percent = "{:.2f}%".format(change_percent)
    st.metric(label=title, value=formatted_value, delta=f"{formatted_change_percent} | {formatted_change}")

def close(date, action): #Cria dados de variação
    filtered_row = df[df['Date'] == date]

    if not filtered_row.empty:
        row = filtered_row.iloc[0]
        title = f"{action} | {row['Date'].strftime('%d/%m/%Y')}"
        value = row[action]
        change = row[f'{action}_Change'] if not pd.isna(row[f'{action}_Change']) else 0
        change_percent = row[f'{action}_Change_Percent'] if not pd.isna(row[f'{action}_Change_Percent']) else 0
        is_positive = change > 0
        return create_block(title, value, change_percent, change)
    else:
        st.sidebar.error(f"Nenhuma linha encontrada para a data {date.strftime('%Y-%m-%d')}")

def amostra(select_stocks, date): # Amostra de Dados manipuados criando bloco, remete as duas funções anteriores
    num_columns = 6  # Define o número de colunas
    num_stocks = len(select_stocks)
    num_rows = num_stocks // num_columns + (1 if num_stocks % num_columns != 0 else 0)  # Calcula o número de linhas necessárias

    grid = [[] for _ in range(num_rows)]  # Cria uma matriz para armazenar os elementos

    for i, stock in enumerate(select_stocks):
        row = i // num_columns
        grid[row].append(stock)  # Adiciona a ação à linha correspondente

    for row in grid:
        columns = st.columns(num_columns)  # Cria as colunas na linha
        for col, stock in zip(columns, row):
            with col:  # Adiciona o conteúdo na coluna correspondente
                close(date, stock)

def consulta_data(start_date, end_date): # Filtro de data
    date_filter = df[(df['Date'] >= start_date) & (df['Date'] <= end_date)]
    return date_filter

df = pd.read_csv('database/SPX.csv')
df.rename(columns={df.columns[0]: 'Date'}, inplace=True)

df['Date'] = pd.to_datetime(df['Date'])

start_date = df['Date'].min()
end_date = df['Date'].max()
month_ago = end_date - pd.DateOffset(days=365)

st.sidebar.title('💲Monitor de Ações')

stock_select = st.sidebar.multiselect("Selecione a Empresa:", options=df.columns[1:])

from_date = st.sidebar.date_input('De:', month_ago)
to_date = st.sidebar.date_input('Até:', end_date)

st.sidebar.warning(f"Dados de {start_date.strftime('%Y-%m-%d')} até {end_date.strftime('%Y-%m-%d')}")

# Converte from_date e to_date para datetime
from_date = pd.to_datetime(from_date)
to_date = pd.to_datetime(to_date)

load_data = st.sidebar.toggle("Carregar dados")

st.sidebar.write('Criado por:',)
st.sidebar.subheader('Kennyson Chaves Florencio - PD017')

if from_date > to_date:
    st.sidebar.error("Data de início maior que data final")

df = consulta_data(from_date, to_date)

# Calcular a mudança diária no preço de fechamento
for column in df.columns[1:]:
    df[f'{column}_Change'] = df[column].diff()
    df[f'{column}_Change_Percent'] = (df[f'{column}_Change'] / df[column].shift(1)) * 100

#Conteúdo

st.subheader(f"Ativos da Bolsa Americana - SPX")

# 1ª Linha de dados
col = st.columns(1)

with col[0]:
    if stock_select:
        amostra(stock_select, to_date)
        st.write("*Dados da data mais recente filtrada")

# 2ª Linha de dados
col = st.columns(1)

with col[0]:
    if stock_select:
        fig = px.line(df, x='Date', y=stock_select, title='Histórico de Valores')
        fig.update_xaxes(title='Data')
        fig.update_yaxes(title='Valor de Fechamento', tickprefix='$')

        st.plotly_chart(fig, use_container_width=True, clear_on_update=True)

        
if load_data:
    st.dataframe(df)
