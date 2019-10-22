def bike_network_place(name):
    """Download the dedicated bicycle infrastructure graph from a named place.
    IMPORTANT:
    Make sure that the OSMnx configuration includes the following

    useful_tags = ox.settings.useful_tags_path + ['cycleway']
    ox.config(data_folder='../data', logs_folder='../logs',
              imgs_folder='../imgs', cache_folder='../cache',
              use_cache=True, log_console=True, useful_tags_path=useful_tags)

    Args:
        name (string or dict or list) – the place(s) to geocode/download data for

    Returns:
        nx.DiGraph: Networkx MultiDirected Graph.

    """
    G = ox.graph_from_place(name, network_type='all_private',
                            name=name, retain_all=True, simplify=False)
    non_cycleways = [(u, v, k) for u, v, k, d in G.edges(keys=True, data=True)
                     if not ('cycleway' in d or d['highway'] == 'cycleway')]
    G.remove_edges_from(non_cycleways)
    G = ox.simplify_graph(G)
    return ox.project_graph(G)


'''
Functions to run the algorithms in the paper:
Natera, Luis., Battiston, Federico., Iñiguez, Gerardo. Szell, Michael. Data-driven strategies for optimal bicycle network growth. 2019. arXiv:1907.07080
'''


def euclidean_dist_vec(y1, x1, y2, x2):
    '''
    Calculate the euclidean distance between two points.
    '''
    distance = ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5
    return distance


def get_data(G_bike, name, algorithm):
    """Main function to execute the different algorithms.

    Args:
        G_bike (nx.Graph): Bicycle network to use.
        name (str): Name of the city/network.
        algorithm (function): Function containing the main algorithm (L2C, L2S, CC, R2C).

    Returns:
        delta: List containing the Delta measure (meters) of newle added bicycle infrastructure.
        nodes_cc: List containing the number of nodes inside the Largest Connected Component at each step of the algorithm.
        length_cc: List containing the length (km) of the Largest Connected Component at each step of the algorithm
        i_s: List with the source of connections at each step of the algorithms.
        j_s: List with the target of connections at each step of the algorithms.
        G_bike: networkx graph conatining the newly created links
    """

    start = time.time()
    # 0.- Create lists to store data
    nodes_cc = []
    length_cc = []
    directness = []
    delta = []
    i_s = []
    j_s = []
    wcc = [cc for cc in nx.weakly_connected_component_subgraphs(G_bike)]

    # Save a 0 status
    length_cc.append(0)
    delta.append(0)
    nodes_cc.append(0)
    i_s.append(0)
    j_s.append(0)
    # Save original status
    wcc = [cc for cc in nx.weakly_connected_component_subgraphs(
        G_bike)]  # Get a list of the WCC
    wcc.sort(key=len, reverse=True)  # Sort the list from the largest to smallest
    nodes_cc.append(len(wcc[0]))
    l_temp = 0
    for e in wcc[0].edges(data=True):
        try:
            l_temp += e[2]['length']
        except:
            pass
    length_cc.append(l_temp/1000)
    delta.append(0)
    i_s.append(0)
    j_s.append(0)
    to_iterate = len(wcc)-1  # We'll iterate over n-1 connected components
    ncc = 0
    print('  + Starting the algorithm:')
    for cc in range(to_iterate):
        clear_output(wait=True)
        wcc = [cc for cc in nx.weakly_connected_component_subgraphs(
            G_bike)]  # Get a list of the WCC
        wcc.sort(key=len, reverse=True)  # Sort the list from the largest to smallest
        closest_ij = algorithm(wcc)  # Get the clossest pair of nodes between the two LCC's
        i_s.append(closest_ij['i'])  # Store the sequence of links connected
        j_s.append(closest_ij['j'])
        p_delta = delta[-1]  # Get the latest delta
        delta.append(p_delta+closest_ij['dist'])  # Add the new delta measure to the list of deltas
        # Record the new number of nodes inside the LCC after merging the two LCC's
        nodes_cc.append(len(wcc[0])+len(wcc[1]))
        l_temp = 0
        for e in wcc[0].edges(data=True):
            try:
                l_temp += e[2]['length']
            except:
                pass
        for e in wcc[1].edges(data=True):
            try:
                l_temp += e[2]['length']
            except:
                pass
        length_cc.append(l_temp/1000)
        if closest_ij['i'] != closest_ij['j']:
            G_bike.add_edge(closest_ij['i'], closest_ij['j'], length=0)  # closest_ij['dist'
        ncc += 1
        print('{} {}/{} done \nElapsed time {} min, avg. {} seg, \nTime to go: {} min.'.format(name, ncc, to_iterate,
                                                                                               round(
                                                                                                   (time.time() - start)/60, 2),
                                                                                               round(
                                                                                                   (time.time()-start)/ncc, 2),
                                                                                               round((((time.time()-start)/ncc)*(to_iterate-ncc))/60, 2)))
        if delta[-1] > 200000:
            break
    return delta, nodes_cc, length_cc, i_s, j_s, G_bike


