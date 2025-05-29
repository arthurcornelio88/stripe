provider "google" {
  project     = "stripe-b2-gcp"
  region      = "europe-west1"
  credentials = file("gcp_service_account.json")
}

resource "google_storage_bucket" "oltp_data_bucket" {
  name     = "stripe-oltp-bucket-prod"
  location = "EU"
  force_destroy = true

  versioning {
    enabled = true
  }
}


