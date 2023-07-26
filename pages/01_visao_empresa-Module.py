#Importando bibliotecas

import pandas as pd
import numpy as nx
import re
import folium
import plotly.express as px
from haversine import haversine
import plotly.graph_objects as go
import streamlit as st
from PIL import Image
from streamlit_folium import folium_static

#-------------------------------------------------------------------------------------------------------------------------------------
#Import dataset
#-------------------------------------------------------------------------------------------------------------------------------------

arquivo = r"train.csv"
df = pd.read_csv(arquivo)
df1 = df.copy()

#-------------------------------------------------------------------------------------------------------------------------------------
#Funções
#-------------------------------------------------------------------------------------------------------------------------------------

def clean_code( df1 ):
    
    """ Esta função tem a responsibilidade de realizar a limpeza do dataframe
    
        Tipos de limpeza:
        
        1. Remoção dos dados NaN
        2. Mudança do tipo da coluna de dados
        3. Remoção dos espaços das variáveis de texto
        4. Formatação da coluna de datas
        5. Limpeza de coluna de tempos ( remoção do texto da variável numérica)
        
        Input: Dataframe
        Output: Dataframe
    
    """
    
    # Tratando os arquivos

    #Comando para remover texto de numeros
    df1 = df.reset_index( drop=True)
    df1.loc[:,'Time_taken(min)'] = df1.loc[:, 'Time_taken(min)'].apply( lambda x: x.split('(min) ')[1])
    df1.loc[:, 'Time_taken(min)'] = df1.loc[:, 'Time_taken(min)'].astype( int )

    #Removendo NaN condicoes Delivery_person_Age
    linhas_selecionadas =(df1['Delivery_person_Age'] != 'NaN ') 
    df1 = df1.loc[linhas_selecionadas, :].copy()
    #Convertendo a coluna Delivery_person_Age de texto para numero
    df1['Delivery_person_Age'] = df1['Delivery_person_Age'].astype( int )

    #Removendo NaN condicoes Festival
    linhas_selecionadas =(df1['Festival'] != 'NaN ') 
    df1 = df1.loc[linhas_selecionadas, :].copy()

    #Removendo NaN condicoes multiple_deliveries
    linhas_selecionadas = (df1['multiple_deliveries'] != 'NaN ')
    df1 = df1.loc[linhas_selecionadas, :].copy()
    df1['multiple_deliveries'] = df1['multiple_deliveries'].astype( int )

    #Removendo NaN condicoes climaticas
    linhas_selecionadas = (df1['Weatherconditions'] != 'NaN ')
    df1 = df1.loc[linhas_selecionadas, :].copy()

    #Removendo NaN condicoes City
    linhas_selecionadas = (df1['City'] != 'NaN ')
    df1 = df1.loc[linhas_selecionadas, :].copy()

    #Removendo NaN condicoes Type_of_vehicle
    linhas_selecionadas = (df1['Type_of_vehicle'] != 'NaN ')
    df1 = df1.loc[linhas_selecionadas, :].copy()

    #Removendo NaN condicoes Road_traffic_density
    linhas_selecionadas = (df1['Road_traffic_density'] != 'NaN ')
    df1 = df1.loc[linhas_selecionadas, :].copy()

    #Removendo NaN condicoes Type_of_order
    linhas_selecionadas = (df1['Type_of_order'] != 'NaN ')
    df1 = df1.loc[linhas_selecionadas, :].copy()

    #Convertendo a coluna Delivery_person_Ratings de texto para um float
    df1['Delivery_person_Ratings'] = df1['Delivery_person_Ratings'].astype( float )

    #Convertendo a coluna Order_Date de texto para data
    df1['Order_Date'] = pd.to_datetime( df1['Order_Date'], format='%d-%m-%Y')

    # Removendo os espaços dentro de strings/texto/object
    df1.loc[:,'ID'] = df1.loc[:,'ID'].str.strip()
    df1.loc[:, 'Delivery_person_ID'] = df1.loc[:,'Delivery_person_ID'].str.strip()
    df1.loc[:, 'Type_of_order'] = df1.loc[:,'Type_of_order'].str.strip()
    df1.loc[:, 'Type_of_vehicle'] = df1.loc[:,'Type_of_vehicle'].str.strip()
    df1.loc[:, 'City'] = df1.loc[:,'City'].str.strip()
    df1.loc[:, 'Road_traffic_density'] = df1.loc[:,'Road_traffic_density'].str.strip()
    df1.loc[:, 'Festival'] = df1.loc[:,'Festival'].str.strip()


    #Adicionando a coluna semana do ano na lista
    df1['week_of_year'] = df1['Order_Date'].dt.strftime("%U")

    #Resetando o index
    df1 = df1.reset_index( drop=True )

    return df1


def order_metric(df1):
        
    aux = df1.loc[:, ['ID', 'Order_Date']].groupby(['Order_Date']).count().reset_index()
    fig = px.bar(aux, y='ID', x='Order_Date')
            
    return fig

