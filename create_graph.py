import networkx as nx
from pandas import DataFrame
import pandas as pd
import math
from tqdm import tqdm
from multiprocessing import Pool, cpu_count


global_dataset = None


def create_ego_graphs(dataset_info: dict[str, pd.DataFrame]):
    egos = {}

    icu_info = dataset_info["icu_stays"]["subject_id"].unique()
    icu_info = list(icu_info)

    dataset_info["admissions"] = dataset_info["admissions"].groupby("subject_id")
    dataset_info["drg_codes"] = dataset_info["drg_codes"].groupby("subject_id")
    dataset_info["icu_stays"] = dataset_info["icu_stays"].groupby("subject_id")
    dataset_info["procedures"] = dataset_info["procedures"].groupby("stay_id")

    with Pool(cpu_count() - 1, initializer=init_worker, initargs=(dataset_info,)) as p:
        pool_args = list(tqdm(
            p.imap(construct_ego_args, icu_info),
            total=len(icu_info),
            desc="constructing ego inputs"
        ))

    with Pool(cpu_count() - 1) as p:
        results = list(tqdm(
            p.starmap(create_patient_ego_graph, pool_args),
            total=len(pool_args),
            desc="generating ego graphs"
        ))

    for subject_id, graph in results:
        egos[subject_id] = graph

    return egos


def init_worker(dataset):
    global global_dataset
    global_dataset = dataset


def construct_ego_args(subject_info:tuple):
    subject_id = subject_info
    empty_adm = pd.DataFrame(columns=["hadm_id", "admittime", "admit_provider_id", "admission_type", "deathtime"])
    empty_drg = pd.DataFrame(columns=["hadm_id", "drg_type", "drg_code", "drg_severity", "drg_mortality"])
    empty_icu = pd.DataFrame(columns=["hadm_id", "stay_id", "los"])
    empty_procs = pd.DataFrame(columns=["stay_id", "caregiver_id", "locationcategory", "itemid", "value", "valueuom"])

    adm = global_dataset["admissions"].get_group(subject_id) if subject_id in global_dataset["admissions"].groups else empty_adm
    drg = global_dataset["drg_codes"].get_group(subject_id) if subject_id in global_dataset["drg_codes"].groups else empty_drg
    icu_stays = global_dataset["icu_stays"].get_group(subject_id) if subject_id in global_dataset["icu_stays"].groups else empty_icu
    stay_ids = icu_stays["stay_id"].unique()
    grouped_procs = global_dataset["procedures"]

    valid_stays = [stay for stay in stay_ids if stay in global_dataset["procedures"].groups]

    procedures = (
        pd.concat([grouped_procs.get_group(stay) for stay in valid_stays], axis=0)
        if valid_stays else empty_procs
    )

    admission_data = adm[["hadm_id", "admittime", "admit_provider_id", "admission_type", "deathtime"]]
    drg_data = drg[["hadm_id", "drg_type", "drg_code", "drg_severity", "drg_mortality"]]
    admission_data = pd.merge(admission_data, drg_data, on="hadm_id", how="left")

    stay_data = icu_stays[["hadm_id", "stay_id", "los"]]  if not icu_stays.empty else pd.DataFrame()
    procedures_data = procedures[["stay_id", "caregiver_id", "locationcategory", "itemid", "value", "valueuom"]]

    ego_dict = {"admissions": admission_data,
                "icu_stays": stay_data,
                "procedures": procedures_data}

    return subject_id, ego_dict



def create_patient_ego_graph(subject_id, data:dict[str:DataFrame]):
    G = nx.Graph()
    G.add_node(subject_id, type="patient")
    admissions = data["admissions"]
    icu_stays = data["icu_stays"]
    for index, row in admissions.iterrows():
        G.add_node(row["hadm_id"], type="admission", reason=row["admission_type"], death=row["deathtime"])
        G.add_edge(subject_id, row["hadm_id"])

        G.add_node(row["drg_code"], type="diagnosis", severity=row["drg_severity"], mortality=row["drg_mortality"])
        G.add_edge(row["hadm_id"], row["drg_code"])

        G.add_node(row["admit_provider_id"], type="provider")
        G.add_edge(row["hadm_id"], row["admit_provider_id"])

    for index, row in icu_stays.iterrows():
        G.add_node(row["stay_id"], type="icu stay", los=row["los"])
        G.add_edge(row["hadm_id"], row["stay_id"])

    for index, row in data["procedures"].iterrows():
        G.add_node(row["itemid"], type="procedure", value=row["value"], measurement=row["valueuom"],
                   location_category=row["locationcategory"])
        if not math.isnan(row["caregiver_id"]):
            G.add_node(row["caregiver_id"], type="provider")
            G.add_edge(row["itemid"], row["caregiver_id"])
        G.add_edge(row["stay_id"], row["itemid"])

    return subject_id, G


def combine_graphs(subgraphs:dict[int:nx.Graph]):
    return nx.compose_all(subgraphs.values())