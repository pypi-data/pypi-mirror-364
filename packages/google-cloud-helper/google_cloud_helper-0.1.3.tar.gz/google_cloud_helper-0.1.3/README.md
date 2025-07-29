# google-cloud-helper

This repository contains common functions for easy access to Google Cloud Infrastructure, such as Big Query or Google buckets.


## Example Usage

```python
from google_cloud_helper.BigQueryHelper import BigQueryHelper
from google_cloud_helper.GoogleBucketHelper import GoogleBucketHelper
from google_cloud_helper.SecretManagerHelper import SecretManagerHelper

# BigQuery
bq_helper = BigQueryHelper("your-gcp-project-id")
exists = bq_helper.table_exists("your-gcp-project-id.dataset.table")
print(f"Table exists: {exists}")

# Google Cloud Storage
bucket_helper = GoogleBucketHelper("your-gcp-project-id")
bucket_exists = bucket_helper.bucket_exists("your-bucket-name")
print(f"Bucket exists: {bucket_exists}")

# Secret Manager
secret_helper = SecretManagerHelper()
my_secret = secret_helper.get_secret("your-gcp-project-id", "your-secret-id")
print("Successfully retrieved secret!")
```

## Available Functions

### BigQueryHelper

| Function | Description |
| :--- | :--- |
| `table_exists(table_id)` | Checks if a specific BigQuery table exists. |
| `create_dataset(dataset_id)` | Creates a new BigQuery dataset if it doesn't already exist. |
| `delete_table(table_id)` | Deletes a BigQuery table.
| `create_table_from_df(...)` | Creates and populates a table from a pandas DataFrame, with options for partitioning and clustering. |
| `upload_df_to_table(table_id, df)` | Appends a pandas DataFrame to an existing BigQuery table. |
| `incremental_insert_with_deduplication(...)` | Inserts new rows from a DataFrame, avoiding duplicates based on a unique key. |
| `generate_bigquery_schema(df)` | Infers a BigQuery schema from a pandas DataFrame. |

### GoogleBucketHelper

| Function | Description |
| :--- | :--- |
| `download_as_text(bucket, path)` | Downloads a file from a Google Cloud Storage bucket as text. |
| `bucket_exists(bucket_name)` | Checks if a specific Google Cloud Storage bucket exists. |

### SecretManagerHelper

| Function | Description |
| :--- | :--- |
| `get_secret(project_id, secret_id)` | Retrieves the latest version of a secret from Secret Manager. |

## Testing

To run the tests, execute the following command:

```
uv run pytest
```
