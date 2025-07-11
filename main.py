import load_dataset
import create_graph
import networkx as nx
import matplotlib.pyplot as plt


dataset_file_path = "./mimic-iv/"


def draw_graph(graph):
    # Define colors for each node type
    color_map = {
        "patient": "lightgreen",
        "provider": "yellow",
        "procedure": "orange",
        "admission": "violet",
        "icu stay": "pink",
        "diagnosis": "red"
    }

    # Assign labels and colors
    labels = {}
    node_colors = []

    for node in graph.nodes:
        node_type = graph.nodes[node].get("type", "N/A")
        labels[node] = f"{node}\n({node_type})"
        node_colors.append(color_map.get(node_type, "gray"))  # default to gray

    # Layout and draw
    pos = nx.spring_layout(graph)
    nx.draw(
        graph,
        pos,
        labels=labels,
        with_labels=True,
        node_size=800,
        node_color=node_colors,
        font_size=8
    )
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    data_dict = load_dataset.load_dataset_files(dataset_file_path)
    ego_graphs = create_graph.create_ego_graphs(data_dict)

    draw_graph(create_graph.combine_graphs(ego_graphs))

    count = 0
    for patient, graph in ego_graphs.items():
        draw_graph(graph)
        count += 1
        if count >= 2:
            break