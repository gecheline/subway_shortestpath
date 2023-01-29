import streamlit as st
import pandas as pd
import json
from io import StringIO
from utils import data_transform as dt
import networkx as nx
import matplotlib.pyplot as plt

st.set_page_config(
    page_title="Shortest path across subway map ",
    page_icon=":train2:",
)

st.header("Shortest path across subway map :train2:")

st.write("First, let's upload a subway map generated with https://jpwright.github.io/subway/ . This app is designed to work with the specific JSON format that this tool outputs!")

uploaded_file = st.file_uploader("Choose a file to upload")

if uploaded_file is not None:
    stringio = StringIO(uploaded_file.getvalue().decode("utf-8-sig"))
    data = json.load(stringio)
    data_new = dt.clean_data(data)
    lines_df = pd.DataFrame.from_dict(data_new['lines'])
    stations_df = pd.DataFrame.from_dict(data_new['stations'])
    st.write("Below is some of the info contained in the stations data pulled from the subway map:")
    st.write(stations_df[['id', 'name', 'lat', 'lng', 'lines']])

    nodelist, adj_set = dt.construct_nodelist_adjacency_set(stations_df, lines_df)

    G = nx.DiGraph()
    for node in nodelist.keys():
        G.add_node(node, pos=list(nodelist[node]))
    for node, neighbors in adj_set.items():
        for neighbor, weight in neighbors.items():
            G.add_edge(node, neighbor, weight=weight)
            G.add_edge(neighbor, node, weight=weight)

    st.write("Let's visualize the subway map as a graph, where each station represents a 'node', marked with a circle. The path between each pair of connected stations is represented by a graph 'edge', marked with lines. You'll notice that each edge has arrows pointing to each station. This is called a directed graph (the arrow signifies a direction). Here we've assumed that the subway goes in both directions between each pair of stations. An edge with an arrow pointing only one way would mean that there is only a one-way connection between two stations. We won't be dealing with those here for simplicity!")
    fig = plt.figure()
    nx.draw(G, pos=nodelist, with_labels=True)
    nx.draw_networkx_edges(G, pos=nodelist)
    st.pyplot(fig=fig)

    st.write("Now choose a pair of stations to calculate the shortest distance along the subway between.")
    col1, col2 = st.columns(2)
    with col1:
        start_station = st.selectbox('Choose a start station:', nodelist.keys())

    with col2:
        end_station = st.selectbox('Choose an end station:', nodelist.keys())

    if start_station != end_station:
        shortest_path = nx.dijkstra_path(G, start_station, end_station)

        shortest_path_edges = dt.make_path_edges(shortest_path)
        edge_colors = [(0,0,0,0) if edge not in shortest_path_edges else 'red' for edge in list(G.edges())]
        edges_alphas = [0.25 if edge not in shortest_path_edges else 1 for edge in list(G.edges())]
        fig2 = plt.figure()
        nodes = nx.draw_networkx_nodes(G, pos=nodelist)
        edges = nx.draw_networkx_edges(G, pos=nodelist, edge_color=edge_colors)
        M = G.number_of_edges()
        for i in range(M):
            edges[i].set_alpha(edges_alphas[i])


        st.pyplot(fig=fig2)


    
