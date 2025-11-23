# -*- coding: utf-8 -*-
"""
Created on Thu Nov 20 10:11:09 2025

@author: Anaconda
"""

import streamlit as st
import requests
import pandas as pd
import plotly.express as px




# Definir como padro a pagida web extendida, não apenas no centro
st.set_page_config(layout='wide')

# Função para formatar os valores que serão usados nas metricas
def formata_numero(valor, prefixo = ''):
    for unidade in ['', 'mil']:
        if valor <1000:
            return f'{prefixo}{valor:.2f}{unidade}' # formata com mil
        valor /= 1000 # divide por mil e susbstitui a variavel
    return f'{prefixo}{valor:.2f} milhões'


# inserindo um titulo
st.title("DASHBOARD DE VENDAS  🛒 ")

## CARREGANDO OS DADOS EM CACHE

url = 'https://labdados.com/produtos'
# criar uma lista para selecionar o filtro por região com select box
regioes = ["Brasil", "Centro-Oeste", "Nordeste", "Norte", "Sudeste", "Sul"]
# criando a barra lateral e o titulo dela (valerá para as três abas)


st.sidebar.title("Filtros")

#  criar variavel para armazenar a seleção do select box
regiao = st.sidebar.selectbox('Região', (regioes))
if regiao == 'Brasil': #temos que separar o Brasil pois não é filtro é tudo
    regiao = ''   
 
#  Filtro por anos se quer selecionar o ano ou todos os anos
todos_anos = st.sidebar.checkbox('Dados de todo o período', value = True) # por padrão todos os anos  
if todos_anos:   # se vire default
    ano='' # ou seja se estiver marcado nenhuma filtragem
else:
    ano = st.sidebar.slider('Ano', 2020, 2023) # titulo, min e max
# Dicionario para personalizar a URL (seleção por ano dos dados de origem)
query_string = {'regiao':regiao.lower(),'ano':ano} 
# requisição para obter os dados com base nas variaveis

response = requests.get(url, params=query_string) 
dados = pd.DataFrame.from_dict(response.json())
dados['Data da Compra'] = pd.to_datetime(dados['Data da Compra'], format = '%d/%m/%Y')

# aqui vamos criar os filtros
filtro_vendedores = st.sidebar.multiselect('Vendedores', dados['Vendedor'].unique()) # Filtro com os nomes dos vendedores do unique do pandas
if filtro_vendedores: # se vier desmarcado
    dados = dados['Vendedor'].isin(filtro_vendedores)
    


# https://docs.streamlit.io/develop/api-reference


## TABELAS 

# Receita por estado (aba 1)
receita_estados = dados.groupby('Local da compra')[['Preço']].sum()
# Ao agregar perdemos a informação de coordenadas

# Unir duas tabela (aba 1)
receita_estados = dados.drop_duplicates(subset='Local da compra')[['Local da compra', 'lat', 'lon']].merge(receita_estados, left_on = 'Local da compra', right_index = True).sort_values('Preço', ascending = False)

# Criando tabela para o Mapa (aba 1)

receita_mensal = dados.set_index('Data da Compra').groupby(pd.Grouper(freq = 'M'))['Preço'].sum().reset_index()
receita_mensal['Ano'] = receita_mensal['Data da Compra'].dt.year
receita_mensal['Mes'] = receita_mensal['Data da Compra'].dt.month_name()

# Tabela para receita por categoria

receita_categorias = dados.groupby('Categoria do Produto')[['Preço']].sum().sort_values('Preço', ascending = False)


# Quantidade de vendas Por vendedor (aba 3)

# agg permite fazer agregação por soma e contagem ao mesmo tempo 
vendedores = pd.DataFrame(dados.groupby('Vendedor')['Preço'].agg(['sum','count']))



# vendas por estado (aba 2)

vendas_estados = pd.DataFrame(dados.groupby('Local da compra')['Preço'].count())
vendas_estados = dados.drop_duplicates(subset = 'Local da compra')[['Local da compra','lat', 'lon']].merge(vendas_estados, left_on = 'Local da compra', right_index = True).sort_values('Preço', ascending = False)

# quantidade de vendas mensal (aba 2)

vendas_mensal = pd.DataFrame(dados.set_index('Data da Compra').groupby(pd.Grouper(freq = 'M'))['Preço'].count()).reset_index()
vendas_mensal['Ano'] = vendas_mensal['Data da Compra'].dt.year
vendas_mensal['Mes'] = vendas_mensal['Data da Compra'].dt.month_name()

# uantidade de vendas por categoria de produtos (aba 2)
vendas_categorias = pd.DataFrame(dados.groupby('Categoria do Produto')['Preço'].count().sort_values(ascending = False))


## GRAFICOS

