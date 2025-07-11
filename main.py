import load_dataset
import create_graph
import networkx as nx
import matplotlib.pyplot as plt


dataset_file_path = "./mimic-iv/"


def draw_graph(graph):
    # Label format: ID (type)
    labels = {
        node: f"{node}\n({graph.nodes[node].get('type', 'N/A')})"
        for node in graph.nodes
    }

    pos = nx.spring_layout(graph)
    nx.draw(
        graph,
        pos,
        labels=labels,
        with_labels=True,
        node_size=800,
        node_color="lightblue",
        font_size=8
    )
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    data_dict = load_dataset.load_dataset_files(dataset_file_path)
    ego_graphs = create_graph.create_ego_graphs(data_dict)

    draw_graph(ego_graphs[10098215])

    count = 0
    for patient, graph in ego_graphs.items():
        draw_graph(graph)
        count += 1
        if count >= 5:
            break