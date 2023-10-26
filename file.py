import pandas as pd
import networkx as nx
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
import folium

# Load the emails dataset
emails = pd.read_csv("./input/Emails.csv")

# Load the aliases dataset
aliases = pd.read_csv("./input/Aliases.csv")
alias_mapping = dict(zip(aliases['Alias'], aliases['PersonId']))

# Load the persons dataset
persons = pd.read_csv("./input/Persons.csv")
person_mapping = dict(zip(persons['Id'], persons['Name']))

# Function to unify names and aliases
def unify_name(name):
    name = str(name).lower().split("@")[0].replace(",", "")
    return person_mapping.get(alias_mapping.get(name, name), name)

# Create a directed graph
graph = nx.DiGraph()

# Iterate through the emails dataset and add edges with weights
for _, row in emails.iterrows():
    sender = unify_name(row['MetadataFrom'])
    receiver = unify_name(row['MetadataTo'])
    if graph.has_edge(sender, receiver):
        graph[sender][receiver]['weight'] += 1
    else:
        graph.add_edge(sender, receiver, weight=1)

# Calculate PageRank for each node and set it as an attribute
pagerank = nx.pagerank(graph)
nx.set_node_attributes(graph, pagerank, 'pagerank')

# Function to display the network graph using Plotly
def show_graph(graph):
    edge_x = []
    edge_y = []
    for edge in graph.edges():
        x0, y0 = edge[0], edge[1]
        edge_x.append(x0)
        edge_y.append(y0)

    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=0.5, color='#888'),
        hoverinfo='none',
        mode='lines')

    node_x = []
    node_y = []
    node_text = []
    for node in graph.nodes():
        x, y = node, graph.nodes[node]['pagerank']
        node_x.append(x)
        node_y.append(y)
        node_text.append(f'{node}<br>PageRank: {y:.3f}')

    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers',
        text=node_text,
        marker=dict(
            showscale=True,
            colorscale='YlGnBu',
            size=10,
            colorbar=dict(
                thickness=15,
                title='PageRank',
                xanchor='left',
                titleside='right'
            )
        )
    )

    fig = go.Figure(data=[edge_trace, node_trace],
                    layout=go.Layout(
                        showlegend=False,
                        hovermode='closest',
                        title="Hillary's Email Communication Network",
                        xaxis=dict(showgrid=False, zeroline=False),
                        yaxis=dict(showgrid=False, zeroline=False)
                    ))
    fig.show()

# Display the complete network graph using Plotly
show_graph(graph)

# Function to filter and display a simplified network graph using Plotly
def filter_and_show_graph(graph, threshold):
    filtered_graph = graph.copy()
    for node, data in graph.nodes(data=True):
        if data['pagerank'] < threshold:
            filtered_graph.remove_node(node)
    
    show_graph(filtered_graph)

# Display a simplified network graph with a pagerank threshold using Plotly
pagerank_threshold = 0.005
filter_and_show_graph(graph, pagerank_threshold)

# Data Visualization with Seaborn and Matplotlib
sns.set(style="whitegrid")
plt.figure(figsize=(10, 6))
sns.boxplot(x=[data['MetadataFrom'], data['MetadataTo']], y='pagerank', data=graph.nodes(data=True))
plt.xticks(rotation=45)
plt.title('Pagerank Distribution for Senders and Receivers')
plt.show()

# Create a Folium Map
m = folium.Map(location=[0, 0], zoom_start=1)
folium.Marker(location=[0, 0], tooltip="Hillary's Email Communication Network").add_to(m)
m.save("email_network_map.html")
