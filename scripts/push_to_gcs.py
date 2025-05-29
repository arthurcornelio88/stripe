import os
import sys
from google.cloud import storage
from datetime import datetime, timezone

def upload_folder_to_bucket(bucket_name, source_folder, destination_folder=""):
    client = storage.Client()
    bucket = client.bucket(bucket_name)

    for root, _, files in os.walk(source_folder):
        for file in files:
            local_path = os.path.join(root, file)
            relative_path = os.path.relpath(local_path, source_folder)
            
            # Utilise '/' même sur Windows pour avoir des chemins valides GCS
            blob_path = os.path.join(destination_folder, relative_path).replace(os.sep, "/")
            
            blob = bucket.blob(blob_path)
            blob.upload_from_filename(local_path)
            print(f"✅ Uploaded {local_path} to gs://{bucket_name}/{blob_path}")

if __name__ == "__main__":
    creds_path = "./infra/gcp/gcp_service_account.json"

    if not os.path.exists(creds_path):
        print(f"❌ Credential file not found: {creds_path}")
        sys.exit(1)

    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = creds_path

    BUCKET_NAME = "stripe-oltp-bucket-prod"

    print("🚀 Uploading local data folders to GCS bucket...")

    # ➤ Uploader les dumps dans: dump/
    upload_folder_to_bucket(BUCKET_NAME, "data/db_dump", destination_folder="dump")

    # ➤ Uploader les données importées dans: imported_data/{timestamp}/
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    gcs_imported_prefix = f"imported_data/{timestamp}"
    upload_folder_to_bucket(BUCKET_NAME, "data/imported_stripe_data", destination_folder=gcs_imported_prefix)
