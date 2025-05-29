import os
from google.cloud import storage

def upload_folder_to_bucket(bucket_name, source_folder, destination_folder=""):
    client = storage.Client()
    bucket = client.bucket(bucket_name)

    for root, _, files in os.walk(source_folder):
        for file in files:
            local_path = os.path.join(root, file)
            relative_path = os.path.relpath(local_path, source_folder)
            blob_path = os.path.join(destination_folder, relative_path)

            blob = bucket.blob(blob_path)
            blob.upload_from_filename(local_path)
            print(f"✅ Uploaded {local_path} to gs://{bucket_name}/{blob_path}")

if __name__ == "__main__":
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "./infra/gcp/gcp_service_account.json"  # ou via variable ENV
    BUCKET_NAME = os.getenv("GCS_BUCKET", "my-olap-bucket-dev")

    upload_folder_to_bucket(BUCKET_NAME, "data/imported_stripe_data", "stripe_data")
    upload_folder_to_bucket(BUCKET_NAME, "data/db_dump", "db_dumps")
