import pandas as pd


def load_dataset_files(dataset_path):
    icu_stays_path = dataset_path + "/icu/icustays.csv"
    procedures_path = dataset_path + "./icu/procedureevents.csv"
    admissions_path = dataset_path + "/hosp/admissions.csv"
    drg_codes_path = dataset_path + "/hosp/drgcodes.csv"
    icu_stays = pd.read_csv(icu_stays_path)
    procedures_path = pd.read_csv(procedures_path)
    admissions = pd.read_csv(admissions_path)
    # skiprows because we only need APR diagnosis type
    drg_codes = pd.read_csv(drg_codes_path, skiprows=lambda x: x % 2 != 0)
    datasets = {"icu_stays":icu_stays,
                "admissions":admissions,
                "drg_codes":drg_codes,
                "procedures":procedures_path}

    return datasets