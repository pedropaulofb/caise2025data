import csv
import gzip
import os
import pickle
import time
from typing import Union

from loguru import logger
from ontouml_models_lib import Catalog, OntologyDevelopmentContext, Query, Model, OntologyRepresentationStyle

from src.utils import save_object, load_object


def load_and_save_catalog_models(input_catalog_path: str, output_dir: str):
    """Load models from an OntoUML/UFO catalog and save them to an output directory."""
    # Load the catalog models
    catalog = Catalog(input_catalog_path)

    # Save the loaded models to the specified output directory
    save_object(catalog.models, output_dir, "loaded_models", "Loaded catalog models")

    # Return the loaded list of models
    return catalog.models


def generate_list_models_data_csv(input_models_list, output_file_path):
    input_models_list = load_object(input_models_list, "list of models")

    # Normalizing RELEASE DATE, creating IS_CLASSROOM attribute, and preparing data to be saved
    models_data = []
    for model in input_models_list:

        # IMPORTANT: Only OntoUML models. UFO-only models are discarded.
        if OntologyRepresentationStyle.ONTOUML_STYLE not in model.representationStyle:
            continue

        model.modified = model.issued if not model.modified else model.modified
        model.is_classroom = True if OntologyDevelopmentContext.CLASSROOM in model.context else False
        models_data.append((model.id, model.modified, model.is_classroom))

    # Generating CSV output
    header = ['model', 'year', 'is_classroom']

    # Open the CSV file in write mode
    with open(output_file_path, 'w', newline='') as file:
        writer = csv.writer(file)

        # Write the header
        writer.writerow(header)

        # Write the data (each tuple as a row)
        writer.writerows(models_data)

    logger.success(f"Models' data successfully saved in {output_file_path}.")


def query_models(models_to_query: Union[list[Model], str], queries_dir: str, output_dir: str):
    # Load models from file, if necessary

    models_to_query = load_object(models_to_query, "models to query")

    # Load and execute queries on the filtered models
    queries = Query.load_queries(queries_dir)

    for query in queries:
        start_time = time.perf_counter()
        query.execute_on_models(models_to_query, output_dir)
        end_time = time.perf_counter()
        elapsed_time_ms = (end_time - start_time) * 1000
        logger.info(f"Query {query.name} took {elapsed_time_ms:.2f} ms to perform.")
