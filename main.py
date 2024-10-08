import os

from icecream import ic
from loguru import logger

from src.Dataset import Dataset
from src.collect_data import load_and_save_catalog_models, generate_list_models_data_csv, query_models
from src.load_models_data import instantiate_models_from_csv
from src.save_datasets_statistics_to_csv import save_datasets_statistics_to_csv

CATALOG_PATH = "C:/Users/FavatoBarcelosPP/Dev/ontouml-models"
BASE_OUTPUT_DIR = "./outputs"
OUTPUT_DIR_01 = os.path.join(BASE_OUTPUT_DIR, "01_loaded_data")
OUTPUT_DIR_02 = os.path.join(BASE_OUTPUT_DIR, "02_datasets")


def load_data_from_catalog(catalog_path):
    """Load and save catalog models, and generate a CSV for model data."""
    all_models = load_and_save_catalog_models(catalog_path, os.path.join(BASE_OUTPUT_DIR, "01_loaded_data/"))
    generate_list_models_data_csv(all_models, os.path.join(OUTPUT_DIR_01, "models_data.csv"))
    return all_models


def query_data(all_models):
    """Query class and relation stereotypes data for all models."""
    query_models(all_models, "queries", os.path.join(BASE_OUTPUT_DIR, "01_loaded_data/"))


def create_specific_datasets_instances(models_list, suffix: str = ""):
    """Create datasets based on classroom and non-classroom models."""

    datasets = []
    datasets.append(Dataset("ontouml_all", models_list))

    ontouml_classroom = [model for model in models_list if model.is_classroom]
    datasets.append(Dataset("ontouml_classroom", ontouml_classroom))

    ontouml_non_classroom = [model for model in models_list if not model.is_classroom]
    datasets.append(Dataset("ontouml_non_classroom", ontouml_non_classroom))

    ontouml_non_classroom_until_2018 = [model for model in ontouml_non_classroom if model.year <= 2018]
    datasets.append(Dataset("ontouml_non_classroom_until_2018", ontouml_non_classroom_until_2018))

    ontouml_non_classroom_after_2019 = [model for model in ontouml_non_classroom if model.year >= 2019]
    datasets.append(Dataset("ontouml_non_classroom_after_2019", ontouml_non_classroom_after_2019))

    return datasets


def calculate_and_save_datasets_statistics(datasets):
    for dataset in datasets:
        save_dataset_info(dataset)

        dataset.calculate_dataset_statistics()
        dataset.calculate_models_statistics()
        dataset.save_models_statistics_to_csv(OUTPUT_DIR_02)


def load_models_data():
    """Load model data and count stereotypes for each model."""
    models_list = instantiate_models_from_csv(os.path.join(OUTPUT_DIR_01, "models_data.csv"),
                                              os.path.join(OUTPUT_DIR_01,
                                                           "query_count_number_classes_relations_consolidated.csv"))

    class_csv = os.path.join(OUTPUT_DIR_01, "query_get_all_class_stereotypes_consolidated.csv")
    relation_csv = os.path.join(OUTPUT_DIR_01, "query_get_all_relation_stereotypes_consolidated.csv")

    # Count stereotypes and calculate 'none' for each model
    for model in models_list:
        model.count_stereotypes("class", class_csv)
        model.count_stereotypes("relation", relation_csv)
        model.calculate_none()

    return models_list


def save_dataset_info(dataset):
    dataset.save_dataset_general_data_csv(OUTPUT_DIR_02)
    dataset.save_dataset_class_data_csv(OUTPUT_DIR_02)
    dataset.save_dataset_relation_data_csv(OUTPUT_DIR_02)


def calculate_and_save_datasets_statistics_outliers(datasets):

    # Initialize outlier lists to avoid UnboundLocalError if no outliers are found
    ontouml_all_outliers = []
    ontouml_non_classroom_outliers = []
    ontouml_classroom_outliers = []

    # Identify outliers for each dataset
    for dataset in datasets:
        if dataset.name == 'ontouml_all':
            ontouml_all_outliers = dataset.identify_outliers()
        if dataset.name == 'ontouml_non_classroom':
            ontouml_non_classroom_outliers = dataset.identify_outliers()
        if dataset.name == 'ontouml_classroom':
            ontouml_classroom_outliers = dataset.identify_outliers()

    # Create new datasets without the identified outliers
    no_outliers_datasets = []
    for dataset in datasets:
        if 'non_classroom' in dataset.name:
            no_outliers_datasets.append(dataset.fork_without_outliers(ontouml_non_classroom_outliers))
        elif 'classroom' in dataset.name:
            no_outliers_datasets.append(dataset.fork_without_outliers(ontouml_classroom_outliers))
        elif dataset.name == 'ontouml_all':
            no_outliers_datasets.append(dataset.fork_without_outliers(ontouml_all_outliers))
        else:
            logger.warning(f"Dataset {dataset.name} had no outliers cleaned.")

    # Calculate and save statistics for the datasets without outliers
    calculate_and_save_datasets_statistics(no_outliers_datasets)

    # Combine original datasets with filtered ones and save combined statistics
    all_datasets = datasets + no_outliers_datasets
    save_datasets_statistics_to_csv(all_datasets, OUTPUT_DIR_02)

    return all_datasets


def calculate_and_save_datasets_stereotypes_statistics(all_datasets):
    pass


if __name__ == "__main__":
    # all_models = load_data_from_catalog(CATALOG_PATH)   # Uncomment to load models
    # query_data(all_models)     # Uncomment to query stereotypes

    all_models = load_models_data()  # Load model data and count stereotypes
    datasets = create_specific_datasets_instances(all_models)
    calculate_and_save_datasets_statistics(datasets)
    all_datasets = calculate_and_save_datasets_statistics_outliers(datasets)
    calculate_and_save_datasets_stereotypes_statistics(all_datasets)
