import streamlit as st
import pandas as pd
import json
from io import StringIO
from utils import data_transform as dt
import networkx as nx
import matplotlib.pyplot as plt

st.set_page_config(
    page_title="Shortest path across subway map ",
    page_icon="train2"
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
    edges_list = []
    for index, line in lines_df.iterrows():
        edges_list.append(dt.make_path_edges(line['stations']))
    lines_df['edges_set'] = edges_list

    st.write("Below is some of the info contained in the stations data pulled from the subway map:")
    st.write(stations_df[['id', 'name', 'lat', 'lng', 'lines']])

    nodelist, node_sizes, adj_set = dt.construct_nodelist_adjacency_set(stations_df, lines_df)

    G = nx.DiGraph()
    posList = {}
    for node in nodelist.keys():
        [lat, lng] = list(nodelist[node])
        posList[node] = [lng,lat] 
        G.add_node(node, pos=[lng,lat])

    for node, neighbors in adj_set.items():
        for neighbor, weight in neighbors.items():
            G.add_edge(node, neighbor, weight=weight)
            G.add_edge(neighbor, node, weight=weight)

    edges_widths = []
    edges_colors = []
    for edge in list(G.edges):
        colors_list = []
        for index, line in lines_df.iterrows():
            if edge in line['edges_set'] or edge[::-1] in line['edges_set']:
                colors_list.append(line['color_bg'])

        edges_widths.append(5*len(colors_list))
        edges_colors.append('lightgrey' if len(colors_list)>1 else colors_list[0])

    st.write("To implement algorithms for shortest path calculation, we need to transform this data into a more computer-understandable format, like an adjacency matrix or set. [Here](https://medium.com/outco/how-to-build-a-graph-data-structure-d779d822f9b4) you can read more about what these formats look like. We'll use the adjacency set format here, in which each station has associated with it its neighbors and the distances to each:")
    st.write(adj_set)

    st.write("Now we can use the adjacency set to visualize the subway map as a graph, where each station represents a 'node', marked with a circle. The path between each pair of connected stations is represented by a graph 'edge', marked with lines. You'll notice that each edge has arrows pointing to each station. This is called a directed graph (the arrow signifies a direction). Here we've assumed that the subway goes in both directions between each pair of stations. An edge with an arrow pointing only one way would mean that there is only a one-way connection between two stations. We won't be dealing with those here for simplicity!")
    fig = plt.figure(figsize=(20,10))
    nx.draw_networkx_nodes(G, pos=posList, node_size=node_sizes, node_color='cornflowerblue')
    nx.draw_networkx_labels(G, pos=posList, font_color='white')
    
    nx.draw_networkx_edges(G, pos=posList, edge_color=edges_colors, width=edges_widths, arrowstyle='->', arrowsize=15)
    st.pyplot(fig=fig)

    st.write("Now choose a pair of stations between which to calculate the shortest distance along the subway graph. The code implemented here uses Dijkstra's algorithm, a classic method for finding the shortest path along the graph. You can learn more about it through this [simulation](https://algorithms.discrete.ma.tum.de/graph-algorithms/spp-dijkstra/index_en.html). Keep in mind that this algorithm only knows about the graph nodes, edges and the distances along each edge measured in angular distance (we compute this using the latitude and longitude of each station). It's not aware of the specific subway lines so sometimes it may lead to several unnecessary transfers! Can you think of how we can improve or penalize it to lead to less transfers?")
    col1, col2 = st.columns(2)
    with col1:
        start_station = st.selectbox('Choose a start station:', nodelist.keys())

    with col2:
        end_station = st.selectbox('Choose an end station:', nodelist.keys())

    if start_station != end_station:
        shortest_path = nx.dijkstra_path(G, start_station, end_station)
        shortest_path_length = nx.dijkstra_path_length(G, start_station, end_station)

        shortest_path_edges = dt.make_path_edges(shortest_path)
        edge_colors = [(0,0,0,0) if edge not in shortest_path_edges else 'red' for edge in list(G.edges())]
        edges_alphas = [0.1 if edge not in shortest_path_edges else 1 for edge in list(G.edges())]

        fig2 = plt.figure(figsize=(20,10))
        nodes = nx.draw_networkx_nodes(G, pos=posList, node_size=node_sizes, node_color='cornflowerblue')
        node_labels = nx.draw_networkx_labels(G, pos=posList, font_color='white')
        edge_labels = dict([((u,v,), f"{d['weight']:.4f}") for u,v,d in G.edges(data=True)])
        # edge_labels = nx.get_edge_attributes(G,'weight')
        edges = nx.draw_networkx_edges(G, pos=posList, edge_color=edges_colors, width=edges_widths, arrowstyle='->', arrowsize=15)

        M = G.number_of_edges()
        for i in range(M):
            edges[i].set_alpha(edges_alphas[i])

        nx.draw_networkx_edge_labels(G,pos=posList,edge_labels=edge_labels, bbox={'boxstyle':'round', 'ec':(1.0, 1.0, 1.0, 0.0), 'fc':(1.0, 1.0, 1.0, 0.0)})


        st.pyplot(fig=fig2)
        st.write(f"Shortest path length: {shortest_path_length}")


    