# Usando o Plotly Mapa  (aba 1)
fig_mapa_receita = px.scatter_geo(receita_estados,
                                  lat = 'lat',
                                  lon = 'lon',
                                  scope= 'south america',
                                  size = 'Preço',
                                  template = 'seaborn',
                                  hover_name = 'Local da compra', # cria balao com nome
                                  hover_data = {'lat': False, 'lon': False},
                                  title = 'Receita por Estado')


# Usando o Plotly linha (aba 1)
fig_receita_mensal = px.line(receita_mensal,
                             x = 'Mes',
                             y = 'Preço',
                             markers= True,
                             range_y= (0, receita_mensal.max()),
                             color= 'Ano',
                             line_dash= 'Ano',
                             title= 'Receita Mensal')
fig_receita_mensal.update_layout(yaxis_title= 'Receita')


# Usando o Plotly Barras (aba 1)
fig_receita_estados = px.bar(receita_estados.head(),
                             x = 'Local da compra',
                             y = 'Preço',
                             text_auto = True,
                             title = 'Top estados (receita)')
fig_receita_estados.update_layout(yaxis_title= 'Receita')


# Usando o Plotly Barras - categorias (aba 1)

fig_receita_categorias = px.bar(receita_categorias,
                             text_auto = True,
                             title = 'Receita por Categoria')
fig_receita_categorias.update_layout(yaxis_title= 'Receita')


# Quantidade de vendas por estado (aba 2)

fig_mapa_vendas = px.scatter_geo(vendas_estados, 
                     lat = 'lat', 
                     lon= 'lon', 
                     scope = 'south america', 
                     #fitbounds = 'locations', 
                     template='seaborn', 
                     size = 'Preço', 
                     hover_name ='Local da compra', 
                     hover_data = {'lat':False,'lon':False},
                     title = 'Vendas por estado',
                     )

# Quantidade de vendas mensal (aba 2)
fig_vendas_mensal = px.line(vendas_mensal, 
              x = 'Mes',
              y='Preço',
              markers = True, 
              range_y = (0,vendas_mensal.max()), 
              color = 'Ano', 
              line_dash = 'Ano',
              title = 'Quantidade de vendas mensal')

fig_vendas_mensal.update_layout(yaxis_title='Quantidade de vendas')


# 5 estados com maior quantidade de vendas (aba 2)

fig_vendas_estados = px.bar(vendas_estados.head(),
                             x ='Local da compra',
                             y = 'Preço',
                             text_auto = True,
                             title = 'Top 5 estados'
)

fig_vendas_estados.update_layout(yaxis_title='Quantidade de vendas')

# Quantidade de vendas por categoria de produto (aba 2)

fig_vendas_categorias = px.bar(vendas_categorias, 
                                text_auto = True,
                                title = 'Vendas por categoria')
fig_vendas_categorias.update_layout(showlegend=False, yaxis_title='Quantidade de vendas')




## VISUALIZAÇÃO NO STREAMLIT

# Criando abas para painel
aba1, aba2, aba3 = st.tabs(['Receita', 'Quantidade de Vendas', "Vendedores"])

# para poulara as ABA segue o mesmo conceito das colunas uso do WITH
with aba1:
    
    # Usando os conceitos de colunas e layouts
    coluna1, coluna2 = st.columns(2)
    
    with coluna1:
        # Adicionar uma metrica (ex. receita total, quantidade dae vendas,...)
        st.metric('Receita',formata_numero(dados['Preço'].sum(), 'R$'))
        st.plotly_chart(fig_mapa_receita, use_container_width=True)
        st.plotly_chart(fig_receita_estados, use_container_width=True)    
        
    with coluna2:
        st.metric('Quantidade de Vendas', formata_numero(dados.shape[0])) 
        # shape retorna numero de registros que corresponde a quantidade de
        # vendas
        st.plotly_chart(fig_receita_mensal, use_container_width=True)
        st.plotly_chart(fig_receita_categorias, use_container_width=True) 

        # O uso do , use_container_width=True serve para não deixar o grafico sair do limite da coluna

with aba2:
    coluna1, coluna2 = st.columns(2)
    with coluna1:
        st.metric('Receita', formata_numero(dados['Preço'].sum(), 'R$'))
        st.plotly_chart(fig_mapa_vendas, use_container_width = True)
        st.plotly_chart(fig_vendas_estados, use_container_width = True)

    with coluna2:
        st.metric('Quantidade de vendas', formata_numero(dados.shape[0]))
        st.plotly_chart(fig_vendas_mensal, use_container_width = True)
        st.plotly_chart(fig_vendas_categorias, use_container_width = True)

