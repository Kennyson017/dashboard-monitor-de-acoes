import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go

# Configurações da pagina
st.set_page_config(
    page_title="Relátorio de Ações",
    page_icon="💲",
    layout="wide",
    initial_sidebar_state="expanded")

# Style CSS
with open('style.css', 'r') as fp:
    st.markdown(f"<style>{fp.read()}</style>", unsafe_allow_html=True)

# Funções
def create_block(title, value, change_percent, change,  is_positive): # Cria um bloco de visualização de dados
    color = "inverse" if is_positive is True else "normal"
    formatted_value = "${:.2f}".format(value)
    formatted_change = "${:.2f}".format(change)
    formatted_change_percent = "{:.2f}%".format(change_percent) 
    st.metric(label=title, value=formatted_value, delta=f"{formatted_change_percent} | {formatted_change}", delta_color=color)

def open(date): # Remete aos valores e variações de abertura
    filtered_row = df[df['Date'] == date]

    if not filtered_row.empty:
        row = filtered_row.iloc[0]  # Pegar a primeira (e única) linha filtrada
        title = "Abertura" # f"Date: {row['Date'].strftime('%d / %m / %y')}"
        value = row['Open']
        change = row['Open_Change'] if not pd.isna(row['Open_Change']) else 0
        change_percent = row['Open_Change_Percent'] if not pd.isna(row['Open_Change_Percent']) else 0
        is_positive = row['Is_Positive'] if not pd.isna(row['Is_Positive']) else False
        return create_block(title, value, change_percent, change, is_positive)
    
def high(date): # Remete aos valores e variações de alta
    filtered_row = df[df['Date'] == date]

    if not filtered_row.empty:
        row = filtered_row.iloc[0]  # Pegar a primeira (e única) linha filtrada
        title = "Alta do Dia" # f"Date: {row['Date'].strftime('%d / %m / %y')}"
        value = row['High']
        change = row['High_Change'] if not pd.isna(row['High_Change']) else 0
        change_percent = row['High_Change_Percent'] if not pd.isna(row['High_Change_Percent']) else 0
        is_positive = row['Is_Positive'] if not pd.isna(row['Is_Positive']) else False
        return create_block(title, value, change_percent, change, is_positive)
    
def low(date): # Remete aos valores e variações de baixa
    filtered_row = df[df['Date'] == date]

    if not filtered_row.empty:
        row = filtered_row.iloc[0]  # Pegar a primeira (e única) linha filtrada
        title = "Baixa do Dia" # f"Date: {row['Date'].strftime('%d / %m / %y')}"
        value = row['Low']
        change = row['Low_Change'] if not pd.isna(row['Low_Change']) else 0
        change_percent = row['Low_Change_Percent'] if not pd.isna(row['Low_Change_Percent']) else 0
        is_positive = row['Is_Positive'] if not pd.isna(row['Is_Positive']) else False
        return create_block(title, value, change_percent, change, is_positive)

def close(date): # Remete aos valores e variações de fechamento
    filtered_row = df[df['Date'] == date]

    if not filtered_row.empty:
        row = filtered_row.iloc[0]  # Pegar a primeira (e única) linha filtrada
        title = "Fechamento" # f"Date: {row['Date'].strftime('%d / %m / %y')}"
        value = row['Close']
        change = row['Close_Change'] if not pd.isna(row['Close_Change']) else 0
        change_percent = row['Close_Change_Percent'] if not pd.isna(row['Close_Change_Percent']) else 0
        is_positive = row['Is_Positive'] if not pd.isna(row['Is_Positive']) else False
        return create_block(title, value, change_percent, change, is_positive)
    
    else:
        st.sidebar.error(f"Nenhuma linha encontrada para a data {to_date.strftime('%Y-%m-%d')}")

def consulta_data(start_date, end_date): # Filtro de data
    date_filter = df[(df['Date'] >= start_date) & (df['Date'] <= end_date)]
    return date_filter

