# Import dependencies
import streamlit as st
import streamlit.components.v1 as components #to display the HTML code
import pandas as pd
import networkx as nx #Networkx for creating graph data
from pyvis.network import Network #to create the graph as an interactive html object

def data_load():
    flights_df = pd.read_csv("data/flights_df_1000.csv", usecols = ["ORIGIN_AIRPORT", "DESTINATION_AIRPORT","YEAR"])
    print(f"Original dataset size: {flights_df.size}") #this dataset is quite big 
    flights_df1=flights_df[(flights_df.DESTINATION_AIRPORT.str.len()<=3)&(flights_df.ORIGIN_AIRPORT.str.len()<=3)]
    print(f"Working dataset size: {flights_df1.size}") #this dataset is quite big
    return flights_df1


def data_proc(df):
    df_between_airports = df.groupby(by=["ORIGIN_AIRPORT", "DESTINATION_AIRPORT"]).count().reset_index()
    df_between_airports.rename(columns={"YEAR":"N_fligths"}, inplace=True)
    df_between_airports.sort_values(by="N_fligths", ascending=False, inplace=True)
    df_between_airports['Perc']=df_between_airports["N_fligths"]/df_between_airports.shape[0] #the Nflights has been normalized 
    return df_between_airports

def makeEdgeTitle(x):
    return "N_flights: "+str(x)

def setGraphData(df):
    #node_sizes=df.groupby("ORIGIN_AIRPORT").count()["N_fligths"]
    # get all the nodes from the two columns
    nodes = list(set([*df['ORIGIN_AIRPORT'], 
                  *df['DESTINATION_AIRPORT']
                 ]))
    # extract the size of each airport
    #values = [node_sizes[node] for node in nodes]
    #values=[int(item) for item in values]
    #values = [int(node_sizes.loc[node_sizes.index==node]) for node in nodes]
    
    df["edge_titles"]=df["N_fligths"].apply(makeEdgeTitle)
    # extract the edges between airports
    edges = df.loc[:,["ORIGIN_AIRPORT", "DESTINATION_AIRPORT"]].values.tolist()   
    
    return nodes,edges
    
    

def buildGraph(nodes,edges,selected_origin_airports):
    netFlights = Network(
                bgcolor ="#242020",
                font_color = "white",
                height = "1000px",
                width = "100%",
                directed = True)
    
    # initialize graph
    g = nx.DiGraph()
    # add the nodes
    g.add_nodes_from(nodes) # !!! not netFlights.add_nodes(nodes)
    print(g.nodes)
    # add the edges
    g.add_edges_from(edges) # !!! not netFlights.add_edges(edges)
    print(g.edges)
    # generate the graph
    netFlights.from_nx(g)    
    
    netFlights.save_graph('L1_Network_of_flights.html')
    st.header(f'Lab1. Building Interactive Network of flights from {selected_origin_airports}')
    HtmlFile = open(f'L1_Network_of_flights.html', 'r', encoding='utf-8')
    # Load HTML file in HTML component for display on Streamlit page
    components.html(HtmlFile.read(), height = 1200,width=1000)
    
    

def main():
    flights_df=data_load()
    df_between_airports=data_proc(flights_df)
    #nodes,edges=setGraphData(df_between_airports)
    
    # Set header title
    st.title('Network Graph Visualization - lab1. Example')
    origin_airports=df_between_airports['ORIGIN_AIRPORT'].unique().tolist()
    origin_airports.sort()
    
    # Implement multiselect dropdown menu for option selection
    selected_origin_airports = st.multiselect('Select origin airports to visualize', origin_airports)
    # Set info message on initial site load
    if len(selected_origin_airports) == 0:
        st.text('Please choose at least 1 origin airport to get started')
        # Create network graph when user selects >= 1 item
    else:
        df_select = df_between_airports.loc[df_between_airports['ORIGIN_AIRPORT'].isin(selected_origin_airports)]
        df_select = df_select.reset_index(drop=True)
        st.dataframe(df_select.loc[:, ['ORIGIN_AIRPORT', 'DESTINATION_AIRPORT', 'N_fligths']], hide_index=True)
        nodes,edges=setGraphData(df_select)
        #st.text(nodes)
        buildGraph(nodes,edges,selected_origin_airports)
        #flight_net.save_graph('L1_Network_of_flights.html')
        #HtmlFile = open(f'L1_Network_of_flights.html', 'r', encoding='utf-8')
        # Load HTML file in HTML component for display on Streamlit page
        #components.html(HtmlFile.read(), height=1000)
        
        


        
if __name__ == '__main__':
    main()
    
    
    
    
    
    

    
    
