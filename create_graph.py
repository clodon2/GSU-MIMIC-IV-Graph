import networkx as nx
from pandas import DataFrame
import pandas as pd


def create_ego_graphs(dataset_info: dict[str, pd.DataFrame]):
    egos = {}
    adm = dataset_info["admissions"]
    drg = dataset_info["drg_codes"]

    for subject_id, hadm_id, stay_id, los in dataset_info["icu_stays"][["subject_id", "hadm_id", "stay_id", "los"]].itertuples(index=False, name=None):
        admission_data = adm.loc[adm["subject_id"] == subject_id, ["hadm_id", "admittime", "admit_provider_id"]]
        drg_data = drg.loc[drg["subject_id"] == subject_id, ["hadm_id", "drg_type", "drg_code", "drg_severity", "drg_mortality"]]
        admission_data = pd.merge(admission_data, drg_data, on="hadm_id", how="left")
        patient_ego = create_patient_ego_graph(subject_id, admission_data)
        egos[subject_id] = patient_ego

    return egos


def create_patient_ego_graph(subject_id, data:DataFrame):
    G = nx.Graph()
    G.add_node(subject_id, type="patient")
    for index, row in data.iterrows():
        G.add_node(row["hadm_id"], type="admission")
        G.add_edge(subject_id, row["hadm_id"])
        G.add_node(row["drg_code"], type="diagnosis")
        G.add_edge(row["hadm_id"], row["drg_code"])

    return G