st.sidebar.title('💲Relatorio de Ações') # Sidebar

# Empresas para analise
databases = ['Apple', 'Google', 'Microsoft', 'Netflix', 'Tesla', 'Uber']

# Intervalos de data
intervals = ['Daily', 'Weekly', 'Monthly']

company_select = st.sidebar.selectbox("Selecione a Empresa:", databases) # Sidebar


company_names = {
    'Apple': 'AAPL',
    'Google': 'GOOGL',
    'Microsoft': 'MSFT',
    'Netflix': 'NFLX',
    'Tesla': 'TSLA',
    'Uber': 'UBER',
}

# Carregar dados com base na seleção do usuário e definir stock_name
if company_select in company_names:
    stock_name = company_names[company_select]
    df = pd.read_csv(f'database/{company_select}.csv')
else:
    st.error("Empresa selecionada não reconhecida")

df['Date'] = pd.to_datetime(df['Date'])

start_date = df['Date'].min()
end_date = df['Date'].max()
month_ago = end_date - pd.DateOffset(days=30)

from_date = st.sidebar.date_input('De:', month_ago) # Sidebar
to_date = st.sidebar.date_input('Até:', end_date) # Sidebar
st.sidebar.warning(f"Dados de {start_date.strftime('%Y-%m-%d')} até {end_date.strftime('%Y-%m-%d')}")


load_data = st.sidebar.toggle("Carregar dados") # Sidebar

st.sidebar.write('Criado por:',)
st.sidebar.subheader('Kennyson Chaves Florencio - PD017')

if from_date > to_date:
    st.sidebar.error("Data de início maior que data final") # Sidebar

# Manipulação de Dados

# Convertendo a coluna 'Date' para o formato datetime
df['Date'] = pd.to_datetime(df['Date'])
df['Date'] = df['Date'].dt.date

# Cria o filtro de data para o dataframe

df = consulta_data(from_date, to_date)

# Calcular a mudança diária no preço de fechamento
df['Close_Change'] = df['Close'].diff()
df['Open_Change'] = df['Open'].diff()
df['High_Change'] = df['High'].diff()
df['Low_Change'] = df['Low'].diff()

df['Close_Change_Percent'] = (df['Close_Change'] / df['Close'].shift(1)) * 100
df['Open_Change_Percent'] = (df['Open_Change'] / df['Open'].shift(1)) * 100
df['High_Change_Percent'] = (df['High_Change'] / df['High'].shift(1)) * 100
df['Low_Change_Percent'] = (df['Low_Change'] / df['Low'].shift(1)) * 100


# Determinar se a mudança é positiva
df['Is_Positive'] = df['Close_Change'] > 0

# Contéudo
st.subheader(f"Ativo: {'ativo desconhecido' if not stock_name else stock_name}")

# 1ª Linha de dados
col = st.columns(4)

with col[0]:
    open(to_date)

with col[1]:
    high(to_date)

with col[2]:
    low(to_date)

with col[3]:
    close(to_date)

st.write("*Dados da data mais recente filtrada")

# 2ª Linha de dados
col = st.columns(2)

with col[0]:
    st.write()
    
    fig = go.Figure()
    fig = go.Figure(data=[go.Candlestick(x=df['Date'],
                open=df['Open'], high=df['High'],
                low=df['Low'], close=df['Close'])
                     ])
    
    fig.update_layout(
    xaxis_title='Data',
    yaxis_title='Valor',
    yaxis=dict(tickprefix='$'),  # Adicionar símbolo da moeda no eixo y
    )

    st.plotly_chart(fig, use_container_width=True, clear_on_update=True)

with col[1]:

    st.write()
    fig = px.line(df, x='Date', y="Close")
    fig.update_xaxes(title='Data')
    fig.update_yaxes(title='Valor de Fechamento', tickprefix='$')

    st.plotly_chart(fig, use_container_width=True, clear_on_update=True)
    
if load_data is True:
    df