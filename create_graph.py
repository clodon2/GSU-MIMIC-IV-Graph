import torch_geometric as tg
import networkx as nx
from pandas import DataFrame


def initialize_graphs(dataset_info:dict[str:DataFrame]):
    # load stuff here
    G = nx.Graph()
    for patient in dataset_info["icu_stays"]["subject_id"]:
        print(patient)