def L2S(wcc):
    '''
    Find the closest pair of nodes between two different connected components.
    ---
    wcc: list connected components

    returns: dict nodes i and j and distance
    '''
    closest_pair = {'i': 0, 'j': 0, 'dist': np.inf}
    for i in wcc[0].nodes(data=True):
        i_coord = (i[1]['y'], i[1]['x'])
        for j in wcc[1].nodes(data=True):
            j_coord = (j[1]['y'], j[1]['x'])
            dist = euclidean_dist_vec(i_coord[0], i_coord[1], j_coord[0], j_coord[1])
            if dist < closest_pair['dist']:
                closest_pair['i'] = i[0]
                closest_pair['j'] = j[0]
                closest_pair['dist'] = dist
    return closest_pair


def L2C(wcc):
    """Find the closest pair of nodes between the two largest components.

    Parameters
    ----------
    wcc : list
        Sorted list that contains the components of graph G.

    Returns
    -------
    dict
        Dictionary with the nodes 'i' and 'j' and the distance between them.
    """
    closest_pair = {'i': 0, 'j': 0, 'dist': np.inf}
    for i in wcc[0].nodes(data=True):
        i_coord = (i[1]['y'], i[1]['x'])
        for cc in wcc[1:]:
            for j in cc.nodes(data=True):
                j_coord = (j[1]['y'], j[1]['x'])
                dist = euclidean_dist_vec(i_coord[0], i_coord[1], j_coord[0], j_coord[1])
                if dist < closest_pair['dist']:
                    closest_pair['i'] = i[0]
                    closest_pair['j'] = j[0]
                    closest_pair['dist'] = dist
    return closest_pair


def R2C(wcc):
    """
    Find the closest nodes between two connected component.

    wcc: List of weakly connected components
    """
    closest_pair = {'i': 0, 'j': 0, 'dist': np.inf}
    pick = random.choice(wcc)  # Pick a random component
    for i in pick.nodes(data=True):  # Pick a random component, iterate over its nodes
        i_coord = (i[1]['y'], i[1]['x'])
        for cc in wcc:
            if cc != pick:
                for j in cc.nodes(data=True):
                    j_coord = (j[1]['y'], j[1]['x'])
                    dist = euclidean_dist_vec(i_coord[0], i_coord[1], j_coord[0], j_coord[1])
                    if dist < closest_pair['dist']:
                        closest_pair['i'] = i[0]
                        closest_pair['j'] = j[0]
                        closest_pair['dist'] = dist
    return closest_pair


def CC(wcc):
    """
    Find the closest nodes between two connected component.

    wcc: List of weakly connected components
    """
    closest_pair = {'i': 0, 'j': 0, 'dist': np.inf}
    pick = random.choice(wcc)  # Pick a random component
    for cccc in combinations(wcc, 2):
        for i in cccc[0].nodes(data=True):
            i_coord = (i[1]['y'], i[1]['x'])
            for j in cccc[1].nodes(data=True):
                j_coord = (j[1]['y'], j[1]['x'])
                dist = euclidean_dist_vec(i_coord[0], i_coord[1], j_coord[0], j_coord[1])
                if dist < closest_pair['dist']:
                    closest_pair['i'] = i[0]
                    closest_pair['j'] = j[0]
                    closest_pair['dist'] = dist
    return closest_pair

    '''
    Plots
    '''


def plot_trips_over(G_city, trajectory, show=True):
    """Plot one trajectory over a city graph (OSMnx graph).

    Args:
        G_city (graph): City graph obtained from OSMnx.
        trajectory (type): Series of a dataframe containing one trajectory.
        show (bool): Select if show or not the plot.

    Returns:
        type: Description of returned object.

    """
    fig, ax = ox.plot_graph(G_city, node_color='#aaaaaa', node_size=0, show=False,
                            close=True, fig_height=20, edge_linewidth=0.1, bgcolor='w', edge_color='black')
    ax.plot(first_traj.latitude, first_traj.longitude, 'o-')
    if show == True:
        plt.show()
    return fig, ax
