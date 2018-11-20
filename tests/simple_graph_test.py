from simple_graph import Graph


def test_construct_simple_graph():
    """
    happy path test for constructing a Graph
    """
    g = Graph()
    g.add_node("A")
    g.add_node("B")
    g.add_node("C")

    g.add_edge("B", "A", 1.0)
    g.add_edge("A", "B", 2.0)
    g.add_edge("C", "B", -1.0)
    g.add_edge("B", "C", 5.0)

    assert {"C": 5.0, "A": 1.0} == g.get_node("B").get_neighbors()
    assert {"B": 2.0} == g.get_node("A").get_neighbors()
    assert {"B": -1.0} == g.get_node("C").get_neighbors()


def test_eq():
    g = Graph()
    g.add_node("A")
    g.add_node("B")
    g.add_node("C")

    g.add_edge("B", "A", 1.0)
    g.add_edge("A", "B", 2.0)
    g.add_edge("C", "B", -1.0)
    g.add_edge("B", "C", 5.0)

    # Construct in different order, both keys and values for a given key (B->C, B->A, in this case)
    h = Graph()
    h.add_node("C")
    h.add_node("A")
    h.add_node("B")

    h.add_edge("A", "B", 2.0)
    h.add_edge("B", "C", 5.0)
    h.add_edge("B", "A", 1.0)
    h.add_edge("C", "B", -1.0)

    assert g == h
