import pandas as pd
import re
from io import BytesIO
from google.cloud import storage
from google.cloud import bigquery
import logging

def append_gcs_file_with_year(dataset_current: str, 
                              table_name_current: str, 
                              bucket_name_old: str, 
                              blob_path_old: str, 
                              current_df: pd.DataFrame, 
                              columns_to_drop_duplicates: list = None) -> pd.DataFrame:
    """
    Downloads a file from GCS, extracts year from filename, adds it as a column, and concatenates with an in-memory DataFrame.

    Args:
        dataset_current (str): Name of the current dataset.
        table_name_current (str): Table name for schema reference.
        bucket_name_old (str): GCS bucket name.
        blob_path_old (str): Path to the file in the bucket.
        current_df (pd.DataFrame): The DataFrame already in memory.
        columns_to_drop_duplicates (list, optional): Columns to use for dropping duplicates.

    Returns:
        pd.DataFrame: Concatenated DataFrame.
    """

    logging.info(f"Starting append process for blob: {blob_path_old} from bucket: {bucket_name_old}")

    # Get old file from historical bucket
    client = storage.Client()
    bucket = client.bucket(bucket_name_old)
    blob = bucket.blob(blob_path_old)
    
    logging.info(f"Downloading blob: {blob_path_old}")
    old_df = pd.read_csv(BytesIO(blob.download_as_bytes()))
    logging.info(f"Downloaded blob with shape: {old_df.shape}")

    # Extract year string from filename like 'star_assessment_results_24-25.csv'
    match = re.search(r'(\d{2}-\d{2})(?=\.csv$)', blob_path_old)
    year_value = match.group(1) if match else None

    if year_value:
        old_df['year'] = year_value
        logging.info(f"Extracted year: {year_value} from filename")
    else:
        logging.error(f"Could not extract year from filename: {blob_path_old}")
        raise ValueError(f"Could not extract year from filename: {blob_path_old}")

    # Normalize schema to match BigQuery
    logging.info(f"Fetching BQ schema for {dataset_current}.{table_name_current}")
    bq_types = get_bq_schema("icef-437920", dataset_current, table_name_current)
    pandas_dtypes = map_bq_to_pandas(bq_types)
    filtered_dtypes = {col: dtype for col, dtype in pandas_dtypes.items() if col in old_df.columns}
    
    logging.info(f"Casting DataFrame to match BQ schema: {list(filtered_dtypes.items())}")
    old_df = cast_df_to_bq_types(old_df, filtered_dtypes)

    # Combine and drop duplicates
    logging.info(f"Concatenating current data (shape: {current_df.shape}) with old data (shape: {old_df.shape})")
    final = pd.concat([current_df, old_df], ignore_index=True)

    if columns_to_drop_duplicates:
        original_shape = final.shape
        final = final.drop_duplicates(subset=columns_to_drop_duplicates)
        logging.info(f"Dropped duplicates using columns {columns_to_drop_duplicates}. Shape before: {original_shape}, after: {final.shape}")
    else:
        logging.info("No columns specified for dropping duplicates. Skipping deduplication.")

    logging.info(f"Final DataFrame shape after append: {final.shape}")
    return final



def get_bq_schema(project_id, dataset_id, table_name):
    client = bigquery.Client(project=project_id)
    table = client.get_table(f"{project_id}.{dataset_id}.{table_name}")
    return {field.name: field.field_type for field in table.schema}


def map_bq_to_pandas(bq_types):
    type_map = {
        "STRING": "string",
        "INTEGER": "Int64",  # nullable
        "INT64": "Int64",
        "FLOAT": "float64",
        "FLOAT64": "float64",
        "BOOLEAN": "boolean",
        "DATE": "datetime64[ns]",
        "DATETIME": "datetime64[ns]",
        "TIMESTAMP": "datetime64[ns]",
    }
    return {col: type_map.get(bq_type, "object") for col, bq_type in bq_types.items()}

def cast_df_to_bq_types(df, dtype_map):
    return df.astype(dtype_map, errors='ignore')

# final_df = append_gcs_file_with_year("historicalbucket-icefschools-1", "star_assessment_results_24-25.csv", df)

