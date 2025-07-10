import pandas as pd


def load_dataset_files(dataset_path):
    icu_stays_path = dataset_path + "/icu/icustays.csv"
    admissions_path = dataset_path + "/hosp/admissions.csv"
    drg_codes_path = dataset_path + "/hosp/drgcodes.csv"
    icu_stays = pd.read_csv(icu_stays_path)
    admissions = pd.read_csv(admissions_path)
    drg_codes = pd.read_csv(drg_codes_path)
    datasets = {"icu_stays":icu_stays,
                "admissions":admissions,
                "drg_codes":drg_codes}

    return datasets