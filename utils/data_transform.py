import numpy as np
import pandas as pd


def clean_data(data_json):
    new_data = {}
    new_data['lines'] = []
    new_data['stations'] = data_json['stations']

    for line in data_json['lines']:
        if len(line['stations']) == 0:
            pass
        else:
            new_data['lines'].append(line)
    return new_data

def find_neighbors_and_distances(station, lines_df, stations_df):
    neighbors = {}
    station_coords = station[['lat','lng']].values

    for line in station['lines']:
        line_info_stations = lines_df[lines_df['id']==line]['stations'].values[0]
        station_arg = line_info_stations.index(station['id'])

        if station_arg - 1 >= 0:
            left_station_id = line_info_stations[station_arg-1]
            left_station = stations_df[stations_df['id']==left_station_id]
            left_station_coords = stations_df[stations_df['id']==left_station_id][['lat', 'lng']].values
            left_station_distance = np.sum((station_coords - left_station_coords)**2)
            neighbors[left_station_id] = left_station_distance
        if station_arg + 1 < len(line_info_stations):
            right_station_id = line_info_stations[station_arg+1]
            right_station = stations_df[stations_df['id']==right_station_id]
            right_station_coords = stations_df[stations_df['id']==right_station_id][['lat', 'lng']].values
            right_station_distance = np.sum((station_coords - right_station_coords)**2)
            neighbors[right_station_id] = right_station_distance

    return neighbors

def construct_nodelist_adjacency_set(stations_df, lines_df):
    nodelist = {}
    adjacency_set = {}
    for index, station in stations_df.iterrows():
        if station['active']:
            nodelist[station['id']] = station[['lat', 'lng']].values
            adjacency_set[station['id']] = find_neighbors_and_distances(station, lines_df, stations_df)
    return nodelist, adjacency_set

def make_path_edges(shortest_path):
    edges = []
    for i in range(0,len(shortest_path)-1):
        edges.append((shortest_path[i], shortest_path[i+1]))

    return edges