with aba3:
    # entrada de valor min 2 max 10, 5 valor padrão
    qtd_vendedores = st.number_input('Quantidade de vendedores', 2, 10, ) 
   


    # Usando os conceitos de colunas e layouts
    coluna1, coluna2 = st.columns(2)
    
    with coluna1:
        # Adicionar uma metrica (ex. receita total, quantidade dae vendas,...)
        st.metric('Receita',formata_numero(dados['Preço'].sum(), 'R$'))
        # grafico precisa ser chamado aqui poi vai utilizar o valor do imput
        # apenas a quantidade de vendedores do input
        fig_receita_vendedores = px.bar(vendedores[['sum']].sort_values('sum', ascending = False).head(qtd_vendedores),
                                        x= 'sum',
                                        y = vendedores[['sum']].sort_values('sum', ascending = False).head(qtd_vendedores).index,
                                        text_auto= True, # os valores da recieta em cada uma das barras
                                        title = f'Top {qtd_vendedores} vendedores (receita)') # titulo personalisado com base na quantidade de vendedores
        st.plotly_chart(fig_receita_vendedores)
        
    with coluna2:
        st.metric('Quantidade de Vendas', formata_numero(dados.shape[0])) 
        # shape retorna numero de registros que corresponde a quantidade de
        # vendas
        fig_vendas_vendedores = px.bar(vendedores[['count']].sort_values('count', ascending = False).head(qtd_vendedores),
                                        x= 'count',
                                        y = vendedores[['count']].sort_values('count', ascending = False).head(qtd_vendedores).index,
                                        text_auto= True, # os valores da recieta em cada uma das barras
                                        title = f'Top {qtd_vendedores} vendedores (quantidade de vendas)') # titulo personalisado com base na quantidade de vendedores
        st.plotly_chart(fig_vendas_vendedores)





# para mostrar a tabela com os dados o DataFrame
# st.dataframe(dados)



# inserir um grafico de mapa (já tem as coordenadas no data frame)
# fazer bolhas de tamnha por venda

# tabela agregada por estado





## TAMANHO DAS COLUNAS

# se o usuário especificar st.columns(2), isso criará duas colunas
# iguais. Caso seja passada uma lista de valores, será criada uma
# coluna para cada valor da lista, com tamanho proporcional ao valor
# fornecido. Por exemplo, st.columns([3,1]) cria duas colunas, com a
# primeira coluna sendo 3 vezes maior que a segunda.




## METRICAS

# Para exibir métricas existem algumas opções de parâmetros para essa função:

# label: o rótulo ou título da métrica;

# value: o valor da métrica, podendo ser um número ou uma string;

# delta: indicador de como a métrica se alterou. Caso o valor seja 
# positivo, será mostrado o valor e uma seta verde para cima, indicando
# que a métrica cresceu. Se for negativo, será mostrado o valor e uma seta 
# vermelha para baixo, indicando que a métrica diminuiu;

# delta_color: permite alterar a cor da variação da métrica. Se colocado 
# como 'normal', que é o valor padrão do parâmetro, será colocado verde 
# para valores positivos e vermelho para negativos. Se colocado como 
# 'inverse', as cores verde e vermelha serão invertidas. Se colocado como 
# 'off', a cor será cinza;

# help: texto informativo que pode ser colocado para explicar sobre a 
# métrica. Ele aparece como uma tooltip, ou seja, um texto que só é 
# mostrado caso o mouse esteja sobreposto ao ícone de ajuda;

# label_visibility: define a visibilidade do rótulo. Pode ser colocado 
# como 'visible' para manter a visibilidade, 'hidden' para deixar oculto 
# mantendo o espaço que contém o texto, ou 'collapsed' para deixar oculto 
# o rótulo e também remover o espaço destinado ao texto.



## VIDEOS E IMAGENS

# O método st.image() suporta diversos formatos de imagem, como JPEG,
# PNG e GIF, permite redimensionar e cortar imagens, e também permite
# exibir legendas. Já o método st.video() suporta diversos formatos de
# vídeo, como MP4 e WebM, assim como a reprodução de vídeos de URL
# externas.



## CONFIGURACAO DA PAGINA

# lista com parâmetros que podem ser utilizados.

# page_title: define o título da página que será mostrado na aba do
# navegador.

# page_icon: define um ícone para a página que será mostrado na aba do
# navegador. Pode ser uma imagem, uma url contendo uma imagem ou um
# emoji.

# layout: modifica o formato de visualização do aplicativo. O padrão
# é 'centered', que posiciona os elementos centralizados em uma
# coluna de tamanho fixo, mas pode ser trocado para 'wide', que
# utiliza todo o espaço da tela.

# initial_sidebar_state: estado inicial da barra lateral. O valor
# padrão é 'auto', que oculta a barra lateral em dispositivos móveis.
# Pode ser alterado para 'expanded' para sempre iniciar com a barra
# lateral à mostra ou 'collapsed' para sempre iniciar com a barra
# lateral oculta.

# menu_items: configura, a partir de um dicionário de chave-valor, o
# menu que aparece no topo superior direito do aplicativo. Podem ser
# alteradas 3 opções do menu:
    
#'Get help': altera a página de ajuda do aplicativo, bastando passar
# uma URL;
#'Report a bug': altera a página de reportar um bug no aplicativo,
# bastando passar uma URL;
# 'About': altera um texto de informação sobre a página, bastando
# passar uma string em markdown.



