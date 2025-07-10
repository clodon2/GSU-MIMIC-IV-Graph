import load_dataset
import create_graph


dataset_file_path = "./mimic-iv/"


if __name__ == "__main__":
    data_dict = load_dataset.load_dataset_files(dataset_file_path)
    ego_graphs = create_graph.create_ego_graphs(data_dict)