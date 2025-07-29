from google.cloud import exceptions, storage


class GoogleBucketHelper:

    def __init__(self, project_id: str) -> None:
        """Initializes the GoogleBucketHelper.

        Args:
            project_id: The Google Cloud project ID.
        """
        self.client = storage.Client(project=project_id)

    def download_as_text(self, bucket_name: str, path: str) -> str:
        """Reads a file from a Google Cloud Storage bucket and returns it as string

        Args:
            bucket_name: The name of the bucket.
            path: The path to the file in the bucket.
        """
        bucket = self.client.bucket(bucket_name)
        blob = bucket.blob(path)
        return blob.download_as_text()

    def exists_bucket(self, bucket_name: str) -> bool:
        """Checks if a Google Cloud Storage bucket exists.

        Args:
            bucket_name: The name of the bucket.

        Returns:
            True if the bucket exists, False otherwise.
        """
        try:
            self.client.get_bucket(bucket_name)
            return True
        except exceptions.NotFound:
            return False
