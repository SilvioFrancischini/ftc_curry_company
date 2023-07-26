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
import numpy as np
import  plotly.graph_objects as go

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

def distancia_media_de_entregas( df1 ):
            
    cols = ['Delivery_location_latitude','Delivery_location_longitude','Restaurant_latitude','Restaurant_longitude']

    df1['distance'] = df1.loc[:, cols].apply(lambda x:
                                            haversine( (x['Restaurant_latitude'], x['Restaurant_longitude']),
                                                       (x['Delivery_location_latitude'], x['Delivery_location_longitude'] )), axis=1)

    avg_distance = np.round(df1['distance'].mean(), 2)
                
    return avg_distance

#Limpando os dados

df1 = clean_code( df1 )


def entrega_com_ou_sem_festival(df1, operacao , festival):
            
    if (operacao == 'avg') and (festival == 'Sim'):
            
        df_aux = ( df1.loc[:, ['Time_taken(min)','Festival']]
                                  .groupby('Festival')
                                  .agg( {'Time_taken(min)': ['mean','std'] } ) )

        df_aux.columns = ['avg_time','std_time']

        df_aux = df_aux.reset_index()

        resultado = np.round(( df_aux.loc[df_aux['Festival'] == 'Yes', 'avg_time']), 2)
                    
    elif (operacao == 'avg') and (festival == 'Nao'):
                    
        df_aux = ( df1.loc[:, ['Time_taken(min)','Festival']]
                          .groupby('Festival')
                          .agg( {'Time_taken(min)': ['mean','std'] } ) )
            
        df_aux.columns = ['avg_time','std_time']
            
        df_aux = df_aux.reset_index()
            
        resultado = np.round(( df_aux.loc[df_aux['Festival'] == 'No', 'avg_time']), 2)
                  
    elif (operacao == 'std') and (festival == 'Sim'):
                    
        df_aux = ( df1.loc[:, ['Time_taken(min)','Festival']]
                          .groupby('Festival')
                          .agg( {'Time_taken(min)': ['mean','std'] } ) )
            
        df_aux.columns = ['avg_time','std_time']
            
        df_aux = df_aux.reset_index()
            
        resultado = np.round(( df_aux.loc[df_aux['Festival'] == 'Yes', 'std_time']), 2)
                    
    elif (operacao == 'std') and (festival == 'Nao'):
                    
        df_aux = ( df1.loc[:, ['Time_taken(min)','Festival']]
                          .groupby('Festival')
                          .agg( {'Time_taken(min)': ['mean','std'] } ) )
            
        df_aux.columns = ['avg_time','std_time']
            
        df_aux = df_aux.reset_index()
            
        resultado = np.round(( df_aux.loc[df_aux['Festival'] == 'No', 'std_time']), 2)
                
    return resultado

def tempo_medio_de_entrega_por_cidade( df1 ):
        
    cols = ['Delivery_location_latitude','Delivery_location_longitude','Restaurant_latitude','Restaurant_longitude']

    df1['distance'] = df1.loc[:, cols].apply(lambda x:
                                            haversine( (x['Restaurant_latitude'], x['Restaurant_longitude']),
                                                       (x['Delivery_location_latitude'], x['Delivery_location_longitude'] )), axis=1)

    avg_distance = df1.loc[:, ['City', 'distance']].groupby(['City']).mean().reset_index()

    fig = go.Figure( data=[ go.Pie( labels=avg_distance['City'], values= avg_distance['distance'], pull=[0, 0.1 , 0] ) ] )
            
    return fig

def distribuicao_do_tempo_media( df1 ):

    df_aux = df1.loc[: , ['City', 'Time_taken(min)']].groupby(['City']).agg( {'Time_taken(min)': ['mean', 'std'] } )
    df_aux.columns = ['avg_time','std_time']
    df_aux = df_aux.reset_index()
    fig = go.Figure()
    fig.add_trace( go.Bar( name='Control', x=df_aux['City'],y=df_aux['avg_time'],error_y=dict(type='data',array=df_aux['std_time'] ) ) )
    fig.update_layout(barmode='group')
            
    return fig

def sun_burst( df1 ):
    df_aux = df1.loc[: , ['City', 'Time_taken(min)','Road_traffic_density']].groupby(['City','Road_traffic_density']).agg( {'Time_taken(min)': ['mean', 'std'] } )
    df_aux.columns = ['avg_time','std_time']
    df_aux = df_aux.reset_index()
    fig = px.sunburst(df_aux, path=['City','Road_traffic_density'], values='avg_time',color='std_time',color_continuous_scale='RdBu',color_continuous_midpoint=np.average(df_aux['std_time'] ) )
        
    return fig

def distruicao_distancia( df1 ):
        
    df_aux = ( df1.loc[:, ['City','Type_of_order','Time_taken(min)']]
                              .groupby(['City','Type_of_order'])
                              .agg( {'Time_taken(min)': ['mean','std'] } ) )

    df_aux.columns = ['avg_time','std_time']

    df_aux = df_aux.reset_index()
    
    return df_aux

#================================================
#Barra Lateral
#================================================

#image_path='repos/Projetos_FTC/Imagem/'
image= Image.open( 'Delivery.jpg')
st.sidebar.image( image, width=120)

st.header('Marketplace - Visão Restaurantes')

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
linhas_selecionadas = df1['Order_Date'] < data_slider
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
        
        st.title('Overall metrics')
        
        cols1, cols2, cols3 = st.columns( 3 )
        
        with cols1:
            
            delivery_unique = len(df1.loc[:,'Delivery_person_ID'].unique())
            
            st.metric('Entregadores únicos', delivery_unique)
            
        with cols2:
            
            avg_distance = distancia_media_de_entregas( df1 )
            
            st.metric('A distancia media de entregas', avg_distance)
            
        with cols3:
            

            df_aux = entrega_com_ou_sem_festival( df1, 'avg', 'Sim')      
            
            st.metric('TM entrega c/ Festival', df_aux )
            
    with st.container():
        
        cols4, cols5, cols6 = st.columns( 3 )
            
        with cols4:
        
            df_aux = entrega_com_ou_sem_festival( df1, 'std', 'Sim')
            
            st.metric('STD entrega c/ Festival', df_aux )
        
        with cols5:
            
            df_aux = entrega_com_ou_sem_festival( df1, 'avg', 'Nao')
            
            st.metric('TM entrega s/ Festival', df_aux )
            
            
        with cols6:
        
            df_aux = entrega_com_ou_sem_festival( df1, 'std', 'Nao')
            
            st.metric('STD entrega s/ Festival', df_aux )
        
    with st.container():
        
        st.markdown("""---""")
        
        st.title('Tempo medio de entrega por cidade')
        
        fig = tempo_medio_de_entrega_por_cidade( df1 )
            
        st.plotly_chart( fig )
            
        
    with st.container():
        
        st.markdown("""---""")
        
        st.title('Distribuição do Tempo Média')
        
        fig = distribuicao_do_tempo_media( df1 )
        
        st.plotly_chart( fig )
        
    with st.container():
        
        st.markdown("""---""")
        
        st.title('Distribuição do Tempo por STD')           
    
        fig = sun_burst( df1 )
        
        st.plotly_chart(fig)
            
        
    with st.container():
        
        st.markdown("""---""")
        
        st.title('Distribuição da distância')
        
        df_aux = distruicao_distancia( df1 )
        
        st.dataframe(df_aux)

