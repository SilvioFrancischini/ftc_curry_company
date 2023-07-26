#Importando bibliotecas

import pandas as pd
import numpy as nx
import re
#import folium
import plotly.express as px
from haversine import haversine
import plotly.graph_objects as go
import streamlit as st
from PIL import Image
from streamlit_folium import folium_static

#-------------------------------------------------------------------------------------------------------------------------------------
#Import dataset
#-------------------------------------------------------------------------------------------------------------------------------------

arquivo = r"C:\Users\silvi\repos\Projetos_FTC\aula_24_dataframe\train.csv"
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


def calcule_number( cols, operation ):
            
    if operation == 'max':
                    
        resultado = df1.loc[:, cols].max()
                    
    elif operation == 'min':
                    
        resultado = df1.loc[:, cols].min()
                    
    return resultado

def calcular_condicao(cols, operation ):
                
    if operation == 'max':
            
        resultado = df1.loc[:,cols].max()
                
    elif operation == 'min':
                    
        resultado = df1.loc[:,cols].min()
                    
    return resultado

def avaliacao_media_por_entregador( df1 ):
            
    avalicao_media_entregador = (df1.loc[:,['Delivery_person_ID','Delivery_person_Ratings']]
                                         .groupby(['Delivery_person_ID'])
                                         .mean()
                                         .reset_index())
                
    return avalicao_media_entregador

def avaliacao_media_por_transito( df1 ):
            
    avaliacao_media_transito = (df1.loc[:,['Delivery_person_Ratings','Road_traffic_density']]
                                            .groupby(['Road_traffic_density'])
                                            .agg( {'Delivery_person_Ratings': ['mean','std']} ))
                
    #Mudar nome das colunas
    avaliacao_media_transito.columns = ['delivery_mean','delivery_std']

    #Resetar index 
    avaliacao_media_transito = avaliacao_media_transito.reset_index()
            
    return avaliacao_media_transito

def avaliacao_media_por_clima( df1 ):
            
    avaliacao_media_clima = (df1.loc[:,['Delivery_person_Ratings','Weatherconditions']]
                                            .groupby(['Weatherconditions'])
                                            .agg( {'Delivery_person_Ratings': ['mean','std']} ))

    avaliacao_media_clima.columns = ['weather_mean','weather_mean_std']

    avaliacao_media_clima = avaliacao_media_clima.reset_index()
                
    return avaliacao_media_clima


def entregadores_mais_ou_menos_rapidos( df1 , tipo):
                
    if tipo == 'rapido':
            
        top_entregadores_rapidos = (df1.loc[:, ['City','Delivery_person_ID','Time_taken(min)']]
                                                      .groupby(['City','Delivery_person_ID'])
                                                      .mean()
                                                      .sort_values(['City','Time_taken(min)'], ascending=False)
                                                      .reset_index())

        #Separando por tipo
        urban = top_entregadores_rapidos.loc[top_entregadores_rapidos['City'] == 'Urban', : ].head(10)
        metropolitian = top_entregadores_rapidos.loc[top_entregadores_rapidos['City'] == 'Metropolitian', : ].head(10)
        semi_urban = top_entregadores_rapidos.loc[top_entregadores_rapidos['City'] == 'Semi-Urban', : ].head(10)

        #Concatenando urban, metropolitian e semi_urban
        resultado = pd.concat([urban, metropolitian, semi_urban]).reset_index(drop=True)
                
    elif tipo == 'lento':
                    
        top_entregadores_lentos = (df1.loc[:, ['City','Delivery_person_ID','Time_taken(min)']]
                                              .groupby(['City','Delivery_person_ID'])
                                              .mean().sort_values(['City','Time_taken(min)'], ascending=True)
                                              .reset_index())

        urban = top_entregadores_lentos.loc[top_entregadores_lentos['City'] == 'Urban', : ].head(10)
        metropolitian = top_entregadores_lentos.loc[top_entregadores_lentos['City'] == 'Metropolitian', : ].head(10)
        semi_urban = top_entregadores_lentos.loc[top_entregadores_lentos['City'] == 'Semi-Urban', : ].head(10)

        resultado = pd.concat([urban, metropolitian, semi_urban]).reset_index(drop=True)

                
    return resultado

