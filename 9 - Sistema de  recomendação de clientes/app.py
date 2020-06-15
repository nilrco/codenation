import streamlit as st
import pandas as pd
import base64

import matplotlib.pyplot as plt

from joblib import load
from collections import Counter


def percent_common(recomendation, port, column):

    counter_recom = Counter(recomendation).most_common()
    counte_port = Counter(port[column]).most_common()

    percent_recom = counter_recom[0][1] / recomendation.shape[0] * 100
    column_recom = counter_recom[0][0]

    percent_port = counte_port[0][1] / port.shape[0] * 100
    column_port = counte_port[0][0]

    return column_port, round(percent_port, 2), column_recom, round(percent_recom)


def cluster_graph(X, centers, pred):
    st.markdown(
        "Exemplificando como nosso algoritmo separou os dados do portifolio de acordo com os grupos.")

    plt.scatter(X[pred == 0, 0],
                X[pred == 0, 2], s=50, color=['r'], label='Grupo 1')
    plt.scatter(X[pred == 1, 0],
                X[pred == 1, 2], s=50, color=['g'], label='Grupo 2')
    plt.scatter(X[pred == 2, 0],
                X[pred == 2, 2], s=50, color=['b'], label='Grupo 3')
    plt.scatter(X[pred == 3, 0],
                X[pred == 3, 2], s=50, color='purple', label='Grupo 4')
    plt.scatter(X[pred == 4, 0],
                X[pred == 4, 2], s=50, color=['y'], label='Grupo 5')
    plt.scatter(X[pred == 5, 0],
                X[pred == 5, 2], s=50, color=['m'], label='Grupo 6')
    plt.scatter(X[pred == 6, 0],
                X[pred == 6, 2], s=50, color=['c'], label='Grupo 7')
    plt.scatter(centers[:, 0], centers[:, 2], s=100,
                color=['k'], label='centroid')
    plt.legend()
    st.pyplot()


def model_load():
    model = load('modelo.pkl')

    return model


def load_data(filename, columns=None):

    if columns is None:
        dataframe = pd.read_csv(filename, index_col=(0))
    else:
        dataframe = pd.read_csv(filename, usecols=columns)

    dataframe.dropna(inplace=True)

    return dataframe


def recommend_customers(model, port, market, features):
    st.subheader("Começando as recomendações")

    X = model['pipe'].transform(port[features])
    pred = model['model'].predict(X)

    centers = model['model'].cluster_centers_
    common = Counter(pred).most_common()

    cluster_graph(X, centers, pred)

    labels = []
    if common[0][1] >= len(pred / 2):
        labels.append(common[0][0])
    else:
        labels.append(common[0][0])
        labels.append(common[1][0])

    recomendation = market[market['label'].isin(labels)]
    total = port['id'].count()

    predictions = pd.merge(port, recomendation, on='id',
                           how='inner')['id'].count()

    return (predictions / total * 100), recomendation


def download_link(df):

    if df.shape[0] > 150000:
        half_df = df.shape[0] / 2
        csv = df.loc[:half_df, :].to_csv(index=False)
        b64 = base64.b64encode(csv.encode()).decode()
        href = f'<a href="data:file/csv;base64,{b64}" download="recomendado.csv">Download das recomendações - parte 1</a>'
        st.markdown(href, unsafe_allow_html=True)
        csv = df.loc[half_df+1:, :].to_csv(index=False)
        b64 = base64.b64encode(csv.encode()).decode()
        href = f'<a href="data:file/csv;base64,{b64}" download="recomendado.csv">Download das recomendações - parte 2</a>'
        st.markdown(href, unsafe_allow_html=True)
    else:
        csv = df.to_csv(index=False)
        b64 = base64.b64encode(csv.encode()).decode()
        href = f'<a href="data:file/csv;base64,{b64}" download="recomendado.csv">Download das recomendações</a>'
        st.markdown(href, unsafe_allow_html=True)


def show_metrics(recomendation, market, port):
    st.subheader("Segue algumas analises das similaridades em algumas colunas")
    st.markdown(
        f"Foi recomendado: {round(recomendation.shape[0] / market.shape[0] * 100, 2)} % da lista total")

    columns = ['setor', 'de_nivel_atividade', 'sg_uf']
    for column in columns:

        common = percent_common(recomendation[column], port, column)
        st.markdown(column)
        st.markdown(f'Mais comum no porfólio é {common[0]} com um total de {common[1]}%')
        st.markdown(f'Mais comum nas recomendações é {common[2]} com um total de {common[3]}%')


