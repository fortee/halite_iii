def dijkstra(graph, src):
    """
    Following's Skiena's Algorithm Design manual, ch. 6.3. This finds shortest path from src to all other nodes. I don't
    think this is what I want for halite, but should be a good start.

    :param graph:
    :param src:
    :return:

    TODO: Sec 6.3.2 "All-Pairs shortest path may be optimal for deploying drop-offs
    """

    intree = {}
    distance = {}
    parent = {}

    for i in range(0, graph.get_node_count()):
        intree[i] = False
        distance[i] = float('inf')
        parent[i] = -1

    distance[src] = 0
    v = src

    while intree[v] is False:
        intree[v] = True
        for p in v.get_neighbors():
            weight = v.get_weight(p)
            if distance[p] > distance[src] + weight:
                distance[p] = distance[src] + weight
                parent[p] = v