#Limpando os dados

df1 = clean_code( df1 )

#================================================
#Barra Lateral
#================================================

#image_path='repos/Projetos_FTC/Imagem/'
image= Image.open( 'Delivery.jpg')
st.sidebar.image( image, width=120)

st.header('Marketplace - Visão Entregadores')

st.sidebar.markdown('# Cury Company')

st.sidebar.markdown('## Fastest Delivery in Town')

st.sidebar.markdown("""---""")

st.sidebar.markdown('## Selecione uma data limite')

data_slider = st.sidebar.slider(
    'Até qual valor?',
    value=pd.datetime(2022, 4, 13),
    min_value=pd.datetime(2022, 2, 11),
    max_value=pd.datetime(2022, 4, 6),
    format='DD-MM-YYYY')

st.sidebar.markdown("""---""")

traffic_options = st.sidebar.multiselect(
    'Quais as condições do trânsito',
    ['Low','Medium','High','Jam'],
    default=['Low','Medium','High','Jam'])

st.sidebar.markdown("""---""")

st.sidebar.markdown('### Powered by Silvio Francischini')

#Filtro de data
linhas_selecionadas = (df1['Order_Date'] < data_slider)

df1 = df1.loc[linhas_selecionadas, :]

#Filtro de transito

linhas_selecionadas = df1['Road_traffic_density'].isin( traffic_options )
df1 = df1.loc[linhas_selecionadas, :]

#================================================
#Layout Steamlit
#================================================

tab1, tab2, tab3 = st.tabs(["Visão Gerêncial", "-", "-"])

with tab1:
    
    with st.container():
        
        st.title('Overall Metrics')
    
        cols1, cols2, cols3, cols4 = st.columns(4, gap='large')
        with cols1:
            st.subheader('Maior de idade')
            
            maior_idade = calcule_number('Delivery_person_Age', 'max')
            
            st.metric('Maior de idade', maior_idade)
            
            
        with cols2:
            st.subheader('Menor de idade')
            
            menor_idade = calcule_number('Delivery_person_Age', 'max')
            
            st.metric('Menor de idade', menor_idade)
            
        with cols3:
            st.subheader('Melhor condicao de veiculos')
            
            melhor_condicao = calcular_condicao('Vehicle_condition', 'max')
            
            st.metric('Melhor condicao', melhor_condicao)
            
            
            
        with cols4:
            st.subheader('Pior condicao de veiculos')
            
            pior_condicao = calcular_condicao('Vehicle_condition', 'min')
            
            st.metric('Pior condicao', pior_condicao)
            
            
    with st.container():
        
        st.markdown("""---""")
        
        st.title('Avaliações')
        
        cols1, cols2 = st.columns(2, gap='large')
        
        with cols1:
            
            st.subheader('Avaliacao media por entregador')
            
            avalicao_media_entregador = avaliacao_media_por_entregador( df1 )
            
            st.dataframe(avalicao_media_entregador)
        
        with cols2:
            
            st.subheader('Avaliacao media por transito')
            
            avaliacao_media_transito = avaliacao_media_por_transito( df1 )
                
            st.dataframe(avaliacao_media_transito)
            
            st.subheader('Avaliacao media por clima')
            
            avaliacao_media_clima = avaliacao_media_por_clima( df1 )
            
            st.dataframe(avaliacao_media_clima)
        
    with st.container():

        st.markdown("""---""")

        st.title('Velocidade de entrega')

        cols1, cols2 = st.columns(2, gap='large')

        with cols1:

            st.subheader('Top entregadores mais rapidos')
            
            top_entregadores_rapidos = entregadores_mais_ou_menos_rapidos ( df1, 'rapido')            

            st.dataframe(top_entregadores_rapidos)

        with cols2:

            st.subheader('Top entregadores mais lentos')
            
            top_entregadores_lentos = entregadores_mais_ou_menos_rapidos ( df1, 'lento')  

            st.dataframe(top_entregadores_lentos)




        
            
        
            


        


    
        
        
        
        
    
    
        