def show_data(df, features):
    df = df[features]

    st.markdown("Abaixo algumas linhas dos dados:")
    st.dataframe(df.head(10))

    df_pivot = pd.DataFrame({
        'Tipos': df.dtypes,
        'Nulos': df.isna().sum(),
        '% Nulos': df.isna().sum() / df.shape[0],
        'Tamanho': df.shape[0],
        'Unicos': df.nunique()})

    st.markdown("Abaixo algumas analises dos dados:")
    st.dataframe(df_pivot.head(10))

    st.markdown("Caso o sistema encontre dados nulos ele ira realizar a imputação desse dados pois o modelo não trabalho com dados nulos.")


def explore_data(model, market, features):
    st.image("https://media.giphy.com/media/l4RKhOL0xiBdbgglFi/giphy.gif", width=500)
    st.markdown("Faça o upload dos seus dados para gerar as recomendações.")

    file = st.file_uploader("Escolha a base de dados que deseja analisar (.csv)", type='csv')
    data = None

    if file is not None:
        data = load_data(file)

    if data is not None:
        show_data(data, list(features))
        percentual, recomendation = recommend_customers(model, data, market, features)

        st.markdown("Segue alguns exemplos de recomendação do nosso sistema.")
        st.dataframe(recomendation.head(50))

        show_metrics(recomendation, market, data)

        download_link(recomendation)

    file = None


def explore_example(model, market, features):
    st.image("https://media.giphy.com/media/xUNd9N5zyIUXjBpfoc/giphy.gif", width=600)
    st.markdown("Abaixo temos alguns portifolios já preparados para você explorar e gerar recomendações.")

    options = ["Selecione", "Portifolio 1", "Portifolio 2", "Portifolio 3"]
    choice = st.selectbox('Selecione o Portifolio :', options)

    port_df = None

    if choice == "Portifolio 1":
        port_df = load_data('port1.csv')
    elif choice == "Portifolio 2":
        port_df = load_data('port2.csv')
    elif choice == "Portifolio 3":
        port_df = load_data('port3.csv')

    if port_df is not None:
        show_data(port_df, list(features))
        percentual, recomendation = recommend_customers(model, port_df, market, features)

        st.markdown("Segue alguns exemplos de recomendação do nosso sistema.")
        st.dataframe(recomendation.head(50))

        show_metrics(recomendation, market, port_df)

        download_link(recomendation)


def our_system(market):
    st.title("Sistema de Recomendação de Clientes")

    st.subheader("O que é nosso sistema ?")
    st.markdown("Esse é um sistema proprietario que se utiliza de determinada base de dados para realizar recomendações de cliente baseado em um portifólio de clientes já existentes, na nossa aplicação você podera explorar nossos exemplos ou gerar recomendações a partir dos seus dados.")

    st.image("https://media.giphy.com/media/pqDkpuv9pzTtRxAzYK/giphy.gif", width=600)
    st.markdown("Esse sistema não funciona de forma generica é necessario que a sua base de dados siga as mesmas premissas das bases de exemplo.")

    st.subheader("Como é realizada a recomendação ?")
    st.markdown("Nosso sistema utiliza conceitos de *Machine Learning* para realizar recomendações de clientes baseado no algoritmo não supervisionado *K-means*, abaixo uma exeplicação de como esse algotmo foi treinado e funciona.")

    st.markdown("Nosso sistema utiliza conceitos de *Machine Learning* para realizar recomendações de clientes baseado no algoritmo não supervisionado *K-means*, abaixo uma exeplicação de como esse algotmo foi treinado e funciona.")
    st.markdown("Apos o treinamento do nosso modelo ele separa os clientes em grupos, após essa separação em nossa base utilizamos do mesmo conceito em seu portifólio e ai *magica* acontece e recomendamos clientes com a similaridade aos que você já tem em seu portifólio.")

    st.markdown(
        "O grafico da uma ideia de como os grupos foram dividios pelo nosso algoritmo em nossa base de dados.")

    prob = market['label'].value_counts()
    prob.plot(kind='bar', color=['r', 'g', 'b', 'k', 'y', 'm', 'c'])

    plt.xlabel('Grupos')
    plt.xticks(rotation=25)

    st.pyplot()


def main():

    model = model_load()
    market = load_data('market_label.csv')

    columns = load_data('features.csv')
    features = list(columns['features'])

    st.sidebar.header("Recomendação de Clientes")
    n_sprites = st.sidebar.radio(
        "Escolha uma opção", options=["O sistema", "Explore nossos exemplos", "Recomendação com seus dados"], index=2
    )

    st.sidebar.markdown("Desenvolvido por: Nilson R. C. Oliveira")
    st.sidebar.markdown("LinkedIn: https://linkedin.com/in/nilrco")
    st.sidebar.markdown("Portifólio: https://github.com/nilrco")

    if n_sprites == "O sistema":
        our_system(market)
    elif n_sprites == "Explore nossos exemplos":
        explore_example(model, market, features)
    elif n_sprites == "Recomendação com seus dados":
        explore_data(model, market, features)


if __name__ == "__main__":
    main()