#Distribuição dos pedidos por tipo de tráfego
def traffic_order_share( df1 ): 
    aux_df1 = df1.loc[:, ['ID', 'Road_traffic_density']].groupby('Road_traffic_density').count().reset_index()
    aux_df1['percent_ID'] = 100 * (aux_df1['ID']/aux_df1['ID'].sum())
    fig = px.pie(aux_df1, values='percent_ID', names='Road_traffic_density')

    return fig

#Distribuição dos pedidos por tipo de tráfego e cidade
def traffic_order_city( df1 ):
                
    df_aux = df1.loc[:,['ID','City','Road_traffic_density']].groupby(['City','Road_traffic_density']).count().reset_index()
    fig = px.scatter(df_aux, x= 'City', y='Road_traffic_density', size='ID', color='City')
                
    return fig

def order_share_by_week( df1 ):
    df1_aux01 = df1.loc[:,['ID','week_of_year']].groupby('week_of_year').count().reset_index()
    df1_aux02 = df1.loc[:,['Delivery_person_ID','week_of_year']].groupby('week_of_year').nunique().reset_index()
    df1_aux = pd.merge(df1_aux01, df1_aux02, how='inner', on= 'week_of_year')
    df1_aux['order_by_delivery'] = (df1_aux['ID']/df1_aux['Delivery_person_ID'])
    fig = px.line(df1_aux, x='week_of_year', y='order_by_delivery')
            
    return fig  

    
def country_maps( df1 ):
    data_plot = df1.loc[:,['City','Road_traffic_density','Delivery_location_latitude','Delivery_location_longitude']].groupby(['City', 'Road_traffic_density']).median().reset_index()

    # Desenhar o mapa
    map_ = folium.Map( zoom_start=11 )

    for index, location_info in data_plot.iterrows():
        folium.Marker( [location_info['Delivery_location_latitude'],
        location_info['Delivery_location_longitude']],
        popup=location_info[['City', 'Road_traffic_density']] ).add_to( map_ )

    folium_static(map_, width=1024, height=600)
    

#Limpando os dados

df1 = clean_code( df1 )

#================================================
#Barra Lateral
#================================================

#image_path='repos/Projetos_FTC/Imagem/'
image= Image.open( 'Delivery.jpg')
st.sidebar.image( image, width=120)

st.header('Marketplace - Visão Empresa')

st.sidebar.markdown('# Cury Company')

st.sidebar.markdown('## Fastest Delivery in Town')

st.sidebar.markdown("""---""")

st.sidebar.markdown('## Selecione uma data limite')

data_slider = st.sidebar.slider('Até qual valor?',
                                value=pd.to_datetime(2022, 4, 13),
                                min_value=pd.to_datetime(2022, 2, 11),
                                max_value=pd.to_datetime(2022, 4, 6),
                                format='DD-MM-YYYY')

st.sidebar.markdown("""---""")

traffic_options = st.sidebar.multiselect(
    'Quais as condições do trânsito',
    ['Low','Medium','High','Jam'],
    default=['Low','Medium','High','Jam'])

st.sidebar.markdown("""---""")

st.sidebar.markdown('### Powered by Silvio Francischini')

#Filtro de data
linhas_selecionadas = df1['Order_Date'] < data_slider
df1 = df1.loc[linhas_selecionadas, :]

#Filtro de transito

linhas_selecionadas = df1['Road_traffic_density'].isin( traffic_options )
df1 = df1.loc[linhas_selecionadas, :]


#================================================
#Layout Steamlit
#================================================

tab1, tab2, tab3 = st.tabs(["Visão Gerêncial", "Visão Tática", "Visão Geográfica"])

with tab1:
    
    with st.container():
    
        st.markdown('# Order by day')
        
        fig = order_metric( df1 )
 
        st.plotly_chart(fig, user_container_width=True)

    
    with st.container():
        cols1, cols2 = st.columns(2)
    
        with cols1:
            st.header('Traffic Order Share')
            fig = traffic_order_share( df1 )
            st.plotly_chart(fig, use_container_width=True)
        
        with cols2:
            st.header('Traffic Order City')
            fig = traffic_order_city( df1 )
            st.plotly_chart(fig, use_container_width=True)

with tab2:
    with st.container():
        st.markdown('# Order by week')
        aux = df1.loc[:,['ID', 'week_of_year']].groupby(['week_of_year']).count().reset_index()

        fig = px.line(aux, y='ID', x='week_of_year')
        st.plotly_chart(fig, use_container_width=True)
        
    with st.container():
        
        st.markdown('# Order share by week')
        
        fig = order_share_by_week( df1 ) 
        
        st.plotly_chart(fig, use_container_width=True)
        
        
with tab3:
    st.markdown('# Country Maps')   
    
    country_maps( df1 )


        

        
        
        

